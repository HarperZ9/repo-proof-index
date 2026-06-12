from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .indexer import format_table, load_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Index proof contract JSON files into table or JSON output."
    )
    parser.add_argument("paths", nargs="*", type=Path, help="Contract JSON files.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Workspace root used when paths are omitted.",
    )
    parser.add_argument(
        "--contracts-dir",
        type=Path,
        default=None,
        help="Directory to scan when paths are omitted.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON rows.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_rows(args.paths, root=args.root, contracts_dir=args.contracts_dir)
    if args.json:
        print(json.dumps([asdict(row) for row in rows], indent=2))
    else:
        print(format_table(rows))
    return 0

