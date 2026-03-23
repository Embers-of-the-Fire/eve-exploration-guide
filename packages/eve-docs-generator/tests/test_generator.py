from __future__ import annotations

import contextlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from eve_docs_generator.generator import resolve_cli_path


class ResolveCliPathTests(unittest.TestCase):
    def test_resolves_new_relative_paths_against_current_working_directory(self):
        with TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)

            with contextlib.chdir(cwd):
                resolved = resolve_cli_path("build/output/data.json")

            self.assertEqual(resolved, (cwd / "build/output/data.json").resolve())
