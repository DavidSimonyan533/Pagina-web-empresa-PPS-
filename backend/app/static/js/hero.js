/*
 * Fondo de la portada: una red de nodos en WebGL que se mueve despacio y reacciona al ratón.
 * Todo se dibuja en el navegador: no hay vídeos ni recursos externos.
 * - Si el usuario prefiere movimiento reducido, se dibuja un solo fotograma estático.
 * - Si el navegador no tiene WebGL, el lienzo se oculta y queda el degradado de CSS.
 * - Se pausa cuando la portada no está a la vista o la pestaña está oculta.
 */
(function () {
  'use strict';
  var canvas = document.getElementById('hero-canvas');
  if (!canvas) return;

  var gl = canvas.getContext('webgl', { antialias: true, alpha: true, premultipliedAlpha: true });
  if (!gl) { canvas.hidden = true; return; }

  var reducir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Shaders ----------
  var VS_LINEAS = [
    'attribute vec2 a_pos;',
    'attribute float a_alpha;',
    'uniform vec2 u_res;',
    'varying float v_alpha;',
    'void main() {',
    '  vec2 c = (a_pos / u_res) * 2.0 - 1.0;',
    '  gl_Position = vec4(c.x, -c.y, 0.0, 1.0);',
    '  v_alpha = a_alpha;',
    '}'
  ].join('\n');
  var FS_LINEAS = [
    'precision mediump float;',
    'uniform vec3 u_color;',
    'varying float v_alpha;',
    'void main() { gl_FragColor = vec4(u_color * v_alpha, v_alpha); }'
  ].join('\n');

  var VS_PUNTOS = [
    'attribute vec2 a_pos;',
    'attribute float a_size;',
    'attribute float a_glow;',
    'uniform vec2 u_res;',
    'varying float v_glow;',
    'void main() {',
    '  vec2 c = (a_pos / u_res) * 2.0 - 1.0;',
    '  gl_Position = vec4(c.x, -c.y, 0.0, 1.0);',
    '  gl_PointSize = a_size;',
    '  v_glow = a_glow;',
    '}'
  ].join('\n');
  var FS_PUNTOS = [
    'precision mediump float;',
    'uniform vec3 u_base;',
    'uniform vec3 u_acento;',
    'varying float v_glow;',
    'void main() {',
    '  vec2 p = gl_PointCoord - 0.5;',
    '  float d = length(p);',
    '  float nucleo = smoothstep(0.34, 0.2, d);',
    '  float halo = smoothstep(0.5, 0.0, d) * (0.18 + 0.4 * v_glow);',
    '  vec3 col = mix(u_base, u_acento, v_glow);',
    '  float a = nucleo * (0.75 + 0.25 * v_glow) + halo;',
    '  if (a < 0.01) discard;',
    '  gl_FragColor = vec4(col * a, a);',
    '}'
  ].join('\n');

  function compilar(tipo, src) {
    var s = gl.createShader(tipo);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  function programa(vs, fs) {
    var p = gl.createProgram();
    gl.attachShader(p, compilar(gl.VERTEX_SHADER, vs));
    gl.attachShader(p, compilar(gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    return p;
  }

  var pLineas, pPuntos;
  try {
    pLineas = programa(VS_LINEAS, FS_LINEAS);
    pPuntos = programa(VS_PUNTOS, FS_PUNTOS);
  } catch (e) {
    canvas.hidden = true;
    return;
  }

  var L = {
    pos: gl.getAttribLocation(pLineas, 'a_pos'),
    alpha: gl.getAttribLocation(pLineas, 'a_alpha'),
    res: gl.getUniformLocation(pLineas, 'u_res'),
    color: gl.getUniformLocation(pLineas, 'u_color')
  };
  var P = {
    pos: gl.getAttribLocation(pPuntos, 'a_pos'),
    size: gl.getAttribLocation(pPuntos, 'a_size'),
    glow: gl.getAttribLocation(pPuntos, 'a_glow'),
    res: gl.getUniformLocation(pPuntos, 'u_res'),
    base: gl.getUniformLocation(pPuntos, 'u_base'),
    acento: gl.getUniformLocation(pPuntos, 'u_acento')
  };
  var bufLineas = gl.createBuffer();
  var bufPuntos = gl.createBuffer();

  // Colores de la marca (0-1)
  var LINEA = [0.72, 0.8, 0.94];      // azul grisáceo
  var BASE = [0.78, 0.84, 0.92];       // nodos
  var ACENTO = [0.91, 0.64, 0.09];     // ámbar #e8a317

  // ---------- Estado ----------
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var ancho = 0, alto = 0;
  var nodos = [];
  var paquetes = [];
  var raton = { x: -9999, y: -9999, activo: false };
  var DIST, GROSOR;

  function crearNodos() {
    var area = (ancho * alto) / (dpr * dpr);
    var n = Math.max(36, Math.min(110, Math.round(area / 11000)));
    DIST = 170 * dpr;
    GROSOR = 0.6 * dpr;
    nodos = [];
    for (var i = 0; i < n; i++) {
      nodos.push({
        x: Math.random() * ancho,
        y: Math.random() * alto,
        vx: (Math.random() - 0.5) * 0.22 * dpr,
        vy: (Math.random() - 0.5) * 0.22 * dpr,
        r: (1.6 + Math.random() * 1.8) * dpr,
        glow: 0,
        fase: Math.random() * Math.PI * 2
      });
    }
    paquetes = [];
  }

  function redimensionar() {
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.round(rect.width * dpr));
    var h = Math.max(1, Math.round(rect.height * dpr));
    if (w === ancho && h === alto) return;
    var habia = nodos.length > 0;
    var ax = ancho, ay = alto;
    ancho = canvas.width = w;
    alto = canvas.height = h;
    gl.viewport(0, 0, ancho, alto);
    if (!habia) { crearNodos(); return; }
    // Reescala las posiciones para no "saltar" al cambiar el tamaño
    nodos.forEach(function (n) { n.x *= ancho / ax; n.y *= alto / ay; });
  }

  // ---------- Simulación ----------
  var lineas = [], puntos = [];

  function paso(t, dt) {
    var i, j, a, b, dx, dy, d2, d;
    var D2 = DIST * DIST;
    var RR = (180 * dpr) * (180 * dpr);

    for (i = 0; i < nodos.length; i++) {
      a = nodos[i];
      a.x += a.vx * dt; a.y += a.vy * dt;
      if (a.x < -20) a.x = ancho + 20; else if (a.x > ancho + 20) a.x = -20;
      if (a.y < -20) a.y = alto + 20; else if (a.y > alto + 20) a.y = -20;

      var objetivo = 0;
      if (raton.activo) {
        dx = a.x - raton.x; dy = a.y - raton.y; d2 = dx * dx + dy * dy;
        if (d2 < RR) {
          objetivo = 1 - d2 / RR;
          // Empuje suave alejándose del cursor
          d = Math.sqrt(d2) || 1;
          a.x += (dx / d) * objetivo * 0.6 * dt;
          a.y += (dy / d) * objetivo * 0.6 * dt;
        }
      }
      a.glow += (objetivo - a.glow) * Math.min(1, 0.08 * dt);
    }

    lineas.length = 0;
    var vecinos = [];
    for (i = 0; i < nodos.length; i++) {
      a = nodos[i];
      for (j = i + 1; j < nodos.length; j++) {
        b = nodos[j];
        dx = a.x - b.x; dy = a.y - b.y; d2 = dx * dx + dy * dy;
        if (d2 < D2) {
          var cerca = 1 - Math.sqrt(d2) / DIST;
          var alpha = Math.min(0.8, cerca * (0.32 + 0.55 * Math.max(a.glow, b.glow)));
          // Cada enlace es un rectángulo fino (dos triángulos): se ve igual en todas las tarjetas gráficas
          var len = Math.sqrt(d2) || 1;
          var nx = -dy / len * GROSOR, ny = dx / len * GROSOR;
          lineas.push(
            a.x + nx, a.y + ny, alpha,  a.x - nx, a.y - ny, alpha,  b.x + nx, b.y + ny, alpha,
            b.x + nx, b.y + ny, alpha,  a.x - nx, a.y - ny, alpha,  b.x - nx, b.y - ny, alpha
          );
          vecinos.push(i, j);
        }
      }
    }

    // "Paquetes" de datos que recorren algunos enlaces
    if (!reducir && vecinos.length && paquetes.length < 6 && Math.random() < 0.035 * dt) {
      var k = (Math.floor(Math.random() * (vecinos.length / 2))) * 2;
      paquetes.push({ a: vecinos[k], b: vecinos[k + 1], t: 0, v: 0.008 + Math.random() * 0.01 });
    }

    puntos.length = 0;
    for (i = 0; i < nodos.length; i++) {
      a = nodos[i];
      var pulso = reducir ? 0 : (Math.sin(t * 0.0012 + a.fase) * 0.5 + 0.5) * 0.15;
      puntos.push(a.x, a.y, a.r * 4 * (1 + a.glow * 0.7), Math.min(1, a.glow + pulso));
    }
    for (i = paquetes.length - 1; i >= 0; i--) {
      var pq = paquetes[i];
      pq.t += pq.v * dt;
      if (pq.t >= 1) { paquetes.splice(i, 1); continue; }
      a = nodos[pq.a]; b = nodos[pq.b];
      dx = a.x - b.x; dy = a.y - b.y;
      if (dx * dx + dy * dy > D2) { paquetes.splice(i, 1); continue; }
      puntos.push(a.x + (b.x - a.x) * pq.t, a.y + (b.y - a.y) * pq.t, 12 * dpr, 1);
    }
  }

  function dibujar() {
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); // colores premultiplicados

    gl.useProgram(pLineas);
    gl.uniform2f(L.res, ancho, alto);
    gl.uniform3fv(L.color, LINEA);
    gl.bindBuffer(gl.ARRAY_BUFFER, bufLineas);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(lineas), gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(L.pos);
    gl.vertexAttribPointer(L.pos, 2, gl.FLOAT, false, 12, 0);
    gl.enableVertexAttribArray(L.alpha);
    gl.vertexAttribPointer(L.alpha, 1, gl.FLOAT, false, 12, 8);
    gl.drawArrays(gl.TRIANGLES, 0, lineas.length / 3);
    gl.disableVertexAttribArray(L.alpha);

    gl.useProgram(pPuntos);
    gl.uniform2f(P.res, ancho, alto);
    gl.uniform3fv(P.base, BASE);
    gl.uniform3fv(P.acento, ACENTO);
    gl.bindBuffer(gl.ARRAY_BUFFER, bufPuntos);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(puntos), gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(P.pos);
    gl.vertexAttribPointer(P.pos, 2, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(P.size);
    gl.vertexAttribPointer(P.size, 1, gl.FLOAT, false, 16, 8);
    gl.enableVertexAttribArray(P.glow);
    gl.vertexAttribPointer(P.glow, 1, gl.FLOAT, false, 16, 12);
    gl.drawArrays(gl.POINTS, 0, puntos.length / 4);
    gl.disableVertexAttribArray(P.size);
    gl.disableVertexAttribArray(P.glow);
  }

  // ---------- Bucle ----------
  var visible = true, corriendo = false, ultimo = 0;

  function frame(t) {
    if (!corriendo) return;
    var dt = ultimo ? Math.min(3, (t - ultimo) / 16.67) : 1;
    ultimo = t;
    redimensionar();
    paso(t, dt);
    dibujar();
    requestAnimationFrame(frame);
  }
  function arrancar() {
    if (corriendo || reducir || !visible || document.hidden) return;
    corriendo = true; ultimo = 0;
    requestAnimationFrame(frame);
  }
  function parar() { corriendo = false; }

  redimensionar();
  if (reducir) {
    paso(0, 1);
    dibujar();
  } else {
    arrancar();
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      visible = e[0].isIntersecting;
      if (visible) arrancar(); else parar();
    }).observe(canvas);
  }
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) parar(); else arrancar();
  });
  window.addEventListener('resize', function () {
    redimensionar();
    if (reducir) { paso(0, 1); dibujar(); }
  });

  var hero = canvas.parentElement;
  hero.addEventListener('pointermove', function (e) {
    var r = canvas.getBoundingClientRect();
    raton.x = (e.clientX - r.left) * dpr;
    raton.y = (e.clientY - r.top) * dpr;
    raton.activo = true;
  });
  hero.addEventListener('pointerleave', function () { raton.activo = false; });

  canvas.addEventListener('webglcontextlost', function (e) { e.preventDefault(); parar(); canvas.hidden = true; });

  canvas.classList.add('is-ready');
})();
