"""
Unit tests for Pydantic schema validation of Gemma model outputs.
"""

import pytest
from pydantic import ValidationError
from app.core.schemas import GemmaAnalysisResult, DocumentType, FindingCategory, SeverityLevel


def test_valid_schema():
    data = {
        "document_type": "internship_offer",
        "summary": "Offer for python developer with upfront fee request.",
        "findings": [
            {
                "id": "F1",
                "category": "payment_request",
                "evidence_quote": "pay Rs. 2000 registration fee",
                "explanation": "Solicits money before joining",
                "severity": "high",
                "confidence": 0.95
            }
        ],
        "unverified_claims": ["Company claims 10,000 employees globally"],
        "positive_signals": ["Clear job role description"],
        "recommended_checks": ["Check official company website directly"]
    }
    result = GemmaAnalysisResult.model_validate(data)
    assert result.document_type == DocumentType.INTERNSHIP_OFFER
    assert len(result.findings) == 1
    assert result.findings[0].severity == SeverityLevel.HIGH


def test_reject_unexpected_extra_fields():
    data = {
        "document_type": "internship_offer",
        "summary": "Valid summary description.",
        "findings": [],
        "unverified_claims": [],
        "positive_signals": [],
        "recommended_checks": [],
        "illegal_extra_field": "This should cause validation failure"
    }
    with pytest.raises(ValidationError):
        GemmaAnalysisResult.model_validate(data)


def test_reject_confidence_out_of_bounds():
    data = {
        "document_type": "phishing_message",
        "summary": "Suspicious SMS message.",
        "findings": [
            {
                "id": "F1",
                "category": "urgency",
                "evidence_quote": "within 2 hours",
                "explanation": "Artificial urgency",
                "severity": "medium",
                "confidence": 1.5  # Invalid: must be <= 1.0
            }
        ],
        "unverified_claims": [],
        "positive_signals": [],
        "recommended_checks": []
    }
    with pytest.raises(ValidationError):
        GemmaAnalysisResult.model_validate(data)


def test_reject_missing_required_fields():
    data = {
        "document_type": "job_ad"
        # missing summary, findings, etc.
    }
    with pytest.raises(ValidationError):
        GemmaAnalysisResult.model_validate(data)
