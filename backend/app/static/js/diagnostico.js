// Autodiagnóstico: recomienda servicios según las respuestas. No envía nada: todo ocurre en el navegador.
(function () {
  var form = document.getElementById('diag-form');
  var out = document.getElementById('diag-result');
  if (!form || !out) return;

  function item(nombre, ref, url) {
    var li = document.createElement('li');
    var a = document.createElement('a');
    a.href = url;
    a.textContent = nombre;
    li.appendChild(a);
    if (ref) {
      var s = document.createElement('span');
      s.className = 'ref';
      s.textContent = ref;
      li.appendChild(s);
    }
    return li;
  }

  function actualizar() {
    var marcadas = form.querySelectorAll('input[type="checkbox"]:checked');
    out.textContent = '';
    if (!marcadas.length) {
      var p = document.createElement('p');
      p.className = 'diag-empty';
      p.textContent = 'Marca las preguntas que encajan con tu organización para ver la recomendación.';
      out.appendChild(p);
      return;
    }
    var h = document.createElement('p');
    h.className = 'diag-title';
    h.textContent = marcadas.length === 1 ? 'Te recomendamos revisar' : 'Te recomendamos revisar, por este orden';
    var ul = document.createElement('ul');
    marcadas.forEach(function (c) { ul.appendChild(item(c.dataset.nombre, c.dataset.ref, c.dataset.url)); });
    ul.appendChild(item(out.dataset.baseNombre, 'Primer paso recomendado', out.dataset.baseUrl));
    out.appendChild(h);
    out.appendChild(ul);
    out.classList.remove('pop');
    void out.offsetWidth; // reinicia la animación
    out.classList.add('pop');
  }

  form.addEventListener('change', actualizar);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
})();
