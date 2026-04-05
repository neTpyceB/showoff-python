from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from showoff_cli.core import batch_rename, format_file, search_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="showoff")
    subcommands = parser.add_subparsers(dest="command", required=True)

    search = subcommands.add_parser("search")
    search.add_argument("root", type=Path)
    search.add_argument("pattern")
    search.set_defaults(handler=run_search)

    rename = subcommands.add_parser("rename")
    rename.add_argument("root", type=Path)
    rename.add_argument("find")
    rename.add_argument("replace")
    rename.add_argument("--glob", default="*")
    rename.set_defaults(handler=run_rename)

    formatter = subcommands.add_parser("format")
    formatter.add_argument("kind", choices=("json", "csv"))
    formatter.add_argument("source", type=Path)
    formatter.add_argument("--output", type=Path)
    formatter.set_defaults(handler=run_format)

    return parser


def run_search(args: argparse.Namespace) -> None:
    for path in search_files(args.root, args.pattern):
        print(path)


def run_rename(args: argparse.Namespace) -> None:
    for source, target in batch_rename(args.root, args.find, args.replace, args.glob):
        print(f"{source} -> {target}")


def run_format(args: argparse.Namespace) -> None:
    print(format_file(args.kind, args.source, args.output))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.handler(args)
    return 0
