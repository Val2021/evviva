from fastapi import APIRouter, HTTPException

from api.models.rag import RAGRequest, RAGResponse
from api.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG"])

rag_service = RAGService()


@router.post("", response_model=RAGResponse)
def rag(request: RAGRequest):
    try:
        return rag_service.generate_answer(
            query=request.query,
            limit=request.limit,
            filter=request.filter,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
