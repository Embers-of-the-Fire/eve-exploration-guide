from __future__ import annotations

import argparse

from dotenv import find_dotenv, load_dotenv

from .generator import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_OUTPUT_DIR,
    generate_docs_data,
    resolve_cli_path,
)
from .source_workspace import (
    DEFAULT_RESOURCE_BASE_URL,
    RESOURCE_CACHE_ENV_VAR,
    WORKSPACE_CACHE_ENV_VAR,
    WORKSPACE_ENV_VAR,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the minimal checked-in EVE docs dataset from a TQ source "
            "workspace and the extension inspect manifest."
        ),
    )
    parser.add_argument(
        "--workspace",
        help=(
            "Path to a source workspace containing resfileindex.txt and either "
            "an fsd/ directory or the FSD files directly. Required unless "
            f"{WORKSPACE_ENV_VAR} is set."
        ),
    )
    parser.add_argument(
        "--resfileindex",
        help="Explicit path to resfileindex.txt. Overrides workspace discovery.",
    )
    parser.add_argument(
        "--fsd-dir",
        help="Explicit path to the directory containing FSD files.",
    )
    parser.add_argument(
        "--start-ini",
        help="Optional path to start.ini for game version/build metadata.",
    )
    parser.add_argument(
        "--resource-cache-dir",
        "--workspace-cache-dir",
        dest="resource_cache_dir",
        help=(
            "Optional cache directory for downloaded TQ resources such as "
            "localization pickles and icons. Defaults to "
            "<workspace>/.cache/eve-docs-generator/resources when a workspace "
            "is configured, otherwise ./.cache/eve-docs-generator/resources. "
            f"Can also be set with {RESOURCE_CACHE_ENV_VAR} or "
            f"{WORKSPACE_CACHE_ENV_VAR}."
        ),
    )
    parser.add_argument(
        "--resource-base-url",
        default=DEFAULT_RESOURCE_BASE_URL,
        help=(
            "Base URL used to resolve resfileindex download URLs for TQ "
            f"(default: {DEFAULT_RESOURCE_BASE_URL})."
        ),
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to the extension inspect manifest JSON.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Target directory for generated docs data and copied images.",
    )
    return parser


def main() -> int:
    load_dotenv(find_dotenv(usecwd=True))
    parser = build_parser()
    args = parser.parse_args()

    summary = generate_docs_data(
        workspace_arg=args.workspace,
        resfileindex_arg=args.resfileindex,
        fsd_dir_arg=args.fsd_dir,
        start_ini_arg=args.start_ini,
        resource_cache_dir_arg=args.resource_cache_dir,
        resource_base_url=args.resource_base_url,
        manifest_path=resolve_cli_path(args.manifest),
        output_dir=resolve_cli_path(args.output_dir),
    )

    game_summary = "unknown build/version"
    if (
        summary.metadata.game_version is not None
        or summary.metadata.game_build is not None
    ):
        game_summary = (
            f"{summary.metadata.game_version or 'unknown version'} "
            f"build {summary.metadata.game_build or 'unknown build'}"
        )

    print(
        "Generated EVE docs data "
        f"for {summary.metadata.server_id} "
        f"({game_summary}) "
        f"into {summary.output_dir}"
    )
    print(
        f"Included {summary.type_count} type(s), "
        f"{summary.localization_count} localization(s), "
        f"and {summary.icon_count} icon asset(s)."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
