# KIMERA SWM MVP

This repository contains a minimal implementation of the KIMERA Semantic Working Memory (SWM) system.

## Requirements

- Python 3.12+
- See `requirements.txt` for Python package dependencies.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the API

Start the FastAPI application using `uvicorn`:

```bash
uvicorn backend.api.main:app --reload
```

The API exposes endpoints for managing geoids and scars. Static images are served from `static/images`.

## Testing

Unit tests are located in the `tests` directory and can be run with `pytest`:

```bash
pytest
```

Some stress tests require significant compute time. Set the environment variable `LIGHTWEIGHT_EMBEDDING=1` to avoid downloading heavy models during testing.

