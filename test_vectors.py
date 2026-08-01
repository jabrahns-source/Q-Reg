#!/usr/bin/env python3
"""
test_vectors.py — Adversarial + regression test suite for Q-Reg.
9 vectors covering GREEN/YELLOW/BLACK edges, zero, high, normal.
Uses deterministic engine so seals and Merkle roots are reproducible.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qreg_engine import QRegEngine


def load_vectors():
    path = Path(__file__).parent / "test_vectors.jsonl"
    vectors = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                vectors.append(json.loads(line))
    return vectors


def test_all_vectors_classify_and_seal():
    # Deterministic key so CI and local runs produce identical seals/roots
    engine = QRegEngine(deterministic=True)
    vectors = load_vectors()
    assert len(vectors) == 9, "Expected exactly 9 test vectors"

    results = []
    for v in vectors:
        rec = engine.process_record(
            v["entity_id"],
            v["interval"],
            v["inputs"],
            timestamp="2024-10-01T00:00:00Z",
        )
        results.append(rec)
        # Basic structural checks
        assert "merkle_leaf" in rec
        assert "seal" in rec
        assert rec["computation"]["gate_state"] in ("GREEN", "YELLOW", "BLACK")
        assert len(rec["seal"]["signature"]) > 0
        assert rec["seal"]["pubkey"].startswith("ed25519:")

    # At least one of each gate expected from the chosen vectors
    gates = [r["computation"]["gate_state"] for r in results]
    assert "GREEN" in gates
    assert "YELLOW" in gates
    assert "BLACK" in gates

    # Merkle root should be non-None after processing
    final_root = engine.merkle.get_root()
    assert final_root is not None
    assert len(final_root) == 64  # SHA256 hex


def test_merkle_consistency():
    vectors = load_vectors()[:3]  # subset for speed

    engine = QRegEngine(deterministic=True)
    for v in vectors:
        engine.process_record(
            v["entity_id"],
            v["interval"],
            v["inputs"],
            timestamp="2024-10-01T00:00:00Z",
        )
    root1 = engine.merkle.get_root()

    # Rebuild fresh with same deterministic key and timestamps
    engine2 = QRegEngine(deterministic=True)
    for v in vectors:
        engine2.process_record(
            v["entity_id"],
            v["interval"],
            v["inputs"],
            timestamp="2024-10-01T00:00:00Z",
        )
    root2 = engine2.merkle.get_root()
    assert root1 == root2, "Merkle root must be deterministic for same inputs/order"


def test_demo_produces_verifiable_ledger(tmp_path, monkeypatch):
    """End-to-end: demo writes a ledger that kerna_verify accepts."""
    import qreg_engine

    monkeypatch.chdir(tmp_path)
    qreg_engine.demo()
    ledger_path = tmp_path / "ledger.jsonl"
    assert ledger_path.exists()

    # Inline a minimal verification to avoid subprocess dependency in unit tests
    from kerna_verify import load_ledger, recompute_merkle_root, validate_signatures, check_gate_consistency

    records = load_ledger(ledger_path)
    assert len(records) == 3
    root = recompute_merkle_root(records)
    assert root == records[-1]["running_merkle_root"]
    assert validate_signatures(records)
    assert check_gate_consistency(records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
