const API_BASE = '/api';
let csrfToken = '';

export function setCsrfToken(token) {
  csrfToken = token || '';
}

async function ensureCsrfToken() {
  if (csrfToken) return csrfToken;
  const response = await fetch(`${API_BASE}/auth/me`, { headers: { Accept: 'application/json' } });
  if (!response.ok) {
    window.location.replace('/login');
    throw new Error('Sessão expirada. Entre novamente.');
  }
  const session = await response.json();
  csrfToken = session.csrfToken;
  return csrfToken;
}

async function fetchJson(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = {
    Accept: 'application/json',
    ...(options.headers || {}),
  };
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method) && !url.includes('/auth/login') && !url.includes('/auth/setup')) {
    headers['X-CSRF-Token'] = await ensureCsrfToken();
  }
  const response = await fetch(url, {
    ...options,
    headers,
  });

  const rawText = await response.text();
  let payload = null;

  if (rawText) {
    try {
      payload = JSON.parse(rawText);
    } catch {
      payload = rawText;
    }
  }

  if (!response.ok) {
    if (response.status === 401) window.location.replace('/login');
    const message = payload && typeof payload === 'object' && 'error' in payload ? payload.error : 'Erro ao processar a requisição.';
    throw new Error(message);
  }

  return payload;
}

export function getDashboardData() {
  return fetchJson(`${API_BASE}/dashboard`);
}

export function getCategories() {
  return fetchJson(`${API_BASE}/categories`);
}

export function getProducts(category = 'all', includeInactive = false) {
  const params = new URLSearchParams();
  if (category && category !== 'all') {
    params.set('category', category);
  }
  if (includeInactive) params.set('include_inactive', '1');
  const query = params.toString();
  return fetchJson(`${API_BASE}/products${query ? `?${query}` : ''}`);
}

export function createClient(payload) {
  return fetchJson(`${API_BASE}/clients`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function createProduct(payload) {
  return fetchJson(`${API_BASE}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function updateProduct(id, payload) {
  return fetchJson(`${API_BASE}/products/${id}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
  });
}

export function productAction(id, action) {
  return fetchJson(`${API_BASE}/products/${id}/${action}`, { method: 'POST' });
}

export function getGoogleSheetsIntegrationStatus() {
  return fetchJson(`${API_BASE}/integrations/google-sheets/status`);
}

export function exportToGoogleSheets() {
  return fetchJson(`${API_BASE}/integrations/google-sheets/export`, { method: 'POST' });
}

export default fetchJson;
