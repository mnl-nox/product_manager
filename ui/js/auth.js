import { setCsrfToken } from './api.js';

const response = await fetch('/api/auth/me', { headers: { Accept: 'application/json' } });
if (!response.ok) {
  window.location.replace('/login');
} else {
  const session = await response.json();
  setCsrfToken(session.csrfToken);
  const nav = document.querySelector('.nav-links');
  const user = session.user;
  document.documentElement.dataset.role = user.role;
  if (user.role !== 'admin' && user.role !== 'finance') {
    document.querySelectorAll('a[href="/finance"]').forEach((link) => { link.hidden = true; });
  }
  if (user.role !== 'admin') {
    document.querySelectorAll('a[href="/admin/users"]').forEach((link) => { link.hidden = true; });
  }
  if (nav) {
    if (user.role === 'admin' || user.role === 'finance') {
      const financeLink = document.createElement('a');
      financeLink.href = '/finance';
      financeLink.textContent = 'Financeiro';
      nav.append(financeLink);
    }
    const alertLink = document.createElement('a');
    alertLink.href = '/alerts';
    alertLink.textContent = 'Alertas';
    nav.append(alertLink);
    const workItemsLink = document.createElement('a');
    workItemsLink.href = '/work-items';
    workItemsLink.textContent = 'Riscos e bugs';
    nav.append(workItemsLink);
    if (user.role === 'admin') {
      const usersLink = document.createElement('a');
      usersLink.href = '/admin/users';
      usersLink.textContent = 'Usuários';
      nav.append(usersLink);
      const hrLink = document.createElement('a');
      hrLink.href = '/hr';
      hrLink.textContent = 'Recursos humanos';
      nav.append(hrLink);
    }
    const identity = document.createElement('span');
    identity.className = 'session-identity';
    identity.textContent = `${user.username} · ${user.role}`;
    nav.append(identity);
    const logout = document.createElement('button');
    logout.type = 'button';
    logout.className = 'secondary-action';
    logout.textContent = 'Sair';
    logout.addEventListener('click', async () => {
      await fetch('/api/auth/logout', { method: 'POST', headers: { 'X-CSRF-Token': session.csrfToken } });
      window.location.replace('/login');
    });
    nav.append(logout);
  }
  const googleExport = document.getElementById('export-google-sheets');
  if (googleExport && user.role !== 'admin') googleExport.hidden = true;
  if (user.role === 'viewer' || user.role === 'finance') {
    document.querySelectorAll('[data-permission="catalog:write"]').forEach((element) => { element.hidden = true; });
  }
  if (user.role !== 'admin' && user.role !== 'finance') {
    document.querySelectorAll('[data-permission="finance:write"]').forEach((element) => { element.hidden = true; });
  }
}
