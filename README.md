# Q-Reg: Deterministic GHG Emissions Compliance Engine

[![CI](https://github.com/jabrahns-source/Q-Reg/actions/workflows/ci.yml/badge.svg)](https://github.com/jabrahns-source/Q-Reg/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A provably oriented, cryptographically sealed compliance surface for California SB 253 / CARB requirements.

## Overview

Q-Reg provides deterministic gate logic, Ed25519 sealing, and Merkle chaining for emissions records. It is designed to interoperate with the **VERA packet** format defined in the sibling repository [kerna-ledger-vci](https://github.com/jabrahns-source/kerna-ledger-vci).

Every material decision can be sealed into a packet that an independent party can verify with the open-core tools (content hash, signature, predicates, Merkle inclusion).

**Filing context:** First SB 253 Scope 1 + Scope 2 reports are due November 10, 2026.

## What It Does

1. Accepts emissions and factor data
2. Applies deterministic gate logic
3. Seals records (Ed25519)
4. Chains via Merkle trees
5. Emits artifacts that align with the VERA packet surface used across the Kerna-Ledger family

## Canonical Sealed Artifact

The preferred interchange format is the VERA packet (see `kerna-ledger-vci`).  
Q-Reg gate decisions and formal properties feed into that packet.  
Independent verification is performed with the clean-room tools in both repositories.

## Key Files

- `qreg_engine.py` — Core gate logic + sealing
- `kerna_verify.py` — Clean-room cryptographic verifier
- `formal/` — Idris 2 specifications and proofs
- `test_vectors.jsonl` / `test_vectors.py` — Adversarial suite

## Relationship to the Rest of the Surface

| Repository | Role |
|------------|------|
| [kerna-ledger-vci](https://github.com/jabrahns-source/kerna-ledger-vci) | VERA packet, content hash, Merkle, Organizational Boundary Packet, Auditor Verification Guide, SB 253 Mapping |
| [GridPulse](https://github.com/jabrahns-source/GridPulse) | Live Scope 2 receipt + penalty-clock demo |
| This repo (Q-Reg) | Formal gates, deterministic classification, clean-room verification patterns |

## Quick Start

```bash
git clone https://github.com/jabrahns-source/Q-Reg.git
cd Q-Reg
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python qreg_engine.py --demo
```

For packet-level verification see the Auditor Verification Guide and `auditor_verify.py` in kerna-ledger-vci.

## License

Apache 2.0

---

Built by Even The Odds Foundry
