# KIMERA SWM MVP

This repository contains a minimal implementation of the KIMERA Semantic Working Memory (SWM) system.
The authoritative implementation lives in the top-level `backend/` package. The `kimera_swm_mvp/` directory is an archived prototype kept for reference only.

## Requirements

- Python 3.12+
- See `requirements.txt` for Python package dependencies.
- The `httpx` dependency is pinned to `<0.27` due to compatibility with
  FastAPI's test client.

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

## Testing

Unit tests are located in the `tests` directory. Make sure all dependencies are installed and, for faster runs, you may opt into the lightweight embedding mode.

```bash
pip install -r requirements.txt
LIGHTWEIGHT_EMBEDDING=1 pytest
```

Setting `LIGHTWEIGHT_EMBEDDING=1` avoids downloading heavy models during testing.

