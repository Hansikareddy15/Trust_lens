# Graph Report - Hactober  (2026-10-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 237 nodes · 599 edges · 12 communities (8 shown, 4 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- test_extractor.py
- RuleHit
- routes.py
- gemma_client.py
- ExtractionMetadata
- schemas.py
- AnalysisResponse
- app.js
- typing
- test_api.py

## God Nodes (most connected - your core abstractions)
1. `RuleHit` - 27 edges
2. `SeverityLevel` - 24 edges
3. `ExtractionMetadata` - 22 edges
4. `FindingCategory` - 21 edges
5. `ProvenanceStatus` - 19 edges
6. `DocumentExtractor` - 18 edges
7. `EvidenceVerifier` - 14 edges
8. `AnalysisResponse` - 14 edges
9. `GemmaAnalysisResult` - 13 edges
10. `DeterministicRule` - 12 edges

## Surprising Connections (you probably didn't know these)
- `test_fabricated_quote_quarantined()` --uses--> `FindingCategory`  [INFERRED]
  tests/test_evidence.py → app/core/schemas.py
- `test_image_provenance_honesty()` --uses--> `FindingCategory`  [INFERRED]
  tests/test_evidence.py → app/core/schemas.py
- `test_quote_verified_in_text()` --uses--> `FindingCategory`  [INFERRED]
  tests/test_evidence.py → app/core/schemas.py
- `test_deduplication_between_ai_and_rules()` --uses--> `FindingCategory`  [INFERRED]
  tests/test_scoring.py → app/core/schemas.py
- `test_high_risk_scam_scoring()` --uses--> `FindingCategory`  [INFERRED]
  tests/test_scoring.py → app/core/schemas.py

## Import Cycles
- None detected.

## Communities (12 total, 4 thin omitted)

### Community 0 - "test_extractor.py"
Cohesion: 0.11
Nodes (16): CorruptedFileError, DocumentExtractor, ExtractionError, FileOversizedError, UnsupportedFileTypeError, generate_fake_internship_pdf(), generate_legitimate_offer_pdf(), create_minimal_pdf_bytes() (+8 more)

### Community 1 - "RuleHit"
Cohesion: 0.16
Nodes (20): DeterministicRule, FreeEmailSenderRule, LookalikeDomainRule, MessagingAppMoveRule, PaymentRequestRule, RulesEngine, UnrealisticOfferRule, UrgencyPressureRule (+12 more)

### Community 2 - "routes.py"
Cohesion: 0.07
Nodes (6): get_demo_samples(), health_check(), Settings, AnalyzeTextRequest, rate_limit_middleware(), serve_index()

### Community 3 - "gemma_client.py"
Cohesion: 0.11
Nodes (9): GemmaApiKeyMissingError, GemmaClient, GemmaClientError, GemmaSchemaValidationError, GemmaAnalysisResult, test_reject_confidence_out_of_bounds(), test_reject_missing_required_fields(), test_reject_unexpected_extra_fields() (+1 more)

### Community 4 - "ExtractionMetadata"
Cohesion: 0.21
Nodes (8): EvidenceVerifier, normalize_whitespace(), ExtractionMetadata, GemmaFinding, ProvenanceStatus, test_fabricated_quote_quarantined(), test_image_provenance_honesty(), test_quote_verified_in_text()

### Community 5 - "schemas.py"
Cohesion: 0.22
Nodes (12): DocumentType, HealthResponse, RiskLevel, ScoreBreakdown, ScoreSignal, VerifiedFinding, ScoringEngine, make_metadata() (+4 more)

### Community 6 - "AnalysisResponse"
Cohesion: 0.16
Nodes (6): analyze_document(), analyze_text_json(), export_markdown(), DocumentAnalyzer, ReportBuilder, AnalysisResponse

### Community 9 - "test_api.py"
Cohesion: 0.36
Nodes (4): test_analyze_text_json_endpoint(), test_export_markdown_endpoint(), test_health_endpoint(), test_samples_endpoint()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RuleHit` connect `RuleHit` to `schemas.py`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `RuleHit` (e.g. with `DeterministicRule` and `FreeEmailSenderRule`) actually correct?**
  _`RuleHit` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_extractor.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10897435897435898 - nodes in this community are weakly interconnected._
- **Why does `AnalysisResponse` connect `AnalysisResponse` to `routes.py`, `ExtractionMetadata`, `schemas.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `SeverityLevel` (e.g. with `DeterministicRule` and `FreeEmailSenderRule`) actually correct?**
  _`SeverityLevel` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Should `routes.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07196969696969698 - nodes in this community are weakly interconnected._
- **Why does `ExtractionMetadata` connect `ExtractionMetadata` to `test_extractor.py`, `schemas.py`, `AnalysisResponse`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._