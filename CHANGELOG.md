# Changelog

## Unreleased

- Adds `project-docs/specs/SPEC-repo-proof-index-forward-delivery.md` and a
  delivery regression test for public/developer packaging.
- Updates GitHub Actions workflows to current action majors.
- Normalizes forward-facing punctuation for public-surface scanner
  compatibility.
- Hardens proof-surface v0.1 validation so `claims` and `checks` must each
  contain at least one item.
- Adds an invalid conformance fixture for empty proof-surface evidence carriers.

## 2026-06-29 - Forward Delivery Contract

- Public surface scanner status: `MATCH`.
- Behavioral scope unchanged: indexer, CLI, schema validation, conformance
  export, and research harness behavior remain covered by existing tests.

## v0.1.1 - 2026-06-14

- Adds strict proof-surface v0.1 packet validation.
- Adds proof-surface conformance fixtures, contract export, and research scoring
  harness.
- Adds release-artifact packaging workflow and release checklist.

## v0.1.0 - 2026-06-12

- Initial public release of proof artifact indexing and summary output.
