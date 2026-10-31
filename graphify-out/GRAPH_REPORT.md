# Graph Report - Hactober  (2026-10-31)

## Corpus Check
- 35 files · ~20,578 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 364 nodes · 788 edges · 18 communities (14 shown, 4 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 141 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- test_extractor.py
- RuleHit
- routes.py
- gemma_client.py
- ExtractionMetadata
- TrustLens AI - Requirements Traceability Matrix
- AnalysisResponse
- app.js
- typing
- TrustLens AI 🔍🛡️
- 4. Phase-by-Phase Execution Roadmap
- trustlens
- 2. Step-by-Step Server Setup Guide
- TrustLens AI - Integration Verification & Feasibility Analysis
- 2. Live Demo Steps (85 Seconds)
- TrustLens AI - Build & Milestone Status

## God Nodes (most connected - your core abstractions)
1. `RuleHit` - 30 edges
2. `SeverityLevel` - 27 edges
3. `DocumentExtractor` - 23 edges
4. `FindingCategory` - 23 edges
5. `ExtractionMetadata` - 23 edges
6. `ProvenanceStatus` - 20 edges
7. `TrustLens AI - Requirements Traceability Matrix` - 18 edges
8. `EvidenceVerifier` - 17 edges
9. `AnalysisResponse` - 17 edges
10. `RiskLevel` - 16 edges

## Surprising Connections (you probably didn't know these)
- `8. REST API Documentation` --references--> `AnalysisResponse`  [INFERRED]
  README.md → app/core/schemas.py
- `3. Technology & Prize Integrations Walkthrough (20 Seconds)` --references--> `EvidenceVerifier`  [INFERRED]
  docs/demo-script.md → app/core/evidence.py
- `3. Top Architectural God Nodes (Core Central Abstractions)` --references--> `EvidenceVerifier`  [INFERRED]
  docs/graphify.md → app/core/evidence.py
- `Graph-Assisted Impact Analysis:` --references--> `EvidenceVerifier`  [INFERRED]
  docs/graphify.md → app/core/evidence.py
- `3. Technology & Prize Integrations Walkthrough (20 Seconds)` --references--> `DocumentExtractor`  [INFERRED]
  docs/demo-script.md → app/core/extractor.py

## Import Cycles
- None detected.

## Communities (18 total, 4 thin omitted)

### Community 0 - "test_extractor.py"
Cohesion: 0.12
Nodes (16): CorruptedFileError, DocumentExtractor, ExtractionError, FileOversizedError, UnsupportedFileTypeError, generate_fake_internship_pdf(), generate_legitimate_offer_pdf(), create_minimal_pdf_bytes() (+8 more)

### Community 1 - "RuleHit"
Cohesion: 0.16
Nodes (22): ConflictingClaimsRule, DeterministicRule, FreeEmailSenderRule, LookalikeDomainRule, MessagingAppMoveRule, PaymentRequestRule, RulesEngine, UnrealisticOfferRule (+14 more)

### Community 2 - "routes.py"
Cohesion: 0.07
Nodes (5): get_demo_samples(), health_check(), Settings, rate_limit_middleware(), serve_index()

### Community 3 - "gemma_client.py"
Cohesion: 0.10
Nodes (10): GemmaApiKeyMissingError, GemmaClient, GemmaClientError, GemmaSchemaValidationError, DocumentType, GemmaAnalysisResult, test_reject_confidence_out_of_bounds(), test_reject_missing_required_fields() (+2 more)

### Community 4 - "ExtractionMetadata"
Cohesion: 0.13
Nodes (14): EvidenceVerifier, normalize_whitespace(), AnalyzeTextRequest, ExtractionMetadata, GemmaFinding, HealthResponse, ProvenanceStatus, ScoreBreakdown (+6 more)

### Community 5 - "TrustLens AI - Requirements Traceability Matrix"
Cohesion: 0.15
Nodes (13): RiskLevel, TrustLens AI - Requirements Traceability Matrix, test_case_1_several_warning_signs(), test_case_2_ordinary_offer_without_warning_signs(), test_case_3_document_with_conflicting_information(), test_case_4_incomplete_sparse_document(), test_adversarial_prompt_injection_does_not_suppress_rules(), test_full_rules_engine_multi_hit() (+5 more)

### Community 6 - "AnalysisResponse"
Cohesion: 0.11
Nodes (11): analyze_document(), analyze_text_json(), export_markdown(), DocumentAnalyzer, ReportBuilder, AnalysisResponse, Graph-Assisted Impact Analysis:, test_analyze_text_json_endpoint() (+3 more)

### Community 9 - "TrustLens AI 🔍🛡️"
Cohesion: 0.06
Nodes (33): 1. Core Engineering & Ethical Principles, 2. Local Development Setup, 3. Good First Issue Opportunities, 4. Submitting a Pull Request, Contributing to TrustLens AI, Installation, Prerequisites, Running the Test Suite (+25 more)

### Community 12 - "4. Phase-by-Phase Execution Roadmap"
Cohesion: 0.12
Nodes (16): 1. Executive Summary & Problem Statement, 2. Target Prizes & Verification Status, 3. Technology Stack & Licensing, 4. Phase-by-Phase Execution Roadmap, Phase 0: Inspection, Feasibility, and Traceability (Current), Phase 10: Open-Source Readiness & Submission Package, Phase 1: Smallest Real End-to-End Flow, Phase 2: Input & Extraction Pipeline (+8 more)

### Community 13 - "trustlens"
Cohesion: 0.12
Nodes (15): context, dockerfile, interval, retries, start_period, test, timeout, services (+7 more)

### Community 14 - "2. Step-by-Step Server Setup Guide"
Cohesion: 0.14
Nodes (13): 1. Hosting Architecture Overview, 2. Step-by-Step Server Setup Guide, 3. Deployment Verification Checklist, 4. Current Status & Honest Reporting, Key Architectural Strengths:, Step 1: Provision Cloudways Application, Step 2: SSH Access & Code Deployment, Step 3: Python Virtual Environment & Dependencies (+5 more)

### Community 15 - "TrustLens AI - Integration Verification & Feasibility Analysis"
Cohesion: 0.18
Nodes (10): 1. Gemma 4 Integration Verification (Google DeepMind), 2. Cloudways Hosting Verification, 3. Graphify Codebase Knowledge Graph Verification, 4. Open-Source AI (DigitalOcean) Prize Verification, 5. Summary of Decision Classifications, Status: **VERIFIED**, Status: **VERIFIED (Architecture & Capabilities)**; **BLOCKED (Server SSH / API Access)**, Status: **VERIFIED (Endpoint and Specifications)**; **PENDING CREDENTIALS (Live API Key)** (+2 more)

### Community 16 - "2. Live Demo Steps (85 Seconds)"
Cohesion: 0.22
Nodes (8): 1. Quick Pitch (15 Seconds), 2. Live Demo Steps (85 Seconds), 3. Technology & Prize Integrations Walkthrough (20 Seconds), Step 1: Uploading a Suspicious Offer (20 Seconds), Step 2: Explainable Scoring & Verbatim Evidence (30 Seconds), Step 3: Markdown Export & Report Generation (15 Seconds), Step 4: Comparison with Legitimate Offer Letter (20 Seconds), TrustLens AI — 2-Minute Demonstration Script & Judge Walkthrough

### Community 17 - "TrustLens AI - Build & Milestone Status"
Cohesion: 0.40
Nodes (4): 1. Milestone Execution Summary, 2. Test Execution Record, 3. Active Blockers & Next Actions, TrustLens AI - Build & Milestone Status

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AnalysisResponse` connect `AnalysisResponse` to `RuleHit`, `routes.py`, `ExtractionMetadata`, `TrustLens AI 🔍🛡️`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `RuleHit` (e.g. with `ConflictingClaimsRule` and `DeterministicRule`) actually correct?**
  _`RuleHit` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_extractor.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1214574898785425 - nodes in this community are weakly interconnected._
- **Why does `8. REST API Documentation` connect `TrustLens AI 🔍🛡️` to `AnalysisResponse`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `SeverityLevel` (e.g. with `ConflictingClaimsRule` and `DeterministicRule`) actually correct?**
  _`SeverityLevel` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07386363636363637 - nodes in this community are weakly interconnected._
- **Are the 14 inferred relationships involving `DocumentExtractor` (e.g. with `DocumentAnalyzer` and `ExtractionMetadata`) actually correct?**
  _`DocumentExtractor` has 14 INFERRED edges - model-reasoned connections that need verification._