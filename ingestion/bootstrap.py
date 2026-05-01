from ingestion.check_collection import check_collection
from ingestion.create_indexes import create_indexes
from ingestion.ingest_mock_data import ingest_mock_data
from ingestion.reset_collection import reset_collection


def bootstrap() -> None:
    print("=" * 80)
    print("Starting Evviva ingestion bootstrap")
    print("=" * 80)

    print("\n[1/4] Resetting Qdrant collection...")
    reset_collection()

    print("\n[2/4] Creating payload indexes...")
    create_indexes()

    print("\n[3/4] Ingesting mock WhatsApp and email data...")
    ingest_mock_data()

    print("\n[4/4] Checking collection status...")
    check_collection()

    print("\n" + "=" * 80)
    print("Evviva ingestion bootstrap completed successfully")
    print("=" * 80)


if __name__ == "__main__":
    bootstrap()
