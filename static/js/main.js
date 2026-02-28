// ═══════════════════════════════════════
// main.js — SecureShop Global JavaScript
// Loaded on every page via base.html
// ═══════════════════════════════════════

// ── CSRF Token Helper ──────────────────────────────────────
function getCSRFToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content ||
         document.getElementById('csrfHidden')?.value || '';
}

// ── Toast Notification System ─────────────────────────────
function showToast(message, type = 'success') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = `
      position: fixed; top: 80px; right: 1.5rem; z-index: 9999;
      display: flex; flex-direction: column; gap: 0.5rem;
      pointer-events: none;
    `;
    document.body.appendChild(container);
  }

  const colors = {
    success: { bg: '#2ecc71', icon: '✅' },
    error:   { bg: '#e74c3c', icon: '❌' },
    info:    { bg: '#3498db', icon: 'ℹ️' },
    warning: { bg: '#f39c12', icon: '⚠️' },
  };
  const { bg, icon } = colors[type] || colors.info;

  const toast = document.createElement('div');
  toast.style.cssText = `
    background: ${bg}; color: white;
    padding: 0.75rem 1.25rem; border-radius: 12px;
    font-size: 0.88rem; font-weight: 600;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    display: flex; align-items: center; gap: 0.5rem;
    pointer-events: all;
    transform: translateX(120%); transition: transform 0.35s cubic-bezier(0.175,0.885,0.32,1.275);
    max-width: 320px; min-width: 200px;
  `;
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);

  // Slide in
  requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; });

  // Auto remove
  setTimeout(() => {
    toast.style.transform = 'translateX(120%)';
    setTimeout(() => toast.remove(), 350);
  }, 3000);
}

// ── Mobile Menu Toggle ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const btn   = document.getElementById('mobileMenuBtn');
  const links = document.querySelector('.nav-links');
  if (btn && links) {
    btn.addEventListener('click', () => {
      links.classList.toggle('mobile-open');
      btn.classList.toggle('active');
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!btn.contains(e.target) && !links.contains(e.target)) {
        links.classList.remove('mobile-open');
        btn.classList.remove('active');
      }
    });
  }

  // Auto-dismiss flash messages after 4s
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-10px)';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });
});
