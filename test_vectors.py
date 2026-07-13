#!/usr/bin/env python3
"""
test_vectors.py — Adversarial + regression test suite for Q-Reg.
9 vectors covering GREEN/YELLOW/BLACK edges, zero, high, normal.
"""

import json
import pytest
from pathlib import Path
from qreg_engine import QRegEngine  # Assumes same dir or PYTHONPATH

def load_vectors():
    path = Path(__file__).parent / "test_vectors.jsonl"
    vectors = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                vectors.append(json.loads(line))
    return vectors

def test_all_vectors_classify_and_seal():
    engine = QRegEngine()
    vectors = load_vectors()
    assert len(vectors) == 9, "Expected exactly 9 test vectors"

    results = []
    for v in vectors:
        rec = engine.process_record(v["entity_id"], v["interval"], v["inputs"])
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
    engine = QRegEngine()
    vectors = load_vectors()[:3]  # subset for speed
    for v in vectors:
        engine.process_record(v["entity_id"], v["interval"], v["inputs"])
    root1 = engine.merkle.get_root()

    # Rebuild fresh
    engine2 = QRegEngine()
    for v in vectors:
        engine2.process_record(v["entity_id"], v["interval"], v["inputs"])
    root2 = engine2.merkle.get_root()
    assert root1 == root2, "Merkle root must be deterministic for same inputs/order"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
