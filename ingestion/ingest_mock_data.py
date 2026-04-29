import uuid
from pathlib import Path

from qdrant_client import QdrantClient, models

from api.config.settings import settings
from api.services.embedding_service import EmbeddingService
from ingestion.loaders.email_loader import load_emails
from ingestion.loaders.whatsapp_loader import load_whatsapp_messages


BASE_DIR = Path(__file__).resolve().parent

WHATSAPP_FILE = BASE_DIR / "mock_data" / "whatsapp_messages.json"
EMAILS_FILE = BASE_DIR / "mock_data" / "emails.json"


def build_deterministic_point_id(metadata: dict) -> str:
    """
    Creates a stable UUID based on the document_id.

    This prevents duplicate points when the same mock data is ingested multiple times.
    """
    document_id = metadata.get("document_id")

    if not document_id:
        raise ValueError("Document metadata must contain a document_id.")

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, document_id))


def build_point(document: dict, embedding_service: EmbeddingService) -> models.PointStruct:
    text = document["text"]
    metadata = document["metadata"]

    dense_embedding, sparse_embedding, colbert_embedding = (
        embedding_service.embed_document(text)
    )

    return models.PointStruct(
        id=build_deterministic_point_id(metadata),
        vector={
            "dense": dense_embedding,
            "sparse": sparse_embedding,
            "colbert": colbert_embedding,
        },
        payload={
            "text": text,
            "metadata": metadata,
        },
    )


def ingest_mock_data():
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    embedding_service = EmbeddingService()

    whatsapp_documents = load_whatsapp_messages(WHATSAPP_FILE)
    email_documents = load_emails(EMAILS_FILE)

    documents = whatsapp_documents + email_documents

    print(f"WhatsApp documents loaded: {len(whatsapp_documents)}")
    print(f"Email documents loaded: {len(email_documents)}")
    print(f"Total documents to ingest: {len(documents)}")

    points = []

    for index, document in enumerate(documents, start=1):
        metadata = document["metadata"]
        print(
            f"[{index}/{len(documents)}] Embedding "
            f"{metadata.get('source')} - {metadata.get('document_id')}"
        )

        point = build_point(document, embedding_service)
        points.append(point)

    qdrant.upload_points(
        collection_name=settings.collection_name,
        points=points,
        batch_size=5,
    )

    print(
        f"Successfully ingested {len(points)} documents "
        f"into collection '{settings.collection_name}'."
    )


if __name__ == "__main__":
    ingest_mock_data()
