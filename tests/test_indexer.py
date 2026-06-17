from __future__ import annotations

import json
from pathlib import Path

from proof_surface.packet import validate_packet_file
from repo_proof_index.indexer import format_table, load_rows, summarize_contract


FIXTURES = Path(__file__).parent / "fixtures"


def test_summarize_product_contract() -> None:
    row = summarize_contract(FIXTURES / "product.json", FIXTURES)

    assert row.contract == "product-demo"
    assert row.kind == "product-use-case"
    assert row.evidence == "pass: unit tests"


def test_load_rows_handles_multiple_shapes() -> None:
    rows = load_rows(contracts_dir=FIXTURES)

    assert {row.kind for row in rows} == {
        "backend-capability",
        "product-use-case",
        "witness-receipt",
    }
    assert "backend-matrix" in {row.status for row in rows}


def test_unknown_contract_shape_gets_best_effort_row(tmp_path: Path) -> None:
    path = tmp_path / "custom.json"
    path.write_text(json.dumps({"id": "custom", "status": "draft"}), encoding="utf-8")

    row = summarize_contract(path, tmp_path)

    assert row.contract == "custom"
    assert row.kind == "contract"
    assert row.status == "draft"


def test_format_table_includes_contract_evidence() -> None:
    table = format_table(load_rows([FIXTURES / "product.json"], root=FIXTURES))

    assert "product-use-case" in table
    assert "unit tests" in table


def test_valid_proof_surface_packet_fixture_passes_validation() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "conformance"
        / "proof-surface"
        / "v0.1"
        / "valid"
        / "minimal.packet.json"
    )

    assert validate_packet_file(path) == []


def test_empty_claims_and_checks_are_invalid(tmp_path: Path) -> None:
    path = tmp_path / "empty.packet.json"
    path.write_text(
        json.dumps(
            {
                "proof_surface_version": "0.1",
                "packet_id": "empty",
                "surface": "empty proof surface",
                "status": "unknown",
                "claims": [],
                "checks": [],
                "action_items": [],
            }
        ),
        encoding="utf-8",
    )

    messages = {(issue.path, issue.message) for issue in validate_packet_file(path)}

    assert ("$.claims", "expected at least 1 item(s)") in messages
    assert ("$.checks", "expected at least 1 item(s)") in messages
