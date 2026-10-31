"""
Unit tests for scoring engine, deduplication, and risk classification.
"""

from app.core.scoring import scoring_engine
from app.core.schemas import (
    VerifiedFinding,
    RuleHit,
    FindingCategory,
    SeverityLevel,
    ProvenanceStatus,
    ExtractionMetadata,
    RiskLevel,
)


def make_metadata(length: int = 500, source_type: str = "pasted_text") -> ExtractionMetadata:
    return ExtractionMetadata(
        source_type=source_type,
        content_length=length,
        page_count=1,
        file_name="sample.txt",
        image_dimensions=None,
        provenance_mode=ProvenanceStatus.TEXT_MATCH_VERIFIED
    )


def test_high_risk_scam_scoring():
    meta = make_metadata(400)
    rule_hits = [
        RuleHit(
            rule_id="RULE_PAYMENT_REQUEST",
            title="Upfront Fee",
            category=FindingCategory.PAYMENT_REQUEST,
            severity=SeverityLevel.HIGH,
            weight=35,
            matched_evidence="pay Rs 3000 fee",
            explanation="Fees not allowed",
            limitations="none",
            source_offset=10
        ),
        RuleHit(
            rule_id="RULE_LOOKALIKE_DOMAIN",
            title="Lookalike Domain",
            category=FindingCategory.DOMAIN,
            severity=SeverityLevel.HIGH,
            weight=30,
            matched_evidence="google-portal.com",
            explanation="Domain mismatch",
            limitations="none",
            source_offset=50
        ),
        RuleHit(
            rule_id="RULE_URGENCY_PRESSURE",
            title="Urgency Pressure",
            category=FindingCategory.URGENCY,
            severity=SeverityLevel.MEDIUM,
            weight=20,
            matched_evidence="within 24 hours",
            explanation="Time pressure",
            limitations="none",
            source_offset=100
        )
    ]

    score = scoring_engine.calculate_score(
        verified_findings=[],
        rule_hits=rule_hits,
        positive_signals=[],
        extraction=meta
    )

    assert score.risk_level == RiskLevel.HIGH
    assert score.heuristic_risk_score >= 70
    assert len(score.signals) == 3


def test_low_risk_legitimate_scoring():
    meta = make_metadata(800)
    score = scoring_engine.calculate_score(
        verified_findings=[],
        rule_hits=[],
        positive_signals=["Corporate headquarters listed", "Official careers portal link", "No fees requested"],
        extraction=meta
    )
    assert score.risk_level == RiskLevel.LOW
    assert score.heuristic_risk_score == 0
    assert score.evidence_sufficiency == "Sufficient"


def test_sparse_input_insufficient_information():
    meta = make_metadata(length=30)  # Sparse text
    score = scoring_engine.calculate_score(
        verified_findings=[],
        rule_hits=[],
        positive_signals=[],
        extraction=meta
    )
    assert score.risk_level == RiskLevel.INSUFFICIENT_INFORMATION
    assert score.evidence_sufficiency == "Sparse"


def test_deduplication_between_ai_and_rules():
    meta = make_metadata(500)
    rule_hit = RuleHit(
        rule_id="RULE_PAYMENT_REQUEST",
        title="Payment Request Rule",
        category=FindingCategory.PAYMENT_REQUEST,
        severity=SeverityLevel.HIGH,
        weight=35,
        matched_evidence="pay 2500 fee",
        explanation="Upfront fee",
        limitations="none",
        source_offset=20
    )

    # AI also found the same payment request category
    ai_finding = VerifiedFinding(
        id="F1",
        category=FindingCategory.PAYMENT_REQUEST,
        evidence_quote="pay 2500 fee",
        explanation="Candidate asked to pay fee",
        severity=SeverityLevel.HIGH,
        confidence=0.95,
        source_page=1,
        source_offset=20,
        provenance=ProvenanceStatus.TEXT_MATCH_VERIFIED,
        is_verified_in_source=True
    )

    score = scoring_engine.calculate_score(
        verified_findings=[ai_finding],
        rule_hits=[rule_hit],
        positive_signals=[],
        extraction=meta
    )

    # Payment request must be deduplicated
    assert score.deduplicated_signals_count >= 1
    # Only 35 points should be counted, NOT 35 + 35 = 70
    assert score.heuristic_risk_score == 35
