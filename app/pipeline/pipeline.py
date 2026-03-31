import os
from typing import List
from sqlalchemy.orm import Session
from app.pipeline.preprocessor import preprocess
from app.pipeline.dfa_matcher import DFAMatcher
from app.pipeline.rule_engine import RuleEngine
from app.pipeline.llm_reviewer import LLMReviewer
from app.pipeline.types import SentenceResult
from app.db.models import WordlistEntry, Rule

def run_pipeline(text: str, doc_type: str, db: Session) -> List[SentenceResult]:
    """Run the full risk review pipeline on a text.

    1. Preprocess (split sentences)
    2. DFA match against enabled wordlist
    3. Rule engine (upgrades risk level only)
    4. LLM review (only for risk_level >= 2, requires GEMINI_API_KEY env var)

    Returns one SentenceResult per sentence.
    """
    words = [
        {"word": e.word, "category": e.category, "risk_level": e.risk_level, "enabled": e.enabled}
        for e in db.query(WordlistEntry).all()
    ]
    rules = [
        {"id": r.id, "name": r.name, "conditions": r.conditions,
         "risk_level": r.risk_level, "enabled": r.enabled, "priority": r.priority}
        for r in db.query(Rule).all()
    ]

    matcher = DFAMatcher(words)
    engine = RuleEngine(rules)
    sentences = preprocess(text)
    results: List[SentenceResult] = []

    for i, sent in enumerate(sentences):
        matched = matcher.match(sent)
        base_risk = max((m.risk_level for m in matched), default=0)
        rule_risk, triggered = engine.evaluate(sent, matched)
        results.append(SentenceResult(
            index=i,
            text=sent,
            risk_level=max(base_risk, rule_risk),
            matched_words=matched,
            triggered_rules=triggered,
            llm_confirmed_risk=None,
            llm_suggestion=None,
        ))

    to_review = [r for r in results if r.risk_level >= 2]
    if to_review:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            LLMReviewer(api_key).review(to_review, sentences)

    return results
