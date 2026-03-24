from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
import pickle
from typing import Any

DEFAULT_LANGUAGES = ("en-us", "zh")
DEFAULT_WORKSPACE_DIRNAME = "workspace"
DEFAULT_LOCALIZATION_SUBDIR = Path(".cache/resources/localizationfsd")
FALLBACK_LOCALIZATION_SUBDIR = Path(
    ".cache/eve-docs-generator/resources/localizationfsd"
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


def resolve_cli_path(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def resolve_workspace_path(workspace_arg: str | None) -> Path:
    workspace_value = workspace_arg or str(Path.cwd() / DEFAULT_WORKSPACE_DIRNAME)
    workspace_path = resolve_cli_path(workspace_value)
    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace path does not exist: {workspace_path}")
    return workspace_path


def resolve_localization_dir(
    localization_dir_arg: str | None,
    workspace_arg: str | None,
) -> Path:
    if localization_dir_arg:
        localization_dir = resolve_cli_path(localization_dir_arg)
        if not localization_dir.is_dir():
            raise FileNotFoundError(
                f"Localization directory does not exist: {localization_dir}"
            )
        return localization_dir

    workspace_path = resolve_workspace_path(workspace_arg)
    candidates = (
        workspace_path / DEFAULT_LOCALIZATION_SUBDIR,
        workspace_path / FALLBACK_LOCALIZATION_SUBDIR,
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    checked_paths = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(
        f"Could not find a localization pickle directory. Checked: {checked_paths}"
    )


def resolve_languages(languages: list[str] | None) -> list[str]:
    raw_languages = languages or list(DEFAULT_LANGUAGES)
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
