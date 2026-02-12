/**
 * GristForm - Generic library for custom Grist forms
 *
 * Handles:
 * - UUID generation
 * - Loading existing records by UUID
 * - Saving (create or update) records
 * - Shareable URL management
 * - Sidebar UI bindings
 */
class GristForm {
  /**
   * @param {Object} options
   * @param {string} options.apiBase - Base URL for the API (e.g., '/api/forms' or 'https://example.com/api/forms')
   * @param {string} options.formId - Form identifier (e.g., 'fagerh')
   * @param {string} [options.uuidField='uuid'] - Name of the UUID field in the form
   * @param {string} [options.urlParam='formulaire'] - URL parameter name for the UUID
 * @param {Function} [options.onPopulate] - Callback after populating form: (record, uuid) => void
 * @param {Function} [options.onBeforeSave] - Callback before saving: (fields) => fields
 * @param {Function} [options.onAfterSave] - Callback after successful save: ({ fields, uuid, response }) => void
   */
  constructor(options) {
    this.apiBase = options.apiBase;
    this.formId = options.formId;
    this.uuidField = options.uuidField || 'uuid';
    this.urlParam = options.urlParam || 'formulaire';
    this.onPopulate = options.onPopulate || null;
    this.onBeforeSave = options.onBeforeSave || null;
    this.onAfterSave = options.onAfterSave || null;

    // UI elements (set via bindSidebar)
    this.statusEl = null;
    this.shareUrlEl = null;
    this.formEl = null;
    this.submitBtn = null;
  }

  /**
   * Generate a UUID v4
   */
  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
  }

  /**
   * Get UUID from URL parameter
   */
  getUuidFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get(this.urlParam);
  }

  /**
   * Get the shareable URL for a UUID
   */
  getShareUrl(uuid) {
    return `${window.location.origin}${window.location.pathname}?${this.urlParam}=${uuid}`;
  }

  /**
   * Update browser URL without reload
   */
  updateUrl(uuid) {
    history.replaceState(null, '', `?${this.urlParam}=${uuid}`);
  }

  /**
   * Show status message
   */
  showStatus(message, type = '') {
    if (!this.statusEl) return;
    this.statusEl.textContent = message;
    this.statusEl.className = 'status-msg' + (type ? ' ' + type : '');
  }

  /**
   * Hide status message after delay
   */
  hideStatusAfter(ms = 3000) {
    setTimeout(() => {
      if (this.statusEl) this.statusEl.className = 'status-msg';
    }, ms);
  }

  /**
   * Load a record by UUID from the API
   */
  async load(uuid) {
    const url = `${this.apiBase}/${this.formId}/record?uuid=${encodeURIComponent(uuid)}`;

    const response = await fetch(url);
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${response.status}`);
    }

    const data = await response.json();
    if (!data.records || data.records.length === 0) {
      throw new Error('Record not found');
    }

    return data.records[0].fields;
  }

  /**
   * Save (create or update) a record
   */
  async save(fields) {
    const url = `${this.apiBase}/${this.formId}/record`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Populate form fields from a record
   */
  populateForm(record, uuid) {
    // Set UUID field
    const uuidInput = document.getElementById(this.uuidField);
    if (uuidInput) uuidInput.value = uuid;

    // Populate standard form fields
    for (const [key, value] of Object.entries(record)) {
      if (key === 'id' || key.startsWith('_')) continue;

      const inputs = document.getElementsByName(key);
      const input = inputs.length ? inputs[0] : null;
      if (!input) continue;

      if (input.type === 'checkbox') {
        input.checked = value === 'true' || value === true;
        input.dispatchEvent(new Event('change'));
      } else if (input.tagName === 'SELECT') {
        input.value = value || '';
        input.dispatchEvent(new Event('change'));
      } else {
        input.value = value ?? '';
      }
    }

    // Call custom populate callback
    if (this.onPopulate) {
      this.onPopulate(record, uuid);
    }
  }

  /**
   * Collect form data as object
   */
  collectFormData(formElement) {
    const formData = new FormData(formElement);
    const fields = {};
    for (const [key, value] of formData.entries()) {
      fields[key] = value;
    }

    // Call custom collect callback
    if (this.onBeforeSave) {
      return this.onBeforeSave(fields);
    }
    return fields;
  }

  /**
   * Bind to a form element for auto-submit handling
   */
  bindForm(formElement, submitBtn) {
    this.formEl = formElement;
    this.submitBtn = submitBtn;

    formElement.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Get or generate UUID
      const uuidInput = document.getElementById(this.uuidField);
      let uuid = uuidInput?.value;
      if (!uuid) {
        uuid = this.generateUUID();
        if (uuidInput) uuidInput.value = uuid;
      }

      // Collect fields
      const fields = this.collectFormData(formElement);

      // Save
      if (submitBtn) submitBtn.disabled = true;
      this.showStatus('Enregistrement en cours...', 'loading');

      try {
        const response = await this.save(fields);

        this.showStatus('Enregistré !', 'success');
        this.hideStatusAfter();

        // Update URL and share field
        this.updateUrl(uuid);
        if (this.shareUrlEl) {
          this.shareUrlEl.value = this.getShareUrl(uuid);
        }

        if (this.onAfterSave) {
          this.onAfterSave({ fields, uuid, response });
        }
      } catch (err) {
        console.error('Save failed:', err);
        this.showStatus('Erreur : ' + err.message, 'error');
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  /**
   * Bind sidebar UI elements
   */
  bindSidebar({ statusEl, shareUrlEl, copyBtn, newBtn }) {
    this.statusEl = statusEl;
    this.shareUrlEl = shareUrlEl;

    if (copyBtn) {
      copyBtn.addEventListener('click', () => this.copyShareUrl());
    }

    if (newBtn) {
      newBtn.addEventListener('click', () => {
        window.location.href = window.location.pathname;
      });
    }
  }

  /**
   * Copy share URL to clipboard
   */
  async copyShareUrl() {
    const url = this.shareUrlEl?.value;
    if (!url) {
      this.showStatus('Enregistrez d\'abord le formulaire', 'error');
      this.hideStatusAfter(2000);
      return;
    }

    try {
      await navigator.clipboard.writeText(url);
      this.showStatus('Lien copié !', 'success');
      this.hideStatusAfter(2000);
    } catch {
      this.shareUrlEl.select();
      document.execCommand('copy');
      this.showStatus('Lien copié !', 'success');
      this.hideStatusAfter(2000);
    }
  }

  /**
   * Initialize: load existing record if UUID in URL
   */
  async init() {
    const uuid = this.getUuidFromUrl();
    if (!uuid) return false;

    this.showStatus('Chargement du formulaire...', 'loading');

    try {
      const record = await this.load(uuid);
      this.populateForm(record, uuid);

      if (this.shareUrlEl) {
        this.shareUrlEl.value = this.getShareUrl(uuid);
      }

      this.showStatus('Formulaire chargé', 'success');
      this.hideStatusAfter();
      return true;
    } catch (err) {
      console.error('Load failed:', err);
      this.showStatus('Erreur chargement: ' + err.message, 'error');
      return false;
    }
  }
}

// Export for use as ES module or global
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GristForm;
} else if (typeof window !== 'undefined') {
  window.GristForm = GristForm;
}
