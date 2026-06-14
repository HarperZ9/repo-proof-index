# repo-proof-index v0.1.1

## Release Type

Patch release for current public package behavior and release-artifact
normalization.

## Verification

- `python -m pytest -q`
- `python scripts/check_proof_surface_conformance.py`
- `python scripts/export_proof_surface_contract.py --out .release-check/proof-surface-contract-v0.1`
- `python scripts/score_proof_surface_research.py`
- `python -m json.tool schemas/proof-surface-packet.schema.json`
- `python -m build`
- `python -m twine check dist/*`
- `git diff --check`

## Artifacts

- `repo_proof_index-0.1.1-py3-none-any.whl`
- `repo_proof_index-0.1.1.tar.gz`

## Publishing Notes

GitHub Release artifacts are in scope. PyPI publication remains separate and
requires registry credentials.
