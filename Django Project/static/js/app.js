/**
 * app.js — General UI interactions for CityMender SA
 */
(function () {
  'use strict';

  /* ── Django template filter: dict_get polyfill ───────── */
  // Note: dict_get template tag is handled server-side.
  // This file handles client-side interactions only.

  /* ── Auto-dismiss flash messages ─────────────────────── */
  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.4s';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 400);
    }, 4000);
  });

  /* ── Map panel drag to expand ────────────────────────── */
  const panel = document.getElementById('map-panel');
  if (panel) {
    let startY = 0;
    let startH = 0;
    const handle = panel.querySelector('.map-panel__handle');
    if (handle) {
      handle.addEventListener('touchstart', (e) => {
        startY = e.touches[0].clientY;
        startH = panel.offsetHeight;
      }, { passive: true });
      handle.addEventListener('touchmove', (e) => {
        const dy = startY - e.touches[0].clientY;
        const newH = Math.min(Math.max(startH + dy, 80), window.innerHeight * 0.75);
        panel.style.maxHeight = newH + 'px';
      }, { passive: true });
    }
  }

  /* ── Smooth scroll to form errors ───────────────────── */
  const firstError = document.querySelector('.field-error, .form-error-banner');
  if (firstError) {
    firstError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  /* ── Voice lang select styling ───────────────────────── */
  const langSelect = document.querySelector('.voice-lang-select');
  if (langSelect) {
    Object.assign(langSelect.style, {
      display: 'block',
      width: '100%',
      marginTop: '6px',
      padding: '8px 12px',
      border: '1.5px solid var(--border)',
      borderRadius: '8px',
      fontFamily: 'var(--font-body)',
      fontSize: '13px',
      color: 'var(--ink)',
      background: '#fff',
      cursor: 'pointer',
    });
  }

  /* ── Category item selection feedback ─────────────────── */
  document.querySelectorAll('.cat-item').forEach(item => {
    item.addEventListener('click', () => {
      item.style.transform = 'scale(0.96)';
      setTimeout(() => { item.style.transform = ''; }, 150);
    });
  });

})();
