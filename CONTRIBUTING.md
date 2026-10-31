# Contributing to TrustLens AI

Thank you for your interest in contributing to **TrustLens AI**! Our mission is to protect students, job seekers, and digital citizens from predatory scam offers, phishing communications, and fraudulent solicitations through transparent, explainable AI and deterministic rules.

---

## 1. Core Engineering & Ethical Principles

Before proposing changes, please review our fundamental non-negotiables:

1. **Evidence First**: Every AI finding must quote verbatim ground-truth text. Never assert a risk without quoting exact source evidence.
2. **Deterministic Precedence**: Rules must run independently on extracted text and never be suppressed by adversarial prompt injections.
3. **Transparent Scoring**: Never present an arbitrary percentage as a "calibrated probability of fraud". Use explainable, per-signal heuristic points (0 to 100).
4. **No Accusations**: The platform reports signals, anomalies, and uncertainty. It **never** asserts that a named person or company is fraudulent or guilty of a crime.
5. **No Synthetic Hallucinations**: Never hardcode fake results or simulate live AI output. Use mocks only in explicitly labelled automated unit tests.

---

## 2. Local Development Setup

### Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Git
- Docker & Docker Compose (optional for local container testing)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/your-org/trustlens-ai.git
cd trustlens-ai

# 2. Create virtual environment
python -m venv .venv

# Activate on Windows:
.\.venv\Scripts\activate
# Activate on Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env
```

### Running the Test Suite
Ensure all 31+ unit and integration tests pass:
```bash
pytest -v
```

### Starting the Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 3. Good First Issue Opportunities

If you're looking for an impactful first contribution, we welcome PRs for these prioritized tasks:

1. **[Good First Issue] Expand Target Brands for Lookalike Domain Detection**:
   - Location: `app/core/domain_checks.py` & `app/core/rules.py`
   - Scope: Add regional tech employers, banking portals, and educational institutions with corresponding negative tests.
2. **[Good First Issue] Add OCR Bounding Box Canvas Rendering**:
   - Location: `app/static/app.js` & `app/core/extractor.py`
   - Scope: Render visual bounding boxes over suspicious passages on the rendered PDF preview.
3. **[Good First Issue] Multi-Lingual Regex Support for Indian Languages**:
   - Location: `app/core/rules.py`
   - Scope: Add transliterated and script-based triggers for Hindi/Telugu fee solicitations (e.g. "रजिस्ट्रेशन फीस", "డబ్బులు చెల్లించండి").
4. **[Good First Issue] CLI Analysis Tool**:
   - Location: `app/cli.py`
   - Scope: Provide a terminal command `trustlens analyze sample.pdf --json` for terminal-based pipeline verification.

---

## 4. Submitting a Pull Request

1. Fork the repository and create a feature branch (`git checkout -b feature/my-new-rule`).
2. Implement your changes adhering to existing typing and Pydantic schemas.
3. Add positive and negative unit tests in `tests/`.
4. Run `pytest -v` to ensure all tests pass.
5. Submit your PR with a clear description of the evidence rules or fixes introduced.
