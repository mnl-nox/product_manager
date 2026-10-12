import fetchJson from './api.js';

const rowsEl = document.getElementById('work-item-rows');
const form = document.getElementById('work-item-form');
const statusEl = document.getElementById('page-status');
const typeEl = document.getElementById('item-type');
const riskFields = document.getElementById('risk-fields');
const authResponse = await fetch('/api/auth/me', { headers: { Accept: 'application/json' } });
const canUpdate = authResponse.ok && ['admin', 'operator'].includes((await authResponse.json()).user.role);

const labels = {
  type: { bug: 'Bug', risk: 'Risco' },
  severity: { low: 'Baixa', medium: 'Média', high: 'Alta', critical: 'Crítica' },
  status: { open: 'Aberto', in_progress: 'Em andamento', resolved: 'Resolvido', closed: 'Encerrado' },
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[character]);
}

async function loadItems() {
  const items = await fetchJson('/api/work-items');
  rowsEl.innerHTML = items.length ? items.map((item) => `
    <tr><td>${labels.type[item.item_type]}</td><td><strong>${escapeHtml(item.title)}</strong><details><summary>Descrição</summary><p>${escapeHtml(item.description)}</p></details></td>
    <td>${labels.severity[item.severity]}</td><td>${item.item_type === 'risk' ? `${item.probability} × ${item.impact} = ${item.probability * item.impact}` : '—'}</td>
    <td>${escapeHtml(item.owner || 'Não atribuído')}</td><td>${escapeHtml(item.due_date || '—')}</td>
    <td>${labels.status[item.status]}</td><td>${canUpdate ? `<div class="work-item-actions"><select aria-label="Atualizar estado de ${escapeHtml(item.title)}" data-status="${item.id}">${Object.entries(labels.status).map(([value, label]) => `<option value="${value}" ${item.status === value ? 'selected' : ''}>${label}</option>`).join('')}</select><input data-owner="${item.id}" aria-label="Responsável por ${escapeHtml(item.title)}" maxlength="64" value="${escapeHtml(item.owner)}" /><button type="button" data-update="${item.id}">Salvar</button></div>` : '—'}</td></tr>`).join('')
    : '<tr><td colspan="8">Nenhum risco ou bug registrado.</td></tr>';
  rowsEl.querySelectorAll('[data-update]').forEach((button) => button.addEventListener('click', async () => {
    const itemId = Number(button.dataset.update);
    const select = rowsEl.querySelector(`[data-status="${itemId}"]`);
    const ownerInput = rowsEl.querySelector(`[data-owner="${itemId}"]`);
    try {
      await fetchJson(`/api/work-items/${itemId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: select.value, owner: ownerInput.value || '' }),
      });
      statusEl.textContent = 'Estado atualizado.';
      await loadItems();
    } catch (error) { statusEl.textContent = error.message; }
  }));
}

typeEl.addEventListener('change', () => {
  const isRisk = typeEl.value === 'risk';
  riskFields.hidden = !isRisk;
  riskFields.querySelectorAll('input').forEach((input) => { input.required = isRisk; input.disabled = !isRisk; });
});
typeEl.dispatchEvent(new Event('change'));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  if (payload.item_type === 'risk') {
    payload.probability = Number(payload.probability);
    payload.impact = Number(payload.impact);
  }
  try {
    const result = await fetchJson('/api/work-items', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    });
    statusEl.textContent = result.message;
    form.reset();
    typeEl.dispatchEvent(new Event('change'));
    await loadItems();
  } catch (error) { statusEl.textContent = error.message; }
});

loadItems().catch((error) => { statusEl.textContent = error.message; });
