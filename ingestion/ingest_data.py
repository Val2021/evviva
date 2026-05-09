import uuid
from pathlib import Path

import psycopg
from qdrant_client import QdrantClient, models

from api.config.settings import settings
from api.services.embedding_service import EmbeddingService
from ingestion.loaders.postgres_email_loader import load_email_chunks_from_postgres
from ingestion.loaders.whatsapp_loader import load_whatsapp_messages


BASE_DIR = Path(__file__).resolve().parent
WHATSAPP_FILE = BASE_DIR / "mock_data" / "whatsapp_messages.json"


def build_deterministic_point_id(metadata: dict) -> str:
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


def connect_postgres() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def mark_email_chunks_as_indexed(documents: list[dict]) -> None:
    email_chunk_ids = [
        document["metadata"].get("email_chunk_id")
        for document in documents
        if document["metadata"].get("channel") == "email"
        and document["metadata"].get("email_chunk_id")
    ]

    if not email_chunk_ids:
        return

    conn = connect_postgres()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE email_chunks
                SET
                    qdrant_status = 'indexed',
                    qdrant_indexed_at = NOW(),
                    qdrant_error = NULL,
                    updated_at = NOW()
                WHERE id = ANY(%s::uuid[]);
                """,
                (email_chunk_ids,),
            )

            cur.execute(
                """
                UPDATE email_messages em
                SET
                    qdrant_status = 'indexed',
                    qdrant_indexed_at = NOW(),
                    qdrant_error = NULL,
                    updated_at = NOW()
                WHERE em.id IN (
                    SELECT DISTINCT ec.email_message_id
                    FROM email_chunks ec
                    WHERE ec.id = ANY(%s::uuid[])
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM email_chunks ec2
                    WHERE ec2.email_message_id = em.id
                    AND ec2.qdrant_status <> 'indexed'
                );
                """,
                (email_chunk_ids,),
            )

        conn.commit()

    finally:
        conn.close()


def ingest_data():
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    embedding_service = EmbeddingService()

    whatsapp_documents = load_whatsapp_messages(WHATSAPP_FILE)
    email_documents = load_email_chunks_from_postgres()

    documents = whatsapp_documents + email_documents

    print(f"WhatsApp documents loaded: {len(whatsapp_documents)}")
    print(f"Email chunks loaded from PostgreSQL: {len(email_documents)}")
    print(f"Total documents to ingest: {len(documents)}")

    if not documents:
        print("No documents to ingest.")
        return

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

    mark_email_chunks_as_indexed(email_documents)

    print(
        f"Successfully ingested {len(points)} documents "
        f"into collection '{settings.collection_name}'."
    )


if __name__ == "__main__":
    ingest_data()
