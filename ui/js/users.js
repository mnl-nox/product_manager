import { default as fetchJson } from './api.js';

const rowsEl = document.getElementById('user-rows');
const statusEl = document.getElementById('page-status');
const form = document.getElementById('user-form');
const authResponse = await fetch('/api/auth/me', { headers: { Accept: 'application/json' } });
const currentUserId = authResponse.ok ? (await authResponse.json()).user.id : null;

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);
}

const roleNames = { admin: 'Administrador', operator: 'Operação', finance: 'Financeiro', viewer: 'Somente leitura' };

async function loadUsers() {
  const users = await fetchJson('/api/auth/users');
  rowsEl.innerHTML = users.map((user) => `
    <tr><td>${escapeHtml(user.username)}</td><td>${roleNames[user.role] || escapeHtml(user.role)}</td>
    <td>${user.active ? 'Ativo' : 'Desativado'}</td><td>${escapeHtml(user.created_at)}</td>
    <td>${user.active && user.id !== currentUserId ? `<button type="button" data-deactivate="${user.id}">Desativar</button>` : '—'}</td></tr>`).join('');
  rowsEl.querySelectorAll('[data-deactivate]').forEach((button) => button.addEventListener('click', async () => {
    if (!window.confirm('Desativar este usuário e encerrar as sessões dele?')) return;
    try {
      const result = await fetchJson(`/api/auth/users/${button.dataset.deactivate}/deactivate`, { method: 'POST' });
      statusEl.textContent = result.message;
      await loadUsers();
    } catch (error) { statusEl.textContent = error.message; }
  }));
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const result = await fetchJson('/api/auth/users', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    });
    statusEl.textContent = result.message;
    form.reset();
    await loadUsers();
  } catch (error) { statusEl.textContent = error.message; }
});

loadUsers().catch((error) => { statusEl.textContent = error.message; });
