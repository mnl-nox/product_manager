import { default as fetchJson } from './api.js';

const summaryEl = document.getElementById('finance-summary');
const entriesEl = document.getElementById('finance-entries');
const statusEl = document.getElementById('page-status');
const form = document.getElementById('finance-form');
const authResponse = await fetch('/api/auth/me', { headers: { Accept: 'application/json' } });
const canDelete = authResponse.ok && ['admin', 'finance'].includes((await authResponse.json()).user.role);

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);
}

function money(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value || 0));
}

async function loadFinance() {
  const [summary, entries] = await Promise.all([
    fetchJson('/api/finance/summary'),
    fetchJson('/api/finance/entries'),
  ]);
  summaryEl.innerHTML = `
    <article class="summary-card"><span class="label">Receitas realizadas</span><strong class="value">${money(summary.income)}</strong></article>
    <article class="summary-card"><span class="label">Despesas realizadas</span><strong class="value">${money(summary.expenses)}</strong></article>
    <article class="summary-card accent"><span class="label">Saldo realizado</span><strong class="value">${money(summary.balance)}</strong></article>
    <article class="summary-card"><span class="label">Saldo projetado</span><strong class="value">${money(summary.projectedBalance)}</strong></article>`;
  entriesEl.innerHTML = entries.length ? entries.map((entry) => `
    <tr><td>${escapeHtml(entry.entry_date)}</td><td>${entry.entry_type === 'income' ? 'Receita' : 'Despesa'}</td>
    <td>${escapeHtml(entry.category)}</td><td>${escapeHtml(entry.description)}</td>
    <td>${money(entry.amount)}</td><td>${entry.status === 'paid' ? 'Realizado' : 'Previsto'}</td>
    <td>${canDelete ? `<button type="button" class="table-action danger-action" data-delete="${entry.id}">Remover</button>` : '—'}</td></tr>`).join('')
    : '<tr><td colspan="7">Nenhum lançamento cadastrado.</td></tr>';
  entriesEl.querySelectorAll('[data-delete]').forEach((button) => button.addEventListener('click', async () => {
    if (!window.confirm('Remover este lançamento financeiro?')) return;
    try {
      await fetchJson(`/api/finance/entries/${button.dataset.delete}/delete`, { method: 'POST' });
      await loadFinance();
      statusEl.textContent = 'Lançamento removido.';
    } catch (error) { statusEl.textContent = error.message; }
  }));
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.amount = Number(payload.amount);
  try {
    const result = await fetchJson('/api/finance/entries', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    });
    form.reset();
    statusEl.textContent = result.message;
    await loadFinance();
  } catch (error) {
    statusEl.textContent = error.message;
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const dateInput = form.elements.entry_date;
  dateInput.value = new Date().toISOString().slice(0, 10);
  loadFinance().catch((error) => { statusEl.textContent = error.message; });
});
