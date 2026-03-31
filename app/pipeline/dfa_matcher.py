import ahocorasick
from typing import List, Dict, Any
from app.pipeline.types import MatchedWord

class DFAMatcher:
    def __init__(self, words: List[Dict[str, Any]]):
        self._automaton = ahocorasick.Automaton()
        for entry in words:
            if not entry.get("enabled", True):
                continue
            self._automaton.add_word(
                entry["word"],
                {"word": entry["word"], "category": entry.get("category", ""), "risk_level": entry["risk_level"]}
            )
        if len(self._automaton) > 0:
            self._automaton.make_automaton()

    def match(self, text: str) -> List[MatchedWord]:
        if len(self._automaton) == 0:
            return []
        results = []
        seen: set = set()
        for end_idx, data in self._automaton.iter(text):
            word = data["word"]
            if word in seen:
                continue
            seen.add(word)
            position = end_idx - len(word) + 1
            results.append(MatchedWord(
                word=word,
                category=data["category"],
                risk_level=data["risk_level"],
                position=position
            ))
        return results
