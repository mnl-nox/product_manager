import { createProduct, getCategories, getProducts } from './api.js';

const categoryFilterEl = document.getElementById('category-filters');
const productSummaryEl = document.getElementById('product-summary');
const productsTableEl = document.getElementById('products-table');
let selectedCategory = 'all';
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
    productsTableEl.innerHTML = '<tr><td colspan="8">Nenhum produto encontrado para este filtro.</td></tr>';
    renderProductSummary([]);
    return;
  }

  productsTableEl.innerHTML = rows.map((product) => `
    <tr>
      <td>${escapeHtml(product.id)}</td>
      <td>${escapeHtml(product.name)}</td>
      <td>${escapeHtml(product.category)}</td>
      <td>${escapeHtml(product.sku)}</td>
      <td>${escapeHtml(product.brand)}</td>
      <td>${money(product.price)}</td>
      <td>${escapeHtml(product.quantity)}</td>
      <td>${escapeHtml(product.status)}</td>
    </tr>
  `).join('');

  renderProductSummary(rows);
}

async function loadCategories() {
  const categories = await getCategories();
  renderCategoryFilters(categories);
}

async function loadProducts() {
  setStatus('Carregando produtos.');
  const products = await getProducts(selectedCategory);
  renderProducts(products);
  setStatus(`${products.length} produto(s) exibido(s).`);
}

async function handleProductSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = Object.fromEntries(new FormData(form).entries());

  try {
    const result = await createProduct(payload);
    form.reset();
    await loadCategories();
    await loadProducts();
    setStatus(result.message || 'Produto criado com sucesso.');
  } catch (error) {
    setStatus(error.message || 'Erro ao criar produto.');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const productForm = document.getElementById('product-form');
  if (productForm) {
    productForm.addEventListener('submit', handleProductSubmit);
  }

  Promise.all([loadCategories(), loadProducts()]).catch((error) => {
    console.error(error);
    setStatus(error.message || 'Falha ao carregar os produtos.');
  });
});
