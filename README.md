# repo-proof-index

`repo-proof-index` turns JSON proof contracts, receipts, and capability
descriptors into a compact table or JSON index.

The parser is intentionally schema-tolerant. Unknown contract shapes still get
best-effort identifiers, status, surface, evidence, and source path fields.

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

## Authorship

Created and maintained by Zain Dana Harper. Claude Code contributed to the
initial implementation.

