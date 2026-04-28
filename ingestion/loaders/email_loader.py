import json
from pathlib import Path
from typing import Any


def load_emails(file_path: str | Path) -> list[dict[str, Any]]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        emails = json.load(file)

    return [normalize_email(email) for email in emails]


def normalize_email(email: dict[str, Any]) -> dict[str, Any]:
    cc_text = format_recipients(email.get("cc", []))
    bcc_text = format_recipients(email.get("bcc", []))
    attachments_text = format_attachments(email.get("attachments", []))

    text = f"""## Email Message

**Document ID:** {email.get("document_id")}
**Email ID:** {email.get("email_id")}
**Thread ID:** {email.get("thread_id")}
**Channel:** {email.get("channel")}
**Direction:** {email.get("direction")}

**Contact:** {email.get("contact_name")} ({email.get("contact_email")})

**From:** {email.get("sender_name")} ({email.get("sender_email")}) - {email.get("sender_type")}
**To:** {email.get("receiver_name")} ({email.get("receiver_email")}) - {email.get("receiver_type")}
**CC:** {cc_text}
**BCC:** {bcc_text}

**Timestamp:** {email.get("timestamp")}
**Subject:** {email.get("subject")}

### Body

{email.get("body")}

### Attachments

{attachments_text}
"""

    metadata = {
        "source": email.get("source"),
        "channel": email.get("channel"),
        "document_id": email.get("document_id"),
        "email_id": email.get("email_id"),
        "thread_id": email.get("thread_id"),
        "direction": email.get("direction"),
        "contact_name": email.get("contact_name"),
        "contact_email": email.get("contact_email"),
        "sender_type": email.get("sender_type"),
        "sender_name": email.get("sender_name"),
        "sender_email": email.get("sender_email"),
        "receiver_type": email.get("receiver_type"),
        "receiver_name": email.get("receiver_name"),
        "receiver_email": email.get("receiver_email"),
        "timestamp": email.get("timestamp"),
        "subject": email.get("subject"),
        "cc": email.get("cc", []),
        "bcc": email.get("bcc", []),
        "attachments": email.get("attachments", []),
    }

    return {
        "text": text,
        "metadata": metadata,
    }


def format_recipients(recipients: list[dict[str, Any]]) -> str:
    if not recipients:
        return "None"

    return "; ".join(
        f"{recipient.get('name')} <{recipient.get('email')}> ({recipient.get('role')})"
        for recipient in recipients
    )


def format_attachments(attachments: list[dict[str, Any]]) -> str:
    if not attachments:
        return "No attachments"

    return "\n".join(
        f"- {attachment.get('file_name')} ({attachment.get('file_type')}): {attachment.get('description')}"
        for attachment in attachments
    )
