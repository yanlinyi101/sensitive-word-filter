from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MatchedWord:
    word: str
    category: str
    risk_level: int   # 1-3
    position: int     # 句内字符起始位置

@dataclass
class SentenceResult:
    index: int
    text: str
    risk_level: int                        # 0=无 1=低 2=中 3=高
    matched_words: List[MatchedWord]
    triggered_rules: List[str]             # 触发规则名列表
    llm_confirmed_risk: Optional[str]      # high|medium|low|none|skipped|None
    llm_suggestion: Optional[str]
