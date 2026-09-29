/* Stwórz prezentację — Dobra Kaloria
   Logika interfejsu. Bez frameworków, bez CDN. Działa offline w pywebview / WebView2.

   Python -> JS:  App.analyze(path), App.showOptions(result), App.onProgress(p),
                  App.onLog(line), App.onDone(result), App.onError(message), App.goto(screen)
   JS -> Python:  window.pywebview.api.{get_info, pick_folder, analyze, build,
                  open_path, open_folder, copy_text, open_ai, check_update, apply_update, cancel}

   W przeglądarce (bez pywebview) sam doładowuje mock.js z udawanym backendem. */
(function () {
  'use strict';

  /* ---------- pomocnicze ---------- */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var SVGNS = 'http://www.w3.org/2000/svg';

  function icon(name, cls) {
    var s = document.createElementNS(SVGNS, 'svg');
    s.setAttribute('class', 'ic' + (cls ? ' ' + cls : ''));
    s.setAttribute('aria-hidden', 'true');
    var u = document.createElementNS(SVGNS, 'use');
    u.setAttribute('href', '#i-' + name);
    s.appendChild(u);
    return s;
  }

  function h(tag, props) {
    var e = document.createElement(tag);
    if (props) {
      Object.keys(props).forEach(function (k) {
        var v = props[k];
        if (v == null || v === false) return;
        if (k === 'class') e.className = v;
        else if (k === 'text') e.textContent = v;
        else if (k === 'on') Object.keys(v).forEach(function (ev) { e.addEventListener(ev, v[ev]); });
        else e.setAttribute(k, v === true ? '' : v);
      });
    }
    for (var i = 2; i < arguments.length; i++) {
      var kids = [].concat(arguments[i]);
      for (var j = 0; j < kids.length; j++) {
        var c = kids[j];
        if (c == null || c === false) continue;
        e.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
      }
    }
    return e;
  }

  function plural(n, one, few, many) {
    var a = Math.abs(n), m10 = a % 10, m100 = a % 100;
    if (a === 1) return one;
    if (m10 >= 2 && m10 <= 4 && !(m100 >= 12 && m100 <= 14)) return few;
    return many;
  }
  function num(n, one, few, many) { return n + ' ' + plural(n, one, few, many); }

  function fmtDur(s) {
    s = Math.round(Number(s) || 0);
    if (s < 60) return s + ' s';
    var m = Math.floor(s / 60), r = s % 60;
    return r ? m + ' min ' + r + ' s' : m + ' min';
  }
  function fmtEta(s) {
    if (s == null || isNaN(s)) return 'liczę czas…';
    s = Math.round(s);
    if (s <= 3) return 'jeszcze chwilkę';
    if (s < 60) return 'jeszcze ok. ' + (s >= 20 ? Math.round(s / 5) * 5 : s) + ' s';
    var m = Math.floor(s / 60), r = Math.round((s % 60) / 10) * 10;
    if (r === 60) { m += 1; r = 0; }
    return 'jeszcze ok. ' + m + ' min' + (r ? ' ' + r + ' s' : '');
  }
  function txt(x) {
    if (x == null) return '';
    if (typeof x === 'string') return x;
    return x.tekst || x.text || x.opis || x.message || String(x);
  }
  function baseName(p) { return String(p || '').replace(/[\\/]+$/, '').split(/[\\/]/).pop(); }
  function dirName(p) { var s = String(p || ''), i = Math.max(s.lastIndexOf('\\'), s.lastIndexOf('/')); return i > 0 ? s.slice(0, i) : s; }
  function errMsg(e) { return (e && e.message) ? e.message : String(e || 'Coś poszło nie tak.'); }

  /* ---------- stan ---------- */
  var state = {
    screen: 'start',
    info: null,
    result: null,
    secs: [],
    packFiles: [],
    packs: {},
    analyzing: false,
    picking: false,
    building: false,
    cancelled: false,
    pct: 0,
    stepIdx: 0,
    done: null
  };
  var started = false;

  function hasApi() { return !!(window.pywebview && window.pywebview.api); }
  function apiFn(name) {
    var api = window.pywebview && window.pywebview.api;
    return (api && typeof api[name] === 'function') ? api : null;
  }
  /* Most do programu bywa gotowy dopiero po chwili (pierwsze uruchomienie, dysk sieciowy, antywirus) -
     czekamy cierpliwie do 3 minut zamiast od razu pokazywać błąd (29.09). */
  function whenApi(name) {
    return new Promise(function (resolve, reject) {
      var t0 = Date.now();
      (function tick() {
        var api = apiFn(name);
        if (api) return resolve(api);
        if (Date.now() - t0 > 180000) {
          return reject(new Error('Program nie odpowiada. Zamknij okno i uruchom aplikację jeszcze raz.'));
        }
        setTimeout(tick, 250);
      })();
    });
  }
  function call(name) {
    var args = Array.prototype.slice.call(arguments, 1);
    return whenApi(name).then(function (api) { return api[name].apply(api, args); });
  }

  /* ---------- ekrany i kroki ---------- */
  var SCREENS = ['start', 'analiza', 'opcje', 'praca', 'wynik'];
  var STEP_OF = { start: 1, analiza: 1, opcje: 2, praca: 3, wynik: 4 };

  function updateSteps() {
    var cur = STEP_OF[state.screen] || 1;
    $$('#steps li').forEach(function (li) {
      var n = +li.getAttribute('data-step');
      var badge = $('.n', li);
      li.classList.toggle('done', n < cur || (n === 4 && cur === 4));
      if (n === cur) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
      badge.replaceChildren();
      if (n < cur || (n === 4 && cur === 4)) badge.appendChild(icon('check')); else badge.textContent = String(n);
    });
  }

  function goto(name, noFocus) {
    if (SCREENS.indexOf(name) < 0) return;
    state.screen = name;
    document.body.setAttribute('data-screen', name);
    updateSteps();
    window.scrollTo(0, 0);
    if (!noFocus) {
      var head = $('#screen-' + name + ' [data-focus]');
      if (head) { try { head.focus({ preventScroll: true }); } catch (e) { /* stary silnik */ } }
    }
  }

  /* ---------- toasty ---------- */
  function toast(msg, kind, ms) {
    kind = kind || 'info';
    var host = $('#toasts');
    while (host.children.length >= 3) host.removeChild(host.firstChild);
    var t = h('div', { class: 'toast ' + kind, role: kind === 'error' ? 'alert' : 'status' },
      icon(kind === 'error' ? 'circle-alert' : (kind === 'ok' ? 'check' : 'info')),
      h('span', { text: msg }),
      h('button', { type: 'button', class: 'x', 'aria-label': 'Zamknij komunikat', on: { click: function () { close(); } } }, icon('x'))
    );
    var timer = null;
    function close() {
      clearTimeout(timer);
      t.classList.add('leaving');
      setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 220);
    }
    host.appendChild(t);
    timer = setTimeout(close, ms || (kind === 'error' ? 10000 : 4500));
    return t;
  }

  /* ---------- aktualizacja z najnowszego wydania ---------- */
  function checkUpdate() {
    call('check_update').then(function (r) {
      if (!r || !r.jest) return;
      state.update = r;
      var box = $('#update');
      $('#update-text').textContent = 'Jest nowa wersja ' + r.wersja + ' (masz ' + r.obecna + ').';
      var b = $('#btn-update');
      if (r.sam) { b.hidden = false; $('#update-note').textContent = 'Trwa ok. minuty. Program sam uruchomi się ponownie.'; }
      else { b.hidden = true; $('#update-note').textContent = 'Tę kopię zaktualizuje opiekun programu (' + r.powod + ').'; }
      box.hidden = false;
    }).catch(function () { /* brak sieci: program działa bez aktualizacji */ });
  }
  function onUpdate(p) {
    var b = $('#btn-update');
    if (p.blad) { b.disabled = false; b.lastChild.textContent = 'Zaktualizuj'; toast(p.blad, 'error', 15000); return; }
    b.lastChild.textContent = p.restart ? 'Uruchamiam ponownie…' : 'Pobieram… ' + (p.procent || 0) + '%';
  }

  /* ---------- instrukcja po skopiowaniu polecenia dla AI ---------- */
  function showGuide(r) {
    var g = $('#guide');
    var app = r.gdzie === 'aplikacja', claude = r.klucz === 'claude';
    $('#guide-title').textContent = r.klucz === 'inny' ? 'Polecenie skopiowane' : 'Otwieram ' + r.nazwa;
    var s2;
    if (claude && app) s2 = ['Wybierz tryb Cowork albo Code', 'W tych trybach Claude widzi pliki na komputerze, więc sam otworzy folder i poprawi prezentację.'];
    else if (claude) s2 = ['Najlepiej użyj aplikacji Claude na komputerze', 'W przeglądarce Claude nie widzi plików. W aplikacji wybierz tryb Cowork albo Code. W przeglądarce dołącz plik prezentacji ręcznie.'];
    else if (r.klucz === 'inny') s2 = ['Otwórz swój czat AI', 'Masz Claude na komputerze? Wybierz tryb Cowork albo Code, wtedy AI widzi pliki. W innym czacie dołącz plik prezentacji.'];
    else s2 = ['Dołącz plik prezentacji', r.nazwa + ' nie widzi plików na komputerze. Przeciągnij do czatu plik prezentacji z folderu.'];
    $('#guide-s2-t').textContent = s2[0];
    $('#guide-s2-d').textContent = s2[1];
    g.hidden = false;
    g.classList.remove('run'); void g.offsetWidth; g.classList.add('run');
    $('#guide-ok').focus();
  }
  function hideGuide() { $('#guide').hidden = true; }

  /* ---------- start: stopka, wybór folderu, przeciąganie ---------- */
  function renderFooter() {
    var i = state.info || {};
    var f = $('#foot-info');
    f.replaceChildren();
    f.appendChild(h('span', { text: 'Wersja ' + (i.wersja || '—') }));
    var names = { nowy: 'nowy styl', stary: 'stary styl' };
    var list = (i.szablony && i.szablony.length ? i.szablony : ['nowy', 'stary']).map(function (k) { return names[k] || k; });
    f.appendChild(h('span', { text: 'Szablon: ' + list.join(' / ') }));
    if (i.powerpoint === false) {
      f.appendChild(h('span', { class: 'warn', text: 'Nie widzę programu PowerPoint — zrobię prezentację, ale jej nie sprawdzę.' }));
    }
  }

  function pickFolder() {
    if (state.picking || state.analyzing) return;
    state.picking = true;
    call('pick_folder').then(function (p) {
      state.picking = false;
      if (p) analyze(p);
    }).catch(function (e) {
      state.picking = false;
      onError(errMsg(e));
    });
  }

  function initDrop() {
    var dz = $('#dropzone');
    var depth = 0;
    dz.addEventListener('dragenter', function (e) { e.preventDefault(); depth++; dz.classList.add('is-over'); });
    dz.addEventListener('dragover', function (e) {
      e.preventDefault();
      if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
      dz.classList.add('is-over');
    });
    dz.addEventListener('dragleave', function () {
      depth = Math.max(0, depth - 1);
      if (!depth) dz.classList.remove('is-over');
    });
    dz.addEventListener('drop', function (e) {
      e.preventDefault();
      depth = 0;
      dz.classList.remove('is-over');
      /* W programie upuszczenie obsługuje Python (zdarzenie DOM pywebview na #dropzone)
         i sam woła App.analyze(pełnaŚcieżka). Tu wyłącznie mock (window.pywebview.mock === true)
         symuluje to nazwą pliku. */
      if (window.pywebview && window.pywebview.mock === true) {
        var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (f) analyze(f.name);
      }
    });
    /* Upuszczenie obok strefy nie może otworzyć pliku w oknie. */
    window.addEventListener('dragover', function (e) { e.preventDefault(); });
    window.addEventListener('drop', function (e) { e.preventDefault(); });
    dz.addEventListener('click', pickFolder);
  }

  /* ---------- analiza ---------- */
  var analyzeWatchdog = null;
  function analyze(path) {
    if (state.analyzing) return;
    state.analyzing = true;
    var lbl = $('#analiza-folder');
    var name = baseName(path);
    lbl.textContent = name || '';
    lbl.hidden = !name;
    goto('analiza');
    clearTimeout(analyzeWatchdog);
    analyzeWatchdog = setTimeout(function () {
      if (state.analyzing && state.screen === 'analiza') onError('Czytanie folderu trwa za długo. Spróbuj jeszcze raz albo wybierz inny folder.');
    }, 180000);
    call('analyze', path).then(function (res) {
      clearTimeout(analyzeWatchdog);
      if (res) showOptions(res);      /* gdy Python zwróci null, czekamy na jego App.showOptions */
    }).catch(function (e) {
      clearTimeout(analyzeWatchdog);
      onError(errMsg(e));
    });
  }

  /* ---------- opcje: lewa kolumna ---------- */
  function foundRow(kind, main, sub, extra) {
    var ic = kind === 'ok' ? 'check' : (kind === 'warn' ? 'alert' : 'minus');
    return h('li', { class: kind === 'none' ? 'f-none' : '' },
      h('span', { class: 'f-ic', 'aria-hidden': 'true' }, icon(ic)),
      h('div', { class: 'f-txt' },
        main,
        sub ? h('span', { class: 'f-sub', text: sub }) : null,
        extra || null));
  }

  /* Karta smaku z miniaturą paczki. Klik w miniaturę = następny plik z packshoty_pliki. */
  function packSrcFor(name) {
    var f = state.packFiles.filter(function (x) { return x.plik === name; })[0];
    return f ? f.miniatura : null;
  }

  function makeFlav(s) {
    var f = {
      nazwa: s.nazwa,
      file: s.packshot_plik || null,
      origSrc: s.miniatura || null,
      hadNone: !s.packshot_plik && !s.miniatura && s.packshot !== true,
      legacyOk: !s.packshot_plik && !s.miniatura && s.packshot === true,   /* stary kontrakt: jest, ale bez obrazka */
      media: null
    };
    if (f.file) state.packs[f.nazwa] = f.file;
    f.media = h('span', { class: 'flav-media' });
    f.card = h('div', { class: 'flav' },
      f.media,
      h('div', { class: 'flav-txt' },
        h('span', { class: 'flav-name', text: s.nazwa }),
        s.masa ? h('span', { class: 'flav-mass', text: s.masa }) : null));
    paintFlav(f);
    return f;
  }

  function paintFlav(f) {
    var files = state.packFiles;
    var src = f.file ? (packSrcFor(f.file) || f.origSrc) : null;
    var interactive = files.length > 0 && (files.length > 1 || !f.file);
    var el = h(interactive ? 'button' : 'span', { class: 'flav-media' });
    if (interactive) el.setAttribute('type', 'button');

    if (src) {
      el.appendChild(h('img', { src: src, alt: '', draggable: 'false' }));
      if (interactive) el.appendChild(h('span', { class: 'flav-swap', 'aria-hidden': 'true' }, icon('refresh')));
    } else if (f.legacyOk && !f.file) {
      el.classList.add('is-ok');
      el.appendChild(icon('check'));
    } else {
      el.classList.add('is-none');
      el.appendChild(h('span', { text: 'brak packshotu' }));
    }

    var label = f.nazwa + ': ' + (f.file ? 'zdjęcie opakowania ' + f.file : 'brak zdjęcia opakowania (packshotu)');
    el.setAttribute('title', interactive ? label + '. Kliknij, żeby zamienić.' : label);
    if (interactive) {
      el.setAttribute('aria-label', 'Zamień zdjęcie opakowania dla smaku ' + f.nazwa + '. Teraz: ' + (f.file || 'brak') + '.');
      el.addEventListener('click', function () { cycleFlav(f); });
    } else {
      el.setAttribute('aria-label', label);
      el.setAttribute('role', 'img');
    }
    if (f.media.parentNode) f.media.parentNode.replaceChild(el, f.media);
    f.media = el;
  }

  function cycleFlav(f) {
    var opts = state.packFiles.map(function (x) { return x.plik; });
    if (f.hadNone) opts.unshift(null);           /* smak bez paczki: brak -> pliki -> brak */
    if (!opts.length) return;
    var i = opts.indexOf(f.file);
    var next = opts[(i + 1) % opts.length];
    f.file = next;
    if (next) state.packs[f.nazwa] = next; else delete state.packs[f.nazwa];
    paintFlav(f);
    var b = f.media;
    if (b && b.focus && b.tagName === 'BUTTON') b.focus({ preventScroll: true });
  }

  function renderFound(r) {
    $('#h-opcje').textContent = r.produkt || 'Produkt';
    var list = $('#found-list');
    list.replaceChildren();

    var smaki = r.smaki || [];
    state.packFiles = (r.packshoty_pliki || []).filter(function (f) { return f && f.plik; });
    state.packs = {};
    if (smaki.length) {
      var flavs = smaki.map(function (s) { return makeFlav(s); });
      var cards = h('div', { class: 'flavs' }, flavs.map(function (f) { return f.card; }));
      var hint = state.packFiles.length > 1
        ? h('span', { class: 'f-sub f-hint' }, icon('refresh'), h('span', { text: 'Paczka nie pasuje do smaku? Kliknij miniaturę, żeby zamienić.' }))
        : null;
      list.appendChild(foundRow('ok',
        h('strong', { text: num(smaki.length, 'smak', 'smaki', 'smaków') }), null, [cards, hint]));
    } else {
      list.appendChild(foundRow('none', h('span', { text: 'Nie znalazłem żadnego smaku' })));
    }

    var karty = r.karty | 0;
    list.appendChild(karty
      ? foundRow('ok', h('strong', { text: num(karty, 'karta wprowadzenia', 'karty wprowadzenia', 'kart wprowadzenia') }))
      : foundRow('none', h('span', { text: 'Brak kart wprowadzenia' })));

    var ak = r.copy_akapity | 0;
    list.appendChild(ak
      ? foundRow('ok', h('span', null, 'Copy: ', h('strong', { text: num(ak, 'akapit', 'akapity', 'akapitów') })))
      : foundRow('none', h('span', { text: 'Brak copy' })));

    var bad = r.badania || [];
    if (bad.length) {
      list.appendChild(foundRow('ok', h('span', null, 'Badanie: ', h('strong', { text: bad[0] })),
        bad.length > 1 ? '+ ' + num(bad.length - 1, 'inny plik', 'inne pliki', 'innych plików') : null));
    } else {
      list.appendChild(foundRow('none', h('span', { text: 'Badanie: brak' })));
    }

    var g = r.grafiki || {};
    var pk = g.packshoty | 0, el = g.elementy | 0, pom = g.pominiete | 0;
    if (pk || el) {
      var parts = [];
      if (pk) parts.push(num(pk, 'zdjęcie opakowania', 'zdjęcia opakowań', 'zdjęć opakowań'));
      if (el) parts.push(num(el, 'element', 'elementy', 'elementów'));
      list.appendChild(foundRow('ok',
        h('span', null, 'Grafiki: ', h('strong', { text: parts.join(' i ') })),
        pom ? num(pom, 'plik pominięty', 'pliki pominięte', 'plików pominiętych') : null));
    } else {
      list.appendChild(foundRow('none', h('span', { text: 'Grafiki: brak' })));
    }

    var uw = r.uwagi || [];
    var box = $('#notes'), nl = $('#notes-list');
    nl.replaceChildren();
    uw.forEach(function (u) {
      var warn = (u && u.typ) !== 'info';
      nl.appendChild(h('li', { class: warn ? 'warn' : 'info' }, icon(warn ? 'alert' : 'info'), h('span', { text: txt(u) })));
    });
    box.hidden = !uw.length;
  }

  /* ---------- opcje: suwaki ---------- */
  var SLIDERS = {
    dlugosc: { root: '#sl-dlugosc', input: '#in-dlugosc', vals: [
      { n: 'Krótka', d: '≈ 6 slajdów' }, { n: 'Standardowa', d: '≈ 9 slajdów' }, { n: 'Pełna', d: '≈ 13 slajdów' }] },
    tekst: { root: '#sl-tekst', input: '#in-tekst', vals: [
      { n: 'Mniej', d: 'krótkie hasła' }, { n: 'Standardowo', d: 'hasło i zdanie opisu' }, { n: 'Więcej', d: 'pełniejsze opisy' }] }
  };

  function syncSlider(key) {
    var c = SLIDERS[key], root = $(c.root), input = $(c.input);
    var v = Math.max(0, Math.min(2, +input.value || 0));
    root.style.setProperty('--pct', (v * 50) + '%');
    $$('.dot', root).forEach(function (d, i) { d.classList.toggle('on', i <= v); });
    $$('.stops button', root).forEach(function (b, i) { b.classList.toggle('on', i === v); });
    $('.slider-value strong', root).textContent = c.vals[v].n;
    $('.slider-value span', root).textContent = c.vals[v].d;
    input.setAttribute('aria-valuetext', c.vals[v].n + ', ' + c.vals[v].d);
  }
  function setSlider(key, v) { $(SLIDERS[key].input).value = String(v); syncSlider(key); }

  function initSliders() {
    Object.keys(SLIDERS).forEach(function (key) {
      var c = SLIDERS[key], input = $(c.input);
      input.addEventListener('input', function () {
        syncSlider(key);
        if (key === 'dlugosc') applyPreset(+input.value);
      });
      $$('.stops button', $(c.root)).forEach(function (b) {
        b.addEventListener('click', function () {
          setSlider(key, +b.getAttribute('data-v'));
          if (key === 'dlugosc') applyPreset(+b.getAttribute('data-v'));
        });
      });
      syncSlider(key);
    });
  }

  /* ---------- opcje: sekcje ---------- */
  var LOCKED = { okladka: 1, koniec: 1 };
  var PRESET = [
    ['okladka', 'smaki', 'wyroznia', 'sklad', 'koniec'],
    ['copy', 'badanie'],
    ['karty_smakow', 'wartosci', 'film']
  ];

  function filmLink() { return ($('#in-film').value || '').trim(); }

  function refreshSec(o) {
    o.avail = !!(o.locked || o.dostepna || (o.id === 'film' && filmLink()));
    if (o.locked) o.checked = true;
    if (!o.avail) o.checked = false;
    o.input.checked = o.checked;
    o.input.disabled = !o.avail || o.locked;
    o.row.classList.toggle('is-on', o.checked);
    o.row.classList.toggle('is-off', !o.avail);
    o.row.classList.toggle('is-locked', o.locked);
    o.desc.textContent = o.avail ? o.opis : (o.id === 'film' ? 'wpisz link do filmu poniżej' : 'brak danych w folderze');
  }

  function renderSecs(r) {
    var ul = $('#secs');
    ul.replaceChildren();
    state.secs = (r.sekcje || []).map(function (s) {
      var locked = !!LOCKED[s.id];
      var o = { id: s.id, nazwa: s.nazwa, opis: s.opis || '', dostepna: !!s.dostepna, locked: locked, checked: !!s.domyslnie || locked };
      var nameId = 'sec-n-' + s.id, descId = 'sec-d-' + s.id;
      o.input = h('input', { type: 'checkbox', role: 'switch', name: 'sekcja', value: s.id, 'aria-labelledby': nameId, 'aria-describedby': descId });
      o.desc = h('span', { class: 'sec-desc', id: descId });
      var img = h('img', { class: 'sec-img', src: 'img/sekcja-' + s.id + '.png', alt: '', decoding: 'async' });
      img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
      o.row = h('label', { class: 'sec', 'data-id': s.id },
          img,
          h('span', { class: 'sec-txt' },
            h('span', { class: 'sec-name', id: nameId },
              h('span', { text: s.nazwa }),
              locked ? h('span', { class: 'sec-tag' }, icon('lock'), 'zawsze') : null),
            o.desc),
          h('span', { class: 'switch' },
            o.input,
            h('i', { class: 'track' }),
            h('i', { class: 'knob' }, icon('check'))));
      o.li = h('li', null, o.row);
      o.input.addEventListener('change', function () { o.checked = o.input.checked; refreshSec(o); });
      ul.appendChild(o.li);
      return o;
    });
    /* jeśli Python nie zaznaczył nic poza obowiązkowymi, użyj presetu długości */
    var any = state.secs.some(function (o) { return !o.locked && o.checked && o.dostepna; });
    if (!any) applyPreset(+$('#in-dlugosc').value);
    else state.secs.forEach(refreshSec);
  }

  function applyPreset(level) {
    var set = {};
    for (var i = 0; i <= level; i++) PRESET[i].forEach(function (id) { set[id] = 1; });
    state.secs.forEach(function (o) {
      o.checked = !!set[o.id];
      refreshSec(o);
    });
  }

  function initFilm() {
    var inp = $('#in-film'), hint = $('#film-hint');
    inp.addEventListener('input', function () {
      var v = filmLink(), o = state.secs.filter(function (s) { return s.id === 'film'; })[0];
      var wasAvail = o ? o.avail : false;
      if (o) {
        refreshSec(o);
        if (o.avail && !wasAvail) { o.checked = true; refreshSec(o); }
      }
      if (!v) { hint.textContent = 'Wklej link, a dodam slajd z filmem.'; hint.style.color = ''; }
      else if (!/^(https?:\/\/)?([\w-]+\.)?(youtube\.com|youtu\.be)\//i.test(v)) {
        hint.textContent = 'To nie wygląda na link do YouTube — sprawdź, czy jest wklejony w całości.';
        hint.style.color = 'var(--amber-ink)';
      } else { hint.textContent = 'Dodam slajd z tym filmem.'; hint.style.color = ''; }
    });
  }

  /* ---------- opcje: cała strona ---------- */
  function renderOptions(r) {
    renderFound(r);
    var d = r.domyslne || {};
    var styl = d.styl === 'stary' ? 'stary' : 'nowy';
    $$('input[name="styl"]').forEach(function (i) { i.checked = i.value === styl; });
    $('#in-film').value = '';
    $('#in-claimy').value = '';
    $('#film-hint').textContent = 'Wklej link, a dodam slajd z filmem.';
    $('#film-hint').style.color = '';
    setSlider('dlugosc', d.dlugosc == null ? 1 : d.dlugosc);
    setSlider('tekst', d.tekst == null ? 1 : d.tekst);
    renderSecs(r);
    var s = Math.round((+r.szacowany_czas_s || 30) / 5) * 5;
    $('#bar-eta').textContent = 'zwykle ok. ' + num(Math.max(s, 5), 'sekunda', 'sekundy', 'sekund');
  }

  function collectOpts() {
    var styl = ($('input[name="styl"]:checked') || {}).value || 'nowy';
    return {
      styl: styl,
      dlugosc: +$('#in-dlugosc').value,
      tekst: +$('#in-tekst').value,
      sekcje: state.secs.filter(function (o) { return o.checked && o.avail; }).map(function (o) { return o.id; }),
      film: filmLink(),
      claimy: ($('#in-claimy').value || '').split(/\r?\n/).map(function (l) { return l.trim(); }).filter(Boolean).join('\n'),
      packshoty: JSON.parse(JSON.stringify(state.packs || {}))
    };
  }

  /* Lewa kolumna jest "lepka". Gdy jest wyższa niż okno, przykleja się dołem
     (top ujemny), więc po przewinięciu widać jej koniec, a nie ucięty środek. */
  function fitSticky() {
    var col = $('.col-left');
    if (!col || state.screen !== 'opcje') return;
    var bar = $('#bar');
    var top = Math.min(16, window.innerHeight - (bar ? bar.offsetHeight : 0) - col.offsetHeight - 16);
    col.style.top = top + 'px';
    col.classList.add('is-sticky');
  }

  function showOptions(res) {
    state.analyzing = false;
    if (!res || res.ok === false) {
      onError((res && res.blad) || 'Nie udało się odczytać folderu. Sprawdź, czy to folder z produktem.');
      return;
    }
    state.result = res;
    renderOptions(res);
    goto('opcje');
    fitSticky();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitSticky);
  }

  /* ---------- praca ---------- */
  var STEPS = [
    ['folder', 'Czytam folder'],
    ['grafiki', 'Przygotowuję grafiki'],
    ['slajdy', 'Układam slajdy'],
    ['budowa', 'Buduję prezentację'],
    ['qa', 'Sprawdzam w PowerPoint'],
    ['zapis', 'Zapisuję']
  ];
  var ALIAS = {
    folder: 'folder', czytanie: 'folder', analiza: 'folder', wczytanie: 'folder', czytam: 'folder',
    grafiki: 'grafiki', obrazy: 'grafiki', obrazki: 'grafiki', assets: 'grafiki',
    slajdy: 'slajdy', uklad: 'slajdy', układ: 'slajdy', layout: 'slajdy', spec: 'slajdy', plan: 'slajdy',
    budowa: 'budowa', budowanie: 'budowa', pptx: 'budowa', build: 'budowa', render: 'budowa',
    qa: 'qa', sprawdzenie: 'qa', sprawdzanie: 'qa', powerpoint: 'qa', kontrola: 'qa',
    zapis: 'zapis', zapisywanie: 'zapis', save: 'zapis'
  };
  var PCT_STEP = [8, 40, 62, 82, 94];   /* granice etapów, gdy Python nie poda znanego "krok" */

  function stepList() {
    var noPP = state.info && state.info.powerpoint === false;
    return STEPS.filter(function (s) { return !(noPP && s[0] === 'qa'); });
  }
  function stepIndexFor(krok, pct) {
    var list = stepList();
    var id = ALIAS[String(krok || '').toLowerCase()];
    if (!id) {
      var f = PCT_STEP.findIndex(function (t) { return pct < t; });
      id = STEPS[f < 0 ? STEPS.length - 1 : f][0];
    }
    var full = STEPS.findIndex(function (s) { return s[0] === id; });
    for (var k = full; k < STEPS.length; k++) {
      var j = list.findIndex(function (s) { return s[0] === STEPS[k][0]; });
      if (j >= 0) return j;
    }
    return list.length - 1;
  }

  function renderChecklist() {
    var ol = $('#checklist');
    ol.replaceChildren();
    stepList().forEach(function (s, i) {
      ol.appendChild(h('li', { 'data-i': i },
        h('span', { class: 'st', 'aria-hidden': 'true' }),
        h('span', { text: s[1] })));
    });
    paintChecklist(0, false);
  }
  function paintChecklist(idx, allDone) {
    $$('#checklist li').forEach(function (li, i) {
      var st = $('.st', li);
      var done = allDone || i < idx, now = !allDone && i === idx;
      li.classList.toggle('done', done);
      li.classList.toggle('now', now);
      st.replaceChildren();
      if (done) st.appendChild(icon('check'));
      else if (now) st.appendChild(h('span', { class: 'spinner' }));
      if (now) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
    });
  }

  function setProgress(pct) {
    pct = Math.max(0, Math.min(100, Math.round(pct)));
    $('#pct').textContent = String(pct);
    $('#progress-fill').style.width = pct + '%';
    $('#progress').setAttribute('aria-valuenow', String(pct));
  }

  function resetProgress() {
    state.pct = 0;
    state.stepIdx = 0;
    $('#screen-praca').setAttribute('data-state', 'run');
    setProgress(0);
    $('#work-step').textContent = 'Zaczynam…';
    $('#work-eta').textContent = 'liczę czas…';
    $('#log').textContent = '';
    renderChecklist();
  }

  function setPracaError(msg) {
    $('#praca-error-text').textContent = msg;
    $('#screen-praca').setAttribute('data-state', 'error');
  }

  function startBuild() {
    if (state.building || !state.result) return;
    var opts = collectOpts();
    state.building = true;
    state.cancelled = false;
    resetProgress();
    goto('praca');
    call('build', opts).then(function (r) {
      if (r && r.started === false) onError(r.blad || 'Nie mogę zacząć tworzenia prezentacji.');
    }).catch(function (e) {
      onError(errMsg(e));
    });
  }

  function cancelBuild() {
    state.cancelled = true;
    state.building = false;
    call('cancel').catch(function () { /* i tak wracamy do ustawień */ });
    goto('opcje');
    toast('Anulowano. Możesz zmienić ustawienia i spróbować jeszcze raz.');
  }

  function onProgress(p) {
    if (!p || state.cancelled) return;
    if (state.screen !== 'praca' || !state.building) {
      state.building = true;
      resetProgress();
      goto('praca', true);
    }
    var pct = Math.max(state.pct, Math.max(0, Math.min(100, Number(p.procent) || 0)));
    state.pct = pct;
    setProgress(pct);
    if (p.opis) $('#work-step').textContent = p.opis;
    $('#work-eta').textContent = pct >= 100 ? 'kończę…' : fmtEta(p.eta_s);
    var idx = Math.max(state.stepIdx, stepIndexFor(p.krok, pct));
    state.stepIdx = idx;
    paintChecklist(idx, false);
  }

  function onLog(line) {
    var pre = $('#log');
    var atEnd = pre.scrollTop + pre.clientHeight >= pre.scrollHeight - 24;
    var t = pre.textContent + String(line == null ? '' : line) + '\n';
    if (t.length > 24000) t = t.slice(t.length - 20000);
    pre.textContent = t;
    if (atEnd) pre.scrollTop = pre.scrollHeight;
  }

  /* ---------- wynik ---------- */
  function renderResult(res) {
    state.done = res;
    $('#res-name').textContent = res.nazwa || baseName(res.pptx) || 'Prezentacja.pptx';
    var meta = [];
    if (res.slajdy != null) meta.push(num(res.slajdy | 0, 'slajd', 'slajdy', 'slajdów'));
    if (res.czas_s != null) meta.push('gotowe w ' + fmtDur(res.czas_s));
    $('#res-meta').textContent = meta.join(' · ');

    var strip = $('#strip');
    strip.replaceChildren();
    var thumbs = res.miniatury || [];
    thumbs.forEach(function (src, i) {
      strip.appendChild(h('li', null,
        h('img', { src: src, alt: 'Slajd ' + (i + 1) + ' z ' + thumbs.length, draggable: 'false' }),
        h('span', { class: 'num', 'aria-hidden': 'true', text: String(i + 1) })));
    });
    strip.hidden = !thumbs.length;
    strip.scrollLeft = 0;
    updateStripEdge();

    var qa = res.qa || {};
    var n = qa.problemy | 0;
    var q = $('#res-qa');
    q.replaceChildren();
    q.className = 'qa' + (n ? ' warn' : '');
    q.appendChild(icon(n ? 'alert' : 'shield'));
    q.appendChild(h('span', { text: 'Sprawdzone: ' + num(n, 'problem', 'problemy', 'problemów') + ' z tekstem' }));
    var ql = $('#res-qa-list');
    ql.replaceChildren();
    (qa.szczegoly || []).forEach(function (s) { ql.appendChild(h('li', { text: txt(s) })); });
    ql.hidden = !(n && (qa.szczegoly || []).length);

    var todo = res.uwagi || [];
    var tl = $('#res-todo-list');
    tl.replaceChildren();
    todo.forEach(function (u) { tl.appendChild(h('li', { text: txt(u) })); });
    $('#res-todo').hidden = !todo.length;
  }

  function updateStripEdge() {
    var s = $('#strip');
    s.classList.toggle('at-end', s.scrollLeft + s.clientWidth >= s.scrollWidth - 4);
  }
  function initStrip() {
    var s = $('#strip');
    s.addEventListener('scroll', updateStripEdge, { passive: true });
    s.addEventListener('wheel', function (e) {
      if (s.scrollWidth <= s.clientWidth || Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
      var atStart = s.scrollLeft <= 0, atEnd = s.scrollLeft + s.clientWidth >= s.scrollWidth - 1;
      if ((e.deltaY < 0 && atStart) || (e.deltaY > 0 && atEnd)) return;
      s.scrollLeft += e.deltaY;
      e.preventDefault();
    }, { passive: false });
  }

  function onDone(res) {
    if (state.cancelled) return;
    if (!res || res.ok === false) {
      onError((res && res.blad) || 'Nie udało się dokończyć prezentacji.');
      return;
    }
    state.building = false;
    setProgress(100);
    paintChecklist(0, true);
    $('#work-eta').textContent = 'kończę…';
    renderResult(res);
    setTimeout(function () { if (!state.building) goto('wynik'); }, 450);
  }

  function onError(message) {
    var text = String(message || 'Coś poszło nie tak. Spróbuj jeszcze raz.');
    console.info('[App.onError] ' + text);
    toast(text, 'error');
    state.analyzing = false;
    state.picking = false;
    if (state.screen === 'analiza') {
      goto('start');
    } else if (state.screen === 'praca' && state.building) {
      state.building = false;
      setPracaError(text);
    }
  }

  function resetAll() {
    state.result = null;
    state.done = null;
    state.secs = [];
    state.building = false;
    state.cancelled = false;
    state.analyzing = false;
  }

  /* ---------- przyciski ---------- */
  function initButtons() {
    $('#btn-other-folder').addEventListener('click', function () { resetAll(); goto('start'); });
    $('#opcje-form').addEventListener('submit', function (e) { e.preventDefault(); startBuild(); });
    $('#btn-cancel').addEventListener('click', cancelBuild);
    $('#btn-back-opts').addEventListener('click', function () { state.building = false; goto('opcje'); });

    $('#btn-open').addEventListener('click', function () {
      if (!state.done) return;
      call('open_path', state.done.pptx).catch(function (e) { onError(errMsg(e)); });
    });
    $('#btn-folder').addEventListener('click', function () {
      if (!state.done) return;
      call('open_folder', dirName(state.done.pptx)).catch(function (e) { onError(errMsg(e)); });
    });
    $('#btn-copy-ai').addEventListener('click', function () {
      var t = state.done && state.done.prompt_ai;
      if (!t) { onError('Nie mam czego skopiować.'); return; }
      call('copy_text', t).then(function () {
        showGuide({ nazwa: 'czat', klucz: 'inny', gdzie: 'inny' });
      }).catch(function (e) { onError(errMsg(e)); });
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-ai]'), function (b) {
      b.addEventListener('click', function () {
        var t = state.done && state.done.prompt_ai;
        if (!t) { onError('Nie mam czego wysłać do czatu.'); return; }
        call('open_ai', b.getAttribute('data-ai'), t).then(function (r) {
          if (!r || !r.ok) { onError((r && r.blad) || 'Nie udało się otworzyć czatu.'); return; }
          if (!r.skopiowano) { toast('Otwieram ' + r.nazwa + ', ale nie udało się skopiować polecenia. Kliknij „Kopiuj” i wklej je w czacie.', 'error', 12000); return; }
          showGuide(r);
        }).catch(function (e) { onError(errMsg(e)); });
      });
    });
    $('#btn-again').addEventListener('click', function () { resetAll(); goto('start'); });
    $('#btn-update').addEventListener('click', function () {
      var b = this;
      b.disabled = true; b.lastChild.textContent = 'Pobieram… 0%';
      call('apply_update').then(function (r) {
        if (!r || !r.started) onUpdate({ blad: (r && r.blad) || 'Nie udało się rozpocząć aktualizacji.' });
      }).catch(function (e) { onUpdate({ blad: errMsg(e) }); });
    });
    $('#guide-ok').addEventListener('click', hideGuide);
    $('#guide-folder').addEventListener('click', function () {
      if (state.done) call('open_folder', state.done.pptx).catch(function (e) { onError(errMsg(e)); });
    });
    $('#guide').addEventListener('click', function (e) { if (e.target === this) hideGuide(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !$('#guide').hidden) hideGuide(); });

    $('#log-box').addEventListener('toggle', function () {
      $('#log-label').textContent = this.open ? 'Ukryj szczegóły' : 'Pokaż szczegóły';
    });

    /* Enter = główna akcja ekranu, gdy fokus nie jest na czymś innym */
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' || e.defaultPrevented || e.isComposing) return;
      var t = e.target;
      if (t && t.closest && t.closest('button, a, summary, textarea, select, [role="button"], form')) return;
      if (state.screen === 'start') { e.preventDefault(); pickFolder(); }
      else if (state.screen === 'opcje') { e.preventDefault(); startBuild(); }
      else if (state.screen === 'wynik') { e.preventDefault(); $('#btn-open').click(); }
    });
  }

  /* ---------- API dla Pythona ---------- */
  window.App = {
    analyze: analyze,
    showOptions: showOptions,
    onProgress: onProgress,
    onLog: onLog,
    onDone: onDone,
    onUpdate: onUpdate,
    onError: onError,
    goto: goto
  };

  /* ---------- start ---------- */
  function ready() {
    if (started) return;
    started = true;
    call('get_info').then(function (i) { state.info = i || {}; }, function () { state.info = {}; })
      .then(renderFooter);
  }

  function noBackend() {
    if (started) return;
    toast('Nie mogę połączyć się z programem. Zamknij okno i uruchom aplikację jeszcze raz.', 'error', 20000);
  }

  function loadMock() {
    return new Promise(function (resolve) {
      var s = document.createElement('script');
      s.src = 'mock.js';
      s.onload = function () { resolve(true); };
      s.onerror = function () { resolve(false); };
      document.head.appendChild(s);
    });
  }

  function inHost() { return !!(window.pywebview || (window.chrome && window.chrome.webview)); }

  function boot() {
    initDrop();
    initSliders();
    initFilm();
    initStrip();
    initButtons();
    window.addEventListener('resize', fitSticky);
    updateSteps();
    renderFooter();
    checkUpdate();

    var m = new URLSearchParams(location.search).get('mock');
    if (m === '1' || (m == null && !inHost())) {
      /* przeglądarka bez pywebview: udawany backend */
      loadMock().then(function (ok) { if (ok) ready(); else noBackend(); });
      return;
    }
    /* call() samo czeka na most (whenApi) - startujemy od razu, a błąd pokazujemy dopiero po 3 minutach ciszy */
    ready();
    window.addEventListener('pywebviewready', renderFooter, { once: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
