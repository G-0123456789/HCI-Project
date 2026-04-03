/**
 * offline.js — Offline detection + IndexedDB queue for deferred reports
 * Service Worker is registered from here.
 */
(function () {
  'use strict';

  const DB_NAME = 'citymender_offline';
  const STORE   = 'pending_reports';

  /* ── Connectivity indicator ─────────────────────────── */
  function updateConnectivity() {
    const banner = document.getElementById('offline-banner');
    const icon   = document.getElementById('connectivity-icon');
    const online = navigator.onLine;

    if (banner) banner.hidden = online;
    if (icon)   icon.textContent = online ? '📶' : '📵';
    if (icon)   icon.title       = online ? 'Online' : 'Offline';

    if (online) syncPendingReports();
  }

  window.addEventListener('online',  updateConnectivity);
  window.addEventListener('offline', updateConnectivity);
  updateConnectivity();

  /* ── IndexedDB helpers ──────────────────────────────── */
  function openDB() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, 1);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(STORE)) {
          db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror   = () => reject(req.error);
    });
  }

  async function saveReportOffline(formData) {
    const db = await openDB();
    const data = {};
    for (const [k, v] of formData.entries()) {
      if (typeof v === 'string') data[k] = v;
    }
    data.timestamp = Date.now();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).add(data);
      tx.oncomplete = () => resolve();
      tx.onerror    = () => reject(tx.error);
    });
  }

  async function getPendingReports() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx  = db.transaction(STORE, 'readonly');
      const req = tx.objectStore(STORE).getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror   = () => reject(req.error);
    });
  }

  async function deletePendingReport(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).delete(id);
      tx.oncomplete = () => resolve();
      tx.onerror    = () => reject(tx.error);
    });
  }

  async function syncPendingReports() {
    if (!navigator.onLine) return;
    let reports;
    try { reports = await getPendingReports(); }
    catch (e) { return; }

    for (const report of reports) {
      try {
        const fd = new FormData();
        for (const [k, v] of Object.entries(report)) {
          if (k !== 'id') fd.append(k, v);
        }
        const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
        const res = await fetch('/report/submit/', {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken },
          body: fd,
        });
        if (res.ok || res.redirected) {
          await deletePendingReport(report.id);
        }
      } catch (e) {
        break; // stay offline
      }
    }
  }

  /* ── Intercept report form for offline queue ─────────── */
  document.addEventListener('DOMContentLoaded', () => {
    const reportForm = document.getElementById('report-form');
    if (!reportForm) return;

    reportForm.addEventListener('submit', async (e) => {
      if (navigator.onLine) return; // let normal submit proceed

      e.preventDefault();
      const fd = new FormData(reportForm);
      try {
        await saveReportOffline(fd);
        // Show offline confirmation
        const banner = document.createElement('div');
        banner.className = 'message message--info';
        banner.textContent = '📴 Saved offline — will be submitted when you reconnect.';
        reportForm.prepend(banner);
        setTimeout(() => banner.remove(), 5000);
      } catch (err) {
        console.error('Could not save offline:', err);
      }
    });
  });

  /* ── Service Worker registration ────────────────────── */
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/sw.js', { scope: '/' })
      .then(reg => console.log('[SW] Registered, scope:', reg.scope))
      .catch(err => console.warn('[SW] Registration failed:', err));
  }

  // Expose sync for debugging
  window._citymender = { syncPendingReports, getPendingReports };
})();
