/*
 * Efectos visuales de Davem Cyber Consulting.
 * Todo es JavaScript propio, sin librerías ni recursos externos.
 * Cada efecto se desactiva solo si el usuario prefiere movimiento reducido.
 */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(pointer: fine)').matches;
  var doc = document.documentElement;
  doc.classList.add('js');

  // ---- 1. Barra de progreso de scroll ----
  var bar = document.createElement('div');
  bar.className = 'scroll-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  function progreso() {
    var h = doc.scrollHeight - doc.clientHeight;
    var p = h > 0 ? (window.scrollY / h) : 0;
    bar.style.transform = 'scaleX(' + Math.min(1, Math.max(0, p)) + ')';
  }

  // ---- 2. Botón "volver arriba" ----
  var up = document.createElement('button');
  up.type = 'button';
  up.className = 'to-top';
  up.setAttribute('aria-label', 'Volver arriba');
  up.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V6M6 12l6-6 6 6"/></svg>';
  up.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });
  document.body.appendChild(up);
  function verBoton() { up.classList.toggle('show', window.scrollY > 600); }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { progreso(); verBoton(); lecturaBlog(); ticking = false; });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', progreso, { passive: true });
  progreso(); verBoton();

  // ---- 3. Aparición al hacer scroll (con escalonado) ----
  var items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) || reduce) {
    items.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
  }

  // ---- 4. Foco de luz que sigue al cursor en las tarjetas ----
  if (finePointer && !reduce) {
    var spots = document.querySelectorAll('.svc-card, .pack, .case, .post-card, .value, .cred');
    spots.forEach(function (card) {
      card.classList.add('spot');
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        card.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });
  }

  // ---- 5. Botones magnéticos ----
  if (finePointer && !reduce) {
    document.querySelectorAll('.btn-lg, .cta-v4 .btn, .cta .btn').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        var dx = (e.clientX - (r.left + r.width / 2)) / r.width;
        var dy = (e.clientY - (r.top + r.height / 2)) / r.height;
        b.style.transform = 'translate(' + (dx * 8).toFixed(1) + 'px,' + (dy * 8).toFixed(1) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  }

  // ---- 6. Progreso de lectura en artículos del blog ----
  var articulo = document.querySelector('.article');
  var leerBar = null;
  if (articulo) {
    leerBar = document.createElement('div');
    leerBar.className = 'read-progress';
    leerBar.setAttribute('aria-hidden', 'true');
    leerBar.innerHTML = '<span></span>';
    articulo.parentNode.insertBefore(leerBar, articulo);
  }
  function lecturaBlog() {
    if (!leerBar || !articulo) return;
    var r = articulo.getBoundingClientRect();
    var total = r.height - window.innerHeight;
    var leido = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 1;
    leerBar.firstChild.style.transform = 'scaleX(' + leido + ')';
  }

  // ---- 7. Medidor de fuerza de la contraseña ----
  var pass = document.getElementById('password');
  if (pass) {
    var medidor = document.createElement('div');
    medidor.className = 'pw-meter';
    medidor.innerHTML = '<span class="pw-track"><span class="pw-fill"></span></span><span class="pw-text" aria-live="polite"></span>';
    pass.parentNode.appendChild(medidor);
    var fill = medidor.querySelector('.pw-fill');
    var txt = medidor.querySelector('.pw-text');
    var niveles = [
      { t: 'Muy débil', c: '#a8321f' },
      { t: 'Débil', c: '#a8321f' },
      { t: 'Aceptable', c: '#8a5a00' },
      { t: 'Buena', c: '#1d6f60' },
      { t: 'Excelente', c: '#1d6f60' }
    ];
    pass.addEventListener('input', function () {
      var v = pass.value, s = 0;
      if (v.length >= 12) s++;
      if (v.length >= 16) s++;
      if (/[a-z]/.test(v) && /[A-Z]/.test(v)) s++;
      if (/\d/.test(v) || /[^\w]/.test(v)) s++;
      if (!v) { fill.style.width = '0'; txt.textContent = ''; return; }
      s = Math.min(4, s);
      var n = niveles[s];
      fill.style.width = ((s + 1) * 20) + '%';
      fill.style.background = n.c;
      txt.textContent = n.t;
      txt.style.color = n.c;
    });
  }
})();

// ---- 8. Números que cuentan hacia arriba al aparecer ----
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var nums = document.querySelectorAll('.count');
  if (!nums.length) return;
  function animar(el) {
    var destino = parseInt(el.getAttribute('data-to'), 10) || 0;
    var sufijo = el.getAttribute('data-suffix') || '';
    if (reduce) { el.textContent = destino + sufijo; return; }
    var t0 = null, dur = 1100;
    function paso(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / dur);
      var e = 1 - Math.pow(1 - p, 3); // easing suave
      el.textContent = Math.round(destino * e) + sufijo;
      if (p < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }
  if (!('IntersectionObserver' in window)) { nums.forEach(animar); return; }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { animar(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.6 });
  nums.forEach(function (n) { io.observe(n); });
})();

// ---- 9. Buscador de servicios (filtra la lista al escribir) ----
(function () {
  var input = document.getElementById('svc-filter');
  if (!input) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.service[data-buscar]'));
  var vacio = document.getElementById('svc-empty');
  function quitarTildes(s) { return s.normalize ? s.normalize('NFD').replace(/[̀-ͯ]/g, '') : s; }
  input.addEventListener('input', function () {
    var q = quitarTildes(input.value.trim().toLowerCase());
    var visibles = 0;
    cards.forEach(function (c) {
      var hay = !q || quitarTildes(c.getAttribute('data-buscar')).indexOf(q) !== -1;
      c.classList.toggle('oculto', !hay);
      if (hay) visibles++;
    });
    if (vacio) vacio.classList.toggle('show', visibles === 0);
  });
})();
