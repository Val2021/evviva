import json
from pathlib import Path
from typing import Any


def load_whatsapp_messages(file_path: str | Path) -> list[dict[str, Any]]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        messages = json.load(file)

    return [normalize_whatsapp_message(message) for message in messages]


def normalize_whatsapp_message(message: dict[str, Any]) -> dict[str, Any]:
    text = f"""## WhatsApp Message

**Document ID:** {message.get("document_id")}
**Message ID:** {message.get("message_id")}
**Conversation ID:** {message.get("conversation_id")}
**Channel:** {message.get("channel")}
**Direction:** {message.get("direction")}

**Business:** {message.get("business_display_name")} ({message.get("business_phone_number")})
**Contact:** {message.get("contact_name")} ({message.get("contact_phone")})

**From:** {message.get("sender_name")} ({message.get("sender_phone")}) - {message.get("sender_type")}
**To:** {message.get("receiver_name")} ({message.get("receiver_phone")}) - {message.get("receiver_type")}

**Timestamp:** {message.get("timestamp")}
**Message Type:** {message.get("message_type")}

### Message

{message.get("text")}
"""

    metadata = {
        "source": message.get("source"),
        "channel": message.get("channel"),
        "document_id": message.get("document_id"),
        "message_id": message.get("message_id"),
        "conversation_id": message.get("conversation_id"),
        "direction": message.get("direction"),
        "business_phone_number": message.get("business_phone_number"),
        "business_display_name": message.get("business_display_name"),
        "contact_name": message.get("contact_name"),
        "contact_phone": message.get("contact_phone"),
        "sender_type": message.get("sender_type"),
        "sender_name": message.get("sender_name"),
        "sender_phone": message.get("sender_phone"),
        "receiver_type": message.get("receiver_type"),
        "receiver_name": message.get("receiver_name"),
        "receiver_phone": message.get("receiver_phone"),
        "timestamp": message.get("timestamp"),
        "message_type": message.get("message_type"),
    }

    return {
        "text": text,
        "metadata": metadata,
    }
