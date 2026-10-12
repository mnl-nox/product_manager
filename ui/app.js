const state = {
  clients: [],
  products: [],
  mapping: {}
};

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderSummary() {
  const summary = document.getElementById('summary');
  summary.innerHTML = `
    <div class="summary-card">
      <div class="label">Clientes</div>
      <div class="value">${state.clients.length}</div>
    </div>
    <div class="summary-card">
      <div class="label">Produtos</div>
      <div class="value">${state.products.length}</div>
    </div>
    <div class="summary-card">
      <div class="label">Ativos</div>
      <div class="value">${state.clients.filter((client) => client.status === 'active').length}</div>
    </div>
    <div class="summary-card">
      <div class="label">Estoque total</div>
      <div class="value">${state.products.reduce((sum, product) => sum + Number(product.quantity || 0), 0)}</div>
    </div>
  `;
}

function renderClients() {
  const tbody = document.getElementById('clients-table');
  tbody.innerHTML = state.clients.length
    ? state.clients.map((client) => `
      <tr>
        <td>${escapeHtml(client.id)}</td>
        <td>${escapeHtml(client.name)}</td>
        <td>${escapeHtml(client.username)}</td>
        <td>${escapeHtml(client.email)}</td>
        <td>${escapeHtml(client.phone)}</td>
        <td>${escapeHtml(client.cpf)}</td>
        <td>${escapeHtml(client.status)}</td>
      </tr>
    `).join('')
    : '<tr><td colspan="7">Nenhum cliente cadastrado.</td></tr>';
}

function renderProducts() {
  const tbody = document.getElementById('products-table');
  tbody.innerHTML = state.products.length
    ? state.products.map((product) => `
      <tr>
        <td>${escapeHtml(product.id)}</td>
        <td>${escapeHtml(product.name)}</td>
        <td>${escapeHtml(product.category)}</td>
        <td>${escapeHtml(product.sku)}</td>
        <td>${escapeHtml(product.brand)}</td>
        <td>R$ ${Number(product.price).toFixed(2)}</td>
        <td>${escapeHtml(product.quantity)}</td>
        <td>${escapeHtml(product.status)}</td>
      </tr>
    `).join('')
    : '<tr><td colspan="8">Nenhum produto cadastrado.</td></tr>';
}

function renderFieldMap() {
  const pre = document.getElementById('field-map');
  pre.textContent = JSON.stringify(state.mapping, null, 2);
}

async function loadData() {
  const [clientsResponse, productsResponse, mappingResponse] = await Promise.all([
    fetch('/api/clients'),
    fetch('/api/products'),
    fetch('/api/field-mapping')
  ]);

  if (!clientsResponse.ok || !productsResponse.ok || !mappingResponse.ok) {
    throw new Error('Não foi possível carregar os dados do sistema.');
  }

  state.clients = await clientsResponse.json();
  state.products = await productsResponse.json();
  state.mapping = await mappingResponse.json();

  renderSummary();
  renderClients();
  renderProducts();
  renderFieldMap();
}

async function submitClient(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());

  const response = await fetch('/api/clients', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  if (!response.ok) {
    alert(result.error || 'Erro ao criar cliente.');
    return;
  }

  form.reset();
  await loadData();
  alert(result.message || 'Cliente criado com sucesso.');
}

async function submitProduct(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());

  const response = await fetch('/api/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  if (!response.ok) {
    alert(result.error || 'Erro ao criar produto.');
    return;
  }

  form.reset();
  await loadData();
  alert(result.message || 'Produto criado com sucesso.');
}

(async () => {
  document.getElementById('client-form').addEventListener('submit', submitClient);
  document.getElementById('product-form').addEventListener('submit', submitProduct);

  try {
    await loadData();
  } catch (error) {
    console.error(error);
    alert(error.message || 'Falha ao iniciar a interface.');
  }
})();
