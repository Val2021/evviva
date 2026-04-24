from qdrant_client import QdrantClient, models

from api.config.settings import settings


def create_indexes():
    qdrant = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    fields_to_index = [
        "metadata.source",
        "metadata.document_id",
        "metadata.conversation_id",
        "metadata.sender",
        "metadata.date",
        "metadata.file_name",
    ]

    for field_name in fields_to_index:
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


if __name__ == "__main__":
    create_indexes()
