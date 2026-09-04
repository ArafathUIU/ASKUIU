# ASKUIU - Intelligent University RAG System

ASKUIU is a state-of-the-art Retrieval-Augmented Generation (RAG) powered question-answering system engineered for the **United International University (UIU)** community. It enables students, faculty, and visitors to ask natural language questions and receive accurate, grounded answers backed by verified citations from official university data.

---

## Key Features & Improvements

- **Hybrid Retrieval Engine**:
  - **Dense Semantic Search**: FAISS vector indexing with `sentence-transformers/all-MiniLM-L6-v2` (Cosine similarity).
  - **BM25 Lexical Search**: Keyword and exact-token ranking for faculty names, course codes, deadlines, and room numbers.
  - **Reciprocal Rank Fusion (RRF)**: Combines dense semantic and sparse lexical signals with confidence scoring.
- **Self-Healing & Auto-Indexing**: Automatically builds missing embeddings and indices from `AskUIU.csv` on startup. Zero crash risk from missing pickle files.
- **Multi-Provider LLM Dispatcher**:
  - **Google Gemini** (Gemini 2.5/2.0 Flash) - recommended, ultra-fast.
  - **Opencode Go** (`kimi-k2.7-code`).
  - **OpenAI-Compatible** (OpenAI, Groq, DeepSeek, Local Ollama).
  - **Offline Extractive Fallback**: Directly synthesizes grounded, cited answers even without an external API key.
- **Grounded Citations & Metadata Preservation**: Every answer cites sources `[1]`, `[2]` with document titles, categories, and direct clickable links to official `uiu.ac.bd` pages.
- **Real-time Streaming (SSE)**: Word-by-word streaming generation via Server-Sent Events (`/api/stream`).
- **Interactive UI & Mars Rover Edition Theme**:
  - Category filter pills (Admissions, Academics, Campus Life, About, Research).
  - Expandable Source Citation cards with confidence ratings.
  - One-click copy answer to clipboard.
  - Dark / Light mode with persistent preferences.
  - LocalStorage chat history mission log.

---

## Tech Stack

- **Backend**: Python 3.11+, Flask application factory, single-instance RAG service
- **Search & Vectors**: FAISS (`IndexFlatIP`), BM25 Okapi, `sentence-transformers`
- **LLM Integrations**: Google Gemini API, OpenAI-compatible REST endpoints, HTTPX streaming
- **Frontend**: HTML5, Vanilla JS, Tailwind CSS, Glassmorphism & Mars Rover theme
- **Testing**: PyTest with full unit and integration test coverage

---

## Project Structure

```
ASKUIU/
├── app/
│   ├── __init__.py            # Flask app factory & extensions
│   ├── rag/
│   │   ├── service.py         # Singleton RAG service manager
│   │   ├── retriever.py       # Hybrid FAISS + BM25 RRF retriever
│   │   ├── generator.py       # Multi-provider LLM & fallback engine
│   │   └── data/
│   │       ├── AskUIU.csv     # UIU knowledge base (118 documents)
│   │       └── article_embeddings.pkl  # Cached embeddings
│   └── routes/
│       ├── api.py             # /api/query, /api/stream, /api/health
│       └── web.py             # / web chat interface
├── scripts/
│   └── generate_embeddings.py # Standalone embedding generation script
├── static/                    # CSS, JS, UIU badges & Mars Rover assets
├── templates/                 # index.html with streaming & citations
├── tests/                     # Pytest suite (14 passing tests)
├── app.py                     # Development entry point (dynamic port binding)
├── wsgi.py                    # Production entry point
├── gunicorn.conf.py           # Gunicorn configuration
├── config.py                  # Multi-provider configuration
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## Quickstart

### 1. Clone & Setup

```bash
git clone https://github.com/ArafathUIU/ASKUIU.git
cd ASKUIU
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` to select your preferred provider:

```env
SECRET_KEY=uiu-secret-key
LLM_PROVIDER=auto

# Option 1: Google Gemini (Recommended)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Option 2: Opencode Go
OPENCODEGO_API_KEY=your-opencodego-key
OPENCODEGO_BASE_URL=https://opencode.ai/zen/go/v1
OPENCODEGO_MODEL=kimi-k2.7-code

# Option 3: OpenAI / Groq / Local Ollama
OPENAI_API_KEY=your-openai-or-groq-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

*(Note: If no API key is configured, ASKUIU runs in offline verified-citation mode with zero downtime).*

### 4. Run the Application

```bash
python app.py
```

The system will start and bind cleanly (defaults to `http://127.0.0.1:5050` or `5000`).

---

## API Endpoints

### 1. JSON Query (`POST /api/query`)

```json
POST /api/query
Content-Type: application/json

{
  "query": "What are the admission requirements for undergraduate programs?",
  "category": "admission",
  "k": 3
}
```

Response:
```json
{
  "response": "According to official UIU guidelines...",
  "provider": "gemini",
  "latency_seconds": 0.32,
  "sources": [
    {
      "title": "Admission Requirements - United International University (UIU)",
      "source": "https://www.uiu.ac.bd/admission/admission-requirements/",
      "category": "admission",
      "confidence": 0.89,
      "text": "..."
    }
  ]
}
```

### 2. Live SSE Streaming (`GET /api/stream`)

```
GET /api/stream?query=What+scholarships+are+available&category=admission
Accept: text/event-stream
```

Streams `sources`, real-time `token` events, and `done` event.

### 3. Health & Index Stats (`GET /api/health`)

```json
{
  "status": "healthy",
  "active_provider": "gemini",
  "index_stats": {
    "total_documents": 118,
    "categories": {
      "admission": 39,
      "general": 30,
      "academics": 24,
      "about": 10,
      "campus_life": 9,
      "research": 3,
      "administration": 3
    }
  }
}
```

---

## Running Tests

Execute the complete test suite:

```bash
python -m pytest -v
```

All 14 tests covering hybrid retrieval, metadata retention, multi-provider fallbacks, SSE streaming, and health checks will run.

---

## License

MIT License. Developed for the United International University (UIU) Community.
