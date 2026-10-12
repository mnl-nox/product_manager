const brandContainer = document.querySelector('.brand-block') || document.querySelector('.auth-panel');
const heading = brandContainer?.querySelector('h1');

if (heading) {
  const badge = document.createElement('span');
  badge.className = 'opensource-badge';
  badge.setAttribute('aria-label', 'Software de código aberto, licença MIT');
  badge.innerHTML = '<img src="/assets/icons/open-source-mark.svg" alt="" width="16" height="16"><span>Open Source · MIT</span>';
  heading.after(badge);
}
