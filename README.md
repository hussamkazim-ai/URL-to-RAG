# URL to RAG

Turn any website into a searchable knowledge base and chat with it using Retrieval-Augmented Generation (RAG).

## How It Works

1. **Scrape** — Submit a URL and Firecrawl fetches every page on the site as Markdown
2. **Embed** — Content is chunked and embedded locally using FastEmbed (dense + BM25 sparse vectors)
3. **Store** — Embeddings are stored in a local Qdrant vector database
4. **Chat** — Ask questions and get answers grounded in the scraped content, powered by an LLM via OpenRouter

## Tech Stack

- **FastAPI** — REST API
- **Qdrant** — Vector database (local)
- **Firecrawl** — Web scraping
- **FastEmbed** — Local embeddings (dense + sparse)
- **LangChain** — Document loading, splitting, and retrieval chain
- **OpenRouter** — LLM provider (default: `openai/gpt-oss-20b:free`)

## Prerequisites

- Python 3.10+
- A running Qdrant instance on `localhost:6333`
- A [Firecrawl](https://www.firecrawl.dev/) API key
- An [OpenRouter](https://openrouter.ai/) API key (or any OpenAI-compatible provider)

## Installation

```bash
git clone https://github.com/your-username/url-to-rag.git
cd url-to-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
FIRECRAWL_API_KEY=your_firecrawl_key
OPENAI_API_KEY=your_openrouter_key
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `FIRECRAWL_API_KEY` | — | Required. Firecrawl API key |
| `OPENAI_API_KEY` | — | Required. LLM provider API key |
| `BASE_URL` | `https://openrouter.ai/api/v1` | OpenAI-compatible API base URL |
| `OPENAI_MODEL` | `openai/gpt-oss-20b:free` | Model for generation |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `COLLECTION_NAME` | `url_to_rag` | Qdrant collection name |
| `USE_HYBRID_RAG` | `True` | Enable dense + sparse hybrid search |
| `RETRIEVAL_K` | `5` | Number of chunks to retrieve |

## Running

Start Qdrant (if not already running):

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Start the application:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/process-url/` | Scrape, embed, and store a website |
| `POST` | `/query/` | Ask a question and get a response |
| `POST` | `/stream/` | Ask a question with streaming response |
| `DELETE` | `/delete-data/` | Remove a website's data from the vector store |

### Examples

**Process a URL:**
```bash
curl -X POST http://localhost:8000/process-url/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Query:**
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What services does this company offer?"}'
```

**Stream:**
```bash
curl -X POST http://localhost:8000/stream/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize the homepage"}'
```

**Delete data:**
```bash
curl -X DELETE http://localhost:8000/delete-data/ \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

## License

MIT
