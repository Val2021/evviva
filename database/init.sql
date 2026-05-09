CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source TEXT NOT NULL DEFAULT 'gmail_imap',
    mailbox TEXT NOT NULL,

    gmail_uid BIGINT NOT NULL,
    document_id TEXT NOT NULL,

    subject TEXT,
    sender_name TEXT,
    sender_email TEXT,

    to_recipients JSONB DEFAULT '[]'::jsonb,
    cc_recipients JSONB DEFAULT '[]'::jsonb,
    bcc_recipients JSONB DEFAULT '[]'::jsonb,
    reply_to JSONB DEFAULT '[]'::jsonb,

    sent_at TEXT,
    message_id TEXT,

    body_text TEXT,
    body_html TEXT,
    body_preview TEXT,

    has_attachments BOOLEAN NOT NULL DEFAULT FALSE,
    attachments_json JSONB DEFAULT '[]'::jsonb,

    raw_payload JSONB,

    content_hash TEXT NOT NULL,

    qdrant_status TEXT NOT NULL DEFAULT 'pending',
    qdrant_indexed_at TIMESTAMP NULL,
    qdrant_error TEXT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_email_messages_mailbox_uid UNIQUE (mailbox, gmail_uid)
);

CREATE TABLE IF NOT EXISTS email_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email_message_id UUID NOT NULL REFERENCES email_messages(id) ON DELETE CASCADE,

    file_name TEXT,
    content_type TEXT,
    size_bytes BIGINT,

    storage_path TEXT,
    extracted_text TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email_message_id UUID NOT NULL REFERENCES email_messages(id) ON DELETE CASCADE,

    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,

    qdrant_point_id TEXT,
    qdrant_status TEXT NOT NULL DEFAULT 'pending',
    qdrant_indexed_at TIMESTAMP NULL,
    qdrant_error TEXT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_email_chunks_message_index UNIQUE (email_message_id, chunk_index)
);
