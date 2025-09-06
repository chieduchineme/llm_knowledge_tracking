from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    text: Optional[str] = Field(default=None, description="Single text to analyze")
    title: Optional[str] = None
    texts: Optional[List[str]] = Field(default=None, description="Batch processing")


class AnalysisResponse(BaseModel):
    id: int
    title: Optional[str] = None
    summary: str
    topics: list[str]
    sentiment: str
    keywords: list[str]
    confidence: float
    created_at: str
