# repo-proof-index

`repo-proof-index` turns JSON proof contracts, receipts, and capability
descriptors into a compact table or JSON index.

The parser is intentionally schema-tolerant. Unknown contract shapes still get
best-effort identifiers, status, surface, evidence, and source path fields.

Use it when a repo or workspace has proof artifacts but no quick way to see
what they claim, what surface they describe, what status they report, and where
the evidence lives.

## Install

```bash
python -m pip install repo-proof-index
```

For local development:

```bash
python -m pip install -e ".[test]"
python -m pytest
```

## Usage

Index explicit JSON files:

```bash
repo-proof-index contracts/*.json
repo-proof-index contracts/*.json --json
```

Index the common workspace location:

```bash
repo-proof-index --root .
```

Use a custom contracts directory:

```bash
repo-proof-index --contracts-dir project-docs/contracts
```

Run the bundled quick demo:

```bash
repo-proof-index examples/contracts/*.json
```

Malformed input example:

```bash
repo-proof-index examples/malformed/not-object.json
```

Expected behavior: the command prints an `error:` line and exits with status
`1` instead of producing a proof row.

## What it indexes

Known shapes:

- product use-case manifests with `manifest_id` and `product`
- backend capability descriptors with `descriptor_id` and `backends`
- witness receipts with `receipt_id` and `verdict`
- generic JSON contracts with common fields such as `id`, `report_id`,
  `manifest_id`, `descriptor_id`, `status`, `maturity`, `verdict`, `claims`,
  `verification`, and `notes`

Default discovery path when explicit files are omitted:

```text
project-docs/roadmaps/contracts/*.json
```

## Output fields

| Field | Meaning |
| --- | --- |
| `kind` | Best-effort contract type. |
| `surface` | Product, language, witness implementation, root, or contract name. |
| `status` | Status, maturity, verdict, or fallback status. |
| `evidence` | Short evidence summary from verification, claims, notes, or backend counts. |
| `path` | Source JSON path in JSON mode. |

## Example table output

```text
kind                   | surface                | status             | evidence
---------------------- | ---------------------- | ------------------ | ------------------------------------------------------------------------
product-use-case       | sample-tool            | release-candidate  | pass: example tests passed
witness-receipt        | sample-witness         | MATCH              | sample receipt available
backend-capability     | rust                   | backend-matrix     | pass=1, planned=1
```

## Example JSON output

```json
[
  {
    "contract": "product-usecase-quanta-ui",
    "kind": "product-use-case",
    "surface": "quanta-ui",
    "status": "private-gated",
    "evidence": "pass: 17 tests passed",
    "path": "contracts/quanta-ui.json"
  }
]
```

## What it does not do

- It does not validate a JSON Schema.
- It does not certify that evidence is sufficient.
- It does not read private payloads referenced by a contract.
- It does not decide whether a claim is true.
- It does not replace tests, audits, or release review.

## Release-readiness use

`repo-proof-index` is the evidence assembly point in a proof-surface pipeline:

```text
contracts and receipts -> proof index -> report -> reviewer handoff
```

Its job is to make proof artifacts visible enough for a maintainer, reviewer,
client, or employer to see what exists and what still needs a stronger gate.

## Authorship

Created and maintained by Zain Dana Harper. Claude Code contributed to the
initial implementation.
