# Evviva

MVP RAG backend for querying mocked WhatsApp and email data using FastAPI, Qdrant, FastEmbed, OpenAI, Docker, and uv.

## Stack

* Python 3.13
* FastAPI
* Qdrant
* FastEmbed
* OpenAI
* Docker
* uv

## Project structure

```text
evviva/
├── api/
│   ├── config/
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── main.py
├── ingestion/
│   ├── loaders/
│   ├── mock_data/
│   ├── create_collection.py
│   ├── create_indexes.py
│   ├── reset_collection.py
│   ├── ingest_mock_data.py
│   └── check_collection.py
├── storage/qdrant/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Environment variables

Create a `.env` file from `.env.example`:


## Run locally with Qdrant in Docker

Start Qdrant:

```bash
docker compose up -d qdrant
```

Start the FastAPI app locally:

```bash
uv run uvicorn api.main:app --reload
```

Useful URLs:

```text
API docs: http://localhost:8000/docs
Health:   http://localhost:8000
Qdrant:   http://localhost:6333/dashboard
```

## Ingestion commands

The ingestion pipeline prepares Qdrant, creates indexes, loads mock data, generates embeddings, and uploads documents to the vector database.

### Reset the collection

```bash
uv run python -m ingestion.reset_collection
```

Deletes and recreates the Qdrant collection. Use it when you want to rebuild the vector database from scratch. This removes all existing points.

### Create payload indexes

```bash
uv run python -m ingestion.create_indexes
```

Creates Qdrant indexes for metadata fields used in filters, such as source, document ID, conversation ID, sender, date, and file name.

### Ingest mock data

```bash
uv run python -m ingestion.ingest_mock_data
```

Loads mock WhatsApp and email JSON files, normalizes them into Markdown plus metadata, generates dense, sparse, and ColBERT embeddings, and uploads the points to Qdrant.

Current mock dataset:

```text
16 WhatsApp messages
16 email messages
32 total Qdrant points
```

### Check the collection

```bash
uv run python -m ingestion.check_collection
```

Shows the collection status, points count, segments count, and vector configuration. After the current mock ingestion, the expected result is around 32 points.

### Recommended ingestion flow

```bash
uv run python -m ingestion.reset_collection
uv run python -m ingestion.create_indexes
uv run python -m ingestion.ingest_mock_data
uv run python -m ingestion.check_collection
```

## Run with Docker Compose

To run the full stack with Docker Compose:

```bash
docker compose up --build
```

To run in the background:

```bash
docker compose up -d --build
```

To stop:

```bash
docker compose down
```

## Main API endpoints

### `POST /llm/test`

Tests only the OpenAI integration. It does not use Qdrant or retrieval.

### `POST /search`

Runs semantic search against Qdrant. It retrieves relevant documents using dense search, sparse search, and ColBERT reranking. It returns documents, scores, and metadata, but does not generate a final AI answer.

### `POST /rag`

Runs the full RAG flow. It uses the same retrieval logic from `/search` internally, then sends the retrieved context and the user question to OpenAI.

```text
/search = finds the relevant documents
/rag    = finds the relevant documents and answers based on them
```
