#!/usr/bin/env python3
"""
qreg_engine.py — Core deterministic compliance engine for Q-Reg / Kerna-Ledger.

Implements:
- Deterministic gate classification (GREEN / YELLOW / BLACK) from emissions + RTM factors
- Ed25519 non-repudiable sealing (RFC 8032)
- SHA-256 Merkle tree chaining for tamper-evident audit ledger
- Running Merkle root for session consistency

All decisions are pure functions of inputs + fixed policy constants.
No randomness, no external network calls in the critical path.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


# ---------------------------------------------------------------------------
# Policy constants (locked for determinism and regression)
# ---------------------------------------------------------------------------

SCOPE1_YELLOW = 50_000.0
SCOPE1_BLACK = 250_000.0
RTM_YELLOW = 0.35
RTM_BLACK = 0.50

VALID_GATES = {"GREEN", "YELLOW", "BLACK"}


@dataclass
class GateResult:
    gate_state: str
    policy_citations: List[str]
    reasons: List[str]


@dataclass
class MerkleNode:
    leaves: List[str] = field(default_factory=list)

    def add_leaf(self, leaf_hex: str) -> None:
        self.leaves.append(leaf_hex)

    def get_root(self) -> Optional[str]:
        if not self.leaves:
            return None
        level = self.leaves[:]
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else left
                combined = (left + right).encode("utf-8")
                next_level.append(hashlib.sha256(combined).hexdigest())
            level = next_level
        return level[0]


class QRegEngine:
    """
    Deterministic emissions compliance gate + cryptographic sealer.
    One instance owns a single Merkle tree for the processing session.
    """

    def __init__(self, private_key: Optional[Ed25519PrivateKey] = None):
        if private_key is None:
            self._private_key = Ed25519PrivateKey.generate()
        else:
            self._private_key = private_key
        self._public_key = self._private_key.public_key()
        self.merkle = MerkleNode()
        self._running_root: Optional[str] = None

    @property
    def public_key_hex(self) -> str:
        raw = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return "ed25519:" + raw.hex()

    def _classify_gate(self, inputs: Dict[str, float]) -> GateResult:
        """Pure deterministic policy. Order of checks is fixed."""
        scope1 = float(inputs.get("scope1_mte", 0.0))
        scope2 = float(inputs.get("scope2_mte", 0.0))
        rtm = float(inputs.get("rtm_factor", 0.0))

        citations: List[str] = []
        reasons: List[str] = []

        if scope1 >= SCOPE1_BLACK or rtm >= RTM_BLACK:
            state = "BLACK"
            citations.append("Title 17 CCR §95111(f)")
            if scope1 >= SCOPE1_BLACK:
                reasons.append(f"scope1_mte={scope1} >= {SCOPE1_BLACK}")
            if rtm >= RTM_BLACK:
                reasons.append(f"rtm_factor={rtm} >= {RTM_BLACK}")
        elif scope1 >= SCOPE1_YELLOW or rtm >= RTM_YELLOW:
            state = "YELLOW"
            citations.append("Title 17 CCR §95111(c)")
            if scope1 >= SCOPE1_YELLOW:
                reasons.append(f"scope1_mte={scope1} >= {SCOPE1_YELLOW}")
            if rtm >= RTM_YELLOW:
                reasons.append(f"rtm_factor={rtm} >= {RTM_YELLOW}")
        else:
            state = "GREEN"
            citations.append("Title 17 CCR §95111(a)")
            reasons.append("within GREEN thresholds")

        total = scope1 + scope2
        if total > 0 and state == "GREEN" and rtm > 0.25:
            reasons.append(f"total_intensity_note={total:.1f}")

        return GateResult(gate_state=state, policy_citations=citations, reasons=reasons)

    def _make_leaf(self, entity_id: str, interval: str, inputs: Dict[str, float], gate: GateResult) -> str:
        """Canonical serialization for Merkle leaf. ensure_ascii + sorted keys for determinism."""
        payload = {
            "entity_id": entity_id,
            "interval": interval,
            "inputs": {k: float(v) for k, v in sorted(inputs.items())},
            "gate_state": gate.gate_state,
            "policy_citations": gate.policy_citations,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _sign(self, leaf_hex: str) -> Dict[str, str]:
        signature = self._private_key.sign(leaf_hex.encode("utf-8"))
        return {
            "pubkey": self.public_key_hex,
            "signature": signature.hex(),
        }

    def process_record(
        self,
        entity_id: str,
        interval: str,
        inputs: Dict[str, float],
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline for one record:
        1. Classify gate
        2. Build canonical leaf
        3. Sign leaf
        4. Append to Merkle tree
        5. Emit sealed record with running root
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        gate = self._classify_gate(inputs)
        leaf = self._make_leaf(entity_id, interval, inputs, gate)
        seal = self._sign(leaf)

        self.merkle.add_leaf(leaf)
        self._running_root = self.merkle.get_root()

        record = {
            "entity_id": entity_id,
            "interval": interval,
            "inputs": {k: float(v) for k, v in inputs.items()},
            "computation": {
                "gate_state": gate.gate_state,
                "policy_citations": gate.policy_citations,
                "reasons": gate.reasons,
            },
            "merkle_leaf": leaf,
            "running_merkle_root": self._running_root,
            "seal": seal,
            "timestamp": timestamp,
        }
        return record


def demo() -> None:
    """Self-contained demo that produces a small sealed ledger."""
    engine = QRegEngine()
    samples = [
        ("FAC-GREEN-01", "2024-Q3", {"scope1_mte": 12000.0, "scope2_mte": 800.0, "rtm_factor": 0.22}),
        ("FAC-YELLOW-02", "2024-Q3", {"scope1_mte": 78000.0, "scope2_mte": 0.0, "rtm_factor": 0.41}),
        ("CALPORTLAND-REDDING", "2024-Q3", {"scope1_mte": 372761.0, "scope2_mte": 0.0, "rtm_factor": 0.428}),
    ]
    records = []
    for eid, interval, inputs in samples:
        rec = engine.process_record(eid, interval, inputs)
        records.append(rec)
        print(f"{eid}: gate={rec['computation']['gate_state']} leaf={rec['merkle_leaf'][:16]}...")

    print(f"\nFinal Merkle root: {engine.merkle.get_root()}")
    with open("ledger.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")
    print("Wrote ledger.jsonl")


if __name__ == "__main__":
    if "--demo" in sys.argv or len(sys.argv) == 1:
        demo()
        sys.exit(0)
    elif "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python qreg_engine.py [--demo]")
        print("  --demo   Run deterministic demo and write ledger.jsonl")
        sys.exit(0)
    else:
        print("Unknown arguments. Use --demo or --help.")
        sys.exit(1)
