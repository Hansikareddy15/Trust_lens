"""
Safe URL and domain analysis module for TrustLens AI.
Extracts domains from text, evaluates lookalike patterns and free mail providers,
and implements strict safety safeguards (no blind arbitrary HTTP fetching).
"""

import re
from typing import List, Dict, Any
from urllib.parse import urlparse

TARGET_BRANDS = [
    "google", "microsoft", "amazon", "apple", "meta", "netflix",
    "tcs", "infosys", "wipro", "deloitte", "accenture", "cognizant"
]

FREE_MAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "protonmail.com", "zoho.com"
}


class DomainAnalyzer:
    URL_REGEX = r"https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?"
    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"

    @classmethod
    def extract_domains_and_links(cls, text: str) -> Dict[str, Any]:
        """
        Extracts domains from URLs and email addresses found in the text.
        """
        urls = re.findall(cls.URL_REGEX, text)
        emails = re.findall(cls.EMAIL_REGEX, text)

        unique_domains = set()
        for u in urls:
            domain = u.lower().strip()
            unique_domains.add(domain)

        email_domains = set()
        for e in emails:
            domain = e.lower().strip()
            email_domains.add(domain)

        domain_reports = []
        for d in sorted(unique_domains):
            report = cls._evaluate_domain(d, is_email=False)
            domain_reports.append(report)

        for d in sorted(email_domains):
            report = cls._evaluate_domain(d, is_email=True)
            domain_reports.append(report)

        return {
            "total_domains_found": len(domain_reports),
            "domains": domain_reports
        }

    @classmethod
    def _evaluate_domain(cls, domain: str, is_email: bool = False) -> Dict[str, Any]:
        is_free_mail = domain in FREE_MAIL_PROVIDERS
        matched_brand = None
        is_lookalike = False

        for brand in TARGET_BRANDS:
            if brand in domain and not domain.endswith(f".{brand}.com") and domain != f"{brand}.com":
                is_lookalike = True
                matched_brand = brand
                break

        return {
            "domain": domain,
            "type": "email_domain" if is_email else "web_domain",
            "is_free_provider": is_free_mail,
            "is_potential_lookalike": is_lookalike,
            "impersonated_brand": matched_brand,
            "verification_status": "analyzed_heuristically",
            "risk_assessment": (
                "High Risk Lookalike" if is_lookalike
                else "Public Free Email" if is_free_mail
                else "Standard Domain"
            )
        }


domain_analyzer = DomainAnalyzer()
