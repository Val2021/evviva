from typing import Any

import psycopg
from psycopg.rows import dict_row

from api.config.settings import settings


def connect_postgres() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def load_email_chunks_from_postgres() -> list[dict[str, Any]]:
    conn = connect_postgres()

    try:
        sql = """
            SELECT
                ec.id AS email_chunk_id,
                ec.chunk_index,
                ec.chunk_text,
                ec.qdrant_status,

                em.id AS email_message_id,
                em.gmail_uid,
                em.document_id AS parent_document_id,
                em.mailbox,
                em.subject,
                em.sender_name,
                em.sender_email,
                em.sent_at,
                em.message_id,
                em.has_attachments,
                em.attachments_json
            FROM email_chunks ec
            JOIN email_messages em
                ON em.id = ec.email_message_id
            WHERE ec.qdrant_status IN ('pending', 'failed')
            ORDER BY em.created_at ASC, ec.chunk_index ASC;
        """

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [normalize_email_chunk(row) for row in rows]

    finally:
        conn.close()


def normalize_email_chunk(row: dict[str, Any]) -> dict[str, Any]:
    gmail_uid = row["gmail_uid"]
    chunk_index = row["chunk_index"]

    chunk_document_id = f"gmail_imap_{gmail_uid}_chunk_{chunk_index}"

    metadata = {
        "source": "gmail_imap",
        "channel": "email",

        "document_id": chunk_document_id,
        "parent_document_id": row["parent_document_id"],

        "email_message_id": str(row["email_message_id"]),
        "email_chunk_id": str(row["email_chunk_id"]),
        "gmail_uid": gmail_uid,
        "chunk_index": chunk_index,

        "mailbox": row["mailbox"],
        "subject": row["subject"],

        "sender": row["sender_email"],
        "sender_name": row["sender_name"],
        "sender_email": row["sender_email"],

        "date": row["sent_at"],
        "message_id": row["message_id"],

        "has_attachments": row["has_attachments"],
        "attachments": row["attachments_json"] or [],
    }

    return {
        "text": row["chunk_text"],
        "metadata": metadata,
    }
