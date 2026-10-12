const API_BASE = '/api';

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      ...(options.headers || {}),
    },
    ...options,
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

export function getProducts(category = 'all') {
  const params = new URLSearchParams();
  if (category && category !== 'all') {
    params.set('category', category);
  }
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

export default fetchJson;
