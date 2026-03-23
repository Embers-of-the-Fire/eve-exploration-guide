from __future__ import annotations

import contextlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from eve_docs_generator.generator import resolve_cli_path


class ResolveCliPathTests(unittest.TestCase):
    def test_preserves_absolute_paths(self):
        with TemporaryDirectory() as tmp_dir:
            absolute_path = (Path(tmp_dir) / "data.json").resolve()

            self.assertEqual(resolve_cli_path(str(absolute_path)), absolute_path)

    def test_resolves_new_relative_paths_against_current_working_directory(self):
        with TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)

            with contextlib.chdir(cwd):
                resolved = resolve_cli_path("build/output/data.json")

            self.assertEqual(resolved, (cwd / "build/output/data.json").resolve())

    def test_expands_tilde_paths(self):
        expected = (Path.home() / "data.json").resolve()

        self.assertEqual(resolve_cli_path("~/data.json"), expected)
