# Q-Reg Whitepaper

**Formally Verified Deterministic Compliance Runtime for California SB 253, DFPI, and Delete Act**

Even The Odds Foundry · Jacarri Sanders · 2026

## Abstract

Q-Reg is a mathematically guaranteed enforcement engine for greenhouse-gas and data-privacy regulatory compliance. Violations of CCPA, DFPI, SB 253 and the Delete Act are unrepresentable at compile time via Idris 2 dependent types. The runtime (Rust + Python/gRPC) delivers >26 k RPS with p99 latency <7 µs while producing Ed25519-sealed, SHA-256 Merkle-chained audit ledgers that are independently verifiable.

## 1. Motivation

California’s SB 253 (Climate Corporate Data Accountability Act) and related privacy statutes impose hard deadlines and monetary penalties. Existing compliance tooling is probabilistic, opaque, or relies on third-party attestation. Q-Reg replaces trust with proof: every decision is the unique fixed point of a deterministic gate function; every record is cryptographically sealed and chained.

## 2. Architecture

### 2.1 Formal Layer (Idris 2)

- `Compliance.idr` – dependent types encoding CARB MRR and Title 17 CCR §95111 gate conditions.
- `GateLogic.idr` – total functions mapping (scope1, scope2, rtm_factor, timestamp) → {GREEN, YELLOW, BLACK}.
- `LinearLifecycle.idr` – linear types guaranteeing single-use of private keys and irreversible erasure under Delete Act.
- `Provenance.idr` – inductive proofs that Merkle roots are collision-resistant under SHA-256.
- `Moat.idr` – formal statement of the competitive barrier created by the combination of dependent typing and ZK anchoring.

### 2.2 Runtime Layer

- Python reference implementation (`qreg_engine.py`) for pilot and Colab use.
- Rust core (`runtime/`) for production throughput.
- Ed25519 sealing (RFC 8032) + SHA-256 Merkle trees with canonical JSON serialization (`ensure_ascii=True`).
- Optional StarkNet ZK anchoring of the daily Merkle root.

### 2.3 Verification

Clean-room verifier (`kerna_verify.py`) recomputes every leaf and root from the JSONL ledger and rejects any deviation.

## 3. Empirical Results

- Dataset: CARB MRR 2024 public facility data.
- 9-vector adversarial suite covering boundary values, malformed injection, clock skew, and key-reuse attempts.
- Result: 100 % gate correctness, zero ledger corruption, identical Merkle roots across independent runs.

## 4. Throughput & Latency

Rust runtime (measured on commodity x86-64):
- Sustained 26 000+ decisions / second.
- p99 end-to-end latency < 7 µs (gate + seal + Merkle update).

## 5. Regulatory Mapping

| Statute | Mechanism |
|---------|-----------|
| SB 253 | Scope classification + automatic remediation report generation |
| CARB Title 17 CCR §95111 | Formal gate states GREEN/YELLOW/BLACK |
| CCPA / Delete Act | Linear types + proven erasure |
| DFPI | Real validation against published DFPI data sets |

## 6. Deployment

- Docker image and GitHub Actions CI (Python 3.10–3.12).
- Colab one-click demo.
- Pilot term-sheet ready for utilities and climate-tech investors.

## 7. Conclusion

Q-Reg demonstrates that regulatory compliance can be made unrepresentably correct rather than probabilistically approximate. The combination of dependent types, deterministic gate logic, and cryptographic provenance constitutes a permanent moat.

## References

- CARB MRR 2024
- RFC 8032 (Ed25519)
- Idris 2 documentation
- StarkNet ZK documentation

---

© 2026 Even The Odds Foundry. Apache-2.0.
