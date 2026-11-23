// veronikabrixi.cz — mobilní menu, lightbox certifikátů, potvrzení formuláře
(function () {
  var doc = document.documentElement;
  var burger = document.querySelector('.burger');
  if (burger) {
    burger.addEventListener('click', function () {
      var open = doc.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.setAttribute('aria-label', open ? 'Zavřít menu' : 'Otevřít menu');
    });
    document.querySelectorAll('.mobile-nav a').forEach(function (a) {
      a.addEventListener('click', function () {
        doc.classList.remove('nav-open');
        burger.setAttribute('aria-expanded', 'false');
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && doc.classList.contains('nav-open')) {
        doc.classList.remove('nav-open');
        burger.setAttribute('aria-expanded', 'false');
        burger.focus();
      }
    });
  }

  var box = document.querySelector('dialog.lightbox');
  if (box && box.showModal) {
    var img = box.querySelector('img');
    document.querySelectorAll('[data-lightbox]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        img.src = btn.getAttribute('data-lightbox');
        img.alt = btn.querySelector('img').alt;
        box.showModal();
      });
    });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
  }

  var tema = (location.search.match(/[?&]tema=([\w-]+)/) || [])[1];
  if (tema) {
    var opt = document.querySelector('#f-topic option[data-key="' + tema + '"]');
    if (opt) opt.selected = true;
  }

  if (location.search.indexOf('odeslano=1') !== -1) {
    var ok = document.querySelector('.form-ok');
    if (ok) { ok.classList.add('show'); ok.focus(); }
  }
})();
