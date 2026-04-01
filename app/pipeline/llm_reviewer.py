import json
import logging
import time
import os
from typing import List
from openai import OpenAI
from app.pipeline.types import SentenceResult
from app.utils.rate_guard import rate_guard

logger = logging.getLogger(__name__)

_PROMPT = """你是视频内容审核专家。对以下句子进行风险复核，判断在上下文中是否真的有风险，并给出改写建议。

返回纯 JSON（不含其他内容）：
{{"sentences": [{{"index": <编号>, "confirmed_risk": "high|medium|low|none", "reason": "<一句话>", "suggestion": "<改写建议或空字符串>"}}]}}

待复核：
{items}"""

class LLMReviewer:
    def __init__(self, api_key: str):
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )

    def review(self, sentences: List[SentenceResult], all_sentences: List[str]) -> List[SentenceResult]:
        """Batch review sentences with DeepSeek. Modifies sentences in-place and returns them.

        Only call with sentences that already have risk_level >= 2.
        On API failure after retries, sets llm_confirmed_risk='skipped' and preserves risk_level.
        On confirmed_risk='none', downgrades risk_level to 1.
        """
        items = [
            {
                "index": s.index,
                "text": s.text,
                "context_before": all_sentences[s.index - 1] if 0 < s.index < len(all_sentences) else "",
                "context_after": all_sentences[s.index + 1] if s.index + 1 < len(all_sentences) else "",
                "matched_words": [m.word for m in s.matched_words],
            }
            for s in sentences
        ]
        prompt = _PROMPT.format(items=json.dumps(items, ensure_ascii=False, indent=2))
        raw = self._call_with_retry(prompt)
        if raw is None:
            for s in sentences:
                s.llm_confirmed_risk = "skipped"
            return sentences
        try:
            data = json.loads(raw)
            by_index = {r["index"]: r for r in data["sentences"]}
            for s in sentences:
                r = by_index.get(s.index)
                if r:
                    s.llm_confirmed_risk = r["confirmed_risk"]
                    s.llm_suggestion = r.get("suggestion") or ""
                    if r["confirmed_risk"] == "none":
                        s.risk_level = 1
        except (json.JSONDecodeError, KeyError):
            for s in sentences:
                s.llm_confirmed_risk = "skipped"
        return sentences

    def _call_with_retry(self, prompt: str):
        if not rate_guard.llm_allowed():
            logger.warning("LLM skipped by rate_guard")
            return None
        rate_guard.record_llm_call()
        for attempt in range(3):
            try:
                resp = self._client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    timeout=25,
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning("LLM call attempt %d failed: %s", attempt + 1, e)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        return None
