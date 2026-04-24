from qdrant_client import QdrantClient, models

from api.config.settings import settings


def create_collection():
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    if qdrant.collection_exists(settings.collection_name):
        print(f"Collection '{settings.collection_name}' already exists.")
        return

    qdrant.create_collection(
        collection_name=settings.collection_name,
        vectors_config={
            "dense": models.VectorParams(
                size=384,
                distance=models.Distance.COSINE,
            ),
            "colbert": models.VectorParams(
                size=128,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                ),
            ),
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(),
        },
    )

    print(f"Collection '{settings.collection_name}' created successfully.")


if __name__ == "__main__":
    create_collection()
