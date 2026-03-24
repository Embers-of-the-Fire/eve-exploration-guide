from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:
    from .dotenv_compat import find_dotenv, load_dotenv

DEFAULT_WORKSPACE_DIRNAME = "workspace"
DEFAULT_LOCALIZATION_SUBDIR = Path(".cache/resources/localizationfsd")
FALLBACK_LOCALIZATION_SUBDIR = Path(
    ".cache/eve-docs-generator/resources/localizationfsd"
)
FSD_DIR_ENV_VAR = "EVE_LOC_FUZZ_FSD_DIR"
LOCALIZATION_DIR_ENV_VAR = "EVE_LOC_FUZZ_LOCALIZATION_DIR"
RESOURCE_CACHE_ENV_VARS = (
    "EVE_DOCS_RESOURCE_CACHE_DIR",
    "EVE_DOCS_WORKSPACE_CACHE_DIR",
)
WORKSPACE_ENV_VARS = (
    "EVE_LOC_FUZZ_WORKSPACE",
    "EVE_DOCS_WORKSPACE",
)


def load_cli_environment() -> None:
    load_dotenv(find_dotenv(usecwd=True))


def resolve_cli_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()

    if path.is_absolute():
        return path.resolve()

    return (Path.cwd() / path).resolve()


def resolve_config_value(*env_vars: str) -> str | None:
    for env_var in env_vars:
        value = os.environ.get(env_var)
        if value:
            return value

    return None


def resolve_workspace_path(workspace_arg: str | None) -> Path:
    workspace_value = (
        workspace_arg
        or resolve_config_value(*WORKSPACE_ENV_VARS)
        or str(Path.cwd() / DEFAULT_WORKSPACE_DIRNAME)
    )
    workspace_path = resolve_cli_path(workspace_value)
    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace path does not exist: {workspace_path}")
    return workspace_path
