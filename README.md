# Grist Custom Forms

Custom HTML forms that save to Grist documents.
Every submission has a UUID from which the form can be resumed.
This enables Grist-backed forms that need a more custom UI than Grist itself allows.

## Structure

```
assets/     # Shared JS library
forms/      # Form HTML (one folder per form)
server/     # Flask API proxy
```

## Setup

```bash
cd server
cp .env.example .env
# Edit .env with your Grist API key and doc IDs
uv run flask run -p 5005
```

### Adding a new form

1. Create forms/<form-id>/index.html
2. Include the library: <script src="/assets/grist-form.js"></script>
3. Initialize with your form ID:
	```javascript
	const gristForm = new GristForm({
	  apiBase: '/api/forms',
	  formId: '<form-id>',
	  // optional callbacks: onPopulate, onBeforeSave
	});
	```
4. Add env vars:
	```bash
	GRIST_DOC_<FORM_ID>=...  
	GRIST_TABLE_<FORM_ID>=...
	```

### API

- `GET /api/forms/<id>/record?uuid=...` - fetch record
- `POST /api/forms/<id>/record` - create/update record
- `GET /forms/<id>/` - serve form HTML
- `GET /api/forms/<id>/admin/overview` - admin stats (basic auth)

### Admin console

- URL: `/admin/<form-id>/` (example: `/admin/fagerh/`)
- Required env vars:
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD`
  - `BREVO_API_KEY` for transactional emails
  - `BREVO_FROM_EMAIL` for transactional emails
  - `BREVO_FROM_NAME` optional, defaults to `EURES beta`
- The admin page shows:
  - total questionnaires,
  - in progress (`saisie_terminee != true`),
  - completed (`saisie_terminee == true`),
  - searchable/filterable list.
- EURES beta exposes an extra Brevo diagnostic:
  - `GET /api/forms/eures-beta/admin/brevo-health?check=1`
  - checks env configuration and Brevo API reachability without sending an email
- Global deep health check:
  - `GET /health?deep=1`
  - returns HTTP `503` when Brevo is broken or unreachable, which is suitable for a monitor or scheduled probe

### EURES deployment notes

EURES beta now runs as a dedicated Scalingo app, but the public domain
`formulaires.inclusion.gouv.fr` may still be attached to the `fagerh` app.

Use these environment variables to make the split explicit:

- `DEFAULT_HOME_FORM_ID`
  - controls the `/` redirect for the current app
  - set `DEFAULT_HOME_FORM_ID=eures-beta` on the dedicated EURES app
  - set `DEFAULT_HOME_FORM_ID=fagerh` on the Fagerh app
- `PUBLIC_APP_BASE_URL`
  - base URL used in generated public links and emails
- `EURES_PUBLIC_PROXY_ENABLED`
  - when `true`, the app proxies only the EURES beta public routes
- `EURES_PUBLIC_PROXY_BASE_URL`
  - upstream dedicated EURES app, for example `https://eures-beta.osc-fr1.scalingo.io`

Recommended setup:

- on `eures-beta`
  - `DEFAULT_HOME_FORM_ID=eures-beta`
  - `PUBLIC_APP_BASE_URL=https://formulaires.inclusion.gouv.fr`
- on `fagerh`
  - `DEFAULT_HOME_FORM_ID=fagerh`
  - `EURES_PUBLIC_PROXY_ENABLED=true`
  - `EURES_PUBLIC_PROXY_BASE_URL=https://eures-beta.osc-fr1.scalingo.io`

Public routes proxied by `fagerh` when EURES proxying is enabled:

- `/forms/eures-beta/...`
- `/admin/eures-beta`
- `/api/forms/eures-beta/...`
- `/eures-beta/matching-feedback`

### TODO

- [ ] Protect record creation route (via invitation links, auth, rate limiting, etc.)
- [ ] Server side validation with a provided model
