import { default as fetchJson } from './api.js';

const rowsEl = document.getElementById('stock-alerts');
const statusEl = document.getElementById('page-status');
const form = document.getElementById('threshold-form');

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);
}

async function loadAlerts() {
  const [alerts, config, products] = await Promise.all([
    fetchJson('/api/alerts/stock'),
    fetchJson('/api/alerts/config'),
    fetchJson('/api/products'),
  ]);
  document.getElementById('alert-default').textContent = `Limite padrão atual: ${config.defaultMinimumQuantity} unidades.`;
  const productSelect = form.elements.product_id;
  const selectedProduct = productSelect.value;
  productSelect.innerHTML = '<option value="">Selecione um produto</option>' + products.map((product) =>
    `<option value="${product.id}">${escapeHtml(product.name)} · ${escapeHtml(product.sku)}</option>`).join('');
  productSelect.value = selectedProduct;
  rowsEl.innerHTML = alerts.length ? alerts.map((alert) => `
    <tr><td><span class="alert-priority ${alert.severity}">${alert.severity === 'critical' ? 'Crítico' : 'Atenção'}</span></td>
    <td>${escapeHtml(alert.name)}</td><td>${escapeHtml(alert.sku)}</td>
    <td>${alert.quantity}</td><td>${alert.minimum_quantity}</td>
    <td><button type="button" data-ack="${alert.id}">Marcar como visto</button></td></tr>`).join('')
    : '<tr><td colspan="6">Nenhum alerta de estoque ativo.</td></tr>';
  rowsEl.querySelectorAll('[data-ack]').forEach((button) => button.addEventListener('click', async () => {
    try {
      await fetchJson(`/api/alerts/stock/${button.dataset.ack}/acknowledge`, { method: 'POST' });
      await loadAlerts();
      statusEl.textContent = 'Alerta marcado como visto.';
    } catch (error) { statusEl.textContent = error.message; }
  }));
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const result = await fetchJson(`/api/alerts/stock/${payload.product_id}/threshold`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    });
    statusEl.textContent = result.message;
    form.reset();
    await loadAlerts();
  } catch (error) { statusEl.textContent = error.message; }
});

loadAlerts().catch((error) => { statusEl.textContent = error.message; });
