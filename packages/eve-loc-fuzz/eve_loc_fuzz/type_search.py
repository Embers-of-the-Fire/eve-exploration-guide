from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .fsd import load_fsd_payload
from .search import (
    load_localization_pickle,
    normalize_search_text,
    resolve_languages,
    resolve_pickle_path,
)


@dataclass(frozen=True, slots=True)
class TypeMatch:
    lang: str
    type_id: int
    name: str


def search_type_names(
    query: str,
    *,
    languages: list[str] | None,
    localization_dir: Path,
    fsd_dir: Path,
    case_sensitive: bool = False,
    limit: int | None = None,
) -> list[TypeMatch]:
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("Query must not be empty")

    raw_types = load_fsd_payload(fsd_dir, "types")
    if not isinstance(raw_types, dict):
        raise ValueError("Invalid types FSD payload")

    resolved_languages = resolve_languages(languages)
    language_order = {
        language: index for index, language in enumerate(resolved_languages)
    }
    target = normalize_search_text(normalized_query, case_sensitive=case_sensitive)
    matches: list[TypeMatch] = []

    for language in resolved_languages:
        pickle_path = resolve_pickle_path(localization_dir, language)
        localization_data = load_localization_pickle(pickle_path.read_bytes())

        for type_id, type_name_id in iter_type_name_ids(raw_types):
            type_name = string_list_head(
                mapping_lookup(localization_data, type_name_id)
            )
            if type_name == "":
                continue
            if target in normalize_search_text(
                type_name,
                case_sensitive=case_sensitive,
            ):
                matches.append(
                    TypeMatch(lang=language, type_id=type_id, name=type_name)
                )

    matches.sort(
        key=lambda match: (
            len(match.name),
            language_order[match.lang],
            match.type_id,
            match.name,
        )
    )

    if limit is None:
        return matches
    return matches[:limit]


def iter_type_name_ids(raw_types: dict[Any, Any]):
    for raw_type_id, raw_type_data in raw_types.items():
        if not isinstance(raw_type_data, dict):
            continue

        type_id = int_or_none(raw_type_id)
        if type_id is None:
            type_id = int_or_none(raw_type_data.get("typeID"))

        type_name_id = int_or_none(raw_type_data.get("typeNameID"))
        if type_id is None or type_name_id is None:
            continue

        yield type_id, type_name_id


def mapping_lookup(mapping: Any, key: int):
    if not isinstance(mapping, dict):
        return None

    if key in mapping:
        return mapping[key]

    key_as_string = str(key)
    if key_as_string in mapping:
        return mapping[key_as_string]

    return None


def string_list_head(value: Any) -> str:
    if isinstance(value, (list, tuple)) and value and isinstance(value[0], str):
        return value[0]

    return ""


def int_or_none(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None
