from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from . import service, database
from .schemas import AnalyzeRequest, AnalysisResponse

router = APIRouter()


@router.post("/analyze", response_model=List[AnalysisResponse])
def analyze(req: AnalyzeRequest):
    try:
        texts = []
        if req.text:
            texts = [req.text]
        elif req.texts:
            if not req.texts:
                raise ValueError("Texts list cannot be empty")
            texts = req.texts
        else:
            raise ValueError("Provide either 'text' or 'texts'")

        items = [service.analyze_document(t, title=req.title) for t in texts]
        ids = [database.insert(item) for item in items]
        rows = database.search()
        return [
            AnalysisResponse(**r) for r in rows[: len(ids)]
        ]
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {ex}")


@router.get("/search", response_model=List[AnalysisResponse])
def search(topic: Optional[str] = Query(None), keyword: Optional[str] = Query(None)):
    rows = database.search(topic=topic, keyword=keyword)
    return [AnalysisResponse(**r) for r in rows]
