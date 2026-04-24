from fastapi import APIRouter, HTTPException

from api.models.llm import LLMRequest, LLMResponse
from api.services.llm_service import LLMService

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/test", response_model=LLMResponse)
def test_llm(request: LLMRequest):
    try:
        service = LLMService()
        answer = service.generate(request.prompt)
        return LLMResponse(answer=answer)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
