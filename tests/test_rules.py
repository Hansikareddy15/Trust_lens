"""
Unit tests for deterministic rules engine and context-sensitive checks.
"""

from app.core.rules import (
    PaymentRequestRule,
    UrgencyPressureRule,
    FreeEmailSenderRule,
    MessagingAppMoveRule,
    LookalikeDomainRule,
    UnrealisticOfferRule,
    VagueRoleDetailsRule,
    rules_engine,
)


def test_payment_rule_positive():
    rule = PaymentRequestRule()
    text = "To confirm your appointment, please deposit a refundable security deposit of Rs. 3000."
    hit = rule.evaluate(text)
    assert hit is not None
    assert hit.rule_id == "RULE_PAYMENT_REQUEST"
    assert hit.weight == 35


def test_payment_rule_negation_contexts():
    rule = PaymentRequestRule()
    negated_samples = [
        "Decode Labs does not charge any fee or security deposit at any stage.",
        "We never ask for any fee or money for training.",
        "This internship is completely free of cost.",
        "There is no registration fee required for candidates."
    ]
    for sample in negated_samples:
        hit = rule.evaluate(sample)
        assert hit is None, f"Failed for negated sample: '{sample}'"


def test_urgency_rule():
    rule = UrgencyPressureRule()
    text = "You must confirm your seat within 24 hours or your offer will be revoked."
    hit = rule.evaluate(text)
    assert hit is not None
    assert hit.rule_id == "RULE_URGENCY_PRESSURE"


def test_free_email_corporate_sender():
    rule = FreeEmailSenderRule()
    text = "Global Tech Corporation HR team invites you. Contact hr.recruiter@gmail.com for details."
    hit = rule.evaluate(text)
    assert hit is not None
    assert hit.rule_id == "RULE_FREE_EMAIL_SENDER"


def test_free_email_non_corporate():
    rule = FreeEmailSenderRule()
    text = "Hey buddy, drop me an email at my personal email alex@gmail.com about dinner."
    hit = rule.evaluate(text)
    assert hit is None


def test_messaging_app_move():
    rule = MessagingAppMoveRule()
    text = "Please reach out to our talent manager on Telegram @career_hire_hr to finalize paperwork."
    hit = rule.evaluate(text)
    assert hit is not None
    assert hit.rule_id == "RULE_MESSAGING_APP_MOVE"


def test_lookalike_domain():
    rule = LookalikeDomainRule()
    text = "Submit your bank credentials at https://google-careers-portal.com/login."
    hit = rule.evaluate(text)
    assert hit is not None
    assert hit.rule_id == "RULE_LOOKALIKE_DOMAIN"


def test_unrealistic_offer():
    rule = UnrealisticOfferRule()
    text = "No interview required! Earn Rs. 60000 daily from home with zero experience."
    hit = rule.evaluate(text)
    assert hit is not None
    assert hit.rule_id == "RULE_UNREALISTIC_OFFER"


def test_full_rules_engine_multi_hit():
    text = (
        "Urgent: Tech Corp requires Rs. 2000 registration fee. "
        "Pay within 24 hours. Contact on WhatsApp: +919876543210. "
        "Sender: techrecruiter@gmail.com."
    )
    hits = rules_engine.run(text)
    rule_ids = {h.rule_id for h in hits}
    assert "RULE_PAYMENT_REQUEST" in rule_ids
    assert "RULE_URGENCY_PRESSURE" in rule_ids
    assert "RULE_FREE_EMAIL_SENDER" in rule_ids
    assert "RULE_MESSAGING_APP_MOVE" in rule_ids
