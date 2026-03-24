from __future__ import annotations

import os
from pathlib import Path
import shlex


def find_dotenv(*, usecwd: bool = False) -> str:
    start = Path.cwd() if usecwd else Path(__file__).resolve().parent

    for candidate_dir in (start, *start.parents):
        dotenv_path = candidate_dir / ".env"
        if dotenv_path.is_file():
            return str(dotenv_path)

    return ""


def load_dotenv(dotenv_path: str) -> bool:
    if not dotenv_path:
        return False

    try:
        raw_lines = Path(dotenv_path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return False

    loaded = False
    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].lstrip()

        key, separator, raw_value = line.partition("=")
        if not separator:
            continue

        key = key.strip()
        if not key or key in os.environ:
            continue

        os.environ[key] = parse_dotenv_value(raw_value)
        loaded = True

    return loaded


def parse_dotenv_value(raw_value: str) -> str:
    value = raw_value.strip()
    if not value:
        return ""

    if value[0] in {'"', "'"}:
        try:
            parsed = shlex.split(value, comments=True, posix=True)
        except ValueError:
            return value
        return parsed[0] if parsed else ""

    return value.split(" #", 1)[0].rstrip()
