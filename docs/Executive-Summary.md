# Q-Reg Executive Summary

**Even The Odds Foundry — July 2026**

## One-sentence pitch
Q-Reg is the first formally verified, deterministic compliance runtime that makes SB 253 / CARB / DFPI / Delete Act violations unrepresentable at compile time while delivering production-grade throughput and independently verifiable cryptographic ledgers.

## Problem
California’s climate and privacy statutes impose hard deadlines and large penalties. Existing tooling is either probabilistic (ML-based classifiers), opaque (third-party auditors), or non-reproducible. Enterprises cannot prove, to a regulator or a court, that every decision was the unique correct outcome of the statute.

## Solution
1. **Idris 2 dependent types** encode the regulatory rules so illegal states cannot be constructed.
2. **Deterministic gate logic** (GREEN / YELLOW / BLACK) maps every emission or data event to a unique policy state.
3. **Ed25519 sealing + SHA-256 Merkle chaining** produces a tamper-evident, non-repudiable audit trail.
4. **Clean-room verifier** allows any third party to recompute the entire ledger and confirm correctness.
5. **Rust + gRPC runtime** delivers >26 k decisions/s at <7 µs p99.

## Traction & Status
- Full formal proofs for gate logic, linear lifecycle, provenance and erasure.
- Empirical validation against real CARB MRR 2024 data (100 % gate correctness).
- Pilot-ready Docker image and Colab notebook.
- Filing deadline alignment: November 10, 2026 (SB 253).

## Market
Utilities, large emitters, climate-tech SaaS, and any entity subject to SB 253 or CCPA/Delete Act. Immediate pilot candidates: PG&E, SDG&E, and compliance software vendors needing a deterministic core.

## Ask
Pilot term-sheet conversations with utilities and climate investors. Technical diligence package (formal proofs + clean-room verifier + adversarial test suite) available under NDA or public inspection.

## Contact
Jacarri Sanders  
Even The Odds Foundry  
GitHub: @jabrahns-source
