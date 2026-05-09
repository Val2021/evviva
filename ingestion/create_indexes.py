from qdrant_client import QdrantClient, models

from api.config.settings import settings


def create_indexes():
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    keyword_fields = [
        "metadata.source",
        "metadata.channel",
        "metadata.document_id",
        "metadata.parent_document_id",

        # WhatsApp
        "metadata.conversation_id",
        "metadata.contact_name",
        "metadata.sender_name",

        # Email
        "metadata.sender",
        "metadata.sender_email",
        "metadata.mailbox",
        "metadata.subject",
        "metadata.date",
        "metadata.file_name",
    ]

    integer_fields = [
        "metadata.gmail_uid",
        "metadata.chunk_index",
    ]

    for field_name in keyword_fields:
        try:
            qdrant.create_payload_index(
                collection_name=settings.collection_name,
                field_name=field_name,
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            print(f"Index created for {field_name}")
        except Exception as error:
            message = str(error)

            if "already exists" in message.lower():
                print(f"Index already exists for {field_name}")
            else:
                print(f"Could not create index for {field_name}: {error}")
    for field_name in integer_fields:
        try:
            qdrant.create_payload_index(
                collection_name=settings.collection_name,
                field_name=field_name,
                field_schema=models.PayloadSchemaType.INTEGER,
            )
            print(f"Index created for {field_name}")
        except Exception as error:
            message = str(error)

            if "already exists" in message.lower():
                print(f"Index already exists for {field_name}")
            else:
                print(f"Could not create index for {field_name}: {error}")

if __name__ == "__main__":
    create_indexes()
