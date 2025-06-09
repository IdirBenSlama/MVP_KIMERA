# KIMERA SWM MVP

This repository contains a minimal implementation of the KIMERA Semantic Working Memory (SWM) system.
The authoritative implementation lives in the top-level `backend/` package. The `kimera_swm_mvp/` directory is an archived prototype kept for reference only.

## Requirements

- Python 3.12+
- Tested with FastAPI 0.115, Transformers 4.52, Torch 2.7 and
  Sentence-Transformers 4.1.
- See `requirements.txt` for pinned Python package dependencies. The
  `httpx` dependency is pinned to `0.24.*` for FastAPI test client
  compatibility.

Install dependencies with:
```bash
pip install -r requirements.txt
```
The `python-multipart` package is required for endpoints that accept image uploads.

## Running the API

Start the FastAPI application using `uvicorn`:

```bash
uvicorn backend.api.main:app --reload
```

The API exposes endpoints for managing geoids and scars. Static images are served from `static/images`.

### Environment variables

- `ENABLE_JOBS` controls whether periodic background jobs start on startup. Set this variable to `0` to disable them (default `1`).

## Testing

Unit tests are located in the `tests` directory. Make sure all dependencies are installed and, for faster runs, you may opt into the lightweight embedding mode.

```bash
pip install -r requirements.txt
LIGHTWEIGHT_EMBEDDING=1 pytest
```

Setting `LIGHTWEIGHT_EMBEDDING=1` avoids downloading heavy models during testing.
Set `ENABLE_JOBS=0` during testing to skip the background scheduler.

## EchoForm parser

The endpoint `/geoids` accepts an optional `echoform_text` field that is parsed
using the lightweight EchoForm parser implemented in
`backend/linguistic/echoform.py`.
The parser supports a small s-expression style syntax where parentheses denote
nested lists and tokens are separated by whitespace.  Double quoted strings are
treated as string atoms and the single quote character functions as the Lisp
style `quote` operator.  Submitting EchoForm text stores the parsed structure in
the Geoid's symbolic state.

Example request:

```bash
curl -X POST http://localhost:8000/geoids \
     -H "Content-Type: application/json" \
     -d '{"semantic_features": {"greet": 1.0},
         "echoform_text": "(hello (world))"}'
```

The response returns the new `geoid_id` and the symbolic state will contain the
parsed EchoForm list `[["hello", ["world"]]]`.

## Cognitive cycle and vaults

Running `POST /system/cycle` executes one iteration of the
`KimeraCognitiveCycle` which diffuses semantic pressure, detects contradictions
and stores resulting scars using the `VaultManager`. Scars are balanced between
`vault_a` and `vault_b`.

Trigger a cycle:

```bash
curl -X POST http://localhost:8000/system/cycle
```

You can inspect stored scars with:

```bash
curl http://localhost:8000/vaults/vault_a?limit=5
```

The returned list reflects scars generated both by manual contradiction
processing and automatic cycles.

