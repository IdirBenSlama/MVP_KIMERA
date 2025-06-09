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
GPU-accelerated features rely on additional heavy packages. Install them
separately when needed, for example:
```bash
pip install torch
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

#### LIGHTWEIGHT_CLIP

Set this variable to `1` to disable heavy CLIP downloads for image processing
endpoints. They will run in a lightweight mode without pulling the full CLIP
weights.

## Testing

Unit tests are located in the `tests` directory. After installing the
dependencies, run the helper script to execute all tests in lightweight mode.

```bash
pip install -r requirements.txt
./scripts/run_tests.sh
```

The script enables the lightweight embedding mode, disables background jobs, and
adds the repository root to `PYTHONPATH` so that modules are importable without
installing the package.
GPU-heavy packages like `torch` are therefore optional when executing the tests.

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

Example response (truncated for brevity):

```json
{
  "geoid_id": "GEOID_1234ABCD",
  "geoid": {
    "geoid_id": "GEOID_1234ABCD",
    "semantic_state": {"greet": 1.0},
    "symbolic_state": {"echoform": [["hello", ["world"]]]},
    "metadata": {}
  },
  "entropy": 0.0
}
```

The `symbolic_state` now contains the parsed EchoForm list under the
`"echoform"` key.

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
processing and automatic cycles. You can get a summary of scar counts and
their total weights with:

```bash
python scripts/vault_inspect.py
```

To manually rebalance the vaults, call:

```bash
curl -X POST http://localhost:8000/vaults/rebalance
```

### Example EchoForm workflow

Create two geoids with conflicting EchoForm statements:

```bash
curl -X POST http://localhost:8000/geoids \
     -H "Content-Type: application/json" \
     -d '{"semantic_features": {"belief": 1.0},
         "echoform_text": "(claim \"cats are friendly\")"}'

curl -X POST http://localhost:8000/geoids \
     -H "Content-Type: application/json" \
     -d '{"semantic_features": {"belief": -1.0},
         "echoform_text": "(claim \"cats are hostile\")"}'

curl -X POST http://localhost:8000/system/cycle

curl http://localhost:8000/vaults/vault_a?limit=1
```
Example output:
```json
{
  "vault_id": "vault_a",
  "scars": [
    {
      "scar_id": "SC1",
      "geoids": ["G1", "G2"],
      "reason": "Resolved 'polar' tension.",
      "timestamp": "...",
      "resolved_by": "cycle",
      "pre_entropy": 0.5,
      "post_entropy": 0.4,
      "delta_entropy": -0.1,
      "cls_angle": 0.7,
      "semantic_polarity": -0.6,
      "mutation_frequency": 0.0
    }
  ]
}
```


The response resembles the JSON above, showing the scar linking the two geoids.

## Request Profiles

API endpoints can tune behavior by specifying a profile name in the `X-Kimera-Profile` header. `backend/api/middleware.py` loads the JSON config at `backend/core/cim_profiles.json` on startup. For each request the middleware looks up the given profile name and stores the resulting dictionary on `request.state.kimera_profile`. Unknown names result in an empty profile.

A shortened example of the profiles file:

```json
{
  "financial_analysis": {"...": "..."},
  "creative_brainstorming": {"...": "..."}
}
```

Use the header when calling endpoints:

```bash
curl -X POST http://localhost:8000/process/contradictions \
     -H "Content-Type: application/json" \
     -H "X-Kimera-Profile: financial_analysis" \
     -d '{"trigger_geoid_id": "G1"}'

curl http://localhost:8000/system/status \
     -H "X-Kimera-Profile: creative_brainstorming"
```
