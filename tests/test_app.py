import re
import json
import os
import sys

# Ensure project root is on sys.path so tests can import app.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app
from fastapi.testclient import TestClient


def test_get_current_datetime():
    """Happy path: /datetime/current returns ISO 8601 utc datetime string."""
    client = TestClient(app)
    resp = client.get('/datetime/current')
    assert resp.status_code == 200
    data = resp.json()
    assert 'current_datetime_utc' in data
    # Basic ISO 8601 pattern check (YYYY-MM-DDTHH:MM:SS...+00:00)
    iso_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?\+00:00$")
    assert iso_pattern.match(data['current_datetime_utc'])


def test_get_current_date():
    """Happy path: /date/current returns YYYY-MM-DD format."""
    client = TestClient(app)
    resp = client.get('/date/current')
    assert resp.status_code == 200
    data = resp.json()
    assert 'current_date_utc' in data
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    assert date_pattern.match(data['current_date_utc'])


def test_openapi_and_manifest_files_exist():
    """Ensure the app serves the generated OpenAPI and plugin manifest files."""
    client = TestClient(app)
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
    assert "openapi:" in resp_yaml.text

    resp_manifest = client.get('/.well-known/ai-plugin.json')
    assert resp_manifest.status_code == 200
    manifest = resp_manifest.json()
    assert 'name_for_model' in manifest


def test_openapi_json_endpoint():
    """The app should serve a JSON-converted OpenAPI spec at /openapi.json"""
    client = TestClient(app)
    public_dir = os.path.join(ROOT, 'public')
    os.makedirs(public_dir, exist_ok=True)
    # create a minimal openapi.yaml for parsing
    yaml_content = """
openapi: 3.1.0
info:
  title: Test API
  version: '1.0'
paths: {}
"""
    with open(os.path.join(public_dir, 'openapi.yaml'), 'w') as f:
        f.write(yaml_content)

    resp = client.get('/openapi.json')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert data.get('openapi', '').startswith('3')
