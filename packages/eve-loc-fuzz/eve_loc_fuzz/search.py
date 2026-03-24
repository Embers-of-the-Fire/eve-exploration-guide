from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
import pickle
from typing import Any

from .config import (
    DEFAULT_LOCALIZATION_SUBDIR,
    FALLBACK_LOCALIZATION_SUBDIR,
    LOCALIZATION_DIR_ENV_VAR,
    RESOURCE_CACHE_ENV_VARS,
    resolve_cli_path,
    resolve_config_value,
    resolve_workspace_path,
)


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str) -> Any:
        raise pickle.UnpicklingError(
            f"Localization payload cannot reference {module}.{name}"
        )


@dataclass(frozen=True, slots=True)
class LocalizationMatch:
    lang: str
    loc_id: int
    text: str


def resolve_localization_dir(
    localization_dir_arg: str | None,
    workspace_arg: str | None,
) -> Path:
    localization_dir_value = localization_dir_arg or resolve_config_value(
        LOCALIZATION_DIR_ENV_VAR
    )
    if localization_dir_value:
        localization_dir = resolve_cli_path(localization_dir_value)
        if not localization_dir.is_dir():
            raise FileNotFoundError(
                f"Localization directory does not exist: {localization_dir}"
            )
        return localization_dir

    candidates: list[Path] = []
    resource_cache_dir = resolve_config_value(*RESOURCE_CACHE_ENV_VARS)
    if resource_cache_dir:
        candidates.append(resolve_cli_path(resource_cache_dir) / "localizationfsd")

    try:
        workspace_path = resolve_workspace_path(workspace_arg)
    except FileNotFoundError:
        workspace_path = None
    else:
        candidates.extend(
            (
                workspace_path / DEFAULT_LOCALIZATION_SUBDIR,
                workspace_path / FALLBACK_LOCALIZATION_SUBDIR,
            )
        )

    checked_paths: list[str] = []
    seen_paths: set[Path] = set()
    for candidate in candidates:
        if candidate in seen_paths:
            continue

        seen_paths.add(candidate)
        checked_paths.append(str(candidate))
        if candidate.is_dir():
            return candidate

    if not checked_paths and workspace_path is None:
        raise FileNotFoundError(
            "A localization directory is required. Provide --localization-dir, "
            f"set {LOCALIZATION_DIR_ENV_VAR}, configure one of "
            f"{', '.join(RESOURCE_CACHE_ENV_VARS)}, or provide a workspace."
        )

    raise FileNotFoundError(
        "Could not find a localization pickle directory. Checked: "
        f"{', '.join(checked_paths)}"
    )


def resolve_languages(languages: list[str] | None) -> list[str]:
    if languages is None:
        raise ValueError("At least one language is required")

    raw_languages = languages
    resolved_languages: list[str] = []
    for raw_language in raw_languages:
        language = raw_language.strip().lower()
        if language and language not in resolved_languages:
            resolved_languages.append(language)

    if not resolved_languages:
        raise ValueError("At least one language is required")

    return resolved_languages


def resolve_pickle_path(localization_dir: Path, lang: str) -> Path:
    pickle_path = localization_dir / f"localization_fsd_{lang}.pickle"
    if not pickle_path.is_file():
        raise FileNotFoundError(f"Localization pickle does not exist: {pickle_path}")
    return pickle_path


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


def iter_localization_texts(localization_data: dict[Any, Any]):
    for loc_id, raw_entry in localization_data.items():
        if not isinstance(loc_id, int):
            continue
        if not isinstance(raw_entry, (list, tuple)) or not raw_entry:
            continue

        text = raw_entry[0]
        if not isinstance(text, str):
            continue

        yield loc_id, text


def normalize_search_text(value: str, *, case_sensitive: bool) -> str:
    return value if case_sensitive else value.casefold()


def search_localizations(
    query: str,
    *,
    languages: list[str] | None,
    localization_dir: Path,
    case_sensitive: bool = False,
    limit: int | None = None,
) -> list[LocalizationMatch]:
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("Query must not be empty")

    resolved_languages = resolve_languages(languages)
    language_order = {
        language: index for index, language in enumerate(resolved_languages)
    }
    target = normalize_search_text(normalized_query, case_sensitive=case_sensitive)
    matches: list[LocalizationMatch] = []

    for language in resolved_languages:
        pickle_path = resolve_pickle_path(localization_dir, language)
        localization_data = load_localization_pickle(pickle_path.read_bytes())
        for loc_id, text in iter_localization_texts(localization_data):
            if target in normalize_search_text(text, case_sensitive=case_sensitive):
                matches.append(
                    LocalizationMatch(lang=language, loc_id=loc_id, text=text)
                )

    matches.sort(
        key=lambda match: (
            len(match.text),
            language_order[match.lang],
            match.loc_id,
            match.text,
        )
    )

    if limit is None:
        return matches
    return matches[:limit]
