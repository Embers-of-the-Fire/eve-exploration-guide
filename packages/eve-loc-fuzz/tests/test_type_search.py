from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import pickle
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import msgpack

from eve_loc_fuzz.fsd import resolve_fsd_dir
from eve_loc_fuzz.type_main import main
from eve_loc_fuzz.type_search import search_type_names


def write_localization_pickle(
    localization_dir: Path,
    lang: str,
    entries: dict[int, list[object]],
) -> None:
    localization_dir.mkdir(parents=True, exist_ok=True)
    pickle_path = localization_dir / f"localization_fsd_{lang}.pickle"
    pickle_path.write_bytes(pickle.dumps((lang, entries)))


def write_types_fsd(
    workspace_path: Path,
    payload: dict[object, object],
    *,
    suffix: str = ".json",
) -> Path:
    fsd_dir = workspace_path / "fsd"
    fsd_dir.mkdir(parents=True, exist_ok=True)

    if suffix == ".json":
        (fsd_dir / "types.json").write_text(json.dumps(payload), encoding="utf-8")
        return fsd_dir

    if suffix == ".msgpack":
        (fsd_dir / "types.msgpack").write_bytes(
            msgpack.packb(payload, use_bin_type=True)
        )
        return fsd_dir

    raise ValueError(f"Unsupported FSD suffix for test fixture: {suffix}")


class ResolveFsdDirTests(unittest.TestCase):
    def test_prefers_workspace_fsd_subdirectory(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            fsd_dir = workspace_path / "fsd"
            fsd_dir.mkdir(parents=True)

            self.assertEqual(resolve_fsd_dir(None, str(workspace_path)), fsd_dir)

    def test_falls_back_to_workspace_root_when_types_file_exists_there(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            workspace_path.mkdir(parents=True)
            (workspace_path / "types.json").write_text("{}", encoding="utf-8")

            self.assertEqual(
                resolve_fsd_dir(None, str(workspace_path)),
                workspace_path,
            )


class SearchTypeNamesTests(unittest.TestCase):
    def test_search_type_names_reads_msgpack_with_integer_keys(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            fsd_dir = write_types_fsd(
                workspace_path,
                {
                    300: {"typeID": 300, "typeNameID": 30},
                    100: {"typeID": 100, "typeNameID": 10},
                    200: {"typeID": 200, "typeNameID": 20},
                },
                suffix=".msgpack",
            )
            localization_dir = (
                workspace_path / ".cache" / "resources" / "localizationfsd"
            )
            write_localization_pickle(
                localization_dir,
                "en-us",
                {
                    10: ["Warp"],
                    20: ["Warp drive active"],
                    30: ["Warp to"],
                },
            )

            matches = search_type_names(
                "warp",
                languages=["en-us"],
                localization_dir=localization_dir,
                fsd_dir=fsd_dir,
            )

            self.assertEqual([match.type_id for match in matches], [100, 300, 200])
            self.assertEqual(
                [match.name for match in matches],
                ["Warp", "Warp to", "Warp drive active"],
            )

    def test_search_type_names_sorts_matches_by_name_length(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            fsd_dir = write_types_fsd(
                workspace_path,
                {
                    300: {"typeID": 300, "typeNameID": 30},
                    100: {"typeID": 100, "typeNameID": 10},
                    200: {"typeID": 200, "typeNameID": 20},
                    400: {"typeID": 400},
                },
            )
            localization_dir = (
                workspace_path / ".cache" / "resources" / "localizationfsd"
            )
            write_localization_pickle(
                localization_dir,
                "en-us",
                {
                    10: ["Warp"],
                    20: ["Warp drive active"],
                    30: ["Warp to"],
                },
            )

            matches = search_type_names(
                "warp",
                languages=["en-us"],
                localization_dir=localization_dir,
                fsd_dir=fsd_dir,
            )

            self.assertEqual([match.type_id for match in matches], [100, 300, 200])
            self.assertEqual(
                [match.name for match in matches],
                ["Warp", "Warp to", "Warp drive active"],
            )

    def test_main_prints_sorted_matches_for_one_language(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            fsd_dir = write_types_fsd(
                workspace_path,
                {
                    300: {"typeID": 300, "typeNameID": 30},
                    100: {"typeID": 100, "typeNameID": 10},
                    200: {"typeID": 200, "typeNameID": 20},
                },
            )
            localization_dir = (
                workspace_path / ".cache" / "resources" / "localizationfsd"
            )
            write_localization_pickle(
                localization_dir,
                "en-us",
                {
                    10: ["Warp"],
                    20: ["Warp drive active"],
                    30: ["Warp to"],
                },
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "warp",
                        "--workspace",
                        str(workspace_path),
                        "--lang",
                        "en-us",
                        "--limit",
                        "2",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                output.getvalue().splitlines(), ["100\tWarp", "300\tWarp to"]
            )
            self.assertEqual(resolve_fsd_dir(None, str(workspace_path)), fsd_dir)

    def test_main_prints_language_prefix_when_searching_multiple_languages(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            write_types_fsd(
                workspace_path,
                {
                    100: {"typeID": 100, "typeNameID": 10},
                    200: {"typeID": 200, "typeNameID": 20},
                },
            )
            localization_dir = (
                workspace_path / ".cache" / "resources" / "localizationfsd"
            )
            write_localization_pickle(
                localization_dir,
                "en-us",
                {
                    10: ["Ship"],
                    20: ["Warp Ship"],
                },
            )
            write_localization_pickle(
                localization_dir,
                "zh",
                {
                    10: ["ship"],
                    20: ["跃迁舰船"],
                },
            )

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main(
                    [
                        "ship",
                        "--workspace",
                        str(workspace_path),
                        "--lang",
                        "en-us",
                        "--lang",
                        "zh",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                output.getvalue().splitlines(),
                ["[en-us] 100\tShip", "[zh] 100\tship", "[en-us] 200\tWarp Ship"],
            )

    def test_main_accepts_pnpm_style_leading_separator(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            write_types_fsd(
                workspace_path,
                {
                    100: {"typeID": 100, "typeNameID": 10},
                },
            )
            localization_dir = (
                workspace_path / ".cache" / "resources" / "localizationfsd"
            )
            write_localization_pickle(localization_dir, "en-us", {10: ["Warp"]})

            output = io.StringIO()
            with redirect_stdout(output):
                with patch(
                    "sys.argv",
                    [
                        "python",
                        "--",
                        "warp",
                        "--workspace",
                        str(workspace_path),
                        "--lang",
                        "en-us",
                    ],
                ):
                    exit_code = main()

            self.assertEqual(exit_code, 0)
            self.assertEqual(output.getvalue().splitlines(), ["100\tWarp"])

    def test_main_requires_explicit_language(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            write_types_fsd(
                workspace_path,
                {
                    100: {"typeID": 100, "typeNameID": 10},
                },
            )
            localization_dir = (
                workspace_path / ".cache" / "resources" / "localizationfsd"
            )
            write_localization_pickle(localization_dir, "en-us", {10: ["Warp"]})

            stderr = io.StringIO()
            with self.assertRaises(SystemExit) as error:
                with patch("sys.stderr", stderr):
                    main(
                        [
                            "warp",
                            "--workspace",
                            str(workspace_path),
                        ]
                    )

            self.assertEqual(error.exception.code, 2)
