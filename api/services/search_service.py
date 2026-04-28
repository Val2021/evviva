from typing import Any

from qdrant_client import QdrantClient, models

from api.config.settings import settings
from api.models.search import SearchResponse, SearchResult
from api.services.embedding_service import EmbeddingService


class SearchService:
    def __init__(self):
        self.qdrant = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.collection_name
        self.embedding_service = EmbeddingService()

    def search(
        self,
        query: str,
        limit: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> SearchResponse:
        query_dense, query_sparse, query_colbert = self.embedding_service.embed_query(
            query
        )

        query_filter = self._build_qdrant_filter(filter)

        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            prefetch=[
                {
                    "prefetch": [
                        {
                            "query": query_dense,
                            "using": "dense",
                            "limit": 20,
                            "filter": query_filter,
                        },
                        {
                            "query": query_sparse,
                            "using": "sparse",
                            "limit": 20,
                            "filter": query_filter,
                        },
                    ],
                    "query": models.FusionQuery(fusion=models.Fusion.RRF),
                    "limit": 15,
                }
            ],
            query=query_colbert,
            using="colbert",
            limit=limit,
            query_filter=query_filter,
        )

        if not results.points:
            return SearchResponse(query=query, results=[])

        max_score = max(point.score for point in results.points)

        search_results = [
            SearchResult(
                score=point.score / max_score if max_score else point.score,
                text=point.payload.get("text", ""),
                metadata=point.payload.get("metadata", {}),
            )
            for point in results.points
        ]

        return SearchResponse(query=query, results=search_results)

    def _build_qdrant_filter(
        self,
        filter: dict[str, Any] | None,
    ) -> models.Filter | None:
        if not filter:
            return None

        must_conditions = []

        for key, value in filter.items():
            must_conditions.append(
                models.FieldCondition(
                    key=f"metadata.{key}",
                    match=models.MatchValue(value=value),
                )
            )

        return models.Filter(must=must_conditions)
