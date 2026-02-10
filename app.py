"""
Grist Custom Forms - Flask API Server

Proxies requests to Grist API with authentication.
Supports multiple forms via form_id in URL path.

Environment variables:
  GRIST_API_KEY - Default API key (or GRIST_API_KEY_<FORM_ID> per form)
  GRIST_DOC_<FORM_ID> - Document ID for each form
  GRIST_TABLE_<FORM_ID> - Table ID for each form (defaults to "Reponses")
  GRIST_BASE_URL - Grist instance URL (defaults to grist.numerique.gouv.fr)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify, send_from_directory

load_dotenv()

BASE_DIR = Path(__file__).parent
FORMS_DIR = BASE_DIR / 'forms'
ASSETS_DIR = BASE_DIR / 'assets'

app = Flask(__name__)

GRIST_BASE_URL = os.environ.get('GRIST_BASE_URL', 'https://grist.numerique.gouv.fr')


def get_form_config(form_id: str) -> dict:
    """Get configuration for a form from environment variables."""
    form_id_upper = form_id.upper()

    doc_id = os.environ.get(f'GRIST_DOC_{form_id_upper}')
    if not doc_id:
        return None

    return {
        'doc_id': doc_id,
        'table_id': os.environ.get(f'GRIST_TABLE_{form_id_upper}', 'Reponses'),
        'api_key': os.environ.get(f'GRIST_API_KEY_{form_id_upper}') or os.environ.get('GRIST_API_KEY'),
    }


@app.route('/api/forms/<form_id>/record', methods=['GET'])
def get_record(form_id: str):
    """Fetch a record by UUID."""
    config = get_form_config(form_id)
    if not config:
        return jsonify({'error': f'Unknown form: {form_id}'}), 404

    uuid = request.args.get('uuid')
    if not uuid:
        return jsonify({'error': 'UUID parameter required'}), 400

    # Build Grist API URL with filter
    filter_param = f'{{"uuid":["{uuid}"]}}'
    url = f"{GRIST_BASE_URL}/api/docs/{config['doc_id']}/tables/{config['table_id']}/records"

    headers = {'Accept': 'application/json'}
    # API key optional for read if doc is public
    if config['api_key']:
        headers['Authorization'] = f"Bearer {config['api_key']}"

    try:
        resp = requests.get(url, params={'filter': filter_param}, headers=headers)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forms/<form_id>/record', methods=['POST'])
def save_record(form_id: str):
    """Create or update a record."""
    config = get_form_config(form_id)
    if not config:
        return jsonify({'error': f'Unknown form: {form_id}'}), 404

    if not config['api_key']:
        return jsonify({'error': 'API key not configured for this form'}), 500

    data = request.get_json()
    if not data or 'fields' not in data:
        return jsonify({'error': 'Invalid request body'}), 400

    fields = data['fields']
    uuid = fields.get('uuid')
    if not uuid:
        return jsonify({'error': 'UUID required in fields'}), 400

    base_url = f"{GRIST_BASE_URL}/api/docs/{config['doc_id']}/tables/{config['table_id']}"
    headers = {
        'Authorization': f"Bearer {config['api_key']}",
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Check if record exists
    filter_param = f'{{"uuid":["{uuid}"]}}'
    try:
        check_resp = requests.get(f"{base_url}/records", params={'filter': filter_param}, headers=headers)
        if check_resp.status_code != 200:
            return jsonify(check_resp.json()), check_resp.status_code

        existing = check_resp.json()
        record_id = existing['records'][0]['id'] if existing.get('records') else None
    except Exception as e:
        return jsonify({'error': f'Failed to check existing record: {e}'}), 500

    # Create or update
    try:
        if record_id:
            # Update existing
            payload = {'records': [{'id': record_id, 'fields': fields}]}
            resp = requests.patch(f"{base_url}/records", json=payload, headers=headers)
        else:
            # Create new
            payload = {'records': [{'fields': fields}]}
            resp = requests.post(f"{base_url}/records", json=payload, headers=headers)

        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


# Static file serving for forms and frontend
@app.route('/forms/<form_id>/')
@app.route('/forms/<form_id>')
def serve_form(form_id: str):
    """Serve form HTML."""
    return send_from_directory(FORMS_DIR / form_id, 'index.html')


@app.route('/assets/<path:filename>')
def serve_assets(filename: str):
    """Serve static assets (JS, CSS)."""
    return send_from_directory(ASSETS_DIR, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
