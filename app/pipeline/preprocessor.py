import re
from typing import List

_TIMESTAMP_RE = re.compile(r"[\[(]\d{1,2}:\d{2}(?::\d{2})?[\])]")
_SPEAKER_RE = re.compile(r"^[\w\s]{1,10}[：:]")
_SPLIT_RE = re.compile(r"[。！？\n]+")

def preprocess(text: str) -> List[str]:
    text = _TIMESTAMP_RE.sub("", text)
    sentences = _SPLIT_RE.split(text)
    result = []
    for s in sentences:
        s = s.strip()
        s = _SPEAKER_RE.sub("", s).strip()
        if s:
            result.append(s)
    return result
