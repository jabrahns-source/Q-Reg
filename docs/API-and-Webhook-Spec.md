# Q-Reg API & Webhook Spec (v0.3)

## Core Processing Endpoint (local / future gRPC)

### POST /v1/process

**Request**
```json
{
  "entity_id": "string",
  "interval": "YYYY-QN or ISO period",
  "inputs": {
    "scope1_mte": 0.0,
    "scope2_mte": 0.0,
    "rtm_factor": 0.0
  },
  "timestamp": "optional ISO-8601 UTC"
}
```

**Response** (sealed record)
```json
{
  "entity_id": "...",
  "interval": "...",
  "inputs": {...},
  "computation": {
    "gate_state": "GREEN|YELLOW|BLACK",
    "policy_citations": ["Title 17 CCR §95111(...)"],
    "reasons": ["..."]
  },
  "merkle_leaf": "64-char hex",
  "running_merkle_root": "64-char hex",
  "seal": {
    "pubkey": "ed25519:<hex>",
    "signature": "<hex>"
  },
  "timestamp": "..."
}
```

## Batch / Ledger

- Engine maintains an in-memory Merkle tree for the session.
- Final root is deterministic for identical ordered inputs.
- Export as JSONL (one sealed record per line).

## Verification

Any third party can recompute the Merkle root and validate every Ed25519 signature using `kerna_verify.py` with no private material required.

## Webhooks (future)

Planned: `POST /v1/webhook/seal` for asynchronous facility submissions. Payload mirrors the process request. Response includes the sealed record + current root. Signature of the webhook body itself will use the same Ed25519 key for transport integrity.

## Status

Current implementation is the Python reference engine (`qreg_engine.py`). Rust runtime and gRPC surface are next.
