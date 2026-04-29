from api.config.prompts import RAG_PROMPT
from api.models.rag import RAGResponse, RAGSource
from api.services.llm_service import LLMService
from api.services.search_service import SearchService


class RAGService:
    def __init__(self):
        self.search_service = SearchService()
        self.llm_service = LLMService()

    def generate_answer(
        self,
        query: str,
        limit: int = 5,
        filter: dict | None = None,
    ) -> RAGResponse:
        search_response = self.search_service.search(
            query=query,
            limit=limit,
            filter=filter,
        )

        if not search_response.results:
            return RAGResponse(
                query=query,
                answer="I could not find enough information in the available documents to answer this question.",
                sources=[],
            )

        context = self._build_context(search_response.results)

        prompt = RAG_PROMPT.format(
            context=context,
            query=query,
        )

        answer = self.llm_service.generate(prompt)

        sources = [
            RAGSource(
                score=result.score,
                metadata=result.metadata,
                text_preview=result.text[:500],
            )
            for result in search_response.results
        ]

        return RAGResponse(
            query=query,
            answer=answer,
            sources=sources,
        )

    def _build_context(self, results) -> str:
        context_parts = []

        for index, result in enumerate(results, start=1):
            metadata = result.metadata

            source_header = (
                f"[Source {index}]\n"
                f"Source: {metadata.get('source')}\n"
                f"Channel: {metadata.get('channel')}\n"
                f"Document ID: {metadata.get('document_id')}\n"
                f"Contact: {metadata.get('contact_name')}\n"
                f"Timestamp: {metadata.get('timestamp')}\n"
                f"Score: {result.score}\n"
            )

            context_parts.append(
                f"{source_header}\n{result.text}"
            )

        return "\n\n---\n\n".join(context_parts)
