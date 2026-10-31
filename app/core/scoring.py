"""
Transparent risk scoring engine for TrustLens AI.
Combines verified AI findings with deterministic rule hits.
Implements evidence deduplication, positive signal mitigation,
honest uncertainty tracking, and explicit sufficiency assessment.
"""

from typing import List, Tuple
from app.core.schemas import (
    VerifiedFinding,
    RuleHit,
    ScoreBreakdown,
    ScoreSignal,
    RiskLevel,
    SeverityLevel,
    ExtractionMetadata,
)


class ScoringEngine:
    # Heuristic Severity Weights
    SEVERITY_WEIGHTS = {
        SeverityLevel.HIGH: 35,
        SeverityLevel.MEDIUM: 20,
        SeverityLevel.LOW: 10,
    }

    # Scoring Thresholds
    LOW_THRESHOLD = 30     # 0 - 29 -> Low
    HIGH_THRESHOLD = 70    # 70 - 100 -> High (30 - 69 -> Medium)

    # Positive Mitigation
    POINTS_PER_POSITIVE_SIGNAL = 5
    MAX_POSITIVE_MITIGATION = 15

    @classmethod
    def calculate_score(
        cls,
        verified_findings: List[VerifiedFinding],
        rule_hits: List[RuleHit],
        positive_signals: List[str],
        extraction: ExtractionMetadata
    ) -> ScoreBreakdown:
        signals: List[ScoreSignal] = []
        deduplicated_count = 0

        # Check sufficiency: if input is very sparse or extraction indicates minimal content
        is_sparse = (
            extraction.content_length < 60
            and extraction.source_type in ("pasted_text", "digital_pdf")
        )

        # Track categories already scored to prevent double-counting across AI and deterministic rules
        category_contributions = {}

        # 1. Process Deterministic Rule Hits (Highest objective precedence)
        for rule in rule_hits:
            cat_key = rule.category.value
            weight = rule.weight

            if cat_key in category_contributions:
                # Deduplication: already covered by another hit in this category
                deduplicated_count += 1
                if weight > category_contributions[cat_key]:
                    # Upgrade to higher weight
                    diff = weight - category_contributions[cat_key]
                    category_contributions[cat_key] = weight
                    signals.append(
                        ScoreSignal(
                            name=rule.title,
                            category=rule.category.value,
                            points=diff,
                            source="rule_hit",
                            description=f"Rule hit: {rule.explanation} (Incremental +{diff} pts)"
                        )
                    )
            else:
                category_contributions[cat_key] = weight
                signals.append(
                    ScoreSignal(
                        name=rule.title,
                        category=rule.category.value,
                        points=weight,
                        source="rule_hit",
                        description=f"Deterministic rule matched: {rule.explanation}"
                    )
                )

        # 2. Process Verified AI Findings
        for finding in verified_findings:
            # Skip findings that were quarantined
            if not finding.is_verified_in_source:
                continue

            cat_key = finding.category.value
            weight = cls.SEVERITY_WEIGHTS.get(finding.severity, 10)

            # Check if this category was already scored by rules or previous findings
            if cat_key in category_contributions:
                deduplicated_count += 1
                # Deduplicate: do not double-penalize the same category
                continue
            else:
                category_contributions[cat_key] = weight
                signals.append(
                    ScoreSignal(
                        name=f"AI Finding: {finding.id} ({finding.category.value})",
                        category=finding.category.value,
                        points=weight,
                        source="ai_finding",
                        description=f"{finding.explanation} [Quote: '{finding.evidence_quote[:60]}...']"
                    )
                )

        # Sum raw points from all signals
        raw_score = sum(s.points for s in signals)

        # 3. Apply Positive Signals Mitigation
        positive_count = len(positive_signals)
        mitigation_points = min(positive_count * cls.POINTS_PER_POSITIVE_SIGNAL, cls.MAX_POSITIVE_MITIGATION)

        # High severity safety guard: if there are High-severity rules/findings,
        # positive signals cannot drop risk below Medium
        has_high_severity = any(
            r.severity == SeverityLevel.HIGH for r in rule_hits
        ) or any(
            f.severity == SeverityLevel.HIGH and f.is_verified_in_source for f in verified_findings
        )

        final_score = max(0, raw_score - mitigation_points)
        final_score = min(100, final_score)

        if has_high_severity and final_score < cls.LOW_THRESHOLD:
            final_score = cls.LOW_THRESHOLD

        # 4. Determine Risk Level & Evidence Sufficiency
        if is_sparse and not has_high_severity and raw_score == 0:
            risk_level = RiskLevel.INSUFFICIENT_INFORMATION
            sufficiency = "Sparse"
            notes = (
                "Input text was too brief or sparse to evaluate safely. "
                "No planted warning signs were detected, but insufficient content was provided to perform a reliable assessment."
            )
        elif final_score >= cls.HIGH_THRESHOLD:
            risk_level = RiskLevel.HIGH
            sufficiency = "Sufficient"
            notes = (
                "Multiple high-severity warning signs or critical fee solicitations were identified. "
                "Strong indication of deceptive or non-standard practices."
            )
        elif final_score >= cls.LOW_THRESHOLD:
            risk_level = RiskLevel.MEDIUM
            sufficiency = "Sufficient" if extraction.content_length > 150 else "Moderate"
            notes = (
                "Moderate warning signs or inconsistencies were identified. "
                "Exercise caution and complete recommended verification steps before committing."
            )
        else:
            risk_level = RiskLevel.LOW
            sufficiency = "Sufficient" if extraction.content_length > 150 else "Moderate"
            notes = (
                "No critical warning indicators were triggered in the provided text. "
                "Notice: This is a preliminary assessment and does NOT constitute proof of authenticity or legitimacy."
            )

        return ScoreBreakdown(
            heuristic_risk_score=final_score,
            risk_level=risk_level,
            evidence_sufficiency=sufficiency,
            signals=signals,
            positive_mitigations_applied=mitigation_points,
            deduplicated_signals_count=deduplicated_count,
            scoring_notes=notes
        )


scoring_engine = ScoringEngine()
