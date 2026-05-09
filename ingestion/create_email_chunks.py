import re
import sys
from typing import Any

import psycopg
from psycopg.rows import dict_row

from api.config.settings import settings


CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def connect_postgres() -> psycopg.Connection:
    print("\nConnecting to PostgreSQL...")
    print(f"Host: {settings.postgres_host}")
    print(f"Port: {settings.postgres_port}")
    print(f"Database: {settings.postgres_db}")
    print(f"User: {settings.postgres_user}")

    conn = psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )

    print("PostgreSQL connected successfully.")
    return conn


def clean_html(html: str | None) -> str:
    if not html:
        return ""

    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&nbsp;", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_text(text: str | None) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def format_recipients(recipients: Any) -> str:
    if not recipients:
        return ""

    formatted = []

    for item in recipients:
        name = item.get("name") or ""
        email = item.get("email") or ""

        if name and email:
            formatted.append(f"{name} <{email}>")
        elif email:
            formatted.append(email)
        elif name:
            formatted.append(name)

    return ", ".join(formatted)


def build_email_document(email: dict[str, Any]) -> str:
    body_text = email.get("body_text") or ""

    if not body_text.strip():
        body_text = clean_html(email.get("body_html"))

    body_text = normalize_text(body_text)

    to_recipients = format_recipients(email.get("to_recipients"))
    cc_recipients = format_recipients(email.get("cc_recipients"))

    parts = [
        "Source: Email",
        f"Mailbox: {email.get('mailbox') or ''}",
        f"Gmail UID: {email.get('gmail_uid') or ''}",
        f"Subject: {email.get('subject') or ''}",
        f"From: {email.get('sender_name') or ''} <{email.get('sender_email') or ''}>",
        f"To: {to_recipients}",
        f"CC: {cc_recipients}",
        f"Date: {email.get('sent_at') or ''}",
        f"Has attachments: {email.get('has_attachments')}",
        "",
        "Email body:",
        body_text,
    ]

    return normalize_text("\n".join(parts))


def split_text_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    text = normalize_text(text)

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

        if start < 0:
            start = 0

    return chunks


def fetch_emails_to_chunk(conn: psycopg.Connection) -> list[dict[str, Any]]:
    sql = """
        SELECT
            id,
            mailbox,
            gmail_uid,
            document_id,
            subject,
            sender_name,
            sender_email,
            to_recipients,
            cc_recipients,
            sent_at,
            body_text,
            body_html,
            has_attachments,
            qdrant_status
        FROM email_messages
        WHERE qdrant_status IN ('pending', 'failed')
        ORDER BY created_at ASC;
    """

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(sql)
        rows = cur.fetchall()

    return list(rows)


def replace_chunks_for_email(
    conn: psycopg.Connection,
    email_message_id: str,
    chunks: list[str],
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM email_chunks
            WHERE email_message_id = %s;
            """,
            (email_message_id,),
        )

        for index, chunk_text in enumerate(chunks):
            cur.execute(
                """
                INSERT INTO email_chunks (
                    email_message_id,
                    chunk_index,
                    chunk_text,
                    qdrant_status
                )
                VALUES (%s, %s, %s, 'pending');
                """,
                (
                    email_message_id,
                    index,
                    chunk_text,
                ),
            )


def create_email_chunks() -> None:
    conn = connect_postgres()

    total_emails = 0
    total_chunks = 0
    total_failed = 0

    try:
        emails = fetch_emails_to_chunk(conn)

        print(f"\nEmails found for chunking: {len(emails)}")

        if not emails:
            print("No pending emails to chunk.")
            return

        for email in emails:
            total_emails += 1

            print("\n" + "-" * 80)
            print(f"Processing email UID: {email['gmail_uid']}")
            print(f"Subject: {email['subject']}")

            try:
                document_text = build_email_document(email)
                chunks = split_text_into_chunks(document_text)

                if not chunks:
                    print("No text found. Skipping email.")
                    continue

                replace_chunks_for_email(
                    conn=conn,
                    email_message_id=str(email["id"]),
                    chunks=chunks,
                )

                conn.commit()

                total_chunks += len(chunks)

                print(f"Chunks created: {len(chunks)}")

            except Exception as error:
                conn.rollback()
                total_failed += 1

                print(
                    f"Failed to create chunks for email UID "
                    f"{email['gmail_uid']}: {error}"
                )

        print("\n" + "=" * 80)
        print("Email chunking finished.")
        print(f"Total emails processed: {total_emails}")
        print(f"Total chunks created: {total_chunks}")
        print(f"Total failed: {total_failed}")
        print("=" * 80)

    finally:
        conn.close()
        print("\nDisconnected from PostgreSQL.")


if __name__ == "__main__":
    try:
        create_email_chunks()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
