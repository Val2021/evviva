from functools import lru_cache

from fastapi import APIRouter, HTTPException

from api.models.search import SearchRequest, SearchResponse
from api.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])

@lru_cache
def get_search_service() -> SearchService:
    return SearchService()

@router.post("", response_model=SearchResponse)
def search(request: SearchRequest):
    try:
        search_service = get_search_service()
        return search_service.search(
            query=request.query,
            limit=request.limit,
            filter=request.filter,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
