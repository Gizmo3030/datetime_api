# Datetime API

A minimal Flask-based API that returns the current date and time in UTC. Provides two simple endpoints useful for tooling or other APIs that expect either an ISO 8601 datetime or a YYYY-MM-DD date string.

## Features

- GET /datetime/current — returns current UTC date and time in ISO 8601 (see [`app.get_current_datetime`](app.py))
- GET /date/current — returns current UTC date in YYYY-MM-DD format (see [`app.get_current_date`](app.py))
- Serves OpenAPI spec and AI plugin manifest from the `public/` directory

## Quickstart

1. Create a virtual environment (recommended) and install dependencies:

```sh
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:

```sh
python app.py
```

The app listens on http://localhost:5000 by default.

3. Example requests:

```sh
curl http://localhost:5000/datetime/current
curl http://localhost:5000/date/current
```

## OpenAPI & AI Plugin Manifest

The app serves the OpenAPI spec and plugin manifest from `public/`:

- OpenAPI: [/openapi.yaml] served from [public/openapi.yaml](public/openapi.yaml)
- AI Plugin Manifest: [/.well-known/ai-plugin.json] served from [public/ai-plugin.json](public/ai-plugin.json)

If you run the module directly (python app.py) it will attempt to create `public/openapi.yaml` and `public/ai-plugin.json` automatically.

## Testing

Run the test suite with pytest:

```sh
pytest -q
```

Tests exercise the endpoints and the static file serving (see [tests/test_app.py](tests/test_app.py)).

## Files of interest

- Application entrypoint: [app.py](app.py) — contains the Flask `app` and endpoints including [`app.get_current_datetime`](app.py) and [`app.get_current_date`](app.py).
- OpenAPI spec: [public/openapi.yaml](public/openapi.yaml)
- AI plugin manifest: [public/ai-plugin.json](public/ai-plugin.json)
- Requirements: [requirements.txt](requirements.txt)
- Tests: [tests/test_app.py](tests/test_app.py)

## License

MIT — see [LICENSE](LICENSE)
```