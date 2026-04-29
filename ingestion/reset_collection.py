from qdrant_client import QdrantClient, models

from api.config.settings import settings


def reset_collection() -> None:
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    if qdrant.collection_exists(settings.collection_name):
        print(f"Deleting collection '{settings.collection_name}'...")
        qdrant.delete_collection(collection_name=settings.collection_name)

    print(f"Creating collection '{settings.collection_name}'...")

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

    print(f"Collection '{settings.collection_name}' reset successfully.")


if __name__ == "__main__":
    reset_collection()
