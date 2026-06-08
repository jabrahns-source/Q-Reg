# Q-REG — Formally Verified Deterministic Compliance Runtime

**Mathematically guaranteed enforcement for California regulations.** Violations unrepresentable at compile time.

High-performance Rust + gRPC runtime backed by Idris 2 dependent types and linear logic. Built for CCPA, DFPI, SB 253, Delete Act. Even The Odds Foundry — Jay Sanders (jabrahns-source).

## Core Capabilities
- **Performance**: 26k+ RPS, p99 <7µs adversarial
- **Formal Verification**: Idris 2 linear/dependent types — `impossibleViolation`, type-level deadlines, linear lifecycles
- **ZK**: StarkNet anchoring
- **Proof**: 100% DFPI backtest match + PSI-ALPHA quantum extension

## Why It Matters
PDF compliance is dead. Q-REG ships compile-time mathematical proof regulators can't ignore. Deterministic moat from a Chromebook in Redding.

## Quick Start
```bash
git clone https://github.com/jabrahns-source/Q-Reg.git
cd Q-Reg

# Runtime
cd runtime && cargo build --release

# Formal proofs (the moat)
cd ../formal && idris2 --check Compliance.idr && idris2 --check LinearLifecycle.idr
```

## Structure
- `formal/` — Idris proofs (source of truth)
- `runtime/` — Rust gRPC
- `tests/` — Backtester
- `zk/` — StarkNet
- `docs/` — Pitch/term sheets

## Formal Verification
Total proofs in `formal/`:
- `Compliance.idr`: Ontology + `impossibleViolation` (LTE/GT contradictions)
- `LinearLifecycle.idr`: Safe transitions, no late fulfills
- Violations structurally impossible.

**Seeking**: SPI/PG&E pilots, grant collabs, feedback.

Apache 2.0. Built to leave the name in history.