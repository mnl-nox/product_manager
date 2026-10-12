import { createClient, getDashboardData } from './api.js';

const summaryEl = document.getElementById('summary');
const categoryBreakdownEl = document.getElementById('category-breakdown');
const clientsTableEl = document.getElementById('clients-table');
const productsTableEl = document.getElementById('products-table');
const pageStatusEl = document.getElementById('page-status');

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function setStatus(message) {
  if (pageStatusEl) pageStatusEl.textContent = message;
}

function money(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(Number(value || 0));
}

function renderSummary(data) {
  summaryEl.innerHTML = `
    <article class="summary-card accent">
      <span class="label">Clientes</span>
      <strong class="value">${data.clients}</strong>
    </article>
    <article class="summary-card">
      <span class="label">Produtos</span>
      <strong class="value">${data.products}</strong>
    </article>
    <article class="summary-card">
      <span class="label">Ativos</span>
      <strong class="value">${data.activeClients}</strong>
    </article>
    <article class="summary-card">
      <span class="label">Estoque total</span>
      <strong class="value">${data.totalStock}</strong>
    </article>
  `;
}

function renderCategoryBreakdown(categories) {
  if (!categories.length) {
    categoryBreakdownEl.innerHTML = '<p class="empty-state">Nenhuma categoria cadastrada.</p>';
    return;
  }

  const totalProducts = categories.reduce((sum, item) => sum + Number(item.total || 0), 0);
  categoryBreakdownEl.innerHTML = categories.map((category) => {
    const share = totalProducts > 0 ? ((Number(category.total) / totalProducts) * 100).toFixed(1) : '0.0';
    const width = Math.min(100, Math.max(0, Math.round(Number(share) / 10) * 10));
    return `
      <div class="metric-card">
        <div class="metric-header">
          <span>${escapeHtml(category.category)}</span>
          <strong>${escapeHtml(category.total)}</strong>
        </div>
        <div class="progress-bar">
          <span class="progress-fill width-${width}" role="progressbar" aria-label="${escapeHtml(category.category)}" aria-valuenow="${share}" aria-valuemin="0" aria-valuemax="100"></span>
        </div>
        <small>${share}% da base</small>
      </div>
    `;
  }).join('');
}

function renderClients(rows) {
  if (!rows.length) {
    clientsTableEl.innerHTML = '<tr><td colspan="6">Nenhum cliente cadastrado.</td></tr>';
    return;
  }

  clientsTableEl.innerHTML = rows.map((client) => `
    <tr>
      <td>${escapeHtml(client.id)}</td>
      <td>${escapeHtml(client.name)}</td>
      <td>${escapeHtml(client.email)}</td>
      <td>${escapeHtml(client.city)}</td>
      <td>${escapeHtml(client.status)}</td>
      <td>${escapeHtml(client.role)}</td>
    </tr>
  `).join('');
}

function renderProducts(rows) {
  if (!rows.length) {
    productsTableEl.innerHTML = '<tr><td colspan="6">Nenhum produto com estoque crítico.</td></tr>';
    return;
  }

  productsTableEl.innerHTML = rows.map((product) => `
    <tr>
      <td>${escapeHtml(product.id)}</td>
      <td>${escapeHtml(product.name)}</td>
      <td>${escapeHtml(product.category)}</td>
      <td>${escapeHtml(product.quantity)}</td>
      <td>${money(product.price)}</td>
      <td>${escapeHtml(product.status)}</td>
    </tr>
  `).join('');
}

async function loadDashboard() {
  setStatus('Carregando dashboard.');
  const data = await getDashboardData();
  renderSummary(data);
  renderCategoryBreakdown(data.categories || []);
  renderClients(data.recentClients || []);
  renderProducts(data.lowStockProducts || []);
  setStatus('Dashboard atualizado.');
}

async function handleClientSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());

  try {
    const result = await createClient(payload);
    form.reset();
    await loadDashboard();
    setStatus(result.message || 'Cliente criado com sucesso.');
  } catch (error) {
    setStatus(error.message || 'Erro ao criar cliente.');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const clientForm = document.getElementById('client-form');
  if (clientForm) {
    clientForm.addEventListener('submit', handleClientSubmit);
  }

  loadDashboard().catch((error) => {
    console.error(error);
    setStatus(error.message || 'Falha ao carregar o dashboard.');
  });
});
