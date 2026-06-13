# Proof Surface Interop

Proof-surface packets are a small JSON contract for carrying evidence about a
public technical claim. They are designed for review, not authority.

The packet answers five questions:

1. What surface is being shown?
2. What claims are being made?
3. What evidence points support those claims?
4. What checks were run?
5. What action items remain?

## Shape

The canonical schema is:

```text
schemas/proof-surface-packet.schema.json
```

Minimum conceptual shape:

```json
{
  "proof_surface_version": "0.1",
  "packet_id": "example",
  "surface": "public release readiness",
  "status": "needs-polish",
  "claims": [],
  "checks": [],
  "action_items": []
}
```

## Boundaries

A packet is not a certification, safety verdict, compliance decision, or trust
claim. It is an evidence carrier.

Allowed status values are intentionally operational:

- `ready`
- `needs-polish`
- `blocked`
- `unknown`

Allowed check statuses are intentionally modest:

- `pass`
- `warn`
- `fail`
- `unknown`

No packet should claim that a system is trusted, approved, safe, authorized, or
complete. Those decisions belong to downstream reviewers and owners.

## Producer pattern

Any tool can produce a packet when it can honestly map its output into:

```text
tool result -> claim evidence -> check summary -> action item
```

Current producer examples:

- `public-surface-sweeper --proof-packet`
- `model-provenance-validator --proof-packet`

Witness receipts from EMET are indexed separately as `witness-receipt` rows.

## Consumer pattern

`repo-proof-index` consumes packets as `proof-surface-packet` rows and reports
the number of claims, checks, and action items. This lets reviewers combine
release hygiene, provenance validation, and witness receipts without trusting a
single tool as the root of authority.

Example pipeline:

```bash
public-surface-sweeper . --proof-packet > public-surface.packet.json
model-provenance-validator *.provenance.json --proof-packet > provenance.packet.json
repo-proof-index public-surface.packet.json provenance.packet.json --summary
```

## Conformance fixtures

Small v0.1 fixtures live under:

```text
conformance/proof-surface/v0.1/
```

They give producers and consumers a reproducible baseline for what the packet
contract accepts and rejects.

Run the fixture set with:

```bash
python scripts/check_proof_surface_conformance.py
```

## Why it matters

Modern AI-assisted work creates claims faster than teams can review them. A
proof-surface packet slows the public edge down enough to make claims visible,
source-linked, checkable, and actionable before they are repeated.
