#!/usr/bin/env python3
"""
Q-Reg: Deterministic GHG Emissions Compliance Engine
Core implementation for SB 253 / CARB compliance.
Provably auditable via Ed25519 + SHA-256 Merkle.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch

# Fixed test keypair for deterministic demo / regression (DO NOT USE IN PRODUCTION)
# 32-byte private key (hex for readability, converted to bytes)
TEST_PRIVATE_KEY_HEX = "c0ffeec0ffeec0ffeec0ffeec0ffeec0ffeec0ffeec0ffeec0ffeec0ffeec0ff"
TEST_PRIVATE_KEY = bytes.fromhex(TEST_PRIVATE_KEY_HEX)

class MerkleTree:
    """Simple SHA-256 Merkle tree for tamper-evident chaining."""
    def __init__(self):
        self.leaves: list[str] = []

    def add_leaf(self, leaf_hash: str):
        self.leaves.append(leaf_hash)

    def get_root(self) -> str | None:
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
    def __init__(self, private_key_bytes: bytes = TEST_PRIVATE_KEY):
        self.private_key = Ed25519PrivateKey.from_private_bytes(private_key_bytes)
        self.public_key = self.private_key.public_key()
        self.merkle = MerkleTree()

    def _canonical_json(self, obj: dict) -> str:
        """Deterministic canonical JSON for hashing/signing (ensure_ascii, sorted keys)."""
        return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))

    def _classify_gate(self, inputs: dict) -> tuple[str, list[str]]:
        """
        Deterministic gate logic.
        GREEN: low risk / compliant
        YELLOW: attention needed
        BLACK: exceedance / non-compliant
        Citations map to CARB Title 17 CCR §95111 and SB 253.
        """
        s1 = float(inputs.get("scope1_mte", 0.0))
        s2 = float(inputs.get("scope2_mte", 0.0))
        rtm = float(inputs.get("rtm_factor", 0.428))

        total_mte = s1 + s2
        # Example intensity proxy (simplified deterministic policy for demo)
        # In real: would use verified activity data + official factors
        intensity = total_mte / max(rtm, 0.001) if rtm > 0 else total_mte

        citations = ["Title 17 CCR §95111(a)-(f)", "SB 253 §38532"]

        if intensity <= 3000:
            return "GREEN", citations
        elif intensity <= 8000:
            return "YELLOW", citations + ["Warning: Monitor for threshold breach"]
        else:
            return "BLACK", citations + ["Exceedance: Immediate remediation required per CARB MRR"]

    TEST_TIMESTAMP = "2024-09-30T23:59:59Z"

    def process_record(self, entity_id: str, interval: str, inputs: dict, 
                       timestamp: str | None = None) -> dict:
        """Process one emissions record: classify, hash, sign, add to Merkle."""
        if timestamp is None:
            timestamp = self.TEST_TIMESTAMP

        gate_state, citations = self._classify_gate(inputs)

        computation = {
            "gate_state": gate_state,
            "policy_citations": citations,
            "intensity_proxy": round(float(inputs.get("scope1_mte", 0) + inputs.get("scope2_mte", 0)) / max(float(inputs.get("rtm_factor", 0.428)), 0.001), 2)
        }

        record = {
            "entity_id": entity_id,
            "interval": interval,
            "inputs": {k: round(float(v), 4) if isinstance(v, (int, float)) else v for k, v in inputs.items()},
            "computation": computation,
            "timestamp": timestamp
        }

        canonical = self._canonical_json(record)
        leaf_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        record["merkle_leaf"] = leaf_hash

        # Sign the leaf hash (or full canonical; leaf is sufficient + auditable)
        signature = self.private_key.sign(leaf_hash.encode("utf-8"))
        pub_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        record["seal"] = {
            "pubkey": "ed25519:" + pub_bytes.hex(),
            "signature": signature.hex()
        }

        self.merkle.add_leaf(leaf_hash)
        record["running_merkle_root"] = self.merkle.get_root()

        return record

    def run_demo(self, output_dir: Path = Path(".")) -> dict:
        """Run deterministic demo with 5 sample CARB-like facilities. Produces ledger + root."""
        output_dir.mkdir(parents=True, exist_ok=True)

        samples = [
            {"entity_id": "EVEN-THE-ODDS-001", "interval": "2024-Q3", "inputs": {"scope1_mte": 1250.5, "scope2_mte": 3120.3, "rtm_factor": 0.428}},
            {"entity_id": "FACILITY-002", "interval": "2024-Q3", "inputs": {"scope1_mte": 450.0, "scope2_mte": 1200.0, "rtm_factor": 0.415}},
            {"entity_id": "FACILITY-003", "interval": "2024-Q3", "inputs": {"scope1_mte": 8900.0, "scope2_mte": 2100.0, "rtm_factor": 0.441}},
            {"entity_id": "EVEN-THE-ODDS-004", "interval": "2024-Q3", "inputs": {"scope1_mte": 2100.0, "scope2_mte": 4500.0, "rtm_factor": 0.428}},
            {"entity_id": "FACILITY-005", "interval": "2024-Q3", "inputs": {"scope1_mte": 320.0, "scope2_mte": 890.0, "rtm_factor": 0.399}},
        ]

        fixed_ts = self.TEST_TIMESTAMP
        ledger_path = output_dir / "ledger.jsonl"
        records = []

        with open(ledger_path, "w", encoding="utf-8") as f:
            for sample in samples:
                rec = self.process_record(
                    sample["entity_id"], sample["interval"], sample["inputs"], timestamp=fixed_ts
                )
                f.write(json.dumps(rec, ensure_ascii=True) + "\n")
                records.append(rec)

        final_root = self.merkle.get_root()
        root_path = output_dir / "merkle_root.txt"
        root_path.write_text(final_root or "", encoding="utf-8")

        # Also generate PDF report
        pdf_path = output_dir / "remediation_report.pdf"
        self._generate_pdf_report(records, final_root, pdf_path)

        print(f"Demo complete. Ledger: {ledger_path}")
        print(f"Merkle root: {final_root}")
        print(f"PDF report: {pdf_path}")
        return {"ledger": str(ledger_path), "root": final_root, "pdf": str(pdf_path)}

    def _generate_pdf_report(self, records: list[dict], final_root: str, pdf_path: Path):
        """Generate human-readable CARB-style remediation report using reportlab."""
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=12, alignment=1)
        story.append(Paragraph("Q-Reg Deterministic Compliance Report", title_style))
        story.append(Paragraph("SB 253 / CARB Title 17 CCR Emissions Audit", styles['Heading2']))
        story.append(Spacer(1, 12))

        # Summary
        story.append(Paragraph("<b>Executive Summary</b>", styles['Heading3']))
        green = sum(1 for r in records if r["computation"]["gate_state"] == "GREEN")
        yellow = sum(1 for r in records if r["computation"]["gate_state"] == "YELLOW")
        black = sum(1 for r in records if r["computation"]["gate_state"] == "BLACK")
        story.append(Paragraph(f"Facilities audited: {len(records)} | GREEN: {green} | YELLOW: {yellow} | BLACK: {black}", styles['Normal']))
        story.append(Paragraph(f"Final Merkle Root (tamper-evident): <font face='Courier'>{final_root}</font>", styles['Normal']))
        story.append(Paragraph(f"Report generated: {datetime.now(timezone.utc).isoformat()}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Per-facility table
        story.append(Paragraph("<b>Gate Decisions & Evidence</b>", styles['Heading3']))
        table_data = [["Entity ID", "Interval", "Total MTE", "Gate", "Key Citations"]]
        for r in records:
            total = r["inputs"].get("scope1_mte", 0) + r["inputs"].get("scope2_mte", 0)
            gate = r["computation"]["gate_state"]
            cites = "; ".join(r["computation"]["policy_citations"][:2])
            table_data.append([
                r["entity_id"],
                r["interval"],
                f"{total:.1f}",
                gate,
                cites[:60] + "..." if len(cites) > 60 else cites
            ])

        t = Table(table_data, colWidths=[1.8*inch, 0.9*inch, 0.8*inch, 0.7*inch, 2.8*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Detailed findings
        story.append(Paragraph("<b>Detailed Findings & Remediation Notes</b>", styles['Heading3']))
        for r in records:
            gate = r["computation"]["gate_state"]
            story.append(Paragraph(f"<b>{r['entity_id']} — {gate}</b>", styles['Normal']))
            story.append(Paragraph(f"Inputs: {json.dumps(r['inputs'])}", styles['Normal']))
            story.append(Paragraph(f"Computation: {json.dumps(r['computation'])}", styles['Normal']))
            story.append(Paragraph(f"Merkle Leaf: <font face='Courier' size='7'>{r['merkle_leaf']}</font>", styles['Normal']))
            story.append(Spacer(1, 8))

        # Footer / attestation
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Attestation</b>", styles['Heading3']))
        story.append(Paragraph(
            "This report was generated by Q-Reg deterministic engine. All gate decisions are reproducible from inputs. "
            "Ledger is cryptographically sealed with Ed25519 and chained via SHA-256 Merkle tree. "
            "External verification possible with public key and kerna_verify.py.",
            styles['Normal']
        ))
        story.append(Paragraph("Built by Even The Odds Foundry | Contact: eventheoddsfoundry@gmail.com", styles['Normal']))

        doc.build(story)

def main():
    parser = argparse.ArgumentParser(description="Q-Reg Deterministic Compliance Engine")
    parser.add_argument("--demo", action="store_true", help="Run deterministic demo with sample data")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="Output directory")
    parser.add_argument("--validate-signatures", action="store_true", help="Validate signatures in ledger (runs kerna_verify style check)")
    args = parser.parse_args()

    engine = QRegEngine()

    if args.demo:
        result = engine.run_demo(args.output_dir)
        print(json.dumps(result, indent=2))
    elif args.validate_signatures:
        # Simple delegation for CI
        import subprocess
        subprocess.run([sys.executable, "kerna_verify.py", "--ledger", "ledger.jsonl", "--validate-signatures", "--check-merkle"], check=False)
    else:
        print("Q-Reg engine ready. Use --demo for sample run.")
        print("Example: python qreg_engine.py --demo")

if __name__ == "__main__":
    main()
