import sys

import psycopg

from api.config.settings import settings


def connect_postgres() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def create_pdf_tables() -> None:
    conn = connect_postgres()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE EXTENSION IF NOT EXISTS pgcrypto;

                CREATE TABLE IF NOT EXISTS pdf_documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                    source TEXT NOT NULL DEFAULT 'pdf_upload',
                    channel TEXT NOT NULL DEFAULT 'document',

                    document_id TEXT NOT NULL UNIQUE,

                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,

                    document_type TEXT,
                    title TEXT,

                    total_pages INTEGER,

                    extracted_markdown TEXT,
                    raw_metadata JSONB DEFAULT '{}'::jsonb,

                    qdrant_status TEXT NOT NULL DEFAULT 'pending',
                    qdrant_indexed_at TIMESTAMP NULL,
                    qdrant_error TEXT NULL,

                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS pdf_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

                    pdf_document_id UUID NOT NULL REFERENCES pdf_documents(id) ON DELETE CASCADE,

                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,

                    page_start INTEGER,
                    page_end INTEGER,
                    section_title TEXT,

                    qdrant_point_id TEXT,
                    qdrant_status TEXT NOT NULL DEFAULT 'pending',
                    qdrant_indexed_at TIMESTAMP NULL,
                    qdrant_error TEXT NULL,

                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

                    CONSTRAINT uq_pdf_chunks_document_index UNIQUE (pdf_document_id, chunk_index)
                );

                CREATE INDEX IF NOT EXISTS idx_pdf_documents_file_hash
                    ON pdf_documents(file_hash);

                CREATE INDEX IF NOT EXISTS idx_pdf_documents_document_id
                    ON pdf_documents(document_id);

                CREATE INDEX IF NOT EXISTS idx_pdf_chunks_status
                    ON pdf_chunks(qdrant_status);

                CREATE INDEX IF NOT EXISTS idx_pdf_chunks_document
                    ON pdf_chunks(pdf_document_id);
                """
            )

        conn.commit()

        print("PDF tables created successfully.")
        print("Tables:")
        print("- pdf_documents")
        print("- pdf_chunks")

    finally:
        conn.close()


if __name__ == "__main__":
    try:
        create_pdf_tables()
    except Exception as error:
        print(f"ERROR: {error}")
        sys.exit(1)
