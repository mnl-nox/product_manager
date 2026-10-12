import { createProduct, getCategories, getProducts, productAction, updateProduct } from './api.js';

const categoryFilterEl = document.getElementById('category-filters');
const productSummaryEl = document.getElementById('product-summary');
const productsTableEl = document.getElementById('products-table');
let selectedCategory = 'all';
const pageStatusEl = document.getElementById('page-status');
const showInactiveEl = document.getElementById('show-inactive-products');
const searchEl = document.getElementById('product-search');
const statusFilterEl = document.getElementById('product-status-filter');
const productForm = document.getElementById('product-form');
const authResponse = await fetch('/api/auth/me', { headers: { Accept: 'application/json' } });
const role = authResponse.ok ? (await authResponse.json()).user.role : 'viewer';

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

function productStatus(status) {
  return ({ available: 'Disponível', reserved: 'Reservado', out_of_stock: 'Sem estoque' })[status] || status;
}

function renderCategoryFilters(categories) {
  const options = [{ category: 'all', total: categories.reduce((sum, item) => sum + Number(item.total || 0), 0) }, ...categories];

  categoryFilterEl.innerHTML = options.map((entry) => {
    const label = entry.category === 'all' ? 'Todos' : entry.category;
    const activeClass = selectedCategory === entry.category ? 'active' : '';
    return `
      <button type="button" class="chip ${activeClass}" data-category="${escapeHtml(entry.category)}" aria-pressed="${selectedCategory === entry.category}">
        ${escapeHtml(label)} <span>${escapeHtml(entry.total)}</span>
      </button>
    `;
  }).join('');

  categoryFilterEl.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
      selectedCategory = button.dataset.category;
      loadProducts();
    });
  });
}

function renderProductSummary(products) {
  const totalUnits = products.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
  const totalValue = products.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0);

  productSummaryEl.innerHTML = `
    <article class="mini-card">
      <span>Itens exibidos</span>
      <strong>${products.length}</strong>
    </article>
    <article class="mini-card">
      <span>Unidades</span>
      <strong>${totalUnits}</strong>
    </article>
    <article class="mini-card">
      <span>Valor em estoque</span>
      <strong>${money(totalValue)}</strong>
    </article>
  `;
}

function renderProducts(rows) {
  if (!rows.length) {
    productsTableEl.innerHTML = '<tr><td colspan="9">Nenhum produto encontrado para este filtro.</td></tr>';
    renderProductSummary([]);
    return;
  }

  productsTableEl.innerHTML = rows.map((product) => {
    const actions = ['admin', 'operator'].includes(role) ? `
      <button type="button" class="table-action" data-edit="${product.id}" ${product.active ? '' : 'disabled'}>Editar</button>
      <button type="button" class="table-action" data-toggle="${product.id}" data-active="${product.active}">${product.active ? 'Desativar' : 'Reativar'}</button>
      ${role === 'admin' ? `<button type="button" class="table-action danger-action" data-delete="${product.id}">Remover</button>` : ''}` : '—';
    return `
    <tr>
      <td>${escapeHtml(product.id)}</td>
      <td>${escapeHtml(product.name)}</td>
      <td>${escapeHtml(product.category)}</td>
      <td>${escapeHtml(product.sku)}</td>
      <td>${escapeHtml(product.brand)}</td>
      <td>${money(product.price)}</td>
      <td>${escapeHtml(product.quantity)}</td>
      <td>${product.active ? escapeHtml(productStatus(product.status)) : 'Desativado'}</td>
      <td class="row-actions">${actions}</td>
    </tr>
  `;
  }).join('');

  productsTableEl.querySelectorAll('[data-edit]').forEach((button) => button.addEventListener('click', () => {
    const item = rows.find((product) => product.id === Number(button.dataset.edit));
    if (!item) return;
    productForm.elements.id.value = item.id;
    for (const key of ['name', 'category', 'sku', 'reference', 'brand', 'status', 'price', 'quantity', 'supplier', 'notes']) {
      productForm.elements[key].value = item[key] ?? '';
    }
    document.getElementById('product-form-title').textContent = `Editar produto #${item.id}`;
    document.getElementById('save-product').textContent = 'Salvar alterações';
    document.getElementById('cancel-product-edit').hidden = false;
    productForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }));
  productsTableEl.querySelectorAll('[data-toggle]').forEach((button) => button.addEventListener('click', async () => {
    const action = button.dataset.active === '1' ? 'deactivate' : 'activate';
    if (action === 'deactivate' && !window.confirm('Desativar este produto? Ele sairá dos alertas e dos totais ativos, mas poderá ser reativado depois.')) return;
    try {
      const result = await productAction(button.dataset.toggle, action);
      setStatus(result.message);
      await loadProducts();
    } catch (error) { setStatus(error.message); }
  }));
  productsTableEl.querySelectorAll('[data-delete]').forEach((button) => button.addEventListener('click', async () => {
    if (!window.confirm('Remover definitivamente este produto e os limites/alertas associados?')) return;
    try {
      const result = await productAction(button.dataset.delete, 'delete');
      setStatus(result.message);
      await loadCategories();
      await loadProducts();
    } catch (error) { setStatus(error.message); }
  }));

  renderProductSummary(rows);
}

async function loadCategories() {
  const categories = await getCategories();
  renderCategoryFilters(categories);
}

async function loadProducts() {
  setStatus('Carregando produtos.');
  const allProducts = await getProducts(selectedCategory, showInactiveEl?.checked);
  const query = searchEl.value.trim().toLocaleLowerCase('pt-BR');
  const statusFilter = statusFilterEl.value;
  const products = allProducts.filter((product) => {
    const searchable = [product.name, product.sku, product.brand, product.supplier].join(' ').toLocaleLowerCase('pt-BR');
    return (!query || searchable.includes(query)) && (statusFilter === 'all' || product.status === statusFilter);
  });
  renderProducts(products);
  setStatus(`${products.length} produto(s) exibido(s).`);
}

async function handleProductSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());

  try {
    const id = payload.id;
    delete payload.id;
    const result = id ? await updateProduct(id, payload) : await createProduct(payload);
    form.reset();
    resetEditForm();
    await loadCategories();
    await loadProducts();
    setStatus(result.message || 'Produto criado com sucesso.');
  } catch (error) {
    setStatus(error.message || 'Erro ao criar produto.');
  }
}

function resetEditForm() {
  productForm.elements.id.value = '';
  document.getElementById('product-form-title').textContent = 'Cadastrar produto';
  document.getElementById('save-product').textContent = 'Salvar produto';
  document.getElementById('cancel-product-edit').hidden = true;
}

document.addEventListener('DOMContentLoaded', () => {
  const productForm = document.getElementById('product-form');
  if (productForm) {
    productForm.addEventListener('submit', handleProductSubmit);
    document.getElementById('cancel-product-edit').addEventListener('click', () => {
      productForm.reset();
      resetEditForm();
    });
  }
  showInactiveEl?.addEventListener('change', loadProducts);
  searchEl?.addEventListener('input', loadProducts);
  statusFilterEl?.addEventListener('change', loadProducts);

  Promise.all([loadCategories(), loadProducts()]).catch((error) => {
    console.error(error);
    setStatus(error.message || 'Falha ao carregar os produtos.');
  });
});
