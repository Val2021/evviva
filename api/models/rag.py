from typing import Any

from pydantic import BaseModel, Field


class RAGRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    filter: dict[str, Any] | None = None


class RAGSource(BaseModel):
    score: float
    metadata: dict[str, Any]
    text_preview: str


class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: list[RAGSource]
