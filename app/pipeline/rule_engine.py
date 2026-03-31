import json
import re
from typing import List, Dict, Any, Tuple
from app.pipeline.types import MatchedWord

class RuleEngine:
    def __init__(self, rules: List[Dict[str, Any]]):
        self._rules = [r for r in rules if r.get("enabled", True)]

    def evaluate(self, text: str, matched_words: List[MatchedWord]) -> Tuple[int, List[str]]:
        """Evaluate all enabled rules against text and matched words.

        Returns (max_risk_level, list_of_triggered_rule_names).
        Rules only upgrade risk level (never downgrade — that is LLM's job).
        """
        max_risk = 0
        triggered = []
        for rule in sorted(self._rules, key=lambda r: -r.get("priority", 0)):
            config = json.loads(rule["conditions"])
            if self._check_conditions(text, matched_words, config):
                triggered.append(rule["name"])
                max_risk = max(max_risk, rule["risk_level"])
        return max_risk, triggered

    def _check_conditions(self, text: str, matched_words: List[MatchedWord], config: Dict) -> bool:
        logic = config.get("logic", "AND")
        results = [self._check_one(text, matched_words, c) for c in config["conditions"]]
        return all(results) if logic == "AND" else any(results)

    def _check_one(self, text: str, matched_words: List[MatchedWord], condition: Dict) -> bool:
        t = condition["type"]
        if t == "word_match":
            found = {m.word for m in matched_words}
            targets = set(condition["words"])
            return bool(found & targets) if condition["op"] == "any" else targets.issubset(found)
        elif t == "category_count":
            count = sum(1 for m in matched_words if m.category == condition["category"])
            return count >= condition["min"]
        elif t == "regex":
            return bool(re.search(condition["pattern"], text))
        return False
