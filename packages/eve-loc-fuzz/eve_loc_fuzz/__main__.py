from __future__ import annotations

import argparse
import sys

from .search import (
    DEFAULT_LANGUAGES,
    resolve_languages,
    resolve_localization_dir,
    search_localizations,
)


def positive_int(raw_value: str) -> int:
    value = int(raw_value)
    if value <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Search localization_fsd_<lang>.pickle files for localization text that "
            "contains the requested substring."
        ),
    )
    parser.add_argument("query", help="Substring to search for")
    parser.add_argument(
        "--lang",
        action="append",
        dest="languages",
        metavar="LANG",
        help=(
            "Language code to search. Repeat to search multiple languages. "
            f"Defaults to {', '.join(DEFAULT_LANGUAGES)}."
        ),
    )
    parser.add_argument(
        "--workspace",
        help="Workspace root. Defaults to ./workspace from the current directory.",
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
        matches = search_localizations(
            query=args.query,
            languages=languages,
            localization_dir=localization_dir,
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
            print(f"[{match.lang}] {match.loc_id}\t{match.text}")
        else:
            print(f"{match.loc_id}\t{match.text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
