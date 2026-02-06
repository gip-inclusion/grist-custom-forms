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

### TODO

- [ ] Protect record creation route (via invitation links, auth, rate limiting, etc.)
- [ ] Server side validation with a provided model
