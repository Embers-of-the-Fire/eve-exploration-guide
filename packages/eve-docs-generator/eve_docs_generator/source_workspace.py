from __future__ import annotations

import configparser
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import pickle
import time
from typing import Any
from urllib.parse import urljoin, urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .model import (
    BLUEPRINT_CATEGORY_ID,
    CategoryRecord,
    EveDataMetadata,
    GroupRecord,
    LocalizationRecord,
    MetaGroupRecord,
    ResourceEntry,
    ResolvedTypeImage,
    TypeRecord,
)
from .msgpack import loads as load_msgpack

DEFAULT_RESOURCE_BASE_URL = "https://resources.eveonline.com/"
DOWNLOAD_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    ),
}
DOWNLOAD_RETRY_ATTEMPTS = 4
DEFAULT_RESOURCE_CACHE_DIR = (
    Path(os.environ.get("TMPDIR", "/tmp"))
    / "eve-exploration-guide-eve-docs-resource-cache"
)
WORKSPACE_ENV_VAR = "EVE_DOCS_WORKSPACE"
KNOWN_FSD_SUFFIXES = (
    ".msgpack",
    ".mpk",
    ".fsdbinary",
    ".bin",
    ".json",
)
LOC_EN_RESOURCE = "res:/localizationfsd/localization_fsd_en-us.pickle"
LOC_ZH_RESOURCE = "res:/localizationfsd/localization_fsd_zh.pickle"


class FsdSource:
    def __init__(self, fsd_dir: Path):
        self._fsd_dir = fsd_dir
        self._cache: dict[str, Any] = {}

        if not self._fsd_dir.exists() or not self._fsd_dir.is_dir():
            raise FileNotFoundError(
                f"FSD directory does not exist or is not a directory: {self._fsd_dir}"
            )

    def load(self, fsd_name: str):
        if fsd_name in self._cache:
            return self._cache[fsd_name]

        fsd_path = resolve_fsd_file(self._fsd_dir, fsd_name)
        raw_bytes = fsd_path.read_bytes()
        parsed = parse_structured_payload(fsd_path, raw_bytes)
        self._cache[fsd_name] = parsed
        return parsed


class ResourceIndex:
    def __init__(
        self,
        resfileindex_path: Path,
        resource_cache_dir: Path,
        resource_base_url: str = DEFAULT_RESOURCE_BASE_URL,
    ):
        self._entries: dict[str, ResourceEntry] = {}
        self._resource_base_url = resource_base_url
        self._resource_cache_dir = resource_cache_dir
        self._resource_cache_dir.mkdir(parents=True, exist_ok=True)

        with resfileindex_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.reader(handle):
                if len(row) < 2:
                    continue

                resource_path = normalize_resource_path(row[0])
                if not resource_path:
                    continue

                checksum = row[2].strip() if len(row) >= 3 and row[2].strip() else None
                self._entries[resource_path] = ResourceEntry(
                    checksum=checksum,
                    file_name=PurePosixPath(resource_path).name,
                    resource_path=resource_path,
                    url=row[1].strip(),
                )

    def get_resource(self, resource_path: str) -> ResourceEntry | None:
        return self._entries.get(normalize_resource_path(resource_path))

    def get_resources(self, resource_folder: str) -> list[ResourceEntry]:
        normalized_folder = normalize_resource_path(resource_folder).rstrip("/")

        if not normalized_folder:
            return []

        prefix = f"{normalized_folder}/"
        return sorted(
            [entry for path, entry in self._entries.items() if path.startswith(prefix)],
            key=lambda entry: entry.file_name,
        )

    def fetch_bytes(self, resource_path: str) -> bytes:
        entry = self.get_resource(resource_path)
        if entry is None:
            raise FileNotFoundError(
                f"Resource not found in resfileindex: {resource_path}"
            )

        cache_path = self.cache_path_for(entry.resource_path)

        if cache_path.exists():
            payload = cache_path.read_bytes()
            verify_checksum(payload, entry)
            return payload

        download_url = build_download_url(self._resource_base_url, entry.url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        request = Request(download_url, headers=DOWNLOAD_HEADERS)

        for attempt in range(DOWNLOAD_RETRY_ATTEMPTS):
            try:
                with urlopen(request, timeout=60) as response:
                    payload = response.read()
                break
            except (HTTPError, OSError, URLError):
                if attempt == DOWNLOAD_RETRY_ATTEMPTS - 1:
                    raise
                time.sleep(2**attempt)

        verify_checksum(payload, entry)
        cache_path.write_bytes(payload)
        return payload

    def cache_path_for(self, resource_path: str) -> Path:
        normalized = normalize_resource_path(resource_path)

        if ":/" in normalized:
            normalized = normalized.split(":/", 1)[1]

        return self._resource_cache_dir / PurePosixPath(normalized)


def resolve_workspace_path(workspace_arg: str | None, resolve_cli_path):
    workspace_value = workspace_arg or os.environ.get(WORKSPACE_ENV_VAR)

    if not workspace_value:
        raise FileNotFoundError(
            "A TQ source workspace is required. Provide --workspace or set "
            f"{WORKSPACE_ENV_VAR}."
        )

    workspace_path = resolve_cli_path(workspace_value)
    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace path does not exist: {workspace_path}")
    return workspace_path


def resolve_workspace_paths(
    *,
    workspace_arg: str | None,
    resfileindex_arg: str | None,
    fsd_dir_arg: str | None,
    start_ini_arg: str | None,
    resource_cache_dir_arg: str | None,
    resource_base_url: str,
    resolve_cli_path,
):
    workspace_value = workspace_arg or os.environ.get(WORKSPACE_ENV_VAR)
    workspace_root = (
        resolve_workspace_path(workspace_arg, resolve_cli_path)
        if workspace_arg
        or (workspace_value and (not resfileindex_arg or not fsd_dir_arg))
        else None
    )
    resfileindex_path = (
        resolve_cli_path(resfileindex_arg)
        if resfileindex_arg
        else resolve_resfileindex_path(workspace_root)
    )
    fsd_dir = (
        resolve_cli_path(fsd_dir_arg)
        if fsd_dir_arg
        else resolve_fsd_dir(workspace_root)
    )
    start_ini_path = (
        resolve_cli_path(start_ini_arg)
        if start_ini_arg
        else resolve_start_ini_path(workspace_root)
    )
    resource_cache_dir = (
        resolve_cli_path(resource_cache_dir_arg)
        if resource_cache_dir_arg
        else DEFAULT_RESOURCE_CACHE_DIR
    )

    return {
        "fsd": FsdSource(fsd_dir),
        "metadata": load_data_metadata(start_ini_path),
        "resource_base_url": resource_base_url,
        "resource_index": ResourceIndex(
            resfileindex_path=resfileindex_path,
            resource_cache_dir=resource_cache_dir,
            resource_base_url=resource_base_url,
        ),
        "workspace_root": workspace_root,
    }


def resolve_resfileindex_path(workspace_root: Path | None) -> Path:
    if workspace_root is None:
        raise FileNotFoundError(
            "A workspace path or explicit --resfileindex is required"
        )

    path = workspace_root / "resfileindex.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"resfileindex.txt not found in workspace: {workspace_root}"
        )
    return path


def resolve_fsd_dir(workspace_root: Path | None) -> Path:
    if workspace_root is None:
        raise FileNotFoundError("A workspace path or explicit --fsd-dir is required")

    candidate = workspace_root / "fsd"
    if candidate.exists() and candidate.is_dir():
        return candidate

    for fsd_name in ("types", "groups", "categories", "metagroups"):
        try:
            resolve_fsd_file(workspace_root, fsd_name)
        except FileNotFoundError:
            break
    else:
        return workspace_root

    raise FileNotFoundError(
        f"Could not find an FSD directory in workspace: {workspace_root}"
    )


def resolve_start_ini_path(workspace_root: Path | None) -> Path | None:
    if workspace_root is None:
        return None

    path = workspace_root / "start.ini"
    return path if path.exists() else None


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


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str) -> Any:
        raise pickle.UnpicklingError(
            f"Localization payload cannot reference {module}.{name}"
        )


def load_localization_pickle(payload: bytes) -> dict[Any, Any]:
    try:
        parsed = RestrictedUnpickler(io.BytesIO(payload)).load()
    except (
        AttributeError,
        EOFError,
        ImportError,
        TypeError,
        ValueError,
        pickle.PickleError,
    ) as error:
        raise ValueError("Invalid localization pickle payload") from error

    if not isinstance(parsed, tuple) or len(parsed) != 2:
        raise ValueError("Invalid localization pickle payload")

    _, localization_data = parsed
    if not isinstance(localization_data, dict):
        raise ValueError("Invalid localization pickle payload")

    return localization_data


def load_data_metadata(start_ini_path: Path | None) -> EveDataMetadata:
    if start_ini_path is None:
        return EveDataMetadata(game_build=None, game_version=None)

    config = configparser.ConfigParser()
    config.read(start_ini_path, encoding="utf-8")

    return EveDataMetadata(
        game_build=config.get("main", "build", fallback=None),
        game_version=config.get("main", "version", fallback=None),
    )


def normalize_resource_path(resource_path: str) -> str:
    return resource_path.strip().replace("\\", "/").lower()


def build_download_url(resource_base_url: str, resource_url: str) -> str:
    parsed_resource_url = urlsplit(resource_url)
    if parsed_resource_url.scheme or parsed_resource_url.netloc:
        raise ValueError(
            "Resource URLs from resfileindex.txt must be relative to the "
            "configured resource base URL"
        )

    download_url = urljoin(resource_base_url, resource_url.lstrip("/"))
    parsed_base_url = urlsplit(resource_base_url)
    parsed_download_url = urlsplit(download_url)

    if (
        parsed_base_url.scheme and parsed_download_url.scheme != parsed_base_url.scheme
    ) or (
        parsed_base_url.netloc and parsed_download_url.netloc != parsed_base_url.netloc
    ):
        raise ValueError(
            "Resolved resource URL escaped the configured resource base URL"
        )

    return download_url


def verify_checksum(payload: bytes, entry: ResourceEntry) -> None:
    if not entry.checksum:
        return

    actual_checksum = hashlib.md5(payload).hexdigest()
    if actual_checksum != entry.checksum:
        raise ValueError(
            f"Checksum mismatch for {entry.resource_path}: "
            f"expected {entry.checksum}, got {actual_checksum}"
        )


def mapping_lookup(mapping: Any, key: int):
    if not isinstance(mapping, dict):
        return None

    if key in mapping:
        return mapping[key]

    key_as_string = str(key)
    if key_as_string in mapping:
        return mapping[key_as_string]

    return None


def collect_type_records(fsd: FsdSource, wanted_ids: set[int]) -> dict[int, TypeRecord]:
    raw_types = fsd.load("types")
    records: dict[int, TypeRecord] = {}

    for type_id in sorted(wanted_ids):
        type_data = mapping_lookup(raw_types, type_id)
        if not isinstance(type_data, dict):
            continue

        records[type_id] = TypeRecord(
            description_id=int_or_none(type_data.get("descriptionID")),
            graphic_id=int_or_none(type_data.get("graphicID")),
            group_id=int(type_data["groupID"]),
            icon_id=int_or_none(type_data.get("iconID")),
            meta_group_id=int_or_none(type_data.get("metaGroupID")),
            published=bool(type_data.get("published", False)),
            type_id=type_id,
            type_name_id=int(type_data["typeNameID"]),
        )

    return records


def collect_group_records(
    fsd: FsdSource, wanted_ids: set[int]
) -> dict[int, GroupRecord]:
    raw_groups = fsd.load("groups")
    records: dict[int, GroupRecord] = {}

    for group_id in sorted(wanted_ids):
        group_data = mapping_lookup(raw_groups, group_id)
        if not isinstance(group_data, dict):
            continue

        records[group_id] = GroupRecord(
            category_id=int(group_data["categoryID"]),
            group_id=group_id,
            group_name_id=int(group_data["groupNameID"]),
            published=bool(group_data.get("published", False)),
        )

    return records


def collect_category_records(
    fsd: FsdSource, wanted_ids: set[int]
) -> dict[int, CategoryRecord]:
    raw_categories = fsd.load("categories")
    records: dict[int, CategoryRecord] = {}

    for category_id in sorted(wanted_ids):
        category_data = mapping_lookup(raw_categories, category_id)
        if not isinstance(category_data, dict):
            continue

        records[category_id] = CategoryRecord(
            category_id=category_id,
            category_name_id=int(category_data["categoryNameID"]),
            published=bool(category_data.get("published", False)),
        )

    return records


def collect_meta_group_records(
    fsd: FsdSource, wanted_ids: set[int]
) -> dict[int, MetaGroupRecord]:
    raw_meta_groups = fsd.load("metagroups")
    records: dict[int, MetaGroupRecord] = {}

    for meta_group_id in sorted(wanted_ids):
        meta_group_data = mapping_lookup(raw_meta_groups, meta_group_id)
        if not isinstance(meta_group_data, dict):
            continue

        records[meta_group_id] = MetaGroupRecord(
            icon_id=int_or_none(meta_group_data.get("iconID")),
            meta_group_id=meta_group_id,
            name_id=int(meta_group_data["nameID"]),
        )

    return records


def load_localizations(
    resource_index: ResourceIndex,
    wanted_ids: set[int],
) -> dict[int, LocalizationRecord]:
    if not wanted_ids:
        return {}

    en_payload = resource_index.fetch_bytes(LOC_EN_RESOURCE)
    zh_payload = resource_index.fetch_bytes(LOC_ZH_RESOURCE)

    en_data = load_localization_pickle(en_payload)
    zh_data = load_localization_pickle(zh_payload)

    records: dict[int, LocalizationRecord] = {}

    for loc_id in sorted(wanted_ids):
        en_text = string_list_head(mapping_lookup(en_data, loc_id))
        zh_text = string_list_head(mapping_lookup(zh_data, loc_id))

        if en_text == "" and zh_text == "":
            continue

        records[loc_id] = LocalizationRecord(en=en_text, zh_cn=zh_text)

    return records


def resolve_icon_bytes(
    *,
    fsd: FsdSource,
    resource_index: ResourceIndex,
    icon_id: int,
) -> bytes | None:
    raw_icons = fsd.load("iconids")
    icon_data = mapping_lookup(raw_icons, icon_id)
    if not isinstance(icon_data, dict):
        return None

    icon_file = str(icon_data.get("iconFile", "")).strip().lower()
    if not icon_file:
        return None

    return resource_index.fetch_bytes(icon_file)


def resolve_type_image(
    *,
    fsd: FsdSource,
    resource_index: ResourceIndex,
    type_record: TypeRecord,
    category_id: int | None,
) -> ResolvedTypeImage | None:
    raw_graphics = fsd.load("graphicids")

    if type_record.graphic_id is not None:
        graphic_data = mapping_lookup(raw_graphics, type_record.graphic_id)
        if isinstance(graphic_data, dict):
            folder = (
                graphic_data.get("iconInfo", {}).get("folder")
                if isinstance(graphic_data.get("iconInfo"), dict)
                else None
            )
            if isinstance(folder, str) and folder:
                selected_entry = choose_graphic_entry(
                    graphic_id=type_record.graphic_id,
                    category_id=category_id,
                    entries=resource_index.get_resources(folder),
                )
                if selected_entry is not None:
                    entry, source = selected_entry
                    return ResolvedTypeImage(
                        bytes_=resource_index.fetch_bytes(entry.resource_path),
                        source=source,
                    )

    if type_record.icon_id is not None:
        icon_bytes = resolve_icon_bytes(
            fsd=fsd,
            resource_index=resource_index,
            icon_id=type_record.icon_id,
        )
        if icon_bytes is not None:
            return ResolvedTypeImage(bytes_=icon_bytes, source="icon")

    return None


def choose_graphic_entry(
    *,
    graphic_id: int,
    category_id: int | None,
    entries: list[ResourceEntry],
):
    candidates: dict[str, ResourceEntry] = {}

    for entry in entries:
        file_name = entry.file_name.lower()

        if f"{graphic_id}_" not in file_name:
            continue
        if "_64" not in file_name:
            continue
        if any(token in file_name for token in ("t2", "t3", "faction")):
            continue

        if "bpc" in file_name:
            continue

        if "bp" in file_name:
            candidates["graphic-blueprint"] = entry
        else:
            candidates["graphic"] = entry

    if category_id == BLUEPRINT_CATEGORY_ID and "graphic-blueprint" in candidates:
        entry = candidates["graphic-blueprint"]
        return entry, "graphic-blueprint"

    if "graphic" in candidates:
        entry = candidates["graphic"]
        return entry, "graphic"

    if "graphic-blueprint" in candidates:
        entry = candidates["graphic-blueprint"]
        return entry, "graphic-blueprint"

    return None


def int_or_none(value: Any) -> int | None:
    if value is None:
        return None

    return int(value)


def string_list_head(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        if not value:
            return ""
        head = value[0]
        return str(head) if head is not None else ""

    if value is None:
        return ""

    return str(value)
