import json
from unittest.mock import MagicMock, patch
from app.pipeline.llm_reviewer import LLMReviewer
from app.pipeline.types import SentenceResult, MatchedWord

def _sentence(idx, text, rl=3):
    return SentenceResult(
        index=idx, text=text, risk_level=rl,
        matched_words=[MatchedWord("根治", "医疗", 3, 0)],
        triggered_rules=[], llm_confirmed_risk=None, llm_suggestion=None
    )

def _mock_response(payload: dict):
    m = MagicMock()
    m.text = json.dumps(payload, ensure_ascii=False)
    return m

def test_review_updates_confirmed_risk():
    payload = {"sentences": [{"index": 0, "confirmed_risk": "high", "reason": "医疗夸大", "suggestion": "改为辅助控制血糖"}]}
    with patch("google.generativeai.GenerativeModel.generate_content", return_value=_mock_response(payload)):
        reviewer = LLMReviewer(api_key="fake")
        sentences = [_sentence(0, "根治糖尿病")]
        result = reviewer.review(sentences, ["前句", "根治糖尿病", "后句"])
        assert result[0].llm_confirmed_risk == "high"
        assert "辅助控制血糖" in result[0].llm_suggestion

def test_review_none_risk_downgrades_to_low():
    payload = {"sentences": [{"index": 0, "confirmed_risk": "none", "reason": "引用历史文献，无实际夸大", "suggestion": ""}]}
    with patch("google.generativeai.GenerativeModel.generate_content", return_value=_mock_response(payload)):
        reviewer = LLMReviewer(api_key="fake")
        sentences = [_sentence(0, "某文献称根治效果明显", rl=3)]
        result = reviewer.review(sentences, ["", "某文献称根治效果明显", ""])
        assert result[0].llm_confirmed_risk == "none"
        assert result[0].risk_level == 1

def test_review_skips_on_api_failure():
    with patch("google.generativeai.GenerativeModel.generate_content", side_effect=Exception("timeout")):
        reviewer = LLMReviewer(api_key="fake")
        sentences = [_sentence(0, "根治糖尿病")]
        result = reviewer.review(sentences, ["", "根治糖尿病", ""])
        assert result[0].llm_confirmed_risk == "skipped"
        assert result[0].risk_level == 3  # preserved on failure
