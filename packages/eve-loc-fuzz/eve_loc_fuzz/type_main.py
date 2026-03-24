from __future__ import annotations

import argparse
import sys

from .fsd import resolve_fsd_dir
from .search import resolve_languages, resolve_localization_dir
from .type_search import search_type_names


def positive_int(raw_value: str) -> int:
    value = int(raw_value)
    if value <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Search EVE type names by localized substring using the types FSD data "
            "and localization pickle files."
        ),
    )
    parser.add_argument("query", help="Substring to search for")
    parser.add_argument(
        "--lang",
        action="append",
        dest="languages",
        metavar="LANG",
        required=True,
        help=(
            "Language code to search. Repeat to search multiple languages. Required."
        ),
    )
    parser.add_argument(
        "--workspace",
        help="Workspace root. Defaults to ./workspace from the current directory.",
    )
    parser.add_argument(
        "--fsd-dir",
        help="Explicit FSD directory. Overrides the workspace-derived location.",
    )
    parser.add_argument(
        "--localization-dir",
        help="Explicit localization pickle directory. Overrides --workspace.",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use a case-sensitive substring match.",
    )
    parser.add_argument(
        "--limit",
        type=positive_int,
        help="Maximum number of matches to print after sorting.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if raw_argv and raw_argv[0] == "--":
        raw_argv = raw_argv[1:]
    args = parser.parse_args(raw_argv)

    try:
        languages = resolve_languages(args.languages)
        localization_dir = resolve_localization_dir(
            localization_dir_arg=args.localization_dir,
            workspace_arg=args.workspace,
        )
        fsd_dir = resolve_fsd_dir(
            fsd_dir_arg=args.fsd_dir,
            workspace_arg=args.workspace,
        )
        matches = search_type_names(
            query=args.query,
            languages=languages,
            localization_dir=localization_dir,
            fsd_dir=fsd_dir,
            case_sensitive=args.case_sensitive,
            limit=args.limit,
        )
    except (FileNotFoundError, ValueError) as error:
        parser.exit(status=2, message=f"error: {error}\n")

    if not matches:
        print("No matches found.")
        return 0

    include_language = len(languages) > 1
    for match in matches:
        if include_language:
            print(f"[{match.lang}] {match.type_id}\t{match.name}")
        else:
            print(f"{match.type_id}\t{match.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
