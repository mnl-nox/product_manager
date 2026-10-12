const loginForm = document.getElementById('login-form');
const setupForm = document.getElementById('setup-form');
const loginMessage = document.getElementById('login-message');
const setupMessage = document.getElementById('setup-message');

const setupToken = new URLSearchParams(window.location.hash.slice(1)).get('setup_token');
if (setupToken) {
  setupForm.elements.setup_token.value = setupToken;
  history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
}

async function submitJson(path, form, messageEl) {
  messageEl.textContent = 'Processando…';
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Não foi possível concluir o acesso.');
    window.location.replace('/dashboard');
  } catch (error) {
    messageEl.textContent = error.message || 'Falha de conexão.';
  }
}

loginForm.addEventListener('submit', (event) => {
  event.preventDefault();
  submitJson('/api/auth/login', loginForm, loginMessage);
});

setupForm.addEventListener('submit', (event) => {
  event.preventDefault();
  submitJson('/api/auth/setup', setupForm, setupMessage);
});

fetch('/api/auth/setup-status', { headers: { Accept: 'application/json' } })
  .then((response) => response.json())
  .then((state) => {
    const panel = document.getElementById('setup-panel');
    if (state.setupRequired) {
      panel.hidden = false;
      if (!state.setupAvailable) {
        setupMessage.textContent = 'Configure PRODUCT_MANAGER_SETUP_TOKEN no ambiente do servidor para iniciar.';
        setupForm.querySelectorAll('input, button').forEach((element) => { element.disabled = true; });
      }
    } else {
      panel.hidden = true;
    }
  })
  .catch(() => {});

fetch('/api/auth/me', { headers: { Accept: 'application/json' } })
  .then((response) => { if (response.ok) window.location.replace('/dashboard'); })
  .catch(() => {});
