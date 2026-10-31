"""
Deterministic rules engine for TrustLens AI.
Runs independently on extracted source text to identify established fraud/phishing indicators.
Implements context-sensitive checks (e.g. negation handling so 'no registration fee' does not trigger).
"""

import re
from typing import List, Optional
from app.core.schemas import RuleHit, FindingCategory, SeverityLevel


# Common free email providers often misused for corporate impersonation
FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "aol.com", "protonmail.com", "zoho.com"
}

# Known high-profile brand keywords for lookalike detection
TARGET_BRANDS = ["google", "microsoft", "amazon", "tcs", "infosys", "wipro", "apple", "meta", "netflix", "deloitte"]


class DeterministicRule:
    rule_id: str
    title: str
    category: FindingCategory
    severity: SeverityLevel
    weight: int
    explanation: str
    limitations: str

    def evaluate(self, text: str) -> Optional[RuleHit]:
        raise NotImplementedError


class PaymentRequestRule(DeterministicRule):
    rule_id = "RULE_PAYMENT_REQUEST"
    title = "Upfront Fee or Deposit Solicitation"
    category = FindingCategory.PAYMENT_REQUEST
    severity = SeverityLevel.HIGH
    weight = 35
    explanation = (
        "Legitimate employers and internship providers almost never require candidates to pay "
        "registration fees, training fees, kit costs, or refundable deposits."
    )
    limitations = (
        "May flag legitimate paid training workshops or educational bootcamps if presented as job offers."
    )

    # Patterns indicating fees
    FEE_PATTERNS = [
        r"(?:registration|training|kit|onboarding|security|verification|processing)\s+(?:fee|charges?|deposit|cost|amount)",
        r"(?:refundable\s+deposit|pay\s+(?:rs\.?|inr|\$|usd|eur)?\s*\d+)",
        r"(?:deposit|transfer|send)\s+(?:rs\.?|inr|\$|usd)?\s*\d+\s+(?:before|to\s+confirm|for\s+laptop)",
        r"bank\s+transfer\s+of\s+(?:rs\.?|inr|\$)?\s*\d+"
    ]

    # Negations that indicate fee is NOT charged
    NEGATION_PATTERNS = [
        r"no\s+(?:registration|training|kit|security|hidden)?\s*(?:fee|charges?|deposit|cost)",
        r"(?:free\s+of\s+cost|zero\s+cost|without\s+any\s+(?:fee|charge|deposit))",
        r"does\s+not\s+(?:charge|require)\s+any\s+fee",
        r"never\s+ask\s+(?:for\s+money|for\s+any\s+fee)"
    ]

    def evaluate(self, text: str) -> Optional[RuleHit]:
        # Split text into sentences for context-sensitive local evaluation
        sentences = re.split(r"(?<=[.!?\n])\s+", text)

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Check if this sentence contains a fee pattern
            for pat in self.FEE_PATTERNS:
                match = re.search(pat, sentence, re.IGNORECASE)
                if match:
                    # Check if THIS specific sentence contains a negation
                    is_negated = any(re.search(neg, sentence_lower) for neg in self.NEGATION_PATTERNS)
                    if not is_negated:
                        # Real unnegated fee found in this sentence
                        global_offset = text.find(sentence) + match.start() if sentence in text else match.start()
                        return RuleHit(
                            rule_id=self.rule_id,
                            title=self.title,
                            category=self.category,
                            severity=self.severity,
                            weight=self.weight,
                            matched_evidence=match.group(0),
                            explanation=self.explanation,
                            limitations=self.limitations,
                            source_offset=global_offset
                        )
        return None


class ConflictingClaimsRule(DeterministicRule):
    rule_id = "RULE_CONFLICTING_CLAIMS"
    title = "Contradictory or Inconsistent Document Claims"
    category = FindingCategory.UNREALISTIC_CLAIMS
    severity = SeverityLevel.HIGH
    weight = 30
    explanation = (
        "The document contains contradictory statements (for example, claiming no registration fee "
        "in one passage, while demanding a refundable deposit or kit fee in another)."
    )
    limitations = (
        "Multi-track documents with distinct paid and unpaid programs may occasionally show both phrases."
    )

    def evaluate(self, text: str) -> Optional[RuleHit]:
        text_lower = text.lower()
        has_negation = any(re.search(neg, text_lower) for neg in PaymentRequestRule.NEGATION_PATTERNS)
        
        # Check if an unnegated fee pattern exists in any sentence
        sentences = re.split(r"(?<=[.!?\n])\s+", text)
        unnegated_fee = None

        for sentence in sentences:
            sentence_lower = sentence.lower()
            for pat in PaymentRequestRule.FEE_PATTERNS:
                m = re.search(pat, sentence, re.IGNORECASE)
                if m and not any(re.search(neg, sentence_lower) for neg in PaymentRequestRule.NEGATION_PATTERNS):
                    unnegated_fee = m.group(0)
                    break
            if unnegated_fee:
                break

        if has_negation and unnegated_fee:
            return RuleHit(
                rule_id=self.rule_id,
                title=self.title,
                category=self.category,
                severity=self.severity,
                weight=self.weight,
                matched_evidence=f"Claims no fee, but requires '{unnegated_fee}'",
                explanation=self.explanation,
                limitations=self.limitations,
                source_offset=text.find(unnegated_fee) if unnegated_fee in text else 0
            )
        return None


class UrgencyPressureRule(DeterministicRule):
    rule_id = "RULE_URGENCY_PRESSURE"
    title = "Artificial Urgency or Time Pressure"
    category = FindingCategory.URGENCY
    severity = SeverityLevel.MEDIUM
    weight = 20
    explanation = (
        "Artificial deadlines, such as 'within 24 hours' or 'offer expires in 2 hours', "
        "are used to induce anxiety and prevent candidates from performing due diligence."
    )
    limitations = (
        "Legitimate short-window interview scheduling or competitive deadlines might occasionally use urgent phrasing."
    )

    URGENCY_PATTERNS = [
        r"within\s+(?:24|12|48|2|6|\d+)\s*hours?",
        r"(?:pay|act|reply|confirm|register)(?:\s+\w+){0,3}\s+within\s+(?:24|12|48|2|6|\d+)\s*hours?",
        r"(?:lose|forfeit)\s+(?:your\s+seat|your\s+slot|the\s+offer|admission)",
        r"(?:strictly|only)\s+valid\s+for\s+today",
        r"(?:offer|link)\s+expires\s+in\s+\d+\s*(?:minutes?|hours?)",
        r"(?:immediate|urgent)\s+confirmation\s+required",
        r"slots\s+are\s+filling\s+fast"
    ]

    def evaluate(self, text: str) -> Optional[RuleHit]:
        for pat in self.URGENCY_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return RuleHit(
                    rule_id=self.rule_id,
                    title=self.title,
                    category=self.category,
                    severity=self.severity,
                    weight=self.weight,
                    matched_evidence=match.group(0),
                    explanation=self.explanation,
                    limitations=self.limitations,
                    source_offset=match.start()
                )
        return None


class FreeEmailSenderRule(DeterministicRule):
    rule_id = "RULE_FREE_EMAIL_SENDER"
    title = "Free/Public Email Provider for Corporate Communication"
    category = FindingCategory.SENDER_IDENTITY
    severity = SeverityLevel.MEDIUM
    weight = 20
    explanation = (
        "Corporate recruiters and official organizations communicate from custom corporate domain emails, "
        "not generic free email accounts (e.g. @gmail.com, @yahoo.com)."
    )
    limitations = (
        "Early-stage solo founders or informal freelancers may occasionally use free email accounts."
    )

    EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

    def evaluate(self, text: str) -> Optional[RuleHit]:
        matches = re.finditer(self.EMAIL_PATTERN, text)
        for m in matches:
            email = m.group(0).rstrip(".")
            domain = m.group(1).lower().rstrip(".")
            if domain in FREE_EMAIL_DOMAINS:
                # Check if text claims to be an established company or corporate hiring
                is_corporate_claim = bool(re.search(r"(?:company|corporation|\bcorp\b|ltd|pvt|inc|technologies|recruiter|recruitment|hr\s+team|\bhr\b|careers|offer|internship)", text, re.IGNORECASE))
                if is_corporate_claim:
                    return RuleHit(
                        rule_id=self.rule_id,
                        title=self.title,
                        category=self.category,
                        severity=self.severity,
                        weight=self.weight,
                        matched_evidence=email,
                        explanation=self.explanation,
                        limitations=self.limitations,
                        source_offset=m.start()
                    )
        return None


class MessagingAppMoveRule(DeterministicRule):
    rule_id = "RULE_MESSAGING_APP_MOVE"
    title = "Off-Platform Messaging App Redirection"
    category = FindingCategory.SENDER_IDENTITY
    severity = SeverityLevel.MEDIUM
    weight = 20
    explanation = (
        "Directing applicants away from official corporate email or portals onto Telegram or WhatsApp "
        "is a frequent tactic used to avoid enterprise auditing and identity verification."
    )
    limitations = (
        "In some regions, small businesses use WhatsApp for informal initial contact."
    )

    MESSAGING_PATTERNS = [
        r"(?:telegram|whatsapp)\s*(?:only|group|channel|number|account|handle|@\w+|[:\-])",
        r"(?:message|contact|reach\s+out|chat)(?:\s+(?:with|to))?(?:\s+(?:us|hr|manager|recruiter))?\s+(?:on|via)\s+(?:telegram|whatsapp)",
        r"(?:send|share).*(?:on|to)\s+(?:telegram|whatsapp)",
        r"t\.me/[a-zA-Z0-9_]+",
        r"wa\.me/[0-9]+"
    ]

    def evaluate(self, text: str) -> Optional[RuleHit]:
        for pat in self.MESSAGING_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return RuleHit(
                    rule_id=self.rule_id,
                    title=self.title,
                    category=self.category,
                    severity=self.severity,
                    weight=self.weight,
                    matched_evidence=match.group(0),
                    explanation=self.explanation,
                    limitations=self.limitations,
                    source_offset=match.start()
                )
        return None


class LookalikeDomainRule(DeterministicRule):
    rule_id = "RULE_LOOKALIKE_DOMAIN"
    title = "Suspicious or Lookalike Domain Pattern"
    category = FindingCategory.DOMAIN
    severity = SeverityLevel.HIGH
    weight = 30
    explanation = (
        "Brand names combined with keywords like '-careers', '-portal', or '-jobs' (e.g. google-careers-portal.com) "
        "frequently indicate unauthorized lookalike domains designed to imitate legitimate companies."
    )
    limitations = (
        "Some companies occasionally use distinct subdomains or vendor domains for recruiting platforms."
    )

    DOMAIN_REGEX = r"(?:https?://)?([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

    def evaluate(self, text: str) -> Optional[RuleHit]:
        for brand in TARGET_BRANDS:
            # Look for brand-careers, brand-jobs, brand-internships, etc.
            pattern = rf"(?:https?://)?([a-zA-Z0-9-]*{brand}[a-zA-Z0-9-]*(?:-careers|-jobs|-portal|-verify|-desk|-hr)\.[a-zA-Z0-9-.]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                matched_domain = match.group(1)
                # Verify it's not the actual primary brand domain (e.g. careers.google.com)
                if not matched_domain.lower().endswith(f".{brand}.com"):
                    return RuleHit(
                        rule_id=self.rule_id,
                        title=self.title,
                        category=self.category,
                        severity=self.severity,
                        weight=self.weight,
                        matched_evidence=matched_domain,
                        explanation=f"{self.explanation} (Matched target brand '{brand}')",
                        limitations=self.limitations,
                        source_offset=match.start()
                    )
        return None


class UnrealisticOfferRule(DeterministicRule):
    rule_id = "RULE_UNREALISTIC_OFFER"
    title = "Unrealistic Compensation with No Prior Qualifications"
    category = FindingCategory.UNREALISTIC_CLAIMS
    severity = SeverityLevel.MEDIUM
    weight = 20
    explanation = (
        "Promises of disproportionately high compensation for minimal effort, basic data entry, "
        "or with no formal interview/skills assessment are characteristic of employment bait scams."
    )
    limitations = (
        "Legitimate high-tier fellowships or specialized bounties can offer high stipends, but typically require rigorous evaluations."
    )

    UNREALISTIC_PATTERNS = [
        r"(?:earn|salary|stipend)\s+(?:up\s+to\s+)?(?:rs\.?|inr|\$)?\s*(?:[5-9]\d{4}|[1-9]\d{5,})\s*(?:per\s+day|daily|per\s+week)",
        r"(?:no\s+interview|no\s+experience|no\s+skills?)\s+required.*(?:earn|salary|stipend|\$|inr|rs)",
        r"(?:work\s+from\s+home\s+1-2\s+hours?.*earn\s+(?:\$|rs|inr))"
    ]

    def evaluate(self, text: str) -> Optional[RuleHit]:
        for pat in self.UNREALISTIC_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return RuleHit(
                    rule_id=self.rule_id,
                    title=self.title,
                    category=self.category,
                    severity=self.severity,
                    weight=self.weight,
                    matched_evidence=match.group(0),
                    explanation=self.explanation,
                    limitations=self.limitations,
                    source_offset=match.start()
                )
        return None


class VagueRoleDetailsRule(DeterministicRule):
    rule_id = "RULE_VAGUE_ROLE"
    title = "Generic or Vague Role Description"
    category = FindingCategory.VAGUE_DETAILS
    severity = SeverityLevel.LOW
    weight = 10
    explanation = (
        "Legitimate job or internship specifications clearly describe duties, team placement, tools, "
        "and supervisory structure."
    )
    limitations = (
        "Preliminary promotional flyers or summary social posts might omit full job descriptions."
    )

    VAGUE_PATTERNS = [
        r"(?:simple\s+data\s+entry\s+work|copy\s+paste\s+job|earn\s+money\s+by\s+typing)",
        r"(?:any\s+degree\s+holder\s+can\s+apply\s+without\s+any\s+skills)"
    ]

    def evaluate(self, text: str) -> Optional[RuleHit]:
        for pat in self.VAGUE_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return RuleHit(
                    rule_id=self.rule_id,
                    title=self.title,
                    category=self.category,
                    severity=self.severity,
                    weight=self.weight,
                    matched_evidence=match.group(0),
                    explanation=self.explanation,
                    limitations=self.limitations,
                    source_offset=match.start()
                )
        return None


class RulesEngine:
    def __init__(self):
        self.rules: List[DeterministicRule] = [
            PaymentRequestRule(),
            ConflictingClaimsRule(),
            UrgencyPressureRule(),
            FreeEmailSenderRule(),
            MessagingAppMoveRule(),
            LookalikeDomainRule(),
            UnrealisticOfferRule(),
            VagueRoleDetailsRule(),
        ]

    def run(self, source_text: str) -> List[RuleHit]:
        """
        Executes all deterministic rules against the source text.
        """
        hits: List[RuleHit] = []
        for rule in self.rules:
            hit = rule.evaluate(source_text)
            if hit:
                hits.append(hit)
        return hits


rules_engine = RulesEngine()
