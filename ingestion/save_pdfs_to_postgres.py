import hashlib
import sys
from pathlib import Path
from typing import Any

import psycopg
from docling.document_converter import DocumentConverter
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from api.config.settings import settings


PDF_INPUT_DIR = Path("storage/documents")


def connect_postgres() -> psycopg.Connection:
    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def calculate_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def build_document_id(file_hash: str) -> str:
    return f"pdf_{file_hash[:16]}"


def infer_document_type(file_path: Path) -> str:
    file_name = file_path.name.lower()

    if "contrato" in file_name or "contract" in file_name:
        return "contract"

    if "proposta" in file_name or "proposal" in file_name:
        return "proposal"

    if "relatorio" in file_name or "report" in file_name:
        return "report"

    if "invoice" in file_name or "nota" in file_name:
        return "invoice"

    return "pdf_document"


def extract_total_pages(result: Any) -> int | None:
    document = getattr(result, "document", None)

    if document is None:
        return None

    pages = getattr(document, "pages", None)

    if pages is None:
        return None

    try:
        return len(pages)
    except Exception:
        return None


def convert_pdf_to_markdown(
    converter: DocumentConverter,
    file_path: Path,
) -> tuple[str, dict[str, Any]]:
    print(f"Converting PDF with Docling: {file_path}")

    result = converter.convert(str(file_path))

    markdown = result.document.export_to_markdown()

    raw_metadata = {
        "converter": "docling",
        "file_name": file_path.name,
        "file_path": str(file_path),
        "total_pages": extract_total_pages(result),
    }

    return markdown, raw_metadata


def upsert_pdf_document(
    conn: psycopg.Connection,
    file_path: Path,
    file_hash: str,
    markdown: str,
    raw_metadata: dict[str, Any],
) -> str:
    document_id = build_document_id(file_hash)
    document_type = infer_document_type(file_path)
    total_pages = raw_metadata.get("total_pages")

    sql = """
        INSERT INTO pdf_documents (
            source,
            channel,
            document_id,
            file_name,
            file_path,
            file_hash,
            document_type,
            title,
            total_pages,
            extracted_markdown,
            raw_metadata,
            qdrant_status
        )
        VALUES (
            'pdf_upload',
            'document',
            %(document_id)s,
            %(file_name)s,
            %(file_path)s,
            %(file_hash)s,
            %(document_type)s,
            %(title)s,
            %(total_pages)s,
            %(extracted_markdown)s,
            %(raw_metadata)s,
            'pending'
        )
        ON CONFLICT (file_hash)
        DO UPDATE SET
            file_name = EXCLUDED.file_name,
            file_path = EXCLUDED.file_path,
            document_type = EXCLUDED.document_type,
            title = EXCLUDED.title,
            total_pages = EXCLUDED.total_pages,
            extracted_markdown = EXCLUDED.extracted_markdown,
            raw_metadata = EXCLUDED.raw_metadata,
            updated_at = NOW()
        RETURNING id;
    """

    params = {
        "document_id": document_id,
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_hash": file_hash,
        "document_type": document_type,
        "title": file_path.stem,
        "total_pages": total_pages,
        "extracted_markdown": markdown,
        "raw_metadata": Jsonb(raw_metadata),
    }

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()

    if row is None:
        raise RuntimeError(f"Failed to save PDF document: {file_path}")

    return str(row["id"])


def find_pdf_files(input_dir: Path) -> list[Path]:
    input_dir.mkdir(parents=True, exist_ok=True)

    return sorted(input_dir.rglob("*.pdf"))


def save_pdfs_to_postgres() -> None:
    pdf_files = find_pdf_files(PDF_INPUT_DIR)

    print("=" * 80)
    print("Starting PDF import to PostgreSQL")
    print("=" * 80)
    print(f"PDF input directory: {PDF_INPUT_DIR}")
    print(f"PDF files found: {len(pdf_files)}")

    if not pdf_files:
        print("\nNo PDF files found.")
        print(f"Place PDF files inside: {PDF_INPUT_DIR}")
        return

    converter = DocumentConverter()
    conn = connect_postgres()

    total_saved = 0
    total_failed = 0

    try:
        for index, file_path in enumerate(pdf_files, start=1):
            print("\n" + "-" * 80)
            print(f"[{index}/{len(pdf_files)}] Processing: {file_path.name}")

            try:
                file_hash = calculate_file_hash(file_path)
                markdown, raw_metadata = convert_pdf_to_markdown(
                    converter=converter,
                    file_path=file_path,
                )

                if not markdown.strip():
                    raise RuntimeError("Docling returned empty Markdown.")

                pdf_document_id = upsert_pdf_document(
                    conn=conn,
                    file_path=file_path,
                    file_hash=file_hash,
                    markdown=markdown,
                    raw_metadata=raw_metadata,
                )

                conn.commit()
                total_saved += 1

                print(f"Saved PDF document ID: {pdf_document_id}")
                print(f"Document ID: {build_document_id(file_hash)}")
                print(f"File hash: {file_hash}")
                print(f"Markdown length: {len(markdown)} characters")

            except Exception as error:
                conn.rollback()
                total_failed += 1
                print(f"Failed to process PDF '{file_path.name}': {error}")

        print("\n" + "=" * 80)
        print("PDF import finished.")
        print(f"Total PDF files found: {len(pdf_files)}")
        print(f"Total saved/updated: {total_saved}")
        print(f"Total failed: {total_failed}")
        print("=" * 80)

    finally:
        conn.close()
        print("\nDisconnected from PostgreSQL.")


if __name__ == "__main__":
    try:
        save_pdfs_to_postgres()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
