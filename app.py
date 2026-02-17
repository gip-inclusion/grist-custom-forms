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
import json
from functools import wraps
from pathlib import Path
from dotenv import load_dotenv
import requests
from flask import Flask, request, jsonify, redirect, send_from_directory, Response

load_dotenv()

BASE_DIR = Path(__file__).parent
FORMS_DIR = BASE_DIR / 'forms'
ASSETS_DIR = BASE_DIR / 'assets'

app = Flask(__name__)

GRIST_BASE_URL = os.environ.get('GRIST_BASE_URL', 'https://grist.numerique.gouv.fr')


def _require_admin_auth():
    """HTTP Basic auth guard for admin endpoints."""
    username = os.environ.get('ADMIN_USERNAME')
    password = os.environ.get('ADMIN_PASSWORD')
    if not username or not password:
        return Response(
            'Admin access not configured. Set ADMIN_USERNAME and ADMIN_PASSWORD.',
            503,
            {'Content-Type': 'text/plain; charset=utf-8'},
        )

    auth = request.authorization
    if not auth or auth.username != username or auth.password != password:
        return Response(
            'Authentication required',
            401,
            {'WWW-Authenticate': 'Basic realm="Grist Admin"'},
        )
    return None


def admin_required(fn):
    """Decorator to protect admin pages and APIs with basic auth."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        denied = _require_admin_auth()
        if denied:
            return denied
        return fn(*args, **kwargs)
    return wrapper


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


def _as_bool(value) -> bool:
    """Normalize truthy values from Grist fields."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    txt = str(value).strip().lower()
    return txt in {'1', 'true', 'vrai', 'oui', 'yes'}


def fetch_all_records(config: dict, headers: dict):
    """Fetch records for a form table (single pass, up to 5000 rows)."""
    url = f"{GRIST_BASE_URL}/api/docs/{config['doc_id']}/tables/{config['table_id']}/records"
    resp = requests.get(url, params={'limit': 5000}, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f'Failed to read records: HTTP {resp.status_code} - {resp.text}')
    payload = resp.json()
    return payload.get('records', [])


def normalize_finess(value) -> str:
    """Normalize FINESS value for duplicate checks."""
    return str(value or '').strip().upper()

def normalize_email(value) -> str:
    """Normalize email value for lookup."""
    return str(value or '').strip().lower()


def extract_finess_values(fields: dict) -> set:
    """Extract FINESS values from standard and JSON fields."""
    values = set()
    if not isinstance(fields, dict):
        return values

    main = normalize_finess(fields.get('finess_main'))
    if main:
        values.add(main)

    raw_json = fields.get('finess_json')
    parsed = []
    if isinstance(raw_json, str) and raw_json.strip():
        try:
            parsed = json.loads(raw_json)
        except Exception:
            parsed = []
    elif isinstance(raw_json, list):
        parsed = raw_json

    if isinstance(parsed, list):
        for item in parsed:
            v = normalize_finess(item)
            if v:
                values.add(v)

    return values


def find_duplicate_finess(config: dict, current_uuid: str, finess_values: set, headers: dict):
    """Find FINESS values already used by another record in the same table."""
    if not finess_values:
        return set()

    records = fetch_all_records(config, headers)
    duplicates = set()
    cur = normalize_finess(current_uuid)

    for rec in records:
        fields = rec.get('fields', {}) if isinstance(rec, dict) else {}
        rec_uuid = normalize_finess(fields.get('uuid'))
        if cur and rec_uuid == cur:
            continue
        rec_finess = extract_finess_values(fields)
        duplicates.update(finess_values.intersection(rec_finess))

    return duplicates


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

    # Enforce uniqueness of FINESS across records (excluding current UUID)
    try:
        incoming_finess = extract_finess_values(fields)
        duplicates = find_duplicate_finess(config, uuid, incoming_finess, headers)
        if duplicates:
            duplicates_sorted = sorted(duplicates)
            return jsonify({
                'error': 'Un ou plusieurs numéros FINESS sont déjà utilisés par un autre questionnaire.',
                'duplicates': duplicates_sorted,
            }), 409
    except Exception as e:
        return jsonify({'error': f'Failed to validate FINESS uniqueness: {e}'}), 500

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


@app.route('/api/forms/<form_id>/check-finess', methods=['POST'])
def check_finess(form_id: str):
    """Check whether FINESS values already exist in another questionnaire."""
    config = get_form_config(form_id)
    if not config:
        return jsonify({'error': f'Unknown form: {form_id}'}), 404

    data = request.get_json() or {}
    uuid = normalize_finess(data.get('uuid'))
    raw_finess = data.get('finess') or []

    if not isinstance(raw_finess, list):
        return jsonify({'error': 'Invalid request body: finess must be a list'}), 400

    finess_values = {normalize_finess(v) for v in raw_finess if normalize_finess(v)}
    headers = {'Accept': 'application/json'}
    if config['api_key']:
        headers['Authorization'] = f"Bearer {config['api_key']}"

    try:
        duplicates = sorted(find_duplicate_finess(config, uuid, finess_values, headers))
        return jsonify({
            'ok': True,
            'duplicates': duplicates,
            'has_duplicates': len(duplicates) > 0,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forms/<form_id>/recover-by-email', methods=['POST'])
def recover_by_email(form_id: str):
    """Recover a questionnaire UUID from validation email."""
    config = get_form_config(form_id)
    if not config:
        return jsonify({'error': f'Unknown form: {form_id}'}), 404

    data = request.get_json() or {}
    email = normalize_email(data.get('email'))
    if not email:
        return jsonify({'error': 'Email required'}), 400

    url = f"{GRIST_BASE_URL}/api/docs/{config['doc_id']}/tables/{config['table_id']}/records"
    headers = {'Accept': 'application/json'}
    if config['api_key']:
        headers['Authorization'] = f"Bearer {config['api_key']}"

    try:
        # 1) Fast path: exact filter on the email column.
        filter_param = json.dumps({"validateur_email": [email]})
        resp = requests.get(url, params={'filter': filter_param, 'limit': 5000}, headers=headers)
        if resp.status_code != 200:
            return jsonify(resp.json()), resp.status_code
        payload = resp.json()
        records = payload.get('records', [])

        matches = []
        for rec in records:
            fields = rec.get('fields', {}) if isinstance(rec, dict) else {}
            if not fields.get('uuid'):
                continue
            matches.append(rec)

        # 2) Fallback: scan and compare case-insensitively (older rows / casing differences).
        if not matches:
            scan_resp = requests.get(url, params={'limit': 5000}, headers=headers)
            if scan_resp.status_code != 200:
                return jsonify(scan_resp.json()), scan_resp.status_code
            scan_payload = scan_resp.json()
            for rec in scan_payload.get('records', []):
                fields = rec.get('fields', {}) if isinstance(rec, dict) else {}
                if normalize_email(fields.get('validateur_email')) != email:
                    continue
                if not fields.get('uuid'):
                    continue
                matches.append(rec)

        if not matches:
            return jsonify({'error': 'Aucun questionnaire trouvé pour cet email.'}), 404

        chosen = max(matches, key=lambda r: int(r.get('id', 0) or 0))
        chosen_fields = chosen.get('fields', {}) if isinstance(chosen, dict) else {}
        return jsonify({
            'ok': True,
            'uuid': chosen_fields.get('uuid'),
            'count': len(matches),
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forms/<form_id>/admin/overview', methods=['GET'])
@admin_required
def admin_overview(form_id: str):
    """Admin dashboard data: counts + questionnaire list."""
    config = get_form_config(form_id)
    if not config:
        return jsonify({'error': f'Unknown form: {form_id}'}), 404

    headers = {'Accept': 'application/json'}
    if config['api_key']:
        headers['Authorization'] = f"Bearer {config['api_key']}"

    search = str(request.args.get('search', '') or '').strip().lower()
    status = str(request.args.get('status', 'all') or 'all').strip().lower()

    try:
        records = fetch_all_records(config, headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    rows = []
    for rec in records:
        fields = rec.get('fields', {}) if isinstance(rec, dict) else {}
        if not fields:
            continue
        row = {
            'record_id': rec.get('id'),
            'uuid': fields.get('uuid', ''),
            'es_nom': fields.get('es_nom', ''),
            'departement': fields.get('es_departement', ''),
            'finess_main': fields.get('finess_main', ''),
            'validateur_nom': fields.get('validateur_nom', ''),
            'validateur_prenom': fields.get('validateur_prenom', ''),
            'validateur_email': fields.get('validateur_email', ''),
            'saisie_terminee': _as_bool(fields.get('saisie_terminee')),
        }
        rows.append(row)

    total = len(rows)
    termines = sum(1 for r in rows if r['saisie_terminee'])
    en_cours = total - termines

    # Newest first by record id.
    rows.sort(key=lambda r: int(r['record_id'] or 0), reverse=True)

    if status in {'en_cours', 'termines'}:
        want_done = status == 'termines'
        rows = [r for r in rows if r['saisie_terminee'] is want_done]

    if search:
        def _matches(r):
            haystack = ' '.join([
                str(r.get('es_nom', '')),
                str(r.get('departement', '')),
                str(r.get('finess_main', '')),
                str(r.get('validateur_nom', '')),
                str(r.get('validateur_prenom', '')),
                str(r.get('validateur_email', '')),
                str(r.get('uuid', '')),
            ]).lower()
            return search in haystack
        rows = [r for r in rows if _matches(r)]

    return jsonify({
        'ok': True,
        'form_id': form_id,
        'stats': {
            'total_questionnaires': total,
            'en_cours': en_cours,
            'termines': termines,
        },
        'rows': rows,
    }), 200


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


@app.route('/')
def index():
    return redirect('/forms/fagerh/')


# Static file serving for forms and frontend
@app.route('/forms/<form_id>/')
@app.route('/forms/<form_id>')
def serve_form(form_id: str):
    """Serve form HTML."""
    return send_from_directory(FORMS_DIR / form_id, 'index.html')


@app.route('/admin/<form_id>/')
@app.route('/admin/<form_id>')
@admin_required
def serve_admin(form_id: str):
    """Serve admin dashboard HTML for a form."""
    return send_from_directory(FORMS_DIR / form_id, 'admin.html')


@app.route('/assets/<path:filename>')
def serve_assets(filename: str):
    """Serve static assets (JS, CSS)."""
    return send_from_directory(ASSETS_DIR, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
