from __future__ import annotations
import re, math
from collections import Counter

STOPWORDS = set("""
a an and the is are was were be been being am do does did doing have has had having
i me my we our you your he she it they them this that these those here there
of on in at by for from to with without into over under as about above below
up down not no nor so too very can will just than then now out off or if but
""".split())

VERB_HINTS = set("""
be been being am is are was were do does did doing have has had having
say says said make makes made go goes went going take takes took
""".split())


def normalize(text: str) -> str:
    text = (text.replace("’", "'")
                 .replace("‘", "'")
                 .replace("“", '"')
                 .replace("”", '"')
                 .replace("–", "-")
                 .replace("—", "-"))
    return re.sub(r"\s+", " ", text.strip())


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-']+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def is_probable_noun(word: str) -> bool:
    if word in VERB_HINTS:
        return False
    if (word.endswith("ing") or word.endswith("ed")) and len(word) > 5:
        return False
    return True


def extract_keywords(text: str, k: int = 3, boost: list[str] | None = None) -> list[str]:
    tokens = [w for w in tokenize(text) if is_probable_noun(w)]
    if boost:
        for b in boost:
            tokens.extend([b.lower()] * 3)

    counts = Counter(tokens)
    pool = [w for w, _ in counts.most_common(10)]
    pool.sort(key=lambda w: (-(counts[w]), -len(w)))
    return pool[:k]


def sentiment(text: str) -> str:
    pos = set("good great excellent positive progress success happy love like benefit improve improved improvement strong growth win wins winning excited".split())
    neg = set("bad poor terrible negative fail failure sad hate dislike issue problem problems weak decline loss losses losing concerned".split())
    toks = tokenize(text)
    score = sum(1 for t in toks if t in pos) - sum(1 for t in toks if t in neg)
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"


def confidence(text: str, used_llm: bool) -> float:
    n = len(tokenize(text))
    base = 1 - math.exp(-n / 60)  # saturating confidence
    length_bonus = min(0.4, (len(text) / 2000) * 0.4)
    base += length_bonus
    if used_llm:
        base += 0.05
    return round(min(0.99, base), 2)
