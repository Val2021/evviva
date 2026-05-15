from ingestion.check_collection import check_collection
from ingestion.create_email_chunks import create_email_chunks
from ingestion.ingest_data import ingest_data
from ingestion.save_chilkat_emails_to_postgres import save_emails_to_postgres


def bootstrap() -> None:
    print("=" * 80)
    print("Starting Evviva incremental email ingestion bootstrap")
    print("=" * 80)

    print("\n[1/4] Fetching Gmail emails with Chilkat and saving to PostgreSQL...")
    save_emails_to_postgres()

    print("\n[2/4] Creating email chunks from PostgreSQL messages...")
    create_email_chunks()

    print("\n[3/4] Ingesting pending email chunks and WhatsApp mock data into Qdrant...")
    ingest_data()

    print("\n[4/4] Checking Qdrant collection status...")
    check_collection()

    print("\n" + "=" * 80)
    print("Evviva incremental email ingestion bootstrap completed successfully")
    print("=" * 80)


if __name__ == "__main__":
    bootstrap()

##com docker rodando emm background
##docker compose exec api uv run python -m ingestion.bootstrap
