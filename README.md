# CCPA Compliance Detection System

Production-ready FastAPI service that detects potential CCPA violations using a hybrid pipeline:
- deterministic rule-based checks,
- legal retrieval-augmented generation (RAG), and
- strict JSON schema enforcement.

## Architecture

### 1) FastAPI Layer
- `POST /analyze` accepts a natural-language business practice.
- `GET /health` provides liveness status.
- Pydantic models enforce strict request/response schema (`extra="forbid"`).

### 2) Rule-Based System (First Pass)
- Regex-based high-confidence detector in `app/rules.py`.
- Immediately returns known CCPA article mappings for clear policy patterns.
- Avoids unnecessary model calls for deterministic violations.

### 3) RAG Pipeline (Second Pass)
1. PDF statute loader (`app/loader.py`) parses `Section 1798.xxx` chunks.
2. Retriever (`app/retriever.py`) embeds all sections with SentenceTransformers.
3. FAISS in-memory index performs similarity search for top-k legal sections.
4. LLM (`app/model.py`) reasons only over retrieved legal context.

### 4) Strict JSON Enforcement
- `app/utils.py` extracts JSON-only model output.
- Validates with Pydantic strict schema:
	- `harmful: bool`
	- `articles: list[str]`
- Filters `articles` so only retrieved legal sections are allowed.
- Any malformed/non-compliant output falls back to safe default:
	- `{"harmful": false, "articles": []}`

## Project Structure

```text
app/
	__init__.py
	loader.py
	main.py
	model.py
	retriever.py
	rules.py
	utils.py

Dockerfile
requirements.txt
README.md
```

## Environment Variables

- `HF_TOKEN` (optional unless model is gated)
- `MODEL_ID` (default: `microsoft/Phi-3-mini-4k-instruct`)
- `EMBEDDING_MODEL` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `CCPA_PDF_PATH` (default: `ccpa_statute.pdf`)
- `RETRIEVAL_TOP_K` (default: `3`)

## GPU Requirements

- For GPU inference in Docker, install NVIDIA drivers + NVIDIA Container Toolkit.
- Run container with `--gpus all`.
- If GPU is unavailable, service runs in CPU mode automatically (slower inference).

## Docker

### Build

```bash
docker build --build-arg HF_TOKEN=<your_hf_token> -t ccpa-detector .
```

### Run (GPU)

```bash
docker run --gpus all -p 8000:8000 \
	-e HF_TOKEN=<your_hf_token> \
	-e CCPA_PDF_PATH=ccpa_statute.pdf \
	-e RETRIEVAL_TOP_K=3 \
	ccpa-detector
```

### Run (CPU)

```bash
docker run -p 8000:8000 \
	-e HF_TOKEN=<your_hf_token> \
	-e CCPA_PDF_PATH=ccpa_statute.pdf \
	ccpa-detector
```

## Local Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place `ccpa_statute.pdf` at repo root (or set `CCPA_PDF_PATH`).
4. Set optional env vars (`HF_TOKEN`, `MODEL_ID`, `EMBEDDING_MODEL`, `RETRIEVAL_TOP_K`).
5. Start server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

### Analyze Prompt

```bash
curl -X POST "http://localhost:8000/analyze" \
	-H "Content-Type: application/json" \
	-d "{\"prompt\":\"We sell personal data without notice to users.\"}"
```

Example response:

```json
{"harmful": true, "articles": ["Section 1798.120"]}
```
