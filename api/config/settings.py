from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    collection_name: str = "evviva_documents"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    dense_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    sparse_model: str = "Qdrant/bm25"
    colbert_model: str = "colbert-ir/colbertv2.0"

    imap_enabled: bool = False
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993
    imap_use_ssl: bool = True
    imap_user: str | None = None
    imap_password: str | None = None
    imap_mailbox: str = "INBOX"
    imap_search_criteria: str = 'X-GM-RAW "in:inbox category:primary"'
    imap_max_emails: int = 10
    imap_save_attachments: bool = True
    imap_attachments_dir: str = "storage/email_attachments"

    chilkat_license_key: str | None = None

    postgres_db: str = "evviva"
    postgres_user: str = "evviva"
    postgres_password: str = "evviva_password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432


settings = Settings()
