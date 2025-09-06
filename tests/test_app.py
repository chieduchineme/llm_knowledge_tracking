import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import service, database

# Setup TestClient
client = TestClient(app)

# Test data
SAMPLE_TEXT = "Python is a versatile programming language. It is widely used in AI and web development."
SAMPLE_TITLE = "Python AI"

# Service tests
def test_analyze_document_basic():
    result = service.analyze_document(SAMPLE_TEXT, title=SAMPLE_TITLE)
    assert isinstance(result, dict)
    assert "summary" in result
    assert "topics" in result
    assert "keywords" in result
    assert "confidence" in result
    assert result["title"] == SAMPLE_TITLE

def test_analyze_document_empty_text():
    import pytest
    with pytest.raises(ValueError):
        service.analyze_document("")

# Database tests
def test_database_insert_and_search():
    database.init_db()
    rec = service.analyze_document(SAMPLE_TEXT, title=SAMPLE_TITLE)
    new_id = database.insert(rec)
    assert isinstance(new_id, int) and new_id > 0

    results = database.search(topic="Python")
    assert any(r["id"] == new_id for r in results)

# API endpoint tests
def test_root_endpoint():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True

def test_analyze_endpoint_single_text():
    payload = {"text": SAMPLE_TEXT, "title": SAMPLE_TITLE}
    r = client.post("/analyze", json=payload)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert "summary" in items[0]

def test_analyze_endpoint_batch_texts():
    payload = {"texts": [SAMPLE_TEXT, "Another short sentence."], "title": SAMPLE_TITLE}
    r = client.post("/analyze", json=payload)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2

def test_search_endpoint():
    r = client.get("/search", params={"topic": "Python"})
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
