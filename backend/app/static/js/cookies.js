/*
 * Consentimiento de cookies conforme a la guía de la AEPD:
 * - "Rechazar" tan visible como "Aceptar" en la primera capa.
 * - Panel de configuración por categorías.
 * - Nada no esencial se activa sin consentimiento.
 * Esta web solo usa cookies técnicas (la sesión). La categoría de analítica es
 * una demostración didáctica: no carga nada externo, solo guarda tu elección.
 */
(function () {
  'use strict';
  var CLAVE = 'davem_cookies_v1';
  var banner, panel;

  function leer() {
    try { return JSON.parse(localStorage.getItem(CLAVE) || 'null'); } catch (e) { return null; }
  }
  function guardar(obj) {
    obj.fecha = new Date().toISOString();
    try { localStorage.setItem(CLAVE, JSON.stringify(obj)); } catch (e) {}
  }

  function construir() {
    banner = document.createElement('div');
    banner.className = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Aviso de cookies');
    banner.setAttribute('aria-live', 'polite');
    banner.innerHTML =
      '<div class="cookie-inner">' +
        '<div class="cookie-text">' +
          '<h2>Cookies</h2>' +
          '<p>Usamos cookies técnicas, necesarias para iniciar sesión y proteger los formularios. ' +
          'Las cookies opcionales solo se activan si las aceptas. Más información en la ' +
          '<a href="/cookies">política de cookies</a>.</p>' +
        '</div>' +
        '<div class="cookie-actions">' +
          '<button type="button" class="btn btn-small" data-cookie="all">Aceptar todas</button>' +
          '<button type="button" class="btn btn-small btn-ghost" data-cookie="reject">Rechazar</button>' +
          '<button type="button" class="link-button" data-cookie="config">Configurar</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(banner);
    banner.addEventListener('click', function (e) {
      var a = e.target.getAttribute('data-cookie');
      if (a === 'all') aceptar({ analitica: true });
      else if (a === 'reject') aceptar({ analitica: false });
      else if (a === 'config') abrirPanel();
    });
  }

  function abrirPanel() {
    var pref = leer() || { analitica: false };
    panel = document.createElement('div');
    panel.className = 'cookie-modal';
    panel.innerHTML =
      '<div class="cookie-dialog" role="dialog" aria-modal="true" aria-labelledby="ck-tit">' +
        '<h2 id="ck-tit">Preferencias de cookies</h2>' +
        '<p>Elige qué cookies quieres permitir. Puedes cambiarlo cuando quieras desde el pie de página.</p>' +
        '<div class="cookie-cat">' +
          '<div class="cookie-cat-head"><strong>Técnicas (necesarias)</strong>' +
          '<span class="cookie-always">Siempre activas</span></div>' +
          '<p>Mantienen tu sesión iniciada y protegen los formularios frente a ataques CSRF. Sin ellas la web no funciona.</p>' +
        '</div>' +
        '<div class="cookie-cat">' +
          '<div class="cookie-cat-head"><label for="ck-an"><strong>Analítica (demostración)</strong></label>' +
          '<label class="cookie-sw"><input type="checkbox" id="ck-an"' + (pref.analitica ? ' checked' : '') + '><span class="diag-switch"></span></label></div>' +
          '<p>En una web real medirían las visitas de forma anónima. Aquí no se carga ningún servicio externo: es un ejemplo para el proyecto.</p>' +
        '</div>' +
        '<div class="cookie-dialog-actions">' +
          '<button type="button" class="btn" data-ck="save">Guardar preferencias</button>' +
          '<button type="button" class="btn btn-ghost" data-ck="all">Aceptar todas</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(panel);
    document.body.classList.add('no-scroll');
    var chk = panel.querySelector('#ck-an');
    panel.addEventListener('click', function (e) {
      if (e.target === panel) cerrarPanel();
      var a = e.target.getAttribute('data-ck');
      if (a === 'save') { aceptar({ analitica: chk.checked }); cerrarPanel(); }
      else if (a === 'all') { chk.checked = true; aceptar({ analitica: true }); cerrarPanel(); }
    });
    document.addEventListener('keydown', escPanel);
    var primero = panel.querySelector('button, input');
    if (primero) primero.focus();
  }
  function escPanel(e) { if (e.key === 'Escape') cerrarPanel(); }
  function cerrarPanel() {
    if (panel) { panel.remove(); panel = null; }
    document.body.classList.remove('no-scroll');
    document.removeEventListener('keydown', escPanel);
  }

  function aceptar(pref) {
    guardar(pref);
    if (banner) { banner.classList.add('hide'); setTimeout(function () { if (banner) banner.remove(); }, 400); }
  }

  // Enlace del pie para reabrir las preferencias
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-cookie-config]');
    if (t) { e.preventDefault(); abrirPanel(); }
  });

  if (!leer()) {
    // Pequeño retardo para no competir con la animación de entrada de la página
    setTimeout(construir, 700);
  }
})();
