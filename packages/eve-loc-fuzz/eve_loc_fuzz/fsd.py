from __future__ import annotations

import json
from pathlib import Path

from .msgpack import loads as load_msgpack
from .search import resolve_cli_path, resolve_workspace_path

KNOWN_FSD_SUFFIXES = (
    ".msgpack",
    ".mpk",
    ".fsdbinary",
    ".bin",
    ".json",
)


def resolve_fsd_dir(
    fsd_dir_arg: str | None,
    workspace_arg: str | None,
) -> Path:
    if fsd_dir_arg:
        fsd_dir = resolve_cli_path(fsd_dir_arg)
        if not fsd_dir.exists() or not fsd_dir.is_dir():
            raise FileNotFoundError(
                f"FSD directory does not exist or is not a directory: {fsd_dir}"
            )
        return fsd_dir

    workspace_path = resolve_workspace_path(workspace_arg)
    candidate = workspace_path / "fsd"
    if candidate.exists() and candidate.is_dir():
        return candidate

    try:
        resolve_fsd_file(workspace_path, "types")
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"Could not find an FSD directory in workspace: {workspace_path}"
        ) from error

    return workspace_path


def resolve_fsd_file(fsd_dir: Path, fsd_name: str) -> Path:
    for suffix in KNOWN_FSD_SUFFIXES:
        candidate = fsd_dir / f"{fsd_name}{suffix}"
        if candidate.exists() and candidate.is_file():
            return candidate

    recursive_matches = sorted(
        path
        for path in fsd_dir.rglob(f"{fsd_name}*")
        if path.is_file() and path.stem == fsd_name
    )
    if recursive_matches:
        return recursive_matches[0]

    raise FileNotFoundError(f"Could not find FSD file for '{fsd_name}' in {fsd_dir}")


def load_fsd_payload(fsd_dir: Path, fsd_name: str):
    fsd_path = resolve_fsd_file(fsd_dir, fsd_name)
    return parse_structured_payload(fsd_path, fsd_path.read_bytes())


def parse_structured_payload(path: Path, raw_bytes: bytes):
    if path.suffix.lower() == ".json":
        return json.loads(raw_bytes.decode("utf-8"))

    try:
        return load_msgpack(raw_bytes)
    except Exception:
        try:
            return json.loads(raw_bytes.decode("utf-8"))
        except Exception as json_error:
            raise ValueError(
                f"Unable to parse structured FSD payload '{path}' as msgpack or JSON"
            ) from json_error
