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


def load_pdf_chunks_from_postgres() -> list[dict[str, Any]]:
    conn = connect_postgres()

    try:
        sql = """
            SELECT
                pc.id AS pdf_chunk_id,
                pc.chunk_index,
                pc.chunk_text,
                pc.page_start,
                pc.page_end,
                pc.section_title,

                pd.id AS pdf_document_id,
                pd.document_id AS parent_document_id,
                pd.file_name,
                pd.file_path,
                pd.file_hash,
                pd.document_type,
                pd.title,
                pd.total_pages
            FROM pdf_chunks pc
            JOIN pdf_documents pd
                ON pd.id = pc.pdf_document_id
            WHERE pc.qdrant_status IN ('pending', 'failed')
            ORDER BY pd.created_at ASC, pc.chunk_index ASC;
        """

        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        return [normalize_pdf_chunk(row) for row in rows]

    finally:
        conn.close()


def normalize_pdf_chunk(row: dict[str, Any]) -> dict[str, Any]:
    parent_document_id = row["parent_document_id"]
    chunk_index = row["chunk_index"]

    chunk_document_id = f"{parent_document_id}_chunk_{chunk_index}"

    metadata = {
        "source": "pdf_upload",
        "channel": "document",

        "document_id": chunk_document_id,
        "parent_document_id": parent_document_id,

        "pdf_document_id": str(row["pdf_document_id"]),
        "pdf_chunk_id": str(row["pdf_chunk_id"]),

        "file_name": row["file_name"],
        "file_path": row["file_path"],
        "file_hash": row["file_hash"],

        "document_type": row["document_type"],
        "title": row["title"],
        "total_pages": row["total_pages"],

        "chunk_index": chunk_index,
        "page_start": row["page_start"],
        "page_end": row["page_end"],
        "section_title": row["section_title"],
    }

    return {
        "text": row["chunk_text"],
        "metadata": metadata,
    }
