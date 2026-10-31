"""
Unit tests for evidence verification, provenance tagging, and quarantining.
"""

from app.core.evidence import EvidenceVerifier
from app.core.schemas import (
    GemmaFinding,
    FindingCategory,
    SeverityLevel,
    ExtractionMetadata,
    ProvenanceStatus,
)


def test_quote_verified_in_text():
    source = "All candidates are requested to pay a registration fee of Rs. 1000 before onboarding."
    meta = ExtractionMetadata(
        source_type="pasted_text",
        content_length=len(source),
        page_count=1,
        file_name="doc.txt",
        image_dimensions=None,
        provenance_mode=ProvenanceStatus.TEXT_MATCH_VERIFIED
    )

    finding = GemmaFinding(
        id="F1",
        category=FindingCategory.PAYMENT_REQUEST,
        evidence_quote="registration fee of Rs. 1000",
        explanation="Upfront fee requested",
        severity=SeverityLevel.HIGH,
        confidence=0.9
    )

    verified, quarantined = EvidenceVerifier.verify_findings([finding], source, meta)
    assert len(verified) == 1
    assert len(quarantined) == 0
    assert verified[0].is_verified_in_source is True
    assert verified[0].provenance == ProvenanceStatus.TEXT_MATCH_VERIFIED
    assert verified[0].source_offset is not None


def test_fabricated_quote_quarantined():
    source = "Standard employment contract for junior engineer."
    meta = ExtractionMetadata(
        source_type="pasted_text",
        content_length=len(source),
        page_count=1,
        file_name="doc.txt",
        image_dimensions=None,
        provenance_mode=ProvenanceStatus.TEXT_MATCH_VERIFIED
    )

    hallucinated_finding = GemmaFinding(
        id="F2",
        category=FindingCategory.PAYMENT_REQUEST,
        evidence_quote="candidate must wire $500 to Western Union",
        explanation="Fabricated fee not in document",
        severity=SeverityLevel.HIGH,
        confidence=0.8
    )

    verified, quarantined = EvidenceVerifier.verify_findings([hallucinated_finding], source, meta)
    assert len(verified) == 0
    assert len(quarantined) == 1
    assert quarantined[0].is_verified_in_source is False
    assert quarantined[0].provenance == ProvenanceStatus.UNVERIFIED_QUOTED_QUARANTINED
    assert "not found in extracted source text" in quarantined[0].quarantine_reason


def test_image_provenance_honesty():
    meta = ExtractionMetadata(
        source_type="image",
        content_length=5000,
        page_count=1,
        file_name="screenshot.png",
        image_dimensions={"width": 800, "height": 600},
        provenance_mode=ProvenanceStatus.MODEL_TRANSCRIBED
    )

    finding = GemmaFinding(
        id="F3",
        category=FindingCategory.URGENCY,
        evidence_quote="Urgent: reply within 24 hours",
        explanation="Urgent notice on screenshot",
        severity=SeverityLevel.MEDIUM,
        confidence=0.88
    )

    verified, quarantined = EvidenceVerifier.verify_findings([finding], "", meta)
    assert len(verified) == 1
    assert verified[0].provenance == ProvenanceStatus.MODEL_TRANSCRIBED
