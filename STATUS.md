# Project Status

**Current Stage: Open-core audit surface + formal foundation (November 2026)**

## What's Complete

- Full Idris 2 formal verification suite (`Compliance.idr`, `LinearLifecycle.idr`, `GateLogic.idr`, `Provenance.idr`, etc.)
- Type-level guarantees for key regulatory windows (including SB 253 365-day)
- `impossibleViolation` and related compliance theorems
- Deterministic gate logic + Ed25519 sealing + Merkle chaining
- Clean-room verifier (`kerna_verify.py`)
- Integration path with the VERA packet format (canonical sealed artifact used across the Kerna-Ledger family)
- Adversarial test vectors and CI

## What's In Progress

- Tighter runtime extraction from the Idris specifications
- Expanded test coverage for boundary and attestation packet types
- StarkNet / ZK anchoring experiments (non-blocking for core surface)

## What's Not Ready

- Production multi-tenant deployment / SOC 2
- Full enterprise data-ingestion connectors
- Large-scale third-party assurance engagements (the evidence surface exists; the operational scale does not yet)

## Relationship to Sibling Repositories

- **kerna-ledger-vci** — Canonical VERA packet, content hash, Merkle proofs, Organizational Boundary Packet, Auditor Verification Guide, and SB 253 Mapping document.
- **GridPulse** — Public Scope 2 receipt + penalty-clock demonstration that consumes the same packet surface.
- This repository (Q-Reg) supplies the formal gate logic, clean-room verification patterns, and the broader compliance runtime orientation.

The sealed packet is the common language. Formal proofs and gate decisions feed into it; independent verifiers operate on it.

Built by Jacarri Sanders — Even The Odds Foundry.
