// Calculadora de presupuesto orientativo. Lee los datos de los atributos data-* del formulario.
(function () {
  var form = document.getElementById('calculadora');
  if (!form) return;
  var servicio = document.getElementById('calc-servicio');
  var tamano = document.getElementById('calc-tamano');
  var salida = document.getElementById('calc-resultado');

  function euros(n) {
    // Separador de miles con punto también en cifras de 4 dígitos (1.500 €)
    return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' €';
  }
  function redondear(n) { return Math.round(n / 50) * 50; }

  function calcular() {
    var s = servicio.options[servicio.selectedIndex];
    var t = tamano.options[tamano.selectedIndex];
    var p = form.querySelector('input[name="plazo"]:checked');
    var factor = parseFloat(t.dataset.factor) * (p ? parseFloat(p.dataset.factor) : 1);
    var min = redondear(parseFloat(s.dataset.min) * factor);
    var max = redondear(parseFloat(s.dataset.max) * factor);
    var unidad = s.dataset.unidad || '';
    salida.textContent = '';
    var etiqueta = document.createElement('span');
    etiqueta.className = 'calc-label';
    etiqueta.textContent = 'Estimación orientativa';
    var rango = document.createElement('strong');
    rango.textContent = euros(min) + ' – ' + euros(max) + unidad;
    var iva = document.createElement('span');
    iva.className = 'calc-iva';
    iva.textContent = 'sin IVA';
    salida.appendChild(etiqueta);
    salida.appendChild(rango);
    salida.appendChild(iva);
  }

  form.addEventListener('change', calcular);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  calcular();
})();
