"""
Pydantic schemas and data models for TrustLens AI.
Strictly defines model input/output contracts, independent rules output,
risk scoring breakdown, and overall analysis responses.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class DocumentType(str, Enum):
    INTERNSHIP_OFFER = "internship_offer"
    JOB_AD = "job_ad"
    PHISHING_MESSAGE = "phishing_message"
    OTHER = "other"


class FindingCategory(str, Enum):
    PAYMENT_REQUEST = "payment_request"
    URGENCY = "urgency"
    SENDER_IDENTITY = "sender_identity"
    DOMAIN = "domain"
    VAGUE_DETAILS = "vague_details"
    GRAMMAR = "grammar"
    UNREALISTIC_CLAIMS = "unrealistic_claims"
    OTHER = "other"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProvenanceStatus(str, Enum):
    TEXT_MATCH_VERIFIED = "text-match-verified"
    TRANSCRIPT_MATCH_VERIFIED = "transcript-match-verified"
    MODEL_TRANSCRIBED = "model-transcribed"
    UNVERIFIED_QUOTED_QUARANTINED = "unverified-quoted-quarantined"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    INSUFFICIENT_INFORMATION = "Insufficient Information"


# -------------------------------------------------------------
# AI Output Schema (Raw from Gemma 4)
# -------------------------------------------------------------

class GemmaFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique finding identifier (e.g. F1, F2)")
    category: FindingCategory = Field(..., description="Warning signal category")
    evidence_quote: str = Field(..., min_length=1, description="Exact verbatim quote from source document")
    explanation: str = Field(..., min_length=3, description="Explanation of why this is a warning signal")
    severity: SeverityLevel = Field(..., description="Signal severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model self-assessed confidence between 0.0 and 1.0")
    source_page: Optional[int] = Field(None, ge=1, description="1-indexed page number if applicable")
    source_offset: Optional[int] = Field(None, ge=0, description="Character offset in extracted text")


class GemmaAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = Field(..., description="Classified type of document")
    summary: str = Field(..., min_length=5, description="Objective factual summary of document content")
    findings: List[GemmaFinding] = Field(default_factory=list, description="List of observed potential warning signs")
    unverified_claims: List[str] = Field(default_factory=list, description="Claims that cannot be confirmed from document alone")
    positive_signals: List[str] = Field(default_factory=list, description="Signs consistent with a legitimate offer or document")
    recommended_checks: List[str] = Field(default_factory=list, description="Actionable verification steps for user")


# -------------------------------------------------------------
# Verified Finding (AI Finding + Deterministic Provenance)
# -------------------------------------------------------------

class VerifiedFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    category: FindingCategory
    evidence_quote: str
    explanation: str
    severity: SeverityLevel
    confidence: float
    source_page: Optional[int] = None
    source_offset: Optional[int] = None
    provenance: ProvenanceStatus
    is_verified_in_source: bool
    quarantine_reason: Optional[str] = None


# -------------------------------------------------------------
# Rules Engine Models
# -------------------------------------------------------------

class RuleHit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    title: str
    category: FindingCategory
    severity: SeverityLevel
    weight: int = Field(..., ge=0, le=100)
    matched_evidence: str
    explanation: str
    limitations: str
    source_offset: Optional[int] = None


# -------------------------------------------------------------
# Scoring Breakdown
# -------------------------------------------------------------

class ScoreSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    category: str
    points: int
    source: str  # "ai_finding" or "rule_hit" or "mitigation"
    description: str


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    heuristic_risk_score: int = Field(..., ge=0, le=100, description="Heuristic score from 0 (very low risk) to 100 (extreme risk)")
    risk_level: RiskLevel
    evidence_sufficiency: str = Field(..., description="'Sufficient', 'Moderate', or 'Sparse'")
    signals: List[ScoreSignal] = Field(default_factory=list)
    positive_mitigations_applied: int = Field(default=0)
    deduplicated_signals_count: int = Field(default=0)
    scoring_notes: str


# -------------------------------------------------------------
# Extraction Provenance Metadata
# -------------------------------------------------------------

class ExtractionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: str  # "pasted_text", "digital_pdf", "scanned_pdf", "image"
    content_length: int
    page_count: Optional[int] = None
    file_name: Optional[str] = None
    image_dimensions: Optional[Dict[str, int]] = None
    provenance_mode: ProvenanceStatus


# -------------------------------------------------------------
# Full Application Analysis Response
# -------------------------------------------------------------

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    analysis_id: str
    document_type: DocumentType
    summary: str
    model_used: str
    extraction: ExtractionMetadata
    findings: List[VerifiedFinding]
    rule_hits: List[RuleHit]
    score: ScoreBreakdown
    unverified_claims: List[str]
    positive_signals: List[str]
    recommended_checks: List[str]
    quarantined_findings: List[VerifiedFinding]
    disclaimer: str = "Preliminary assessment, not proof of fraud or legal advice. Does not assert fraud against any entity."
    created_at: str


# -------------------------------------------------------------
# Request Models
# -------------------------------------------------------------

class AnalyzeTextRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, max_length=100000, description="Raw text of the document or message")
    source_label: Optional[str] = Field("Pasted Text", max_length=100)


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    model_configured: str
    has_api_key: bool
    limits: Dict[str, Any]
