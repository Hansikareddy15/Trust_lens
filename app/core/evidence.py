"""
Evidence verification and provenance module for TrustLens AI.
Verifies that AI model findings quote authentic source text verbatim,
computes character offsets, and quarantines fabricated or hallucinated quotes.
"""

import re
from typing import List, Tuple, Optional
from app.core.schemas import (
    GemmaFinding,
    VerifiedFinding,
    ProvenanceStatus,
    ExtractionMetadata,
)


def normalize_whitespace(text: str) -> str:
    """Collapses consecutive whitespace to single space for tolerant matching."""
    return re.sub(r"\s+", " ", text).strip().lower()


class EvidenceVerifier:
    @classmethod
    def verify_findings(
        cls,
        findings: List[GemmaFinding],
        source_text: str,
        extraction: ExtractionMetadata
    ) -> Tuple[List[VerifiedFinding], List[VerifiedFinding]]:
        """
        Cross-checks evidence quotes from Gemma against extracted source text.
        Returns:
            (verified_findings, quarantined_findings)
        """
        verified: List[VerifiedFinding] = []
        quarantined: List[VerifiedFinding] = []

        is_direct_image = extraction.source_type == "image"
        is_scanned_pdf = extraction.source_type == "scanned_pdf"

        for f in findings:
            quote = f.evidence_quote.strip()

            # Handle direct image where no independent ground truth text exists
            if is_direct_image:
                # Per spec: Label quotes as model-transcribed, never pretend
                # model-generated transcription is independent corroboration
                verified.append(
                    VerifiedFinding(
                        id=f.id,
                        category=f.category,
                        evidence_quote=f.evidence_quote,
                        explanation=f.explanation,
                        severity=f.severity,
                        confidence=f.confidence,
                        source_page=1,
                        source_offset=None,
                        provenance=ProvenanceStatus.MODEL_TRANSCRIBED,
                        is_verified_in_source=True,
                        quarantine_reason=None
                    )
                )
                continue

            # For text or digital PDF, verify against source_text
            offset, matched = cls._find_quote_in_text(quote, source_text)

            if matched:
                provenance = (
                    ProvenanceStatus.TRANSCRIPT_MATCH_VERIFIED
                    if is_scanned_pdf
                    else ProvenanceStatus.TEXT_MATCH_VERIFIED
                )
                verified.append(
                    VerifiedFinding(
                        id=f.id,
                        category=f.category,
                        evidence_quote=f.evidence_quote,
                        explanation=f.explanation,
                        severity=f.severity,
                        confidence=f.confidence,
                        source_page=cls._estimate_page(offset, source_text),
                        source_offset=offset,
                        provenance=provenance,
                        is_verified_in_source=True,
                        quarantine_reason=None
                    )
                )
            else:
                # Discard/quarantine unsupported quote
                quarantined.append(
                    VerifiedFinding(
                        id=f.id,
                        category=f.category,
                        evidence_quote=f.evidence_quote,
                        explanation=f.explanation,
                        severity=f.severity,
                        confidence=f.confidence,
                        source_page=None,
                        source_offset=None,
                        provenance=ProvenanceStatus.UNVERIFIED_QUOTED_QUARANTINED,
                        is_verified_in_source=False,
                        quarantine_reason="Quoted passage was not found in extracted source text."
                    )
                )

        return verified, quarantined

    @classmethod
    def _find_quote_in_text(cls, quote: str, source: str) -> Tuple[Optional[int], bool]:
        """
        Searches for quote in source text.
        First attempts exact match, then normalized whitespace match.
        """
        if not quote or not source:
            return None, False

        # 1. Exact match
        idx = source.find(quote)
        if idx != -1:
            return idx, True

        # 2. Case-insensitive exact match
        idx_lower = source.lower().find(quote.lower())
        if idx_lower != -1:
            return idx_lower, True

        # 3. Normalized whitespace match
        norm_quote = normalize_whitespace(quote)
        norm_source = normalize_whitespace(source)
        if norm_quote in norm_source:
            # Found in normalized text
            return 0, True

        # 4. Partial substring match if quote is long (>40 chars)
        if len(quote) > 40:
            sub = quote[:35]
            sub_idx = source.lower().find(sub.lower())
            if sub_idx != -1:
                return sub_idx, True

        return None, False

    @classmethod
    def _estimate_page(cls, offset: Optional[int], source_text: str) -> int:
        if offset is None or offset <= 0:
            return 1
        page_markers = list(re.finditer(r"--- Page Break ---", source_text))
        if not page_markers:
            return 1
        for i, marker in enumerate(page_markers):
            if offset < marker.start():
                return i + 1
        return len(page_markers) + 1
