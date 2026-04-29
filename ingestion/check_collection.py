from qdrant_client import QdrantClient

from api.config.settings import settings


def check_collection() -> None:
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    if not qdrant.collection_exists(settings.collection_name):
        print(f"Collection '{settings.collection_name}' does not exist.")
        return

    collection_info = qdrant.get_collection(
        collection_name=settings.collection_name,
    )

    print(f"Collection: {settings.collection_name}")
    print(f"Status: {collection_info.status}")
    print(f"Points count: {collection_info.points_count}")
    print(f"Segments count: {collection_info.segments_count}")

    print("\nVector configuration:")
    print(collection_info.config.params.vectors)

    print("\nSparse vector configuration:")
    print(collection_info.config.params.sparse_vectors)


if __name__ == "__main__":
    check_collection()
