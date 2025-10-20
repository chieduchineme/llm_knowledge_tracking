# LLM Knowledge Extractor

A lightweight FastAPI service that takes unstructured text, summarizes it, and extracts **structured metadata**. The system persistently stores the analysis in SQLite and allows searching by topic or keyword.

It combines **LLM-powered summarization**, **heuristic NLP**, and **robust persistence** into a minimal, maintainable pipeline.

---

## Features

* **Structured Metadata Extraction**:

  * `title` (optional, provided by user)
  * `topics` (top 3 key topics)
  * `sentiment` (`positive`, `neutral`, `negative`)
  * `keywords` (top 3 frequent nouns/terms, computed locally)
  * `confidence` (naive heuristic combining text length and LLM usage)

* **Summarization**:

  * Uses OpenAI LLM when enabled (`USE_OPENAI=true`), producing a concise 1–2 sentence summary.
  * Falls back to a deterministic heuristic if LLM is unavailable or fails, extracting the first sentence(s) and normalizing punctuation.

* **Persistence**:

  * SQLite database (`knowledge.db`) stores all analyses.
  * Topics and keywords are stored as JSON arrays for simple and fast querying.

* **Searchable API**:

  * Search by topic or keyword using case-insensitive matches.
  * Batch and single-text analysis supported.

* **Robust & Resilient**:

  * Graceful handling of empty input or API failures.
  * Confidence score helps evaluate reliability of automated summary.

* **Docker-ready**:

  * Build and run in a container for easy deployment.

---

## Advantages & Design Choices

This system integrates the best practices from multiple approaches to create a **balanced, reliable, and maintainable solution**:

1. **LLM & Heuristic fallback**: Summarization attempts to use an LLM if configured, but always has a local fallback. Ensures the service never fails due to API issues.
2. **Robust JSON extraction**: Metadata is extracted from the LLM reliably, using regex fallback for malformed responses.
3. **Confidence scoring**: Combines token-count saturation with optional LLM usage to provide a naive confidence measure.
4. **Keyword & topic extraction**: Implemented locally using frequency-based heuristics with a stopword filter and noun-bias rules. Fully independent of LLM.
5. **Clean separation of concerns**:

   * `llm_utils.py` handles LLM interaction.
   * `text_utils.py` handles tokenization, keywords, sentiment, and confidence.
   * `service.py` coordinates the analysis pipeline.
   * `database.py` handles persistence.
   * `api.py` exposes HTTP endpoints.
6. **Batch processing & search**: Supports multiple texts per request and search by topic/keyword with simple OR logic.
7. **Docker-ready**: Minimal dependencies and containerization make the service easy to deploy anywhere.

---

## Quickstart

### Clone & Setup

```bash
git clone git@github.com:chieduchineme/llm_knowledge_extractor.git
cd llm_knowledge_extractor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Run API

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive Swagger documentation.

### Optional: LLM Summaries

Create a `.env` file or export environment variables:

```
USE_OPENAI=true
OPENAI_API_KEY=sk-...
```

If `USE_OPENAI` is not set or the key is missing, the local heuristic summarizer is used automatically.

---

## API Endpoints

### `POST /analyze`

**Single Text Request**:

```json
{
  "text": "OpenAI released new tools. Developers are excited.",
  "title": "News blip"
}
```

**Batch Text Request**:

```json
{
  "texts": [
    "Python remains popular for data science.",
    "Go is appreciated for fast, static binaries."
  ]
}
```

**Response Example**:

```json
{
  "items": [{
    "id": 1,
    "title": "News blip",
    "summary": "A concise 1-2 sentence summary...",
    "topics": ["openai", "tools", "developers"],
    "sentiment": "positive",
    "keywords": ["openai", "tools", "developers"],
    "confidence": 0.74,
    "created_at": "2025-01-01T12:00:00Z"
  }]
}
```

### `GET /search`

Search by topic or keyword:

```
/search?topic=openai
/search?keyword=python
```

**Response** mirrors stored analysis records.

---

## Examples

### Kubernetes Cost Controls

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Kubernetes cost controls",
    "text": "Kubernetes cluster costs can spike without guardrails. Use autoscalers and clear budgets..."
  }'
```

```bash
curl "http://127.0.0.1:8000/search?topic=kubernetes"
curl "http://127.0.0.1:8000/search?keyword=autoscaler"
```

### Postgres Vector Search

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Postgres vector search",
    "text": "Postgres with pgvector extension enables similarity search on embeddings..."
  }'
```

```bash
curl "http://127.0.0.1:8000/search?topic=postgres"
curl "http://127.0.0.1:8000/search?keyword=pgvector"
```

---

## Testing

```bash
pytest -v
```

Optionally, set `PYTHONPATH=.` if needed.

---

## Docker

Build and run in a container:

```bash
docker build -t jouster .
docker run -p 8000:8000 --env-file .env jouster
```

---

## Notes

* **Keywords are computed locally**, not via the LLM.
* **Heuristic summarization** ensures service availability even if the LLM fails.
* **Designed to be **lightweight, portable, and easy to review**, with minimal dependencies and full Docker support.


