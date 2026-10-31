"""
Central analysis orchestrator for TrustLens AI.
Coordinates extraction, Gemma 4 analysis, evidence verification,
deterministic rules evaluation, and transparent risk scoring.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.core.schemas import (
    AnalysisResponse,
    DocumentType,
    GemmaAnalysisResult,
    ExtractionMetadata,
    ProvenanceStatus,
)
from app.core.extractor import DocumentExtractor
from app.core.evidence import EvidenceVerifier
from app.core.gemma_client import gemma_client, GemmaApiKeyMissingError
from app.core.rules import rules_engine
from app.core.scoring import scoring_engine


class DocumentAnalyzer:
    @classmethod
    async def analyze_text(cls, text: str, label: str = "Pasted Text") -> AnalysisResponse:
        """
        Executes the full TrustLens AI verification pipeline on raw text.
        """
        extracted_text, img_bytes, img_mime, metadata = DocumentExtractor.extract_from_text(text, label)
        return await cls._run_pipeline(extracted_text, img_bytes, img_mime, metadata)

    @classmethod
    async def analyze_file(cls, file_bytes: bytes, filename: str) -> AnalysisResponse:
        """
        Executes the full TrustLens AI verification pipeline on an uploaded file (PDF or image).
        """
        mime_type = DocumentExtractor.validate_file_bytes(file_bytes, filename)

        if mime_type == "application/pdf":
            extracted_text, img_bytes, img_mime, metadata = DocumentExtractor.extract_from_pdf(file_bytes, filename)
        elif mime_type.startswith("image/"):
            extracted_text, img_bytes, img_mime, metadata = DocumentExtractor.extract_from_image(file_bytes, filename)
        elif mime_type == "text/plain":
            extracted_text, img_bytes, img_mime, metadata = DocumentExtractor.extract_from_text(
                file_bytes.decode("utf-8", errors="replace"), filename
            )
        else:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

        return await cls._run_pipeline(extracted_text, img_bytes, img_mime, metadata)

    @classmethod
    async def _run_pipeline(
        cls,
        extracted_text: str,
        image_bytes: Optional[bytes],
        image_mime: Optional[str],
        metadata: ExtractionMetadata
    ) -> AnalysisResponse:
        analysis_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        active_model = settings.GEMMA_MODEL_ID

        # 1. AI Analysis Phase (Gemma 4)
        ai_result: Optional[GemmaAnalysisResult] = None
        ai_error_note: Optional[str] = None

        try:
            ai_result = await gemma_client.analyze(
                extracted_text=extracted_text,
                image_bytes=image_bytes,
                image_mime_type=image_mime
            )
        except GemmaApiKeyMissingError:
            # Documented, honest fallback: Do not fabricate fake AI findings
            active_model = f"{settings.GEMMA_MODEL_ID} (Key Missing - Rules Engine Only)"
            ai_error_note = "Gemma 4 API key is not configured. Analysis conducted via deterministic rules engine."
            ai_result = GemmaAnalysisResult(
                document_type=DocumentType.OTHER,
                summary=ai_error_note,
                findings=[],
                unverified_claims=["Document claims could not be verified by Gemma 4 because GEMMA_API_KEY is not configured."],
                positive_signals=[],
                recommended_checks=["Verify sender email domain against official company registry.", "Never pay upfront fees."]
            )

        # 2. Evidence Verification & Quarantining Phase
        verified_findings, quarantined = EvidenceVerifier.verify_findings(
            findings=ai_result.findings,
            source_text=extracted_text,
            extraction=metadata
        )

        # 3. Deterministic Rules Engine Phase
        rule_hits = rules_engine.run(extracted_text)

        # 4. Transparent Scoring Phase
        score = scoring_engine.calculate_score(
            verified_findings=verified_findings,
            rule_hits=rule_hits,
            positive_signals=ai_result.positive_signals,
            extraction=metadata
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            document_type=ai_result.document_type,
            summary=ai_result.summary,
            model_used=active_model,
            extraction=metadata,
            findings=verified_findings,
            rule_hits=rule_hits,
            score=score,
            unverified_claims=ai_result.unverified_claims,
            positive_signals=ai_result.positive_signals,
            recommended_checks=ai_result.recommended_checks,
            quarantined_findings=quarantined,
            disclaimer="Preliminary assessment, not proof of fraud or legal advice. Does not assert fraud against any entity.",
            created_at=created_at
        )


document_analyzer = DocumentAnalyzer()
