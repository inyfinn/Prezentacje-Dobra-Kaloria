/* Dobra Kaloria - galeria komponentów.
   Odczytuje żywe zmienne --dk-* z tokens.css (nic nie jest przepisane ręcznie),
   liczy kontrast WCAG i uruchamia kilka żywych przykładów (suwak, przełączniki, strefa upuszczania, toast). */
(function () {
  'use strict';

  var root = document.documentElement;
  var cs = getComputedStyle(root);

  /* ---------- odczyt tokenów ---------- */
  function collectTokens() {
    var out = [];
    for (var i = 0; i < document.styleSheets.length; i++) {
      var sh = document.styleSheets[i];
      if (!sh.href || sh.href.indexOf('tokens.css') === -1) continue;
      var rules;
      try { rules = sh.cssRules; } catch (e) { continue; }
      for (var j = 0; j < rules.length; j++) {
        var st = rules[j].style;
        if (!st) continue;
        for (var k = 0; k < st.length; k++) {
          var n = st[k];
          if (n.indexOf('--dk-') === 0) out.push({ name: n, raw: st.getPropertyValue(n).trim() });
        }
      }
    }
    return out;
  }
  var TOKENS = collectTokens();

  function val(name) { return cs.getPropertyValue(name).trim(); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function code(text) { return el('code', null, text); }

  /* ---------- kolor: CSS -> rgb -> hex, kontrast ---------- */
  var probe = document.createElement('span');
  probe.style.display = 'none';
  document.body.appendChild(probe);
  function rgbOf(cssColor) {
    probe.style.color = '';
    probe.style.color = cssColor;
    var c = getComputedStyle(probe).color;
    return c.match(/[\d.]+/g).slice(0, 3).map(Number);
  }
  function hexOf(rgb) {
    return '#' + rgb.map(function (v) { return Math.round(v).toString(16).padStart(2, '0'); }).join('').toUpperCase();
  }
  function lum(rgb) {
    var c = rgb.map(function (v) {
      v = v / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
  }
  function contrast(a, b) {
    var la = lum(a), lb = lum(b);
    var hi = Math.max(la, lb), lo = Math.min(la, lb);
    return (hi + 0.05) / (lo + 0.05);
  }
  function fmt(r) { return r.toFixed(2).replace('.', ',') + ':1'; }
  function role(n) { return 'var(--dk-color-' + n + ')'; }

  /* ---------- kolory: grupy i pary (tło/tekst) ---------- */
  var GROUPS = [
    ['Tekst', ['text', 'text-muted', 'label', 'on-brand', 'on-cta', 'on-inverse', 'warning-text']],
    ['Powierzchnie', ['bg', 'surface', 'surface-hover', 'disabled-bg', 'inverse-bg']],
    ['Marka i przycisk główny (CTA)', ['brand', 'brand-hover', 'brand-soft', 'brand-soft-strong', 'cta', 'cta-hover']],
    ['Obramowania i fokus', ['border', 'border-strong', 'field-border', 'switch-off', 'focus']],
    ['Statusy', ['danger', 'danger-soft', 'warning-bg', 'warning-border']]
  ];
  /* chipBg/chipFg: co pokazać na próbce; a/b: para do kontrastu; min: wymagane minimum (null = dekoracja) */
  var PAIRS = {
    'text':              { chipBg: 'bg', chipFg: 'text', a: 'text', b: 'bg', min: 4.5, vs: 'na bg' },
    'text-muted':        { chipBg: 'bg', chipFg: 'text-muted', a: 'text-muted', b: 'bg', min: 4.5, vs: 'na bg' },
    'label':             { chipBg: 'bg', chipFg: 'label', a: 'label', b: 'bg', min: 3, vs: 'na bg', warn: 'tylko etykiety, pogrubione, min. 15 px' },
    'on-brand':          { chipBg: 'brand', chipFg: 'on-brand', a: 'on-brand', b: 'brand', min: 4.5, vs: 'na brand' },
    'on-cta':            { chipBg: 'cta', chipFg: 'on-cta', a: 'on-cta', b: 'cta', min: 4.5, vs: 'na cta' },
    'on-inverse':        { chipBg: 'inverse-bg', chipFg: 'on-inverse', a: 'on-inverse', b: 'inverse-bg', min: 4.5, vs: 'na inverse-bg' },
    'warning-text':      { chipBg: 'warning-bg', chipFg: 'warning-text', a: 'warning-text', b: 'warning-bg', min: 4.5, vs: 'na warning-bg' },
    'bg':                { chipBg: 'bg', chipFg: 'text', a: 'text', b: 'bg', min: 4.5, vs: 'z text' },
    'surface':           { chipBg: 'surface', chipFg: 'text', a: 'text', b: 'surface', min: 4.5, vs: 'z text' },
    'surface-hover':     { chipBg: 'surface-hover', chipFg: 'text', a: 'text', b: 'surface-hover', min: 4.5, vs: 'z text' },
    'disabled-bg':       { chipBg: 'disabled-bg', chipFg: 'text-muted', a: 'text-muted', b: 'disabled-bg', min: 4.5, vs: 'z text-muted' },
    'inverse-bg':        { chipBg: 'inverse-bg', chipFg: 'on-inverse', a: 'on-inverse', b: 'inverse-bg', min: 4.5, vs: 'z on-inverse' },
    'brand':             { chipBg: 'brand', chipFg: 'on-brand', a: 'on-brand', b: 'brand', min: 4.5, vs: 'z on-brand' },
    'brand-hover':       { chipBg: 'brand-hover', chipFg: 'on-brand', a: 'on-brand', b: 'brand-hover', min: 4.5, vs: 'z on-brand' },
    'brand-soft':        { chipBg: 'brand-soft', chipFg: 'brand', a: 'brand', b: 'brand-soft', min: 4.5, vs: 'z brand' },
    'brand-soft-strong': { chipBg: 'brand-soft-strong', chipFg: 'text', a: 'text', b: 'brand-soft-strong', min: 4.5, vs: 'z text' },
    'cta':               { chipBg: 'cta', chipFg: 'on-cta', a: 'on-cta', b: 'cta', min: 4.5, vs: 'z on-cta' },
    'cta-hover':         { chipBg: 'cta-hover', chipFg: 'on-cta', a: 'on-cta', b: 'cta-hover', min: 4.5, vs: 'z on-cta' },
    'border':            { line: true, a: 'border', b: 'bg', min: null, vs: 'na bg' },
    'border-strong':     { line: true, a: 'border-strong', b: 'bg', min: null, vs: 'na bg' },
    'field-border':      { line: true, a: 'field-border', b: 'bg', min: 3, vs: 'na bg' },
    'switch-off':        { chipBg: 'switch-off', chipFg: 'bg', a: 'switch-off', b: 'bg', min: 3, vs: 'na bg' },
    'focus':             { line: true, a: 'focus', b: 'bg', min: 3, vs: 'na bg' },
    'danger':            { chipBg: 'danger', chipFg: 'on-inverse', a: 'on-inverse', b: 'danger', min: 4.5, vs: 'z on-inverse' },
    'danger-soft':       { chipBg: 'danger-soft', chipFg: 'danger', a: 'danger', b: 'danger-soft', min: 3, vs: 'z danger (ikona)' },
    'warning-bg':        { chipBg: 'warning-bg', chipFg: 'warning-text', a: 'warning-text', b: 'warning-bg', min: 4.5, vs: 'z warning-text' },
    'warning-border':    { line: true, a: 'warning-border', b: 'warning-bg', min: null, vs: 'na warning-bg', chipBg: 'warning-bg' }
  };

  function buildSwatch(name) {
    var p = PAIRS[name] || { chipBg: name, chipFg: 'text', a: 'text', b: name, min: 4.5, vs: 'z text' };
    var full = '--dk-color-' + name;
    var rawTok = TOKENS.filter(function (t) { return t.name === full; })[0];
    var alias = rawTok ? rawTok.raw.replace(/^var\(--dk-/, '').replace(/\)$/, '') : '';

    var card = el('div', 'g-swatch');
    var chip = el('div', 'g-chip' + (p.line ? ' g-chip--line' : ''));
    if (p.line) {
      chip.style.setProperty('--chip-line', role(name));
      if (p.chipBg) chip.style.background = role(p.chipBg);
      chip.appendChild(el('span'));
    } else {
      chip.style.setProperty('--chip-bg', role(p.chipBg));
      chip.style.setProperty('--chip-fg', role(p.chipFg));
      chip.textContent = 'Aa';
    }
    var body = el('div', 'g-swatch-body');
    body.appendChild(el('span', 'g-swatch-name', full));
    var rgb = rgbOf(role(name));
    body.appendChild(el('span', 'g-swatch-hex', hexOf(rgb)));
    if (alias) body.appendChild(el('span', 'g-swatch-alias', 'alias: ' + alias));

    var ratio = contrast(rgbOf(role(p.a)), rgbOf(role(p.b)));
    var row = el('div', 'g-ratio');
    row.appendChild(el('span', null, fmt(ratio) + ' ' + p.vs));
    var badge;
    if (p.warn) {
      badge = el('span', 'g-badge g-badge--warn', p.warn);
    } else if (p.min == null) {
      badge = el('span', 'g-badge', 'dekoracja');
    } else if (ratio >= 7 && p.min === 4.5) {
      badge = el('span', 'g-badge g-badge--ok', 'AAA');
    } else if (ratio >= p.min) {
      badge = el('span', 'g-badge g-badge--ok', p.min === 3 ? 'AA (element)' : 'AA');
    } else {
      badge = el('span', 'g-badge g-badge--warn', 'poniżej ' + String(p.min).replace('.', ',') + ':1');
    }
    row.appendChild(badge);
    body.appendChild(row);
    card.appendChild(chip);
    card.appendChild(body);
    return card;
  }

  function renderColors() {
    var host = document.getElementById('swatch-groups');
    if (!host) return;
    var roleNames = TOKENS.filter(function (t) { return t.name.indexOf('--dk-color-') === 0; })
      .map(function (t) { return t.name.replace('--dk-color-', ''); });
    var placed = {};
    GROUPS.forEach(function (g) {
      var names = g[1].filter(function (n) { return roleNames.indexOf(n) !== -1; });
      names.forEach(function (n) { placed[n] = true; });
      if (!names.length) return;
      host.appendChild(el('h3', 'g-sub', g[0]));
      var grid = el('div', 'g-swatches');
      names.forEach(function (n) { grid.appendChild(buildSwatch(n)); });
      host.appendChild(grid);
    });
    var rest = roleNames.filter(function (n) { return !placed[n]; });
    if (rest.length) {
      host.appendChild(el('h3', 'g-sub', 'Pozostałe role'));
      var g2 = el('div', 'g-swatches');
      rest.forEach(function (n) { g2.appendChild(buildSwatch(n)); });
      host.appendChild(g2);
    }
    var prims = document.getElementById('prims');
    TOKENS.forEach(function (t) {
      if (t.name.indexOf('--dk-color-') === 0) return;
      if (!/^--dk-(green|brown|tan|sand|cream|white|yellow|red|amber)/.test(t.name)) return;
      var item = el('div', 'g-prim');
      var sw = el('i');
      sw.style.setProperty('--c', 'var(' + t.name + ')');
      var txt = el('span', null, t.name.replace('--dk-', '') + '  ' + hexOf(rgbOf('var(' + t.name + ')')));
      item.appendChild(sw);
      item.appendChild(txt);
      prims.appendChild(item);
    });
  }

  /* ---------- odstępy, promienie, cienie, pozostałe ---------- */
  function renderSpace() {
    var host = document.getElementById('space-list');
    if (!host) return;
    TOKENS.filter(function (t) { return /^--dk-space-\d+$/.test(t.name); }).forEach(function (t) {
      var row = el('div', 'g-space-row');
      row.appendChild(code(t.name));
      row.appendChild(el('span', 'g-space-val', val(t.name)));
      var bar = el('div', 'g-bar');
      bar.style.width = 'calc(var(' + t.name + ') * 4)';
      row.appendChild(bar);
      host.appendChild(row);
    });
  }
  function renderRadius() {
    var host = document.getElementById('radius-list');
    if (!host) return;
    TOKENS.filter(function (t) { return t.name.indexOf('--dk-radius-') === 0; }).forEach(function (t) {
      var fig = el('figure', 'g-state');
      var box = el('div', 'g-radius-box');
      box.style.borderRadius = 'var(' + t.name + ')';
      fig.appendChild(box);
      var cap = el('figcaption');
      cap.appendChild(code(t.name.replace('--dk-', '')));
      cap.appendChild(document.createElement('br'));
      cap.appendChild(document.createTextNode(val(t.name)));
      fig.appendChild(cap);
      host.appendChild(fig);
    });
  }
  function renderShadows() {
    var host = document.getElementById('shadow-list');
    if (!host) return;
    TOKENS.filter(function (t) { return t.name.indexOf('--dk-shadow-') === 0; }).forEach(function (t) {
      var fig = el('figure', 'g-state');
      var box = el('div', 'g-shadow-box');
      box.style.boxShadow = 'var(' + t.name + ')';
      fig.appendChild(box);
      var cap = el('figcaption');
      cap.appendChild(code(t.name.replace('--dk-', '')));
      fig.appendChild(cap);
      host.appendChild(fig);
    });
  }
  function renderOther() {
    var tb = document.querySelector('#other-tokens tbody');
    if (!tb) return;
    TOKENS.filter(function (t) { return /^--dk-(layout|control|motion|font)-/.test(t.name); }).forEach(function (t) {
      var tr = el('tr');
      var th = el('th'); th.setAttribute('scope', 'row'); th.appendChild(code(t.name));
      tr.appendChild(th);
      tr.appendChild(el('td', null, val(t.name)));
      tb.appendChild(tr);
    });
  }

  /* ---------- wartości w opisach (data-tok) ---------- */
  function fillTokenText() {
    document.querySelectorAll('[data-tok]').forEach(function (n) { n.textContent = val(n.getAttribute('data-tok')); });
    var c = document.getElementById('tok-count');
    if (c) c.textContent = TOKENS.length + ' zmiennych';
  }

  /* ---------- ikony ---------- */
  function renderIcons() {
    var host = document.getElementById('icon-grid');
    if (!host) return;
    var NS = 'http://www.w3.org/2000/svg';
    document.querySelectorAll('svg.sprite symbol[id^="i-"]').forEach(function (s) {
      var cell = el('div', 'g-icon');
      var svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('class', 'ic');
      svg.setAttribute('aria-hidden', 'true');
      var use = document.createElementNS(NS, 'use');
      use.setAttribute('href', '#' + s.id);
      svg.appendChild(use);
      cell.appendChild(svg);
      cell.appendChild(el('span', null, s.id));
      host.appendChild(cell);
    });
  }

  /* ---------- suwaki ---------- */
  function initSliders() {
    document.querySelectorAll('.slider').forEach(function (s) {
      var input = s.querySelector('input[type="range"]');
      var labels = (s.getAttribute('data-labels') || '').split('|');
      var notes = (s.getAttribute('data-notes') || '').split('|');
      var dots = s.querySelectorAll('.dot');
      var stops = s.querySelectorAll('.stops button');
      var strong = s.querySelector('.slider-value strong');
      var span = s.querySelector('.slider-value span');
      function paint() {
        var v = +input.value;
        s.style.setProperty('--pct', (v * 50) + '%');
        dots.forEach(function (d, i) { d.classList.toggle('on', i <= v); });
        stops.forEach(function (b) { b.classList.toggle('on', +b.getAttribute('data-v') === v); });
        if (strong) strong.textContent = labels[v] || '';
        if (span) span.textContent = notes[v] || '';
        input.setAttribute('aria-valuetext', (labels[v] || '') + (notes[v] ? ', ' + notes[v] : ''));
      }
      input.addEventListener('input', paint);
      stops.forEach(function (b) {
        b.addEventListener('click', function () { input.value = b.getAttribute('data-v'); paint(); });
      });
      paint();
    });
  }

  /* ---------- wiersze sekcji: klasa .is-on podąża za przełącznikiem ---------- */
  function initSecs() {
    document.querySelectorAll('.sec').forEach(function (row) {
      var input = row.querySelector('input[type="checkbox"]');
      if (!input || input.disabled) return;
      input.addEventListener('change', function () { row.classList.toggle('is-on', input.checked); });
    });
  }

  /* ---------- strefa upuszczania (żywa) ---------- */
  function initDrop() {
    var d = document.getElementById('demo-drop');
    if (!d) return;
    ['dragenter', 'dragover'].forEach(function (ev) {
      d.addEventListener(ev, function (e) { e.preventDefault(); d.classList.add('is-over'); });
    });
    ['dragleave', 'drop'].forEach(function (ev) {
      d.addEventListener(ev, function (e) { e.preventDefault(); d.classList.remove('is-over'); });
    });
  }

  /* ---------- toasty: zamknij / pokaż ponownie ---------- */
  function initToasts() {
    var stack = document.getElementById('toast-stack');
    if (!stack) return;
    stack.addEventListener('click', function (e) {
      var x = e.target.closest ? e.target.closest('.x') : null;
      if (!x) return;
      var t = x.closest('.toast');
      t.classList.add('leaving');
      setTimeout(function () { t.hidden = true; }, 200);
    });
    var reset = document.getElementById('toast-reset');
    if (reset) reset.addEventListener('click', function () {
      stack.querySelectorAll('.toast').forEach(function (t) {
        t.hidden = false;
        t.classList.remove('leaving');
        t.classList.remove('enter');
        void t.offsetWidth;
        t.classList.add('enter');
      });
    });
  }

  /* ---------- nawigacja: bieżąca sekcja ---------- */
  function initNav() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.g-nav a'));
    var secs = links.map(function (a) { return document.querySelector(a.getAttribute('href')); });
    var ticking = false;
    function update() {
      ticking = false;
      var cur = 0;
      secs.forEach(function (s, i) { if (s && s.getBoundingClientRect().top <= 140) cur = i; });
      links.forEach(function (a, i) {
        if (i === cur) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
      });
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  }

  function run() {
    fillTokenText();
    renderColors();
    renderSpace();
    renderRadius();
    renderShadows();
    renderOther();
    renderIcons();
    initSliders();
    initSecs();
    initDrop();
    initToasts();
    initNav();
  }

  /* czcionki muszą się załadować, zanim policzymy układ; kolory nie zależą od nich */
  run();
})();
