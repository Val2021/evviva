from fastapi import APIRouter, HTTPException

from api.models.search import SearchRequest, SearchResponse
from api.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])

search_service = SearchService()


@router.post("", response_model=SearchResponse)
def search(request: SearchRequest):
    try:
        return search_service.search(
            query=request.query,
            limit=request.limit,
            filter=request.filter,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
