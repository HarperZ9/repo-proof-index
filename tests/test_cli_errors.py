from __future__ import annotations

import json
from pathlib import Path

from repo_proof_index.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_returns_error_for_non_object_json(capsys) -> None:
    path = ROOT / "examples" / "malformed" / "not-object.json"

    assert main([str(path)]) == 1
    assert "did not contain a JSON object" in capsys.readouterr().out


def test_cli_validate_accepts_valid_proof_surface_packet(capsys) -> None:
    path = ROOT / "examples" / "contracts" / "proof-surface-packet.json"

    assert main(["--validate", str(path)]) == 0
    assert "valid" in capsys.readouterr().out


def test_cli_json_indexes_organ_exchange_artifact(tmp_path: Path, capsys) -> None:
    path = tmp_path / "organ-exchange.json"
    path.write_text(
        json.dumps(
            {
                "module_id": "orca.module.organ_exchange.bundle",
                "summary": {
                    "subject": "active-organ-pulse-smoke",
                    "bundle_status": "pass",
                    "entry_count": 3,
                    "collected_count": 3,
                    "organ_ids": ["eye.raw_rendering", "provenance.sensorium"],
                    "receipt_kinds": ["raw-health", "provenance-receipt"],
                },
                "bundle": {"bundle_id": "orb-run-active"},
            }
        ),
        encoding="utf-8",
    )

    assert main([str(path), "--json"]) == 0

    rows = json.loads(capsys.readouterr().out)
    assert rows[0]["kind"] == "organ-exchange"
    assert rows[0]["contract"] == "orb-run-active"
    assert rows[0]["evidence"] == "entries=3, collected=3, organs=2, receipts=2"
