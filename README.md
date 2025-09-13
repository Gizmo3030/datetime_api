# Datetime API

Small FastAPI service that returns the current date and time in UTC.

This repo exposes two simple endpoints and serves an OpenAPI spec and an AI plugin manifest from `public/` so it can be used as a tool server.

Features

- GET /datetime/current — returns current UTC date and time in ISO 8601 (e.g. 2023-10-27T10:00:00.123456+00:00)
- GET /date/current — returns current UTC date in YYYY-MM-DD format (e.g. 2023-10-27)
- GET /openapi.yaml — serves the OpenAPI YAML from `public/openapi.yaml`
- GET /openapi.json — returns the OpenAPI spec as JSON (converts `public/openapi.yaml` if present, otherwise returns FastAPI's generated schema)
- GET /.well-known/ai-plugin.json — serves the AI plugin manifest

Quickstart (recommended)

1. Create and activate the virtual environment, install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
.venv/bin/python -m pip install -r requirements.txt
```

2. Start the app with uvicorn:

```bash
.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

Or after activating the venv:

```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

Useful URLs (local)

- Interactive Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc
- OpenAPI JSON: http://localhost:5000/openapi.json
- AI Plugin Manifest: http://localhost:5000/.well-known/ai-plugin.json
- Example endpoint: http://localhost:5000/datetime/current

Testing

Run the test suite using the venv Python so the venv-installed test deps are used:

```bash
.venv/bin/python -m pytest -q
```

Files of interest

- `app.py` — FastAPI application and routes
- `public/openapi.yaml` — OpenAPI YAML used by the plugin manifest
- `public/ai-plugin.json` — AI plugin manifest
- `requirements.txt` — runtime and test dependencies
- `tests/test_app.py` — tests for endpoints and static file serving

License

MIT — see `LICENSE`
```