from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_VERSION = "0.1"
PACKET_STATUSES = {"ready", "needs-polish", "blocked", "unknown"}
CHECK_STATUSES = {"pass", "warn", "fail", "unknown"}
ROOT_FIELDS = {
    "proof_surface_version",
    "packet_id",
    "surface",
    "status",
    "claims",
    "checks",
    "action_items",
}
CLAIM_FIELDS = {"claim", "evidence"}
CHECK_FIELDS = {"tool", "status", "summary"}


@dataclass(frozen=True)
class PacketIssue:
    path: str
    message: str


def load_packet(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def validate_packet(data: dict[str, Any]) -> list[PacketIssue]:
    issues: list[PacketIssue] = []
    _reject_unknown(data, "$", ROOT_FIELDS, issues)
    _require_const(data, "proof_surface_version", PACKET_VERSION, issues)
    _require_text(data, "packet_id", issues)
    _require_text(data, "surface", issues)
    _require_enum(data, "status", PACKET_STATUSES, issues)
    _validate_claims(data.get("claims"), issues)
    _validate_checks(data.get("checks"), issues)
    _validate_action_items(data.get("action_items"), issues)
    return issues


def validate_packet_file(path: Path) -> list[PacketIssue]:
    try:
        return validate_packet(load_packet(path))
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        return [PacketIssue("$", str(exc))]


def format_validation(path: Path, issues: list[PacketIssue]) -> str:
    if not issues:
        return f"{path}: valid"
    lines = [f"{path}: invalid"]
    lines.extend(f"  {issue.path}: {issue.message}" for issue in issues)
    return "\n".join(lines)


def _require_const(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[PacketIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(PacketIssue(f"$.{field}", f"expected {expected!r}"))


def _reject_unknown(
    data: dict[str, Any],
    path: str,
    allowed: set[str],
    issues: list[PacketIssue],
) -> None:
    for field in sorted(set(data) - allowed):
        issues.append(PacketIssue(f"{path}.{field}", "unexpected field"))


def _require_text(
    data: dict[str, Any],
    field: str,
    issues: list[PacketIssue],
    path: str | None = None,
) -> None:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        issues.append(PacketIssue(path or f"$.{field}", "expected non-empty string"))


def _require_enum(
    data: dict[str, Any],
    field: str,
    allowed: set[str],
    issues: list[PacketIssue],
    path: str | None = None,
) -> None:
    value = data.get(field)
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        issues.append(PacketIssue(path or f"$.{field}", f"expected one of: {choices}"))


def _validate_claims(value: Any, issues: list[PacketIssue]) -> None:
    if not isinstance(value, list):
        issues.append(PacketIssue("$.claims", "expected array"))
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            issues.append(PacketIssue(f"$.claims[{index}]", "expected object"))
            continue
        _reject_unknown(item, f"$.claims[{index}]", CLAIM_FIELDS, issues)
        _require_text(item, "claim", issues, f"$.claims[{index}].claim")
        _require_text(item, "evidence", issues, f"$.claims[{index}].evidence")


def _validate_checks(value: Any, issues: list[PacketIssue]) -> None:
    if not isinstance(value, list):
        issues.append(PacketIssue("$.checks", "expected array"))
        return
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            issues.append(PacketIssue(f"$.checks[{index}]", "expected object"))
            continue
        _reject_unknown(item, f"$.checks[{index}]", CHECK_FIELDS, issues)
        _require_text(item, "tool", issues, f"$.checks[{index}].tool")
        _require_enum(item, "status", CHECK_STATUSES, issues, f"$.checks[{index}].status")
        _require_text(item, "summary", issues, f"$.checks[{index}].summary")


def _validate_action_items(value: Any, issues: list[PacketIssue]) -> None:
    if not isinstance(value, list):
        issues.append(PacketIssue("$.action_items", "expected array"))
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            issues.append(PacketIssue(f"$.action_items[{index}]", "expected non-empty string"))
