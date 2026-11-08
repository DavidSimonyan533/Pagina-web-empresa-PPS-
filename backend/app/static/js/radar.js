/*
 * Radar de vigilancia (canvas 2D): un barrido gira y va iluminando "incidencias".
 * Dibujado en el navegador, sin recursos externos.
 * - Movimiento reducido: dibuja un fotograma estático con las incidencias visibles.
 * - Se pausa cuando no está a la vista o la pestaña está oculta.
 */
(function () {
  'use strict';
  var canvas = document.getElementById('radar-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  if (!ctx) return;

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var size = 440;
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  ctx.scale(dpr, dpr);
  var cx = size / 2, cy = size / 2, R = size / 2 - 10;

  // Incidencias fijas (ángulo en radianes, radio relativo, nivel)
  var blips = [
    { a: 0.6, r: 0.55, nivel: 'minor' },
    { a: 2.1, r: 0.78, nivel: 'obs' },
    { a: 3.4, r: 0.4, nivel: 'ok' },
    { a: 4.3, r: 0.68, nivel: 'minor' },
    { a: 5.5, r: 0.5, nivel: 'obs' }
  ];
  var COLORES = { minor: '#e5614a', obs: '#f0b429', ok: '#36c9a6' };

  function rejilla() {
    ctx.clearRect(0, 0, size, size);
    // Círculos concéntricos
    ctx.strokeStyle = 'rgba(145, 170, 210, 0.25)';
    ctx.lineWidth = 1;
    for (var i = 1; i <= 4; i++) {
      ctx.beginPath();
      ctx.arc(cx, cy, (R * i) / 4, 0, Math.PI * 2);
      ctx.stroke();
    }
    // Ejes
    ctx.beginPath();
    ctx.moveTo(cx - R, cy); ctx.lineTo(cx + R, cy);
    ctx.moveTo(cx, cy - R); ctx.lineTo(cx, cy + R);
    ctx.stroke();
  }

  function dibujarBlip(b, intensidad) {
    var x = cx + Math.cos(b.a) * b.r * R;
    var y = cy + Math.sin(b.a) * b.r * R;
    var col = COLORES[b.nivel];
    ctx.globalAlpha = 0.25 + 0.75 * intensidad;
    ctx.fillStyle = col;
    ctx.beginPath();
    ctx.arc(x, y, 4 + 3 * intensidad, 0, Math.PI * 2);
    ctx.fill();
    if (intensidad > 0.05) {
      ctx.globalAlpha = 0.25 * intensidad;
      ctx.beginPath();
      ctx.arc(x, y, 10 + 16 * intensidad, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  var angulo = -Math.PI / 2;
  var intens = blips.map(function () { return 0; });

  function barrido() {
    // Estela del haz
    var grad = ctx.createConicGradient ? null : null;
    ctx.save();
    ctx.translate(cx, cy);
    for (var k = 0; k < 40; k++) {
      var a = angulo - k * 0.03;
      ctx.strokeStyle = 'rgba(232, 163, 23, ' + (0.18 * (1 - k / 40)) + ')';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(a) * R, Math.sin(a) * R);
      ctx.stroke();
    }
    // Haz principal
    ctx.strokeStyle = 'rgba(232, 163, 23, 0.9)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(angulo) * R, Math.sin(angulo) * R);
    ctx.stroke();
    // Punto central
    ctx.fillStyle = '#e8a317';
    ctx.beginPath();
    ctx.arc(0, 0, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function frame() {
    if (!corriendo) return;
    angulo += 0.02;
    if (angulo > Math.PI * 1.5) angulo -= Math.PI * 2;
    rejilla();
    blips.forEach(function (b, i) {
      // Diferencia angular entre el haz y la incidencia
      var d = Math.abs(((b.a - angulo + Math.PI * 3) % (Math.PI * 2)) - Math.PI);
      if (d < 0.12) intens[i] = 1;            // el haz la acaba de pasar
      else intens[i] = Math.max(0, intens[i] - 0.012); // se apaga poco a poco
      dibujarBlip(b, intens[i]);
    });
    barrido();
    requestAnimationFrame(frame);
  }

  var corriendo = false, visible = false;
  function arrancar() { if (corriendo || reduce || !visible || document.hidden) return; corriendo = true; requestAnimationFrame(frame); }
  function parar() { corriendo = false; }

  function estatico() {
    rejilla();
    blips.forEach(function (b) { dibujarBlip(b, 1); });
    ctx.save(); ctx.translate(cx, cy);
    ctx.fillStyle = '#e8a317';
    ctx.beginPath(); ctx.arc(0, 0, 3, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  if (reduce) { estatico(); return; }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      visible = e[0].isIntersecting;
      if (visible) arrancar(); else parar();
    }, { threshold: 0.2 }).observe(canvas);
  } else { visible = true; arrancar(); }
  document.addEventListener('visibilitychange', function () { if (document.hidden) parar(); else arrancar(); });
})();
