import re
import json
import os
import sys

# Ensure project root is on sys.path so tests can import app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app


def test_get_current_datetime():
    """Happy path: /datetime/current returns ISO 8601 utc datetime string."""
    client = app.test_client()
    resp = client.get('/datetime/current')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'current_datetime_utc' in data
    # Basic ISO 8601 pattern check (YYYY-MM-DDTHH:MM:SS...+00:00)
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+00:00$")
    assert iso_pattern.match(data['current_datetime_utc'])


def test_get_current_date():
    """Happy path: /date/current returns YYYY-MM-DD format."""
    client = app.test_client()
    resp = client.get('/date/current')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'current_date_utc' in data
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    assert date_pattern.match(data['current_date_utc'])


def test_openapi_and_manifest_files_exist():
    """Ensure the app serves the generated OpenAPI and plugin manifest files."""
    client = app.test_client()
    # The app only writes the public files when run as __main__, so create minimal
    # files here so the static routes can serve them for the test.
    public_dir = os.path.join(ROOT, 'public')
    os.makedirs(public_dir, exist_ok=True)
    with open(os.path.join(public_dir, 'openapi.yaml'), 'w') as f:
        f.write('openapi: 3.1.0\n')
    with open(os.path.join(public_dir, 'ai-plugin.json'), 'w') as f:
        f.write(json.dumps({"name_for_model": "test"}))

    resp_yaml = client.get('/openapi.yaml')
    assert resp_yaml.status_code == 200
    assert b"openapi:" in resp_yaml.data

    resp_manifest = client.get('/.well-known/ai-plugin.json')
    assert resp_manifest.status_code == 200
    manifest = json.loads(resp_manifest.data)
    assert 'name_for_model' in manifest
