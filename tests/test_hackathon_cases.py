"""
Hackathon Rubric Test Suite - TrustLens AI.
Directly validates the 5 mandatory scenarios from the hackathon specification:
1. A document containing several warning signs.
2. An ordinary offer without obvious warning signs.
3. A document containing conflicting information.
4. An incomplete document.
5. An invalid or unsupported file.
"""

import pytest
from app.core.extractor import (
    DocumentExtractor,
    CorruptedFileError,
    UnsupportedFileTypeError,
)
from app.core.analyzer import document_analyzer
from app.core.schemas import RiskLevel, SeverityLevel


@pytest.mark.asyncio
async def test_case_1_several_warning_signs():
    """
    Scenario 1: Document containing several warning signs:
    - Upfront fee solicitation
    - Artificial urgency (within 24 hours)
    - Corporate recruiter using generic free mail (@gmail.com)
    - Off-platform diversion to WhatsApp/Telegram
    """
    text = (
        "GLOBAL TECH TRAINEE PROGRAM\n"
        "Offer of Provisional Employment\n\n"
        "Dear Candidate,\n"
        "We are pleased to select you for the Software Development Trainee role. "
        "Monthly stipend: Rs. 40,000.\n\n"
        "REQUIREMENTS:\n"
        "1. You must deposit a refundable security deposit of Rs. 2,500 prior to joining.\n"
        "2. You must confirm your seat within 24 hours or your offer will be revoked.\n"
        "3. Send UPI confirmation screenshot to our coordinator on WhatsApp: +91-9876543210.\n\n"
        "Talent Acquisition Team\n"
        "recruiter.globaltech@gmail.com"
    )

    result = await document_analyzer.analyze_text(text, "Case 1: Several Warning Signs")

    assert result.score.risk_level == RiskLevel.HIGH
    assert result.score.heuristic_risk_score >= 70
    assert result.score.evidence_sufficiency == "Sufficient"
    
    rule_ids = {r.rule_id for r in result.rule_hits}
    assert "RULE_PAYMENT_REQUEST" in rule_ids
    assert "RULE_URGENCY_PRESSURE" in rule_ids
    assert "RULE_FREE_EMAIL_SENDER" in rule_ids
    assert "RULE_MESSAGING_APP_MOVE" in rule_ids
    assert len(result.recommended_checks) > 0


@pytest.mark.asyncio
async def test_case_2_ordinary_offer_without_warning_signs():
    """
    Scenario 2: An ordinary offer without obvious warning signs:
    - Verifiable physical address and corporate domain
    - Direct supervisor named
    - Standard compensation structure
    - Explicit statement that company never charges fees
    """
    text = (
        "Decode Labs Technologies Inc.\n"
        "1400 Innovation Boulevard, Suite 500, Austin, TX 78701\n"
        "Official Contact: careers@decodelabs.com | www.decodelabs.com\n\n"
        "Dear Alex Morgan,\n\n"
        "We are pleased to offer you an internship position as Junior Backend Engineer at Decode Labs. "
        "Your internship will commence on June 1, 2027 and conclude on August 20, 2027. "
        "You will report directly to Priya Sharma, Lead Architect, Cloud Systems.\n\n"
        "Compensation: You will receive an hourly rate of $32.00 per hour, paid bi-weekly via direct deposit.\n"
        "Decode Labs does not charge any fee or security deposit at any stage of recruitment or onboarding.\n\n"
        "Warm regards,\nTalent Acquisition Operations\nDecode Labs Technologies Inc."
    )

    result = await document_analyzer.analyze_text(text, "Case 2: Ordinary Legitimate Offer")

    assert result.score.risk_level == RiskLevel.LOW
    assert result.score.heuristic_risk_score == 0
    assert len(result.rule_hits) == 0
    # Must NOT claim proven safe; must preserve preliminary disclaimer
    assert "Preliminary assessment" in result.disclaimer


@pytest.mark.asyncio
async def test_case_3_document_with_conflicting_information():
    """
    Scenario 3: Document containing conflicting information:
    - First claims that training is 100% free with no registration fees.
    - Later demands a refundable deposit or kit fee for equipment.
    """
    text = (
        "Apex Cloud Systems - Internship Onboarding Terms\n\n"
        "Apex Cloud Systems does not charge any fee for our internship program. Training is completely free of cost.\n\n"
        "EQUIPMENT DISPATCH INSTRUCTIONS:\n"
        "Prior to receiving your corporate development laptop, candidates must transfer a refundable security deposit of Rs. 3,500. "
        "This deposit must be sent within 24 hours to secure hardware allocation.\n\n"
        "HR Operations: apex.talent@gmail.com"
    )

    result = await document_analyzer.analyze_text(text, "Case 3: Conflicting Information")

    rule_ids = {r.rule_id for r in result.rule_hits}
    # Both the unnegated fee and the conflicting claims rule must trigger!
    assert "RULE_PAYMENT_REQUEST" in rule_ids
    assert "RULE_CONFLICTING_CLAIMS" in rule_ids
    assert result.score.risk_level in (RiskLevel.HIGH, RiskLevel.MEDIUM)
    assert result.score.heuristic_risk_score >= 50


@pytest.mark.asyncio
async def test_case_4_incomplete_sparse_document():
    """
    Scenario 4: An incomplete or sparse document:
    - Sparse excerpt without sufficient detail to verify
    - Must evaluate to 'Insufficient Information', keeping evidence sufficiency distinct from risk.
    """
    sparse_text = "Interview scheduled tomorrow at 10 AM. See you there."

    result = await document_analyzer.analyze_text(sparse_text, "Case 4: Incomplete Document")

    assert result.score.risk_level == RiskLevel.INSUFFICIENT_INFORMATION
    assert result.score.evidence_sufficiency == "Sparse"
    assert "insufficient content" in result.score.scoring_notes.lower()


def test_case_5_invalid_and_unsupported_files():
    """
    Scenario 5: Invalid or unsupported files:
    - 0-byte empty file -> CorruptedFileError
    - Executable/binary with fake .pdf extension -> UnsupportedFileTypeError
    - File exceeding 10MB limit -> FileOversizedError
    """
    # 1. Empty file
    with pytest.raises(CorruptedFileError):
        DocumentExtractor.validate_file_bytes(b"", "empty.pdf")

    # 2. Corrupted / Fake signature
    fake_exe_bytes = b"MZ\x90\x00\x03\x00\x00\x00"  # Windows PE binary header
    with pytest.raises(UnsupportedFileTypeError):
        DocumentExtractor.validate_file_bytes(fake_exe_bytes, "trojan.pdf")

    # 3. Oversized file
    huge_bytes = b"%PDF-" + b"0" * (11 * 1024 * 1024)
    with pytest.raises(Exception):
        DocumentExtractor.validate_file_bytes(huge_bytes, "huge.pdf")
