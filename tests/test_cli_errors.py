from __future__ import annotations

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
