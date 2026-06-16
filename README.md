# ASKUIU

ASKUIU is a Retrieval-Augmented Generation (RAG) powered intelligent question-answering system designed for the **United International University (UIU)** community. It enables users to ask natural language questions and get accurate, context-aware answers grounded in university-specific data.

---

## Features

- **Opencode Go (`kimi-k2.7-code`)** based intelligent answering
- Contextual RAG from UIU-specific data
- Clean, responsive chat UI with **dark mode**
- Quick-question chips for common queries
- FAISS vector search backend
- Flask API with web and JSON endpoints
- Unit tests with `pytest`

---

## Tech Stack

- Python (Flask)
- Opencode Go API (`kimi-k2.7-code`)
- Hugging Face `sentence-transformers`
- FAISS for vector search
- Tailwind CSS + Vanilla JS
- Pandas, NumPy, Pickle

---

## Project Structure

```
ASKUIU/
├── app/
│   ├── __init__.py
│   ├── rag/
│   │   ├── retriever.py       # FAISS + embedding logic
│   │   ├── generator.py       # Opencode Go LLM client
│   │   └── data/
│   │       ├── AskUIU.csv     # UIU knowledge base
│   │       └── article_embeddings.pkl  # generated locally
│   ├── routes/
│   │   ├── api.py             # /api/query JSON endpoint
│   │   └── web.py             # / web chat endpoint
│   └── tasks/                 # (reserved for future async tasks)
├── scripts/
│   └── generate_embeddings.py # regenerate FAISS embeddings
├── static/                    # CSS, JS, favicon
├── templates/                 # HTML templates
├── tests/                     # pytest test suite
├── docs/screenshots/          # project screenshots
├── app.py                     # development entry point
├── wsgi.py                    # production entry point
├── gunicorn.conf.py           # gunicorn configuration
├── config.py                  # Flask config classes
├── requirements.txt
├── .env.example
└── pytest.ini
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ArafathUIU/ASKUIU.git
cd ASKUIU
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\Activate.ps1     # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your **Opencode Go API key**:

```env
SECRET_KEY=your-secret-key-here
OPENCODEGO_API_KEY=your-opencodego-api-key-here
OPENCODEGO_BASE_URL=https://opencode.ai/zen/go/v1
OPENCODEGO_MODEL=kimi-k2.7-code
```

> Replace `OPENCODEGO_BASE_URL` with the actual endpoint for your Opencode Go account.

### 5. Generate embeddings

The FAISS index is built from `app/rag/data/AskUIU.csv` and stored as `article_embeddings.pkl` locally (it is not committed to Git).

```bash
python scripts/generate_embeddings.py
```

### 6. Run the application

Development:

```bash
python app.py
```

Production with Gunicorn:

```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

Then open `http://localhost:5000` in your browser.

---

## API Usage

### Web Chat

- **URL:** `/`
- **Method:** `POST`
- **Body:** `application/x-www-form-urlencoded`
  - `user_message`: the question

### JSON API

- **URL:** `/api/query`
- **Method:** `POST`
- **Body:** `application/json`

```json
{
  "query": "Who is the head of CSE?",
  "category": null,
  "field": null
}
```

Response:

```json
{
  "response": "...",
  "sources": [
    {"text": "...", "index": 0}
  ]
}
```

---

## Running Tests

```bash
pytest
```

To run with detailed output:

```bash
pytest -v
```

---

## Screenshots

### Chat UI Interface

![Chat UI](docs/screenshots/ss%20(1).png)

### Terminal Output (Flask)

![Terminal](docs/screenshots/ss%20(2).png)
![Terminal](docs/screenshots/ss%20(3).png)

---

## Future Works

- Speech-to-Text feature
- Text-to-Speech feature
- Reinforcement learning with updated data

---

## License

This project is licensed under the [MIT License](LICENSE).
