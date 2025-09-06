from __future__ import annotations
import re
from . import text_utils, llm_utils


def analyze_document(text: str, title: str | None = None) -> dict:
    text = text_utils.normalize(text)
    if not text:
        raise ValueError("Empty input text")

    # Try LLM first
    summary, metadata, used_llm = llm_utils.summarize_and_extract(text)

    if not summary:  # fallback heuristic
        sents = text_utils.split_sentences(text)
        summary = sents[0] if sents else ""
        if len(sents) > 1 and len(summary) < 180:
            summary += " " + sents[1]
        metadata = {
            "title": title,
            "topics": text_utils.extract_keywords(text, 3),
            "sentiment": text_utils.sentiment(text),
        }
        used_llm = False

    boost = re.findall(r"[A-Za-z][A-Za-z\-']+", title) if title else []
    keywords = text_utils.extract_keywords(text, 3, boost=boost)

    return {
        "title": metadata.get("title") or title,
        "text": text,
        "summary": text_utils.normalize(summary),
        "topics": metadata.get("topics", []),
        "keywords": keywords,
        "sentiment": metadata.get("sentiment", "neutral"),
        "confidence": text_utils.confidence(text, used_llm),
    }
