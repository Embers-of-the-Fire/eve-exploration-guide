from __future__ import annotations

from contextlib import redirect_stdout
import io
from pathlib import Path
import pickle
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from eve_loc_fuzz.__main__ import main
from eve_loc_fuzz.search import (
    DEFAULT_LOCALIZATION_SUBDIR,
    FALLBACK_LOCALIZATION_SUBDIR,
    resolve_localization_dir,
    resolve_languages,
    search_localizations,
)


def write_localization_pickle(
    localization_dir: Path,
    lang: str,
    entries: dict[int, list[object]],
) -> None:
    localization_dir.mkdir(parents=True, exist_ok=True)
    pickle_path = localization_dir / f"localization_fsd_{lang}.pickle"
    pickle_path.write_bytes(pickle.dumps((lang, entries)))


class ResolveLocalizationDirTests(unittest.TestCase):
    def test_prefers_primary_cache_path(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            primary_dir = workspace_path / DEFAULT_LOCALIZATION_SUBDIR
            fallback_dir = workspace_path / FALLBACK_LOCALIZATION_SUBDIR
            primary_dir.mkdir(parents=True)
            fallback_dir.mkdir(parents=True)

            self.assertEqual(
                resolve_localization_dir(None, str(workspace_path)),
                primary_dir,
            )

    def test_falls_back_to_eve_docs_generator_cache_path(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            fallback_dir = workspace_path / FALLBACK_LOCALIZATION_SUBDIR
            fallback_dir.mkdir(parents=True)

            self.assertEqual(
                resolve_localization_dir(None, str(workspace_path)),
                fallback_dir,
            )


class SearchLocalizationsTests(unittest.TestCase):
    def test_resolve_languages_rejects_missing_languages(self):
        with self.assertRaisesRegex(ValueError, "At least one language is required"):
            resolve_languages(None)

    def test_search_localizations_sorts_matches_by_text_length(self):
        with TemporaryDirectory() as tmp_dir:
            localization_dir = Path(tmp_dir)
            write_localization_pickle(
                localization_dir,
                "en-us",
                {
                    300: ["Warp to"],
                    100: ["Warp"],
                    200: ["Warp drive active"],
                    400: [],
                    500: [None],
                },
            )

            matches = search_localizations(
                "warp",
                languages=["en-us"],
                localization_dir=localization_dir,
            )

            self.assertEqual([match.loc_id for match in matches], [100, 300, 200])
            self.assertEqual(
                [match.text for match in matches],
                ["Warp", "Warp to", "Warp drive active"],
            )

    def test_main_prints_sorted_matches_for_one_language(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            localization_dir = workspace_path / FALLBACK_LOCALIZATION_SUBDIR
            write_localization_pickle(
                localization_dir,
                "en-us",
                {
                    300: ["Warp to"],
                    100: ["Warp"],
                    200: ["Warp drive active"],
                },
            )
            write_localization_pickle(localization_dir, "zh", {10: ["跃迁"]})

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

    def test_main_prints_language_prefix_when_searching_multiple_languages(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            localization_dir = workspace_path / FALLBACK_LOCALIZATION_SUBDIR
            write_localization_pickle(localization_dir, "en-us", {100: ["Ship"]})
            write_localization_pickle(localization_dir, "zh", {200: ["ship"]})

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
                ["[en-us] 100\tShip", "[zh] 200\tship"],
            )

    def test_main_accepts_pnpm_style_leading_separator(self):
        with TemporaryDirectory() as tmp_dir:
            workspace_path = Path(tmp_dir) / "workspace"
            localization_dir = workspace_path / FALLBACK_LOCALIZATION_SUBDIR
            write_localization_pickle(localization_dir, "en-us", {100: ["Warp"]})
            write_localization_pickle(localization_dir, "zh", {200: ["跃迁"]})

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
            localization_dir = workspace_path / FALLBACK_LOCALIZATION_SUBDIR
            write_localization_pickle(localization_dir, "en-us", {100: ["Warp"]})

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
