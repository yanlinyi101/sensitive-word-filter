from app.pipeline.dfa_matcher import DFAMatcher

WORDS = [
    {"word": "根治", "category": "医疗", "risk_level": 3, "enabled": True},
    {"word": "特效", "category": "医疗", "risk_level": 2, "enabled": True},
    {"word": "最低价", "category": "广告法", "risk_level": 2, "enabled": True},
    {"word": "禁用词", "category": "政治", "risk_level": 3, "enabled": False},
]

def test_finds_single_word():
    m = DFAMatcher(WORDS)
    results = m.match("这款产品能根治糖尿病")
    assert len(results) == 1
    assert results[0].word == "根治"
    assert results[0].risk_level == 3
    assert results[0].category == "医疗"

def test_finds_multiple_words():
    m = DFAMatcher(WORDS)
    results = m.match("特效药最低价出售")
    words_found = {r.word for r in results}
    assert words_found == {"特效", "最低价"}

def test_no_match():
    m = DFAMatcher(WORDS)
    assert m.match("这是一款普通产品") == []

def test_disabled_word_not_matched():
    m = DFAMatcher(WORDS)
    assert m.match("禁用词出现") == []

def test_position_is_correct():
    m = DFAMatcher(WORDS)
    results = m.match("产品根治效果")
    assert results[0].position == 2  # "根治" starts at index 2
