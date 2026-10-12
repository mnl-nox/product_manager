const installButton = document.getElementById('install-app');
const telemetryConsent = document.getElementById('telemetry-consent');
let installPrompt;

const TELEMETRY_KEY = 'product-manager-diagnostic-consent';
let telemetryEnabled = false;
try {
  telemetryEnabled = localStorage.getItem(TELEMETRY_KEY) === 'true';
  if (telemetryConsent) telemetryConsent.checked = telemetryEnabled;
  telemetryConsent?.addEventListener('change', () => {
    telemetryEnabled = telemetryConsent.checked;
    localStorage.setItem(TELEMETRY_KEY, String(telemetryEnabled));
  });
} catch {
  if (telemetryConsent) telemetryConsent.disabled = true;
}

async function reportDiagnostic(event) {
  if (!telemetryEnabled) return;
  try {
    await fetch('/api/telemetry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event }),
      keepalive: true,
    });
  } catch {
    // Diagnostics are best effort and never interrupt normal use.
  }
}

window.addEventListener('error', () => reportDiagnostic('javascript_error'));
window.addEventListener('unhandledrejection', () => reportDiagnostic('unhandled_rejection'));

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').catch((error) => {
      console.error('Não foi possível registrar o modo offline.', error);
    });
  });
}

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  installPrompt = event;
  if (installButton) installButton.hidden = false;
});

installButton?.addEventListener('click', async () => {
  if (!installPrompt) return;
  installPrompt.prompt();
  await installPrompt.userChoice;
  installPrompt = null;
  installButton.hidden = true;
});

window.addEventListener('appinstalled', () => {
  if (installButton) installButton.hidden = true;
  installPrompt = null;
});
