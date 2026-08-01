# Q-Reg / Kerna-Ledger — one-command local verification
# Mirrors the GitHub Actions CI path so Chromebook / local runs stay identical.

.PHONY: help install demo test formal verify-all clean

PYTHON ?= python3
PIP    ?= pip

help:
	@echo "Q-Reg targets:"
	@echo "  make install     Install runtime + test dependencies"
	@echo "  make demo        Run deterministic demo → ledger.jsonl"
	@echo "  make test        Run 9-vector adversarial suite"
	@echo "  make formal      Run Z3 gate-logic verification"
	@echo "  make verify-all  Full path: demo + tests + formal + crypto checks"
	@echo "  make clean       Remove generated ledgers and coverage"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov

demo:
	$(PYTHON) qreg_engine.py --demo

test:
	$(PYTHON) -m pytest test_vectors.py -v --tb=short

formal:
	$(PYTHON) verification/verify_gate_logic.py

# Exact sequence used by CI (plus local convenience)
verify-all: demo test formal
	$(PYTHON) kerna_verify.py --ledger ledger.jsonl --check-merkle --validate-signatures
	@echo ""
	@echo "✓ verify-all passed — ledger is cryptographically consistent"

clean:
	rm -f ledger.jsonl remediation_report.md remediation_report.pdf coverage.xml
	rm -rf .pytest_cache __pycache__ .coverage
