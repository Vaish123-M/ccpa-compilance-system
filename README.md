# CCPA Compliance Detection System

Production-ready, containerized FastAPI service for CCPA violation detection using a hybrid deterministic + Legal RAG + LLM architecture.

## Architecture

### 1) Startup Initialization (one-time)
- Load `ccpa_statute.pdf`
- Parse text into `Section 1798.xxx` blocks
- Embed all sections using `sentence-transformers/all-MiniLM-L6-v2`
- Build in-memory FAISS index
- Load an instruct LLM (`microsoft/Phi-3-mini-4k-instruct`, configurable)

### 2) Request-Time Pipeline
1. `POST /analyze` receives:
	```json
	{"prompt": "<natural language business practice>"}
	```
2. High-confidence rule layer checks deterministic patterns first.
3. If no deterministic hit:
	- Retrieve top-k relevant CCPA sections from FAISS.
	- Run constrained LLM reasoning using only retrieved sections.
4. Strict validator enforces response schema and legal article constraints.
5. Safe fallback returns:
	```json
	{"harmful": false, "articles": []}
	```

## API

### Health
- `GET /health` → `200 OK`

### Analyze
- `POST /analyze`
- Request:
  ```json
  {"prompt": "We sell personal data without notice to users."}
  ```
- Response (strict JSON only):
  ```json
  {"harmful": true, "articles": ["Section 1798.120"]}
  ```

## Project Structure

```text
app/
  main.py
  loader.py
  retriever.py
  model.py
  rules.py
  utils.py

requirements.txt
Dockerfile
README.md
```

## Environment Variables

- `HF_TOKEN` (required for gated Hugging Face models)
- `MODEL_ID` (default: `microsoft/Phi-3-mini-4k-instruct`)
- `EMBEDDING_MODEL` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `CCPA_PDF_PATH` (default: `ccpa_statute.pdf`)
- `RETRIEVAL_TOP_K` (default: `3`)

## Docker

### Build (recommended with HF token)
```bash
docker build --build-arg HF_TOKEN=<token> -t ccpa .
```

### Run (GPU)
```bash
docker run --gpus all -p 8000:8000 -e HF_TOKEN=<token> ccpa
```

### Run (CPU fallback)
```bash
docker run -p 8000:8000 -e HF_TOKEN=<token> ccpa
```

## Local Setup

1. Install Python dependencies:
	```bash
	pip install -r requirements.txt
	```
2. Set environment variables (`HF_TOKEN` if needed).
3. Ensure `ccpa_statute.pdf` is present in project root (or set `CCPA_PDF_PATH`).
4. Start service:
	```bash
	uvicorn app.main:app --host 0.0.0.0 --port 8000
	```

## Example cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"We ignore verified consumer deletion requests.\"}"
```
