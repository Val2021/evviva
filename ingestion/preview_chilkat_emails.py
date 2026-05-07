import json
import re
import sys
from email import policy
from email.parser import Parser
from email.utils import getaddresses
from pathlib import Path
from typing import Any

import chilkat2

from api.config.settings import settings


OUTPUT_DIR = Path("storage/imap_debug")
OUTPUT_FILE = OUTPUT_DIR / "email_preview.json"


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


def parse_email_from_mime(uid: int, mime_source: str) -> dict[str, Any]:
    message = Parser(policy=policy.default).parsestr(mime_source)

    body_data = extract_body(message)
    attachments = extract_attachments(message)

    parsed_email = {
        "uid": uid,
        "document_id": f"gmail_imap_{uid}",
        "source": "email",
        "channel": "email",
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

    return parsed_email


def preview_emails() -> None:
    unlock_chilkat()

    imap = connect_imap()

    try:
        select_mailbox(imap)

        search_criteria = settings.imap_search_criteria
        max_emails = settings.imap_max_emails

        print(f"\nSearching emails with criteria: {search_criteria}")

        # True means: return UIDs instead of sequence numbers.
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
        print(f"Emails to preview: {total_to_process}")

        parsed_emails = []

        # We process the latest emails first.
        for index in range(total_found - 1, max(total_found - total_to_process - 1, -1), -1):
            uid = message_set.GetId(index)

            print("\n" + "-" * 80)
            print(f"Fetching email UID: {uid}")

            email_obj = imap.FetchSingle(uid, True)

            if email_obj is None:
                print(f"Could not fetch email UID {uid}.")
                print(imap.LastErrorText)
                continue

            mime_source = email_obj.GetMime()

            parsed_email = parse_email_from_mime(
                uid=uid,
                mime_source=mime_source,
            )

            parsed_emails.append(parsed_email)

            print(f"Subject: {parsed_email['subject']}")
            print(f"Date: {parsed_email['date']}")
            print(f"From: {parsed_email['from']}")
            print(f"To: {parsed_email['to']}")
            print(f"CC: {parsed_email['cc']}")
            print(f"Has attachments: {parsed_email['has_attachments']}")
            print(f"Attachments: {parsed_email['attachments']}")
            print("\nBody preview:")
            print(parsed_email["body_preview"] or "[empty body]")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(parsed_emails, file, ensure_ascii=False, indent=2)

        print("\n" + "=" * 80)
        print(f"Preview saved to: {OUTPUT_FILE}")
        print("=" * 80)

    finally:
        imap.Disconnect()
        print("\nDisconnected from IMAP server.")


if __name__ == "__main__":
    try:
        preview_emails()
    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
