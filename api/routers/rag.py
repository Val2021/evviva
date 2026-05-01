from functools import lru_cache
from fastapi import APIRouter, HTTPException

from api.models.rag import RAGRequest, RAGResponse
from api.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG"])


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService()

@router.post("", response_model=RAGResponse)
def rag(request: RAGRequest):
    try:
        rag_service = get_rag_service()
        return rag_service.generate_answer(
            query=request.query,
            limit=request.limit,
            filter=request.filter,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
