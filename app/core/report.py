"""
Report generation module for TrustLens AI.
Renders exportable Markdown and styled printable HTML reports from an AnalysisResponse.
"""

from typing import Dict, Any
from app.core.schemas import AnalysisResponse


class ReportBuilder:
    @classmethod
    def generate_markdown(cls, analysis: AnalysisResponse) -> str:
        """
        Builds a comprehensive, transparent Markdown report.
        """
        lines = [
            f"# TrustLens AI - Document Risk Assessment Report",
            f"",
            f"**Report ID**: `{analysis.analysis_id}`  ",
            f"**Generated At**: {analysis.created_at}  ",
            f"**Model Used**: `{analysis.model_used}`  ",
            f"**Document Type**: `{analysis.document_type.value}`  ",
            f"**Source**: {analysis.extraction.file_name or 'Uploaded File'} ({analysis.extraction.source_type}, {analysis.extraction.content_length} chars)  ",
            f"",
            f"> [!IMPORTANT]",
            f"> **Disclaimer**: {analysis.disclaimer}",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary & Risk Classification",
            f"",
            f"- **Preliminary Risk Level**: **{analysis.score.risk_level.value.upper()}**",
            f"- **Heuristic Risk Score**: **{analysis.score.heuristic_risk_score} / 100**",
            f"- **Evidence Sufficiency**: **{analysis.score.evidence_sufficiency}**",
            f"",
            f"### Document Summary",
            f"{analysis.summary}",
            f"",
            f"### Scoring Assessment",
            f"{analysis.score.scoring_notes}",
            f"",
            f"---",
            f"",
            f"## 2. Contributing Risk Signals ({len(analysis.score.signals)})",
            f"",
            f"| Signal Name | Category | Points | Source | Description |",
            f"| :--- | :--- | :---: | :--- | :--- |",
        ]

        if analysis.score.signals:
            for s in analysis.score.signals:
                lines.append(f"| {s.name} | `{s.category}` | +{s.points} | `{s.source}` | {s.description} |")
        else:
            lines.append(f"| None Detected | - | 0 | - | No risk signals were triggered. |")

        if analysis.score.positive_mitigations_applied > 0:
            lines.append(f"")
            lines.append(f"*Note: Risk score was adjusted by -{analysis.score.positive_mitigations_applied} points due to verified positive signals.*")

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Verified Findings Backed by Evidence ({len(analysis.findings)})",
            f"",
        ])

        if analysis.findings:
            for idx, f in enumerate(analysis.findings, 1):
                lines.extend([
                    f"### Finding {idx}: {f.category.value.replace('_', ' ').title()} (Severity: {f.severity.value.upper()})",
                    f"- **Finding ID**: `{f.id}`",
                    f"- **Confidence**: `{f.confidence:.2f}`",
                    f"- **Provenance**: `{f.provenance.value}`",
                    f"- **Exact Quote**: > \"*{f.evidence_quote}*\"",
                    f"- **Explanation**: {f.explanation}",
                    f"",
                ])
        else:
            lines.append("No specific warning signs identified by the AI analysis model.\n")

        # Quarantined findings section
        if analysis.quarantined_findings:
            lines.extend([
                f"### ⚠️ Quarantined / Unsupported Findings ({len(analysis.quarantined_findings)})",
                f"> [!WARNING]",
                f"> The following model claims were excluded from the risk score because their quoted text could not be verified in the source document.",
                f"",
            ])
            for qf in analysis.quarantined_findings:
                lines.append(f"- **{qf.id}**: {qf.explanation} (Quote: \"{qf.evidence_quote}\" - *{qf.quarantine_reason}*)")
            lines.append("")

        # Deterministic Rule Hits
        lines.extend([
            f"---",
            f"",
            f"## 4. Independent Deterministic Rule Hits ({len(analysis.rule_hits)})",
            f"",
        ])

        if analysis.rule_hits:
            for rh in analysis.rule_hits:
                lines.extend([
                    f"- **{rh.title}** (`{rh.rule_id}`):",
                    f"  - **Evidence Matched**: `{rh.matched_evidence}`",
                    f"  - **Weight**: +{rh.weight} pts (Severity: {rh.severity.value})",
                    f"  - **Explanation**: {rh.explanation}",
                    f"  - **Rule Limitations**: {rh.limitations}",
                    f"",
                ])
        else:
            lines.append("No deterministic rule triggers detected.\n")

        # Positive Signals and Unverified Claims
        lines.extend([
            f"---",
            f"",
            f"## 5. Balance: Positive Signals & Unverified Claims",
            f"",
            f"### Positive Signals Consistent with Legitimate Communications",
        ])

        if analysis.positive_signals:
            for ps in analysis.positive_signals:
                lines.append(f"- ✅ {ps}")
        else:
            lines.append("- No explicit positive signals observed.")

        lines.extend([
            f"",
            f"### Unverified Claims (Requires External Confirmation)",
        ])

        if analysis.unverified_claims:
            for uc in analysis.unverified_claims:
                lines.append(f"- ❓ {uc}")
        else:
            lines.append("- None identified.")

        # Recommended Actionable Steps
        lines.extend([
            f"",
            f"---",
            f"",
            f"## 6. Recommended Verification Next Steps",
            f"",
        ])

        if analysis.recommended_checks:
            for step in analysis.recommended_checks:
                lines.append(f"1. **Action**: {step}")
        else:
            lines.append("1. Verify the entity's official domain directly in your browser.")
            lines.append("2. Never pay upfront fees or registration deposits for job or internship offers.")

        lines.extend([
            f"",
            f"---",
            f"*Generated by TrustLens AI — Open Source Fraud & Scam Decision Support.*",
        ])

        return "\n".join(lines)
