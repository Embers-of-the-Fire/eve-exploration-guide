from __future__ import annotations

import os
from pathlib import Path
import pickle
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from eve_docs_generator.source_workspace import (
    DEFAULT_RESOURCE_BASE_URL,
    DEFAULT_RESOURCE_CACHE_SUBDIR,
    LOC_EN_RESOURCE,
    LOC_ZH_RESOURCE,
    RESOURCE_CACHE_ENV_VAR,
    ResourceIndex,
    WORKSPACE_CACHE_ENV_VAR,
    WORKSPACE_ENV_VAR,
    build_download_url,
    load_localizations,
    resolve_icon_bytes,
    resolve_resource_cache_dir,
    resolve_workspace_path,
    resolve_workspace_paths,
)


class FakeResourceIndex:
    def __init__(self, payloads: dict[str, bytes]):
        self._payloads = payloads

    def fetch_bytes(self, resource_path: str) -> bytes:
        try:
            return self._payloads[resource_path]
        except KeyError as error:
            raise FileNotFoundError(resource_path) from error


def resolve_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def build_resource_index(root: Path) -> ResourceIndex:
    resfileindex_path = root / "resfileindex.txt"
    cache_dir = root / "cache"
    resfileindex_path.write_text("", encoding="utf-8")
    return ResourceIndex(resfileindex_path, cache_dir)


class FakeFsdSource:
    def __init__(self, payloads: dict[str, object]):
        self._payloads = payloads

    def load(self, fsd_name: str):
        return self._payloads[fsd_name]


class ResourceIndexCachePathTests(unittest.TestCase):
    def test_rejects_absolute_cache_paths(self):
        with TemporaryDirectory() as tmp_dir:
            resource_index = build_resource_index(Path(tmp_dir))

            with self.assertRaisesRegex(ValueError, "within the configured cache"):
                resource_index.cache_path_for("/etc/passwd")

    def test_rejects_parent_traversal_cache_paths(self):
        with TemporaryDirectory() as tmp_dir:
            resource_index = build_resource_index(Path(tmp_dir))

            with self.assertRaisesRegex(ValueError, "within the configured cache"):
                resource_index.cache_path_for("../../outside.bin")


class ResolveWorkspaceTests(unittest.TestCase):
    def test_resolve_workspace_path_reads_environment_variable(self):
        with TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)

            with patch.dict(os.environ, {WORKSPACE_ENV_VAR: str(workspace)}):
                resolved = resolve_workspace_path(None, resolve_path)

            self.assertEqual(resolved, workspace.resolve())

    def test_resolve_workspace_paths_allows_explicit_inputs_without_workspace(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            resfileindex_path = root / "resfileindex.txt"
            fsd_dir = root / "fsd"
            cache_dir = root / "cache"

            resfileindex_path.write_text("", encoding="utf-8")
            fsd_dir.mkdir()

            with patch.dict(os.environ, {WORKSPACE_ENV_VAR: ""}):
                workspace = resolve_workspace_paths(
                    workspace_arg=None,
                    resfileindex_arg=str(resfileindex_path),
                    fsd_dir_arg=str(fsd_dir),
                    start_ini_arg=None,
                    resource_cache_dir_arg=str(cache_dir),
                    resource_base_url=DEFAULT_RESOURCE_BASE_URL,
                    resolve_cli_path=resolve_path,
                )

            self.assertIsNone(workspace["workspace_root"])
            self.assertTrue(cache_dir.exists())

    def test_explicit_inputs_ignore_workspace_env_when_not_needed(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            resfileindex_path = root / "resfileindex.txt"
            fsd_dir = root / "fsd"

            resfileindex_path.write_text("", encoding="utf-8")
            fsd_dir.mkdir()

            with patch.dict(os.environ, {WORKSPACE_ENV_VAR: str(root / "missing")}):
                workspace = resolve_workspace_paths(
                    workspace_arg=None,
                    resfileindex_arg=str(resfileindex_path),
                    fsd_dir_arg=str(fsd_dir),
                    start_ini_arg=None,
                    resource_cache_dir_arg=None,
                    resource_base_url=DEFAULT_RESOURCE_BASE_URL,
                    resolve_cli_path=resolve_path,
                )

            self.assertIsNone(workspace["workspace_root"])

    def test_workspace_defaults_resource_cache_under_workspace_root(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_root = Path(tmp_dir)
            (workspace_root / "resfileindex.txt").write_text("", encoding="utf-8")
            (workspace_root / "fsd").mkdir()

            with patch.dict(
                os.environ,
                {
                    WORKSPACE_ENV_VAR: "",
                    RESOURCE_CACHE_ENV_VAR: "",
                    WORKSPACE_CACHE_ENV_VAR: "",
                },
                clear=False,
            ):
                workspace = resolve_workspace_paths(
                    workspace_arg=str(workspace_root),
                    resfileindex_arg=None,
                    fsd_dir_arg=None,
                    start_ini_arg=None,
                    resource_cache_dir_arg=None,
                    resource_base_url=DEFAULT_RESOURCE_BASE_URL,
                    resolve_cli_path=resolve_path,
                )

            expected_cache_root = (
                workspace_root.resolve() / DEFAULT_RESOURCE_CACHE_SUBDIR
            )
            self.assertEqual(
                workspace["resource_index"].cache_path_for("res:/ui/icon.png"),
                expected_cache_root / "ui" / "icon.png",
            )

    def test_resource_cache_env_var_overrides_workspace_default(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_root = Path(tmp_dir) / "workspace"
            cache_dir = Path(tmp_dir) / "cache"
            workspace_root.mkdir()

            resolved = None
            with patch.dict(
                os.environ,
                {RESOURCE_CACHE_ENV_VAR: str(cache_dir), WORKSPACE_CACHE_ENV_VAR: ""},
                clear=False,
            ):
                resolved = resolve_resource_cache_dir(
                    resource_cache_dir_arg=None,
                    workspace_root=workspace_root,
                    resolve_cli_path=resolve_path,
                )

            self.assertEqual(resolved, cache_dir.resolve())

    def test_cli_resource_cache_overrides_env_var(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_root = Path(tmp_dir) / "workspace"
            workspace_root.mkdir()
            cli_cache_dir = Path(tmp_dir) / "cli-cache"

            with patch.dict(
                os.environ,
                {
                    RESOURCE_CACHE_ENV_VAR: str(Path(tmp_dir) / "env-cache"),
                    WORKSPACE_CACHE_ENV_VAR: str(Path(tmp_dir) / "legacy-env-cache"),
                },
                clear=False,
            ):
                resolved = resolve_resource_cache_dir(
                    resource_cache_dir_arg=str(cli_cache_dir),
                    workspace_root=workspace_root,
                    resolve_cli_path=resolve_path,
                )

            self.assertEqual(resolved, cli_cache_dir.resolve())

    def test_explicit_start_ini_must_exist(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            resfileindex_path = root / "resfileindex.txt"
            fsd_dir = root / "fsd"

            resfileindex_path.write_text("", encoding="utf-8")
            fsd_dir.mkdir()

            with self.assertRaisesRegex(
                FileNotFoundError,
                "start.ini path does not exist or is not a file",
            ):
                resolve_workspace_paths(
                    workspace_arg=None,
                    resfileindex_arg=str(resfileindex_path),
                    fsd_dir_arg=str(fsd_dir),
                    start_ini_arg=str(root / "missing-start.ini"),
                    resource_cache_dir_arg=None,
                    resource_base_url=DEFAULT_RESOURCE_BASE_URL,
                    resolve_cli_path=resolve_path,
                )

    def test_explicit_start_ini_must_be_a_file(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            resfileindex_path = root / "resfileindex.txt"
            fsd_dir = root / "fsd"
            start_ini_dir = root / "start.ini"

            resfileindex_path.write_text("", encoding="utf-8")
            fsd_dir.mkdir()
            start_ini_dir.mkdir()

            with self.assertRaisesRegex(
                FileNotFoundError,
                "start.ini path does not exist or is not a file",
            ):
                resolve_workspace_paths(
                    workspace_arg=None,
                    resfileindex_arg=str(resfileindex_path),
                    fsd_dir_arg=str(fsd_dir),
                    start_ini_arg=str(start_ini_dir),
                    resource_cache_dir_arg=None,
                    resource_base_url=DEFAULT_RESOURCE_BASE_URL,
                    resolve_cli_path=resolve_path,
                )


class BuildDownloadUrlTests(unittest.TestCase):
    def test_rejects_absolute_or_cross_origin_urls(self):
        for resource_url in (
            "https://evil.invalid/payload",
            "file:///tmp/payload",
            "//evil.invalid/payload",
        ):
            with self.subTest(resource_url=resource_url):
                with self.assertRaisesRegex(ValueError, "relative|escaped"):
                    build_download_url(DEFAULT_RESOURCE_BASE_URL, resource_url)

    def test_resolves_relative_urls_against_base_url(self):
        self.assertEqual(
            build_download_url(DEFAULT_RESOURCE_BASE_URL, "/2c/payload"),
            "https://resources.eveonline.com/2c/payload",
        )

    def test_rejects_resource_urls_that_escape_base_path(self):
        with self.assertRaisesRegex(ValueError, "escaped"):
            build_download_url(
                "https://mirror.example/resources/",
                "../../etc/passwd",
            )

    def test_treats_base_url_without_trailing_slash_as_directory(self):
        self.assertEqual(
            build_download_url(
                "https://mirror.example/resources",
                "icons/payload.bin",
            ),
            "https://mirror.example/resources/icons/payload.bin",
        )


class LoadLocalizationsTests(unittest.TestCase):
    def test_treats_empty_sequences_as_missing(self):
        resource_index = FakeResourceIndex(
            {
                LOC_EN_RESOURCE: pickle.dumps(
                    (
                        None,
                        {
                            1: [],
                            2: ["Ship"],
                            3: [],
                        },
                    )
                ),
                LOC_ZH_RESOURCE: pickle.dumps(
                    (
                        None,
                        {
                            1: (),
                            2: (),
                            3: ["舰船"],
                        },
                    )
                ),
            }
        )

        records = load_localizations(resource_index, {1, 2, 3})

        self.assertNotIn(1, records)
        self.assertEqual(records[2].en, "Ship")
        self.assertEqual(records[2].zh_cn, "")
        self.assertEqual(records[3].en, "")
        self.assertEqual(records[3].zh_cn, "舰船")

    def test_rejects_pickles_that_require_global_class_loading(self):
        resource_index = FakeResourceIndex(
            {
                LOC_EN_RESOURCE: pickle.dumps((None, {1: RuntimeError("boom")})),
                LOC_ZH_RESOURCE: pickle.dumps((None, {1: ["正常"]})),
            }
        )

        with self.assertRaisesRegex(ValueError, "Invalid localization pickle payload"):
            load_localizations(resource_index, {1})


class ResolveIconBytesTests(unittest.TestCase):
    def test_returns_none_when_icon_resource_is_missing_from_index(self):
        fsd = FakeFsdSource({"iconids": {7: {"iconFile": "res:/ui/icon.png"}}})
        resource_index = FakeResourceIndex({})

        self.assertIsNone(
            resolve_icon_bytes(fsd=fsd, resource_index=resource_index, icon_id=7)
        )
