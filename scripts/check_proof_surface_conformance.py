#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from repo_proof_index.packet import format_validation, validate_packet_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check proof-surface v0.1 packet conformance fixtures."
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=ROOT / "conformance" / "proof-surface" / "v0.1",
        help="Fixture root containing valid/ and invalid/ packet JSON files.",
    )
    return parser


def expected_cases(fixtures: Path) -> list[tuple[Path, bool]]:
    valid = sorted((fixtures / "valid").glob("*.packet.json"))
    invalid = sorted((fixtures / "invalid").glob("*.packet.json"))
    return [(path, True) for path in valid] + [(path, False) for path in invalid]


def check_case(path: Path, expected_valid: bool) -> tuple[bool, str]:
    issues = validate_packet_file(path)
    actual_valid = not issues
    status = "PASS" if actual_valid == expected_valid else "FAIL"
    expected = "valid" if expected_valid else "invalid"
    actual = "valid" if actual_valid else "invalid"
    lines = [f"{status} {path.as_posix()} expected={expected} actual={actual}"]
    if status == "FAIL":
        lines.append(format_validation(path, issues))
    return actual_valid == expected_valid, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cases = expected_cases(args.fixtures)
    if not cases:
        print(f"error: no conformance fixtures found under {args.fixtures}", file=sys.stderr)
        return 1

    ok = True
    for path, expected_valid in cases:
        case_ok, output = check_case(path, expected_valid)
        ok = ok and case_ok
        print(output)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
