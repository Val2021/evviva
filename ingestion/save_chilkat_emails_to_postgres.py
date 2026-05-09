import hashlib
import json
import re
import sys
from email import policy
from email.parser import Parser
from email.utils import getaddresses
from typing import Any

import chilkat2
import psycopg
from psycopg.types.json import Jsonb

from api.config.settings import settings


def unlock_chilkat() -> None:
    if not settings.chilkat_license_key:
        raise ValueError("CHILKAT_LICENSE_KEY must be configured in .env")

    glob = chilkat2.Global()
    success = glob.UnlockBundle(settings.chilkat_license_key)

    if not success:
        raise RuntimeError(
            "Failed to unlock Chilkat.\n"
            f"{glob.LastErrorText}"
        )

    print("Chilkat unlocked successfully.")
    print(f"Chilkat status: {glob.UnlockStatus}")


def connect_imap() -> chilkat2.Imap:
    if not settings.imap_user or not settings.imap_password:
        raise ValueError("IMAP_USER and IMAP_PASSWORD must be configured in .env")

    imap = chilkat2.Imap()
    imap.Ssl = settings.imap_use_ssl
    imap.Port = settings.imap_port

    print("\nConnecting to IMAP server...")
    print(f"Host: {settings.imap_host}")
    print(f"Port: {settings.imap_port}")
    print(f"SSL: {settings.imap_use_ssl}")
    print(f"User: {settings.imap_user}")

    success = imap.Connect(settings.imap_host)

    if not success:
        raise RuntimeError(
            "Failed to connect to IMAP server.\n"
            f"{imap.LastErrorText}"
        )

    print("Connected successfully.")

    success = imap.Login(settings.imap_user, settings.imap_password)

    if not success:
        raise RuntimeError(
            "Failed to login to IMAP server.\n"
            f"{imap.LastErrorText}"
        )

    print("Login successful.")

    return imap


def select_mailbox(imap: chilkat2.Imap) -> None:
    print(f"\nSelecting mailbox: {settings.imap_mailbox}")

    success = imap.SelectMailbox(settings.imap_mailbox)

    if not success:
        raise RuntimeError(
            f"Failed to select mailbox '{settings.imap_mailbox}'.\n"
            f"{imap.LastErrorText}"
        )

    print("Mailbox selected successfully.")


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


def parse_addresses(raw_value: str | None) -> list[dict[str, str]]:
    if not raw_value:
        return []

    addresses = []

    for name, address in getaddresses([raw_value]):
        addresses.append(
            {
                "name": name or "",
                "email": address or "",
            }
        )

    return addresses


def clean_html(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_body(message) -> dict[str, str]:
    plain_body = ""
    html_body = ""

    if message.is_multipart():
        for part in message.walk():
            content_disposition = part.get_content_disposition()
            content_type = part.get_content_type()

            if content_disposition == "attachment":
                continue

            try:
                content = part.get_content()
            except Exception:
                continue

            if content_type == "text/plain" and not plain_body:
                plain_body = str(content).strip()

            if content_type == "text/html" and not html_body:
                html_body = str(content).strip()
    else:
        content_type = message.get_content_type()

        try:
            content = message.get_content()
        except Exception:
            content = ""

        if content_type == "text/plain":
            plain_body = str(content).strip()

        if content_type == "text/html":
            html_body = str(content).strip()

    readable_body = plain_body or clean_html(html_body)

    return {
        "plain_body": plain_body,
        "html_body": html_body,
        "readable_body": readable_body,
        "body_preview": readable_body[:800],
    }


def extract_attachments(message) -> list[dict[str, Any]]:
    attachments = []

    for part in message.walk():
        if part.get_content_disposition() != "attachment":
            continue

        filename = part.get_filename()
        content_type = part.get_content_type()

        payload = part.get_payload(decode=True)
        size_bytes = len(payload) if payload else 0

        attachments.append(
            {
                "file_name": filename,
                "content_type": content_type,
                "size_bytes": size_bytes,
            }
        )

    return attachments


def calculate_content_hash(parsed_email: dict[str, Any]) -> str:
    hash_payload = {
        "subject": parsed_email.get("subject"),
        "from": parsed_email.get("from"),
        "to": parsed_email.get("to"),
        "cc": parsed_email.get("cc"),
        "date": parsed_email.get("date"),
        "message_id": parsed_email.get("message_id"),
        "plain_body": parsed_email.get("plain_body"),
        "html_body": parsed_email.get("html_body"),
        "attachments": parsed_email.get("attachments"),
    }

    serialized = json.dumps(hash_payload, ensure_ascii=False, sort_keys=True)

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def parse_email_from_mime(uid: int, mime_source: str) -> dict[str, Any]:
    message = Parser(policy=policy.default).parsestr(mime_source)

    body_data = extract_body(message)
    attachments = extract_attachments(message)

    parsed_email = {
        "uid": uid,
        "document_id": f"gmail_imap_{uid}",
        "source": "gmail_imap",
        "mailbox": settings.imap_mailbox,
        "subject": str(message.get("subject", "") or ""),
        "from": parse_addresses(message.get("from")),
        "to": parse_addresses(message.get("to")),
        "cc": parse_addresses(message.get("cc")),
        "bcc": parse_addresses(message.get("bcc")),
        "date": str(message.get("date", "") or ""),
        "message_id": str(message.get("message-id", "") or ""),
        "reply_to": parse_addresses(message.get("reply-to")),
        "attachments": attachments,
        "has_attachments": len(attachments) > 0,
        "body_preview": body_data["body_preview"],
        "plain_body": body_data["plain_body"],
        "html_body": body_data["html_body"],
    }

    parsed_email["content_hash"] = calculate_content_hash(parsed_email)

    return parsed_email


def get_first_address(addresses: list[dict[str, str]]) -> dict[str, str]:
    if not addresses:
        return {"name": "", "email": ""}

    return addresses[0]


def upsert_email_message(
    conn: psycopg.Connection,
    parsed_email: dict[str, Any],
) -> str:
    sender = get_first_address(parsed_email["from"])

    raw_payload = {
        "uid": parsed_email["uid"],
        "document_id": parsed_email["document_id"],
        "source": parsed_email["source"],
        "mailbox": parsed_email["mailbox"],
        "subject": parsed_email["subject"],
        "from": parsed_email["from"],
        "to": parsed_email["to"],
        "cc": parsed_email["cc"],
        "bcc": parsed_email["bcc"],
        "date": parsed_email["date"],
        "message_id": parsed_email["message_id"],
        "reply_to": parsed_email["reply_to"],
        "attachments": parsed_email["attachments"],
        "has_attachments": parsed_email["has_attachments"],
    }

    sql = """
        INSERT INTO email_messages (
            source,
            mailbox,
            gmail_uid,
            document_id,
            subject,
            sender_name,
            sender_email,
            to_recipients,
            cc_recipients,
            bcc_recipients,
            reply_to,
            sent_at,
            message_id,
            body_text,
            body_html,
            body_preview,
            has_attachments,
            attachments_json,
            raw_payload,
            content_hash,
            qdrant_status
        )
        VALUES (
            %(source)s,
            %(mailbox)s,
            %(gmail_uid)s,
            %(document_id)s,
            %(subject)s,
            %(sender_name)s,
            %(sender_email)s,
            %(to_recipients)s,
            %(cc_recipients)s,
            %(bcc_recipients)s,
            %(reply_to)s,
            %(sent_at)s,
            %(message_id)s,
            %(body_text)s,
            %(body_html)s,
            %(body_preview)s,
            %(has_attachments)s,
            %(attachments_json)s,
            %(raw_payload)s,
            %(content_hash)s,
            'pending'
        )
        ON CONFLICT (mailbox, gmail_uid)
        DO UPDATE SET
            source = EXCLUDED.source,
            document_id = EXCLUDED.document_id,
            subject = EXCLUDED.subject,
            sender_name = EXCLUDED.sender_name,
            sender_email = EXCLUDED.sender_email,
            to_recipients = EXCLUDED.to_recipients,
            cc_recipients = EXCLUDED.cc_recipients,
            bcc_recipients = EXCLUDED.bcc_recipients,
            reply_to = EXCLUDED.reply_to,
            sent_at = EXCLUDED.sent_at,
            message_id = EXCLUDED.message_id,
            body_text = EXCLUDED.body_text,
            body_html = EXCLUDED.body_html,
            body_preview = EXCLUDED.body_preview,
            has_attachments = EXCLUDED.has_attachments,
            attachments_json = EXCLUDED.attachments_json,
            raw_payload = EXCLUDED.raw_payload,
            qdrant_status =
                CASE
                    WHEN email_messages.content_hash IS DISTINCT FROM EXCLUDED.content_hash
                    THEN 'pending'
                    ELSE email_messages.qdrant_status
                END,
            qdrant_indexed_at =
                CASE
                    WHEN email_messages.content_hash IS DISTINCT FROM EXCLUDED.content_hash
                    THEN NULL
                    ELSE email_messages.qdrant_indexed_at
                END,
            qdrant_error =
                CASE
                    WHEN email_messages.content_hash IS DISTINCT FROM EXCLUDED.content_hash
                    THEN NULL
                    ELSE email_messages.qdrant_error
                END,
            content_hash = EXCLUDED.content_hash,
            updated_at = NOW()
        RETURNING id;
    """

    params = {
        "source": parsed_email["source"],
        "mailbox": parsed_email["mailbox"],
        "gmail_uid": parsed_email["uid"],
        "document_id": parsed_email["document_id"],
        "subject": parsed_email["subject"],
        "sender_name": sender["name"],
        "sender_email": sender["email"],
        "to_recipients": Jsonb(parsed_email["to"]),
        "cc_recipients": Jsonb(parsed_email["cc"]),
        "bcc_recipients": Jsonb(parsed_email["bcc"]),
        "reply_to": Jsonb(parsed_email["reply_to"]),
        "sent_at": parsed_email["date"],
        "message_id": parsed_email["message_id"],
        "body_text": parsed_email["plain_body"],
        "body_html": parsed_email["html_body"],
        "body_preview": parsed_email["body_preview"],
        "has_attachments": parsed_email["has_attachments"],
        "attachments_json": Jsonb(parsed_email["attachments"]),
        "raw_payload": Jsonb(raw_payload),
        "content_hash": parsed_email["content_hash"],
    }

    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()

    if row is None:
        raise RuntimeError("Failed to upsert email message.")

    return str(row[0])


def replace_email_attachments(
    conn: psycopg.Connection,
    email_message_id: str,
    attachments: list[dict[str, Any]],
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM email_attachments WHERE email_message_id = %s;",
            (email_message_id,),
        )

        for attachment in attachments:
            cur.execute(
                """
                INSERT INTO email_attachments (
                    email_message_id,
                    file_name,
                    content_type,
                    size_bytes
                )
                VALUES (%s, %s, %s, %s);
                """,
                (
                    email_message_id,
                    attachment.get("file_name"),
                    attachment.get("content_type"),
                    attachment.get("size_bytes"),
                ),
            )


def save_emails_to_postgres() -> None:
    unlock_chilkat()

    imap = connect_imap()
    conn = connect_postgres()

    total_saved = 0
    total_failed = 0

    try:
        select_mailbox(imap)

        search_criteria = settings.imap_search_criteria
        max_emails = settings.imap_max_emails

        print(f"\nSearching emails with criteria: {search_criteria}")

        message_set = imap.Search(search_criteria, True)

        if message_set is None:
            raise RuntimeError(
                "Failed to search emails.\n"
                f"{imap.LastErrorText}"
            )

        total_found = message_set.Count
        print(f"Total emails found in mailbox: {total_found}")

        if total_found == 0:
            print("No emails found.")
            return

        total_to_process = min(total_found, max_emails)
        print(f"Emails to save: {total_to_process}")

        for index in range(total_found - 1, max(total_found - total_to_process - 1, -1), -1):
            uid = message_set.GetId(index)

            print("\n" + "-" * 80)
            print(f"Fetching email UID: {uid}")

            try:
                email_obj = imap.FetchSingle(uid, True)

                if email_obj is None:
                    raise RuntimeError(
                        f"Could not fetch email UID {uid}.\n"
                        f"{imap.LastErrorText}"
                    )

                mime_source = email_obj.GetMime()

                parsed_email = parse_email_from_mime(
                    uid=uid,
                    mime_source=mime_source,
                )

                email_message_id = upsert_email_message(
                    conn=conn,
                    parsed_email=parsed_email,
                )

                replace_email_attachments(
                    conn=conn,
                    email_message_id=email_message_id,
                    attachments=parsed_email["attachments"],
                )

                conn.commit()
                total_saved += 1

                print(f"Saved email UID: {uid}")
                print(f"Database ID: {email_message_id}")
                print(f"Subject: {parsed_email['subject']}")
                print(f"From: {parsed_email['from']}")
                print(f"Has attachments: {parsed_email['has_attachments']}")

            except Exception as error:
                conn.rollback()
                total_failed += 1
                print(f"Failed to save email UID {uid}: {error}")

        print("\n" + "=" * 80)
        print("Email import finished.")
        print(f"Total found: {total_found}")
        print(f"Total processed: {total_to_process}")
        print(f"Total saved: {total_saved}")
        print(f"Total failed: {total_failed}")
        print("=" * 80)

    finally:
        imap.Disconnect()
        conn.close()

        print("\nDisconnected from IMAP server.")
        print("Disconnected from PostgreSQL.")


if __name__ == "__main__":
    try:
        save_emails_to_postgres()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
