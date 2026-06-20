import sys
from typing import Any

import psycopg
from psycopg.rows import dict_row

from api.config.settings import settings
from ingestion.utils.semantic_chunker import SemanticChunker


SECTION_TITLE_DEFAULT = "PDF content"


def connect_postgres() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def fetch_pdf_documents_to_chunk(conn: psycopg.Connection) -> list[dict[str, Any]]:
    sql = """
        SELECT
            id,
            document_id,
            file_name,
            document_type,
            title,
            total_pages,
            extracted_markdown,
            qdrant_status
        FROM pdf_documents
        WHERE qdrant_status IN ('pending', 'failed')
        ORDER BY created_at ASC;
    """

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        return list(cur.fetchall())


def build_pdf_chunk_text(
    pdf_document: dict[str, Any],
    chunk_text: str,
    chunk_index: int,
) -> str:
    file_name = pdf_document.get("file_name") or ""
    document_type = pdf_document.get("document_type") or "pdf_document"
    title = pdf_document.get("title") or file_name
    total_pages = pdf_document.get("total_pages")

    parts = [
        "## PDF Document",
        "",
        f"**File name:** {file_name}",
        f"**Title:** {title}",
        f"**Document type:** {document_type}",
        f"**Total pages:** {total_pages or ''}",
        f"**Section:** {SECTION_TITLE_DEFAULT}",
        f"**Chunk index:** {chunk_index}",
        "",
        "### Content",
        "",
        chunk_text.strip(),
    ]

    return "\n".join(parts).strip()


def replace_chunks_for_pdf_document(
    conn: psycopg.Connection,
    pdf_document: dict[str, Any],
    chunks: list[str],
) -> int:
    pdf_document_id = pdf_document["id"]

    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM pdf_chunks
            WHERE pdf_document_id = %s;
            """,
            (pdf_document_id,),
        )

        for index, chunk in enumerate(chunks):
            formatted_chunk_text = build_pdf_chunk_text(
                pdf_document=pdf_document,
                chunk_text=chunk,
                chunk_index=index,
            )

            cur.execute(
                """
                INSERT INTO pdf_chunks (
                    pdf_document_id,
                    chunk_index,
                    chunk_text,
                    page_start,
                    page_end,
                    section_title,
                    qdrant_status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    NULL,
                    NULL,
                    %s,
                    'pending'
                );
                """,
                (
                    pdf_document_id,
                    index,
                    formatted_chunk_text,
                    SECTION_TITLE_DEFAULT,
                ),
            )

        cur.execute(
            """
            UPDATE pdf_documents
            SET
                qdrant_status = 'pending',
                qdrant_error = NULL,
                updated_at = NOW()
            WHERE id = %s;
            """,
            (pdf_document_id,),
        )

    return len(chunks)


def create_pdf_chunks() -> None:
    print("=" * 80)
    print("Starting PDF chunk creation")
    print("=" * 80)

    conn = connect_postgres()

    total_documents = 0
    total_chunks = 0
    total_failed = 0

    try:
        pdf_documents = fetch_pdf_documents_to_chunk(conn)

        print(f"PDF documents found for chunking: {len(pdf_documents)}")

        if not pdf_documents:
            print("No pending PDF documents to chunk.")
            return

        chunker = SemanticChunker(
            model_name=settings.dense_model,
            max_tokens=300,
        )

        for pdf_document in pdf_documents:
            total_documents += 1

            print("\n" + "-" * 80)
            print(f"Processing PDF: {pdf_document['file_name']}")
            print(f"Document ID: {pdf_document['document_id']}")

            try:
                markdown = pdf_document.get("extracted_markdown") or ""

                if not markdown.strip():
                    raise RuntimeError("PDF document has empty extracted_markdown.")

                chunks = chunker.create_chunks(markdown)

                if not chunks:
                    raise RuntimeError("SemanticChunker returned no chunks.")

                chunks_created = replace_chunks_for_pdf_document(
                    conn=conn,
                    pdf_document=pdf_document,
                    chunks=chunks,
                )

                conn.commit()

                total_chunks += chunks_created

                print(f"Chunks created: {chunks_created}")

            except Exception as error:
                conn.rollback()
                total_failed += 1

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE pdf_documents
                        SET
                            qdrant_status = 'failed',
                            qdrant_error = %s,
                            updated_at = NOW()
                        WHERE id = %s;
                        """,
                        (
                            str(error),
                            pdf_document["id"],
                        ),
                    )
                    conn.commit()

                print(f"Failed to create chunks for PDF '{pdf_document['file_name']}': {error}")

        print("\n" + "=" * 80)
        print("PDF chunk creation finished.")
        print(f"Total PDF documents processed: {total_documents}")
        print(f"Total chunks created: {total_chunks}")
        print(f"Total failed: {total_failed}")
        print("=" * 80)

    finally:
        conn.close()
        print("\nDisconnected from PostgreSQL.")


if __name__ == "__main__":
    try:
        create_pdf_chunks()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
