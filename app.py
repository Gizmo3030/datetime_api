# app.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
CORS(app) # Enable CORS for all routes, essential for browser-based access

# --- API Endpoint for getting current date/time ---
@app.route('/datetime/current', methods=['GET'])
def get_current_datetime():
    """
    Returns the current date and time in UTC, ISO 8601 format.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    return jsonify({
        "current_datetime_utc": now_utc.isoformat()
    })

# --- NEW API Endpoint for getting current date only ---
@app.route('/date/current', methods=['GET'])
def get_current_date():
    """
    Returns the current date in UTC, "yyyy-mm-dd" format,
    specifically for use with APIs that require a date-only string.
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    current_date_str = now_utc.strftime("%Y-%m-%d") # Format to YYYY-MM-DD
    return jsonify({
        "current_date_utc": current_date_str
    })

# --- Routes for serving the OpenAPI specification and AI Plugin Manifest ---
@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin_manifest():
    """Serves the AI Plugin Manifest."""
    return send_from_directory('public', 'ai-plugin.json')

@app.route('/openapi.yaml')
def serve_openapi_yaml():
    """Serves the OpenAPI specification."""
    return send_from_directory('public', 'openapi.yaml')

# Optional: Serve a dummy logo if you include one in the manifest
@app.route('/logo.png')
def serve_logo():
    """Serves a placeholder logo."""
    return send_from_directory('public', 'logo.png')

if __name__ == '__main__':
    # --- Dynamic creation of necessary files for easy setup ---
    base_url = "http://localhost:5000"

    if not os.path.exists("public"):
        os.makedirs("public")

    # 1. Create openapi.yaml content with both endpoints
    openapi_content = f"""
openapi: 3.1.0
info:
  title: Current Date & Time Tool
  version: "1.0.0"
  description: API for retrieving the current date and time, or just the date, in UTC.
servers:
  - url: {base_url}
paths:
  /datetime/current:
    get:
      summary: Get the current UTC date and time (ISO 8601)
      operationId: getCurrentDatetime
      description: "Retrieves the current date and time in UTC, formatted as ISO 8601 (e.g., 2023-10-27T10:00:00.123456+00:00)."
      responses:
        '200':
          description: Successful response with the current UTC date and time.
          content:
            application/json:
              schema:
                type: object
                properties:
                  current_datetime_utc:
                    type: string
                    format: date-time
                    description: Current UTC date and time in ISO 8601 format.
  /date/current:
    get:
      summary: Get the current UTC date (YYYY-MM-DD format)
      operationId: getCurrentDate
      description: "Retrieves the current UTC date in 'YYYY-MM-DD' format, specifically for use with APIs (like NewsAPI) that require a date-only string."
      responses:
        '200':
          description: Successful response with the current UTC date.
          content:
            application/json:
              schema:
                type: object
                properties:
                  current_date_utc:
                    type: string
                    format: date # OpenAPI standard format for YYYY-MM-DD
                    pattern: "^\\d{{4}}-\\d{{2}}-\\d{{2}}$" # Explicit pattern for YYYY-MM-DD
                    description: Current UTC date in YYYY-MM-DD format (e.g., 2023-10-27).
"""
    with open("public/openapi.yaml", "w") as f:
        f.write(openapi_content)

    # 2. Create ai-plugin.json content - update description_for_model
    ai_plugin_content = f"""
{{
  "schema_version": "v1",
  "name_for_model": "current_time_and_date_tool",
  "name_for_human": "Current Time & Date",
  "description_for_model": "Provides the current date and time in UTC. Use `getCurrentDatetime` for the full date and time (ISO 8601) or `getCurrentDate` for just the date in 'YYYY-MM-DD' format. Use this tool whenever the user asks for the current date, current time, 'now', or similar temporal queries, especially when a specific date format is needed for other APIs (e.g., News API).",
  "description_for_human": "A tool to get the current date and time (UTC) in various formats.",
  "auth": {{
    "type": "none"
  }},
  "api": {{
    "type": "openapi",
    "url": "{base_url}/openapi.yaml"
  }},
  "logo_url": "{base_url}/logo.png",
  "contact_email": "support@example.com",
  "legal_info": "https://www.example.com/legal"
}}
"""
    with open("public/ai-plugin.json", "w") as f:
        f.write(ai_plugin_content)

    # 3. Create a dummy logo file (optional but good practice if logo_url is present)
    try:
        from PIL import Image
        img = Image.new('RGB', (60, 30), color = 'red') # Small red rectangle as a placeholder
        img.save("public/logo.png")
    except ImportError:
        print("Pillow not installed. Skipping dummy logo creation. If logo_url is used, ensure 'public/logo.png' exists.")
    except Exception as e:
        print(f"Error creating dummy logo: {e}. Skipping dummy logo creation.")

    # Run the Flask app
    app.run(port=5000, debug=True)