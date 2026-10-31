# TrustLens AI — 2-Minute Demonstration Script & Judge Walkthrough

**Target Audience**: Hackathon Judges & Security Reviewers  
**Duration**: ~120 Seconds  
**Objective**: Demonstrate real, verifiable functionality across all 4 target prize tracks: Open-Source AI (DigitalOcean), Gemma 4 (Google), Graphify, and Cloudways.

---

## 1. Quick Pitch (15 Seconds)

> *"Students and job seekers lose millions every year to fake internship offers, predatory training fees, and lookalike domain phishing. Simple text filters fail because scams now arrive as PDFs and screenshots. 
> TrustLens AI provides evidence-first decision support. It never makes legal accusations; instead, it extracts verbatim ground-truth text, pairs Google's Gemma 4 multimodal model with an independent deterministic rules engine, and gives users an explainable risk breakdown with practical verification steps."*

---

## 2. Live Demo Steps (85 Seconds)

### Step 1: Uploading a Suspicious Offer (20 Seconds)
1. Open the TrustLens AI dashboard at `http://localhost:8000`.
2. Point out the persistent legal banner: *"Preliminary assessment, not proof of fraud."*
3. Click the sample button: **"Fake Internship Fee"** (or upload `samples/fake_internship_fee.pdf`).
4. Click **"Run TrustLens Verification"**.
5. **Show the Result**:
   - The Risk Score circle immediately jumps to **75 / 100 (HIGH RISK)**.
   - Point out the **Evidence Sufficiency: Sufficient** badge.

### Step 2: Explainable Scoring & Verbatim Evidence (30 Seconds)
1. Scroll to the **Transparent Risk Score Breakdown** table:
   - Highlight the **+35 pts** for `RULE_PAYMENT_REQUEST` ("Security Deposit").
   - Highlight the **+20 pts** for `RULE_URGENCY_PRESSURE` ("within 24 hours").
   - Highlight the **+20 pts** for `RULE_FREE_EMAIL_SENDER` ("globaltech.recruiter@gmail.com").
   - Show the **Deduplication counter**: Note that the messaging app redirection was deduplicated under sender identity to prevent unfair double-penalization.
2. Scroll to the **Verified Findings** cards:
   - Point out the exact verbatim quotes in blue code blocks.
   - Point out the provenance badge: `text-match-verified` (proved against extracted PDF text).

### Step 3: Markdown Export & Report Generation (15 Seconds)
1. Click **"Export Markdown Report (.md)"**.
2. Show that a complete, audit-ready Markdown document downloads instantly containing the executive summary, signals table, quoted evidence, unverified claims, and legal disclaimer.

### Step 4: Comparison with Legitimate Offer Letter (20 Seconds)
1. Click the **"Standard Offer Letter"** sample button (or upload `samples/legitimate_offer.pdf`).
2. Click **"Run TrustLens Verification"**.
3. **Show the Result**:
   - Risk score drops to **0 / 100 (LOW RISK)**.
   - Point out the **Context-Sensitive Negation**: Decode Labs stated *"never requests any registration fees or deposits"*, and TrustLens correctly handled the negation rather than falsely triggering a fee alert.
   - Point out the **Balanced Positive Signals**: Direct supervisor named, zero-cost equipment, official domain.
   - Emphasize: Even at 0 points, the system states *"Low Risk (Preliminary)"*, never *"Proven 100% Safe"*.

---

## 3. Technology & Prize Integrations Walkthrough (20 Seconds)

1. **Gemma 4 (Google)**:
   - Integrated via Google AI Studio API (`gemma-4-31b-it`).
   - Supports native multimodal image payloads (PNG/JPEG) for mobile phishing screenshots.
   - Enforced by strict Pydantic schemas with single-retry recovery on malformed output.
2. **Graphify**:
   - Codebase knowledge graph generated locally across 24 source files (237 nodes, 599 edges, 12 communities).
   - Agent queried: *"If I change the document analyzer, what is affected?"* — identifying `DocumentExtractor`, `RulesEngine`, `EvidenceVerifier`, and 3 affected test suites.
   - Output committed in `graphify-out/` with interactive force-directed visual viewer (`graph.html`).
3. **Open-Source AI (DigitalOcean)**:
   - Permissive Apache 2.0 license, clean modular architecture, 31 passing unit tests, and reproducible Docker Compose containerization.
4. **Cloudways**:
   - Production architecture documented for Cloudways Nginx reverse-proxy to Uvicorn process managed by Supervisor.
