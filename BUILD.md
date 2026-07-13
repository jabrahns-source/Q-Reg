# Building & Running Q-Reg

## Prerequisites

- Python 3.10+ (3.11, 3.12 tested)
- Git
- pip or conda

## Option 1: Google Colab (Recommended for Quick Demo)

1. Open https://colab.research.google.com
2. New notebook
3. Run:

```python
!git clone https://github.com/jabrahns-source/q-reg.git
%cd q-reg
!pip install -r requirements.txt
!python qreg_engine.py --demo
```

4. Output appears in current directory as `ledger.jsonl` + `report.pdf`

## Option 2: Local Installation

```bash
git clone https://github.com/jabrahns-source/q-reg.git
cd q-reg

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run engine
python qreg_engine.py

# Run tests
pytest test_vectors.py -v

# Verify cryptographic ledger
python kerna_verify.py --check-merkle
```

## Option 3: Docker

```bash
git clone https://github.com/jabrahns-source/q-reg.git
cd q-reg

docker build -t qreg .
docker run -v $(pwd)/data:/data qreg python qreg_engine.py
```

## Option 4: Chromebook (via Colab)

Q-Reg runs on Chromebook via Google Colab. No local installation needed.

1. Open Colab in Chrome
2. Paste the commands from Option 1
3. Download outputs directly

## Running Tests

```bash
# Full test suite (9-vector adversarial)
pytest test_vectors.py -v

# Merkle tree verification (clean-room)
python kerna_verify.py --check-merkle

# Single test vector
python qreg_engine.py --test-vector vectors/001.json
```

## CI/CD

On GitHub push, GitHub Actions automatically:
- Runs tests on Python 3.10, 3.11, 3.12
- Verifies Merkle root correctness
- Validates Ed25519 signatures
- Generates coverage report

See `.github/workflows/ci.yml` for details.

## Troubleshooting

**ImportError: No module named 'qreg_engine'**
- Ensure you're in the q-reg directory: `cd q-reg`
- Ensure venv is activated: `source venv/bin/activate`

**SHA-256 mismatch errors**
- Verify `ensure_ascii=True` in `json.dumps()` calls
- Check for non-ASCII characters in entity IDs or field names

**Merkle root doesn't match**
- Run `python kerna_verify.py --check-merkle` to identify which record is corrupted
- All downstream records after the corruption are invalidated

**Out of memory on Colab**
- Reduce batch size: `python qreg_engine.py --batch-size 100`
- Run one facility at a time: `python qreg_engine.py --facility FACILITY_ID`

## Output Files

- `ledger.jsonl` — Append-only audit ledger (CARB-compliant format)
- `report.pdf` — Human-readable PDF with gate decisions + regulatory citations
- `merkle_root.txt` — Final Merkle root (for verification)
- `signatures.jsonl` — All Ed25519 signatures (for external audit)

## Next Steps

1. **Verify locally** with test data: `pytest test_vectors.py`
2. **Run against your facility data** (CSV format): `python qreg_engine.py --input your_data.csv`
3. **Generate CARB report** for submission: `python remediation_report_gen.py ledger.jsonl`
4. **Audit externally** using public key: `python kerna_verify.py --ledger ledger.jsonl --pubkey public.key`