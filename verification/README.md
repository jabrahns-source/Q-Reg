# Z3 Formal Verification Certificates — Q-Reg

Machine-checked SMT proofs that complement the Idris 2 dependent-type guarantees in `formal/`.

## Scripts

| Script | What it proves |
|--------|----------------|
| `verify_gate_logic.py` | Deterministic gate partition, mutual exclusion, monotonicity, and exact threshold boundaries for GREEN/YELLOW/BLACK classification. |

## Run locally

```bash
pip install z3-solver
python verification/verify_gate_logic.py
```

Expected output ends with:
```
All Q-Reg gate logic properties verified (UNSAT on all negations).
```

These certificates are intended for CI and for pilot/regulatory scrutiny (SB 253 / CARB Title 17).

Even The Odds Foundry LLC · 2026
