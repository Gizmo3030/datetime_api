from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import datetime
import os
import json

app = FastAPI(title="Current Date & Time Tool", version="1.0.0")

# Serve files from the public directory at the root
public_dir = os.path.join(os.path.dirname(__file__), 'public')
if os.path.isdir(public_dir):
  app.mount("/public", StaticFiles(directory=public_dir), name="public")


@app.get('/datetime/current')
async def get_current_datetime():
  """Returns the current date and time in UTC, ISO 8601 format."""
  now_utc = datetime.datetime.now(datetime.timezone.utc)
  return {"current_datetime_utc": now_utc.isoformat()}


@app.get('/date/current')
async def get_current_date():
  """Returns the current date in UTC as YYYY-MM-DD."""
  now_utc = datetime.datetime.now(datetime.timezone.utc)
  return {"current_date_utc": now_utc.strftime("%Y-%m-%d")}


@app.get('/.well-known/ai-plugin.json')
async def serve_ai_plugin_manifest():
  file_path = os.path.join(public_dir, 'ai-plugin.json')
  if not os.path.exists(file_path):
    raise HTTPException(status_code=404, detail="ai-plugin.json not found")
  return FileResponse(file_path, media_type='application/json')


@app.get('/openapi.yaml')
async def serve_openapi_yaml():
  file_path = os.path.join(public_dir, 'openapi.yaml')
  if not os.path.exists(file_path):
    raise HTTPException(status_code=404, detail='openapi.yaml not found')
  return FileResponse(file_path, media_type='application/x-yaml')


@app.get('/openapi.json')
async def serve_openapi_json():
  # Prefer loading public/openapi.yaml if present so the plugin manifest can reference the same spec.
  yaml_path = os.path.join(public_dir, 'openapi.yaml')
  if not os.path.exists(yaml_path):
    # Fall back to FastAPI's generated OpenAPI schema
    return JSONResponse(content=app.openapi())

  try:
    # import yaml lazily to avoid hard dependency at import time
    import yaml
  except ModuleNotFoundError:
    raise HTTPException(status_code=500, detail='PyYAML is not installed; install PyYAML to serve openapi.json from YAML')

  try:
    with open(yaml_path, 'r') as f:
      spec = yaml.safe_load(f)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to load OpenAPI spec: {e}')

  return JSONResponse(content=spec)


@app.get('/logo.png')
async def serve_logo():
  file_path = os.path.join(public_dir, 'logo.png')
  if not os.path.exists(file_path):
    raise HTTPException(status_code=404, detail='logo.png not found')
  return FileResponse(file_path, media_type='image/png')


# Optional: a small root message
@app.get('/')
async def root():
  return PlainTextResponse('Current Date & Time Tool - use /docs for interactive API docs')