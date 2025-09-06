import os, json, re
from typing import Any, Dict

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def summarize_and_extract(text: str) -> tuple[str, Dict[str, Any], bool]:
    """
    Returns (summary, metadata, used_llm).
    Metadata includes: title, topics, sentiment.
    """
    use_llm = os.getenv("USE_OPENAI", "false").lower() == "true"
    if not (use_llm and os.getenv("OPENAI_API_KEY") and OpenAI):
        return "", {}, False

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        chat = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "Summarize the text in 1-2 sentences, then extract JSON with keys: "
                    "summary, title, topics, sentiment (positive/neutral/negative)."
                )},
                {"role": "user", "content": text[:4000]},
            ],
            temperature=0.2,
        )
        content = chat.choices[0].message.content if chat.choices else "{}"
    except Exception as e:
        return "", {}, False

    try:
        data = json.loads(content)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return "", {}, False
        data = json.loads(match.group(0))

    summary = data.get("summary", "")
    metadata = {
        "title": data.get("title"),
        "topics": data.get("topics", []),
        "sentiment": (data.get("sentiment") or "neutral").lower()
    }
    return summary, metadata, True
