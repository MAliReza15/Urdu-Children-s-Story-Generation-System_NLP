# Urdu Story Generation — FastAPI Backend

REST API that mirrors the `train.py` workflow: load tokenizer → load corpus → train N-gram model → expose generation.

## Setup

From the **backend** directory:

```bash
pip install -r requirements-api.txt
```

## Run

From the **backend** directory (so `config`, `data`, `tokenizer`, etc. resolve):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

## Environment (optional)

| Variable     | Default                     | Description                |
| ------------ | --------------------------- | -------------------------- |
| `VOCAB_PATH` | `Data/vocab.json`           | BPE vocab file             |
| `MERGES_PATH` | `Data/merges.json`        | BPE merges file            |
| `DATA_PATH`  | `Data/processed_stories.json` | Corpus for training     |
| `MODEL_NAME` | `trigram`                   | `trigram`, `5gram`, or `7gram` |

## Endpoints

- **GET /health** — `{"status": "ok"}`
- **GET /**, **GET /api/info** — Model info (name, vocab size, status)
- **POST /api/generate** — Generate a story

### POST /api/generate

Body (all optional):

```json
{
  "prompt": "optional Urdu text to seed context",
  "max_length": 500,
  "temperature": 0.8,
  "top_k": 50
}
```

Response:

```json
{
  "story": "generated Urdu text..."
}
```

At startup the API loads the tokenizer, trains the N-gram model on the corpus (same as `train.py`), then serves requests.
