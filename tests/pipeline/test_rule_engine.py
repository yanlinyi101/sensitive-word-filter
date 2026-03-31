import json
from app.pipeline.rule_engine import RuleEngine
from app.pipeline.types import MatchedWord

def _rule(name, conditions_dict, risk_level=3, enabled=True, priority=0):
    return {"id": 1, "name": name, "conditions": json.dumps(conditions_dict),
            "risk_level": risk_level, "enabled": enabled, "priority": priority}

def _word(w, cat="医疗", rl=2):
    return MatchedWord(word=w, category=cat, risk_level=rl, position=0)

def test_word_match_any_triggers():
    rule = _rule("医疗夸大", {"conditions": [{"type": "word_match", "words": ["根治", "特效"], "op": "any"}], "logic": "AND"})
    engine = RuleEngine([rule])
    level, triggered = engine.evaluate("这产品能根治糖尿病", [_word("根治", rl=2)])
    assert level == 3
    assert "医疗夸大" in triggered

def test_word_match_all_requires_all():
    rule = _rule("组合风险", {"conditions": [{"type": "word_match", "words": ["根治", "特效"], "op": "all"}], "logic": "AND"})
    engine = RuleEngine([rule])
    level, triggered = engine.evaluate("根治", [_word("根治")])
    assert level == 0  # only one word, not triggered
    level2, _ = engine.evaluate("根治特效", [_word("根治"), _word("特效")])
    assert level2 == 3

def test_category_count_triggers():
    rule = _rule("多功效词", {"conditions": [{"type": "category_count", "category": "功效词", "min": 2}], "logic": "AND"})
    engine = RuleEngine([rule])
    words = [MatchedWord("根治", "功效词", 2, 0), MatchedWord("特效", "功效词", 2, 2)]
    level, triggered = engine.evaluate("根治特效药", words)
    assert level == 3

def test_regex_triggers():
    rule = _rule("数字夸大", {"conditions": [{"type": "regex", "pattern": r"\d+%.*效果"}], "logic": "AND"})
    engine = RuleEngine([rule])
    level, _ = engine.evaluate("提升90%效果", [])
    assert level == 3

def test_disabled_rule_skipped():
    rule = _rule("跳过规则", {"conditions": [{"type": "word_match", "words": ["根治"], "op": "any"}], "logic": "AND"}, enabled=False)
    engine = RuleEngine([rule])
    level, triggered = engine.evaluate("根治", [_word("根治")])
    assert level == 0

def test_no_rule_match():
    rule = _rule("医疗夸大", {"conditions": [{"type": "word_match", "words": ["根治"], "op": "any"}], "logic": "AND"})
    engine = RuleEngine([rule])
    level, triggered = engine.evaluate("这是普通产品", [])
    assert level == 0
    assert triggered == []
