from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ProofRow:
    contract: str
    kind: str
    surface: str
    status: str
    evidence: str
    path: str


@dataclass(frozen=True)
class ProofSummary:
    total: int
    kinds: dict[str, int]
    statuses: dict[str, int]
    evidence_gaps: int
    action_items: list[str]


def _as_text(value: Any, default: str = "unknown") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return default


def _verification_evidence(data: dict[str, Any]) -> str:
    verification = data.get("verification")
    if isinstance(verification, list) and verification:
        items = [item for item in verification if isinstance(item, dict)]
        passing = [
            item
            for item in items
            if isinstance(item.get("status"), str)
            and item.get("status", "").lower() == "pass"
        ]
        selected = passing if passing else items
        parts: list[str] = []
        for item in selected[:3]:
            status = _as_text(item.get("status"), "")
            evidence = _as_text(item.get("evidence"), "")
            if status or evidence:
                parts.append(": ".join(part for part in (status, evidence) if part))
        if parts:
            return " | ".join(parts)

    claims = data.get("claims")
    if isinstance(claims, list) and claims and isinstance(claims[0], dict):
        return _as_text(claims[0].get("evidence") or claims[0].get("claim"))

    notes = data.get("notes")
    if isinstance(notes, str):
        return notes

    return "no evidence summary"


def _backend_evidence(data: dict[str, Any]) -> str:
    backends = data.get("backends")
    if not isinstance(backends, list):
        return "no backend summary"
    counts: dict[str, int] = {}
    for backend in backends:
        if isinstance(backend, dict):
            status = _as_text(backend.get("status"), "unknown")
            counts[status] = counts.get(status, 0) + 1
    if not counts:
        return "no backend summary"
    return ", ".join(f"{status}={count}" for status, count in sorted(counts.items()))


def _proof_surface_evidence(data: dict[str, Any]) -> str:
    checks = data.get("checks")
    actions = data.get("action_items")
    claims = data.get("claims")
    check_count = len(checks) if isinstance(checks, list) else 0
    action_count = len(actions) if isinstance(actions, list) else 0
    claim_count = len(claims) if isinstance(claims, list) else 0
    return f"claims={claim_count}, checks={check_count}, actions={action_count}"


def _relative(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def summarize_contract(path: Path, base: Path | None = None) -> ProofRow:
    base = base or path.parent
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")

    rel_path = _relative(path, base)

    if "manifest_id" in data and "product" in data:
        return ProofRow(
            contract=_as_text(data.get("manifest_id")),
            kind="product-use-case",
            surface=_as_text(data.get("product")),
            status=_as_text(data.get("maturity")),
            evidence=_verification_evidence(data),
            path=rel_path,
        )

    if "descriptor_id" in data and "backends" in data:
        return ProofRow(
            contract=_as_text(data.get("descriptor_id")),
            kind="backend-capability",
            surface=_as_text(data.get("language")),
            status="backend-matrix",
            evidence=_backend_evidence(data),
            path=rel_path,
        )

    if "receipt_id" in data and "verdict" in data:
        witness = data.get("witness")
        witness_id = "witness"
        if isinstance(witness, dict):
            witness_id = _as_text(witness.get("implementation"), "witness")
        return ProofRow(
            contract=_as_text(data.get("receipt_id")),
            kind="witness-receipt",
            surface=witness_id,
            status=_as_text(data.get("verdict")),
            evidence=_as_text(data.get("notes"), "receipt available"),
            path=rel_path,
        )

    if "proof_surface_version" in data and "packet_id" in data:
        return ProofRow(
            contract=_as_text(data.get("packet_id")),
            kind="proof-surface-packet",
            surface=_as_text(data.get("surface")),
            status=_as_text(data.get("status")),
            evidence=_proof_surface_evidence(data),
            path=rel_path,
        )

    return ProofRow(
        contract=_as_text(
            data.get("id")
            or data.get("report_id")
            or data.get("manifest_id")
            or data.get("descriptor_id")
            or path.stem
        ),
        kind="contract",
        surface=_as_text(data.get("name") or data.get("surface") or data.get("root") or path.stem),
        status=_as_text(data.get("status") or data.get("maturity") or data.get("verdict")),
        evidence=_verification_evidence(data),
        path=rel_path,
    )


def _default_contracts_dir(root: Path) -> Path:
    return root / "project-docs" / "roadmaps" / "contracts"


def _expand_paths(paths: Iterable[Path], root: Path, contracts_dir: Path | None) -> list[Path]:
    explicit = list(paths)
    if explicit:
        return sorted(path.resolve() for path in explicit)
    directory = contracts_dir or _default_contracts_dir(root)
    if not directory.is_dir():
        raise FileNotFoundError(f"contracts directory not found: {directory}")
    return sorted(directory.glob("*.json"))


def load_rows(
    paths: Iterable[Path] = (),
    *,
    root: Path = Path("."),
    contracts_dir: Path | None = None,
) -> list[ProofRow]:
    base = (contracts_dir or root).resolve()
    return [summarize_contract(path, base) for path in _expand_paths(paths, root, contracts_dir)]


def _clip(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def format_table(rows: list[ProofRow]) -> str:
    columns = [
        ("kind", 22),
        ("surface", 22),
        ("status", 18),
        ("evidence", 72),
    ]
    lines = [
        " | ".join(name.ljust(width) for name, width in columns),
        " | ".join("-" * width for _, width in columns),
    ]
    for row in rows:
        values = {
            "kind": row.kind,
            "surface": row.surface,
            "status": row.status,
            "evidence": row.evidence,
        }
        lines.append(
            " | ".join(_clip(values[name], width).ljust(width) for name, width in columns)
        )
    return "\n".join(lines)


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _has_evidence_gap(row: ProofRow) -> bool:
    evidence = row.evidence.strip().lower()
    return not evidence or evidence.startswith("no ") or evidence == "unknown"


def _needs_action(row: ProofRow) -> bool:
    status = row.status.strip().lower()
    statuses = {
        "blocked",
        "draft",
        "drift",
        "fail",
        "needs-polish",
        "planned",
        "unknown",
        "unverifiable",
        "unverified",
    }
    return status in statuses or _has_evidence_gap(row)


def summarize_rows(rows: list[ProofRow], action_limit: int = 8) -> ProofSummary:
    action_items: list[str] = []
    for row in rows:
        if not _needs_action(row):
            continue
        reason = "add evidence" if _has_evidence_gap(row) else f"resolve {row.status}"
        action_items.append(f"{row.contract}: {reason} ({row.path})")
        if len(action_items) >= action_limit:
            break
    return ProofSummary(
        total=len(rows),
        kinds=_counts(row.kind for row in rows),
        statuses=_counts(row.status for row in rows),
        evidence_gaps=sum(1 for row in rows if _has_evidence_gap(row)),
        action_items=action_items,
    )


def format_summary(summary: ProofSummary) -> str:
    lines = [
        f"total: {summary.total}",
        "kinds: " + _format_counts(summary.kinds),
        "statuses: " + _format_counts(summary.statuses),
        f"evidence_gaps: {summary.evidence_gaps}",
        "action_items:",
    ]
    if summary.action_items:
        lines.extend(f"- {item}" for item in summary.action_items)
    else:
        lines.append("- none")
    return "\n".join(lines)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in counts.items())
