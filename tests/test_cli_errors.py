from __future__ import annotations

from pathlib import Path

from repo_proof_index.cli import main


ROOT = Path(__file__).resolve().parents[1]


def test_cli_returns_error_for_non_object_json(capsys) -> None:
    path = ROOT / "examples" / "malformed" / "not-object.json"

    assert main([str(path)]) == 1
    assert "did not contain a JSON object" in capsys.readouterr().out
