# RAG Chat Backend

A production-grade **Retrieval-Augmented Generation (RAG) chat backend** built with FastAPI, PostgreSQL + pgvector, and Google Gemini AI via PydanticAI.

---

## ✨ Features

- **Context Ingestion** — store text chunks with Google-generated embeddings into PostgreSQL
- **Vector Similarity Search** — cosine-distance search using pgvector's IVFFlat index
- **Multi-thread Chat** — independent conversation threads, each with its own full history
- **Streaming LLM Responses** — SSE streaming powered by PydanticAI + Gemini
- **RAG Pipeline** — every chat query retrieves the most relevant context before calling the LLM
- Production-grade structure: async SQLAlchemy, structured logging, error handling, health checks

---

## 🏗️ Architecture

```
app/
├── api/                      # Central router + health + cache routes
├── core/
│   ├── config/settings.py    # Pydantic settings (env-driven)
│   ├── db/                   # Async SQLAlchemy engine & session
│   ├── embeddings.py         # Shared Google embedding utility
│   ├── cache/                # Redis cache client & service
│   ├── exceptions/           # Custom exception classes & handlers
│   └── logging/              # Structured JSON logging middleware
└── modules/
    ├── context/              # Context ingestion module
    │   ├── context_model.py        # SQLAlchemy: ContextItem (Vector 768d)
    │   ├── context_schema.py       # Pydantic schemas
    │   ├── context_repository.py   # CRUD + cosine similarity search
    │   ├── context_routes.py       # REST API routes
    │   └── services/
    │       └── context_service.py  # Embed → store pipeline
    └── chat/                 # Chat module
        ├── chat_model.py           # SQLAlchemy: ChatThread + ChatMessage
        ├── chat_schema.py          # Pydantic schemas
        ├── chat_repository.py      # Thread & message CRUD
        ├── chat_routes.py          # REST API routes (SSE streaming)
        └── services/
            └── chat_service.py     # Full RAG pipeline + PydanticAI streaming
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ORM | SQLAlchemy (async) + asyncpg |
| Vector DB | PostgreSQL + pgvector |
| Embeddings | Google `text-embedding-004` via `google-genai` |
| LLM | Google Gemini (`gemini-2.0-flash`) via PydanticAI |
| Migrations | Alembic |
| Cache | Redis (optional) |

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+ with the **pgvector** extension available
- A Google AI API key ([Get one here](https://aistudio.google.com/))

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example and fill in your values:

```bash
cp .env.example .env
```

Key variables:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rag_db
GOOGLE_API_KEY=your-google-api-key-here
EMBEDDING_MODEL=text-embedding-004
LLM_MODEL=gemini-2.0-flash
TOP_K_CONTEXT=5
```

### 4. Enable pgvector extension

Connect to your PostgreSQL database and run **once**:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

> ⚠️ **You must do this before running migrations.**

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

API docs available at: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 📡 API Reference

### Context

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/context/` | Add a new context chunk (embeds + stores) |
| `GET` | `/api/v1/context/` | List all context items (paginated) |
| `GET` | `/api/v1/context/{id}` | Get a context item by ID |
| `DELETE` | `/api/v1/context/{id}` | Delete a context item |

**Add context example:**
```bash
curl -X POST http://localhost:8000/api/v1/context/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Return Policy",
    "content": "Our return policy allows returns within 30 days of purchase.",
    "metadata_": {"source": "faq"}
  }'
```

---

### Chat

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/threads` | Create a new chat thread |
| `GET` | `/api/v1/chat/threads` | List all threads (paginated) |
| `GET` | `/api/v1/chat/threads/{id}` | Get a thread by ID |
| `DELETE` | `/api/v1/chat/threads/{id}` | Delete thread + all messages |
| `GET` | `/api/v1/chat/threads/{id}/messages` | Get full message history |
| `POST` | `/api/v1/chat/threads/{id}/messages` | Send a message → SSE streaming response |

**Create thread:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/threads \
  -H "Content-Type: application/json" \
  -d '{"title": "Support Chat", "description": "Customer support conversation"}'
```

**Send a message (streaming):**
```bash
curl -X POST http://localhost:8000/api/v1/chat/threads/1/messages \
  -H "Content-Type: application/json" \
  -d '{"content": "What is your return policy?"}' \
  --no-buffer
```

**Streaming response format (SSE):**
```
data: {"delta": "Our return"}
data: {"delta": " policy allows"}
data: {"delta": " returns within 30 days."}
data: [DONE]
```

---

## 🧠 RAG Pipeline Flow

```
User Message
    │
    ├── 1. Persist user message to DB
    ├── 2. Generate query embedding (google text-embedding-004)
    ├── 3. Cosine similarity search → top-K context chunks
    ├── 4. Build prompt: system(context) + thread history + user message
    ├── 5. Stream Gemini response via PydanticAI
    │       └── Yield SSE chunks to client
    └── 6. Persist complete assistant message to DB
```

---

## 🗄️ Database Schema

### `context_items`
| Column | Type | Notes |
|---|---|---|
| `id` | `BIGINT` PK | |
| `title` | `VARCHAR(255)` | Short label |
| `content` | `TEXT` | Raw user-provided text |
| `embedding` | `VECTOR(768)` | Google embedding, IVFFlat indexed |
| `metadata` | `JSONB` | Optional tags / source info |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

### `chat_threads`
| Column | Type |
|---|---|
| `id` | `BIGINT` PK |
| `title` | `VARCHAR(255)` |
| `description` | `TEXT` |
| `created_at` | `TIMESTAMPTZ` |
| `updated_at` | `TIMESTAMPTZ` |

### `chat_messages`
| Column | Type | Notes |
|---|---|---|
| `id` | `BIGINT` PK | |
| `thread_id` | `BIGINT FK` | → `chat_threads.id`, cascade delete |
| `role` | `VARCHAR(16)` | `"user"` or `"assistant"` |
| `content` | `TEXT` | Message body |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

---

## 🧪 Running Tests

```bash
pytest --cov=app tests/
```

---

## 📋 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | — | Application name |
| `DEBUG` | `false` | Enable debug mode / auto-reload |
| `DATABASE_URL` | — | PostgreSQL connection string (`asyncpg`) |
| `GOOGLE_API_KEY` | — | Google AI API key |
| `EMBEDDING_MODEL` | `text-embedding-004` | Google embedding model |
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model for chat |
| `TOP_K_CONTEXT` | `5` | Context chunks retrieved per query |
| `REDIS_ENABLED` | `false` | Enable Redis caching |
| `REDIS_URL` | — | Redis connection string |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_DIR` | `logs` | Directory for log files |
