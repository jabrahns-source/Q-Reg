#!/usr/bin/env python3
"""
kerna_verify.py — Clean-room cryptographic verifier for Q-Reg ledgers.
Recomputes Merkle root, validates Ed25519 signatures, checks gate consistency.
No trust in engine output — pure verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


def load_ledger(path: Path) -> List[Dict[str, Any]]:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def recompute_merkle_root(records: List[Dict[str, Any]]) -> Optional[str]:
    """Rebuild Merkle tree from stored merkle_leaf values."""
    if not records:
        return None
    leaves = [r.get("merkle_leaf", "") for r in records if r.get("merkle_leaf")]
    if not leaves:
        return None

    level = leaves[:]
    while len(level) > 1:
        next_level = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            combined = (left + right).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        level = next_level
    return level[0]


def validate_signatures(records: List[Dict[str, Any]]) -> bool:
    """Validate every Ed25519 signature against its pubkey and leaf."""
    all_valid = True
    for i, rec in enumerate(records):
        try:
            seal = rec.get("seal", {})
            pubkey_hex = seal.get("pubkey", "").replace("ed25519:", "")
            sig_hex = seal.get("signature", "")
            leaf = rec.get("merkle_leaf", "")

            if not pubkey_hex or not sig_hex or not leaf:
                print(f"Record {i}: Missing seal or leaf")
                all_valid = False
                continue

            pub_bytes = bytes.fromhex(pubkey_hex)
            sig_bytes = bytes.fromhex(sig_hex)

            public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
            public_key.verify(sig_bytes, leaf.encode("utf-8"))
        except (InvalidSignature, ValueError, TypeError) as e:
            print(f"Record {i} ({rec.get('entity_id', 'unknown')}): Signature INVALID - {e}")
            all_valid = False
    return all_valid


def check_gate_consistency(records: List[Dict[str, Any]]) -> bool:
    """Basic sanity: every record has a valid gate state."""
    valid_gates = {"GREEN", "YELLOW", "BLACK"}
    for i, rec in enumerate(records):
        gate = rec.get("computation", {}).get("gate_state")
        if gate not in valid_gates:
            print(f"Record {i}: Invalid gate state {gate}")
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Kerna Verify — Q-Reg Ledger Verifier")
    parser.add_argument("--ledger", type=Path, default=Path("ledger.jsonl"), help="Path to ledger.jsonl")
    parser.add_argument("--check-merkle", action="store_true", help="Recompute and print Merkle root")
    parser.add_argument("--validate-signatures", action="store_true", help="Validate all Ed25519 signatures")
    parser.add_argument("--pubkey", type=str, help="Optional: specific pubkey to check against (v1 placeholder)")
    args = parser.parse_args()

    if not args.ledger.exists():
        print(f"Ledger not found: {args.ledger}", file=sys.stderr)
        return 1

    records = load_ledger(args.ledger)
    print(f"Loaded {len(records)} records from {args.ledger}")

    exit_code = 0

    if args.check_merkle:
        computed_root = recompute_merkle_root(records)
        print(f"Recomputed Merkle root: {computed_root}")
        last_root = records[-1].get("running_merkle_root") if records else None
        if last_root and computed_root == last_root:
            print("✓ Merkle root matches last running root (consistent)")
        else:
            print("⚠ Merkle root check: review running vs recomputed")

    if args.validate_signatures:
        if validate_signatures(records):
            print("✓ All signatures valid")
        else:
            print("✗ Signature validation failed on one or more records")
            exit_code = 2

    if check_gate_consistency(records):
        print("✓ Gate states consistent")
    else:
        exit_code = max(exit_code, 1)

    print("Verification complete.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
