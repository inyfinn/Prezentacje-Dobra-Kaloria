/* Stwórz prezentację — Dobra Kaloria
   Logika interfejsu. Bez frameworków, bez CDN. Działa offline w pywebview / WebView2.

   Python -> JS:  App.analyze(path), App.showOptions(result), App.onProgress(p),
                  App.onLog(line), App.onDone(result), App.onError(message), App.goto(screen)
   JS -> Python:  window.pywebview.api.{get_info, pick_folder, pick_pptx, analyze, build,
                  open_path, open_folder, copy_text, open_ai, check_update, apply_update, cancel}

   W przeglądarce (bez pywebview) sam doładowuje mock.js z udawanym backendem.

   Ekrany: start -> analiza -> opcje (kilka kroków, patrz PANES) -> praca -> wynik. */
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
    mode: 'folder',      /* 'folder' | 'pptx': wyznacza kroki ustawień i pasek kroków */
    pane: 'materialy',   /* bieżący krok ustawień (body[data-pane]) */
    paneMax: 0,          /* najdalszy odwiedzony krok ustawień: do odwiedzonych wolno wrócić kliknięciem w pasek kroków */
    info: null,
    result: null,
    secs: [],
    cel: 'wiernie',
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

  /* Kroki ustawień (07.10.2026): jeden temat na ekran, widać tylko krok z body[data-pane]. Ten sam krok 'slajdy'
     pokazuje slajdy folderu albo rozdziały gotowej prezentacji. Dodatki stoją przed slajdami, bo link do filmu
     włącza slajd z filmem. Pasek kroków u góry = kroki ustawień + Tworzenie + Gotowe. */
  var PANES = { folder: ['materialy', 'styl', 'dodatki', 'slajdy'], pptx: ['materialy', 'cel', 'slajdy'] };
  var PANE_LBL = {
    folder: { materialy: 'Materiały', styl: 'Styl', dodatki: 'Dodatki', slajdy: 'Slajdy' },
    pptx: { materialy: 'Przegląd', cel: 'Cel', slajdy: 'Rozdziały' }
  };
  function panes() { return PANES[state.mode] || PANES.folder; }
  function paneIdx() { return Math.max(0, panes().indexOf(state.pane)); }

  /* numer bieżącego kroku w pasku (od 1); czytanie folderu należy do kroku 1 */
  function stepNow() {
    var n = panes().length;
    if (state.screen === 'opcje') return paneIdx() + 1;
    if (state.screen === 'praca') return n + 1;
    if (state.screen === 'wynik') return n + 2;
    return 1;
  }

  function updateSteps() {
    var ol = $('#steps'), list = panes(), lbl = PANE_LBL[state.mode] || PANE_LBL.folder;
    var names = list.map(function (p) { return lbl[p]; }).concat(['Tworzenie', 'Gotowe']);
    var cur = stepNow(), last = names.length;
    ol.hidden = state.screen === 'start';
    ol.setAttribute('aria-label', 'Postęp: krok ' + cur + ' z ' + last);
    ol.style.setProperty('--steps', String(last));
    ol.replaceChildren();
    names.forEach(function (name, i) {
      var n = i + 1, done = n < cur || (n === last && cur === last);
      /* do odwiedzonego kroku ustawień można wrócić kliknięciem, ale tylko z ekranu ustawień (nie w trakcie tworzenia) */
      var go = state.screen === 'opcje' && i < list.length && n !== cur && i <= state.paneMax;
      var inner = [h('span', { class: 'n', 'aria-hidden': 'true' }, done ? icon('check') : String(n)), h('span', { class: 'lbl', text: name })];
      ol.appendChild(h('li', { class: done ? 'done' : null, 'data-step': n, 'aria-current': n === cur ? 'step' : null },
        go ? h('button', { type: 'button', class: 'step-go', 'aria-label': 'Wróć do kroku ' + n + ': ' + name,
          on: { click: function () { gotoPane(list[i]); } } }, inner)
          : h('span', { class: 'step-in' }, h('span', { class: 'sr-only', text: 'Krok ' + n + ': ' }), inner)));
    });
  }

  function focusHead(sel) {
    var head = $(sel + ' [data-focus]');
    if (head) { try { head.focus({ preventScroll: true }); } catch (e) { /* stary silnik */ } }
  }

  function goto(name, noFocus) {
    if (SCREENS.indexOf(name) < 0) return;
    state.screen = name;
    document.body.setAttribute('data-screen', name);
    updateSteps();
    window.scrollTo(0, 0);
    if (!noFocus) focusHead(name === 'opcje' ? '.pane[data-pane="' + state.pane + '"]' : '#screen-' + name);
  }

  /* Przejście na krok ustawień. Ostatni krok ma przycisk "Stwórz prezentację" zamiast "Dalej";
     pierwszy ma "Inny folder" / "Inna prezentacja" zamiast "Wstecz" (bo wraca na start). */
  function gotoPane(id, noFocus) {
    var list = panes(), i = list.indexOf(id);
    if (i < 0) { i = 0; id = list[0]; }
    state.pane = id;
    state.paneMax = Math.max(state.paneMax, i);
    document.body.setAttribute('data-pane', id);
    var lastPane = i === list.length - 1;
    $('#btn-next').hidden = lastPane;
    $('#btn-build').hidden = !lastPane;
    $('#back-lbl').textContent = i === 0 ? (state.mode === 'pptx' ? 'Inna prezentacja' : 'Inny folder') : 'Wstecz';
    updateSteps();
    window.scrollTo(0, 0);
    if (!noFocus && state.screen === 'opcje') focusHead('.pane[data-pane="' + id + '"]');
  }
  function nextPane() {
    var list = panes(), i = paneIdx();
    if (i < list.length - 1) gotoPane(list[i + 1]); else startBuild();
  }
  function prevPane() {
    var i = paneIdx();
    if (i > 0) gotoPane(panes()[i - 1]); else { resetAll(); goto('start'); }
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

  /* Gotowa prezentacja (.pptx) do przełożenia na styl DK: ten sam przepływ co folder, analyze() rozpoznaje plik. */
  function pickPptx() {
    if (state.picking || state.analyzing) return;
    state.picking = true;
    call('pick_pptx').then(function (p) {
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
    /* Klik w kafel robi to samo co jego przycisk (klik przycisku też tu dociera) */
    $('#choice-folder').addEventListener('click', pickFolder);
    $('#choice-pptx').addEventListener('click', pickPptx);
  }

  /* ---------- analiza ---------- */
  var analyzeWatchdog = null;
  function analyze(path) {
    if (state.analyzing) return;
    state.analyzing = true;
    var lbl = $('#analiza-folder');
    var name = baseName(path);
    lbl.textContent = name || '';
    var isPptx = /\.(pptx|ppsx|potx|pptm)$/i.test(name);
    state.mode = isPptx ? 'pptx' : 'folder';
    state.pane = 'materialy';
    state.paneMax = 0;
    $('#h-analiza').textContent = isPptx ? 'Czytam prezentację…' : 'Czytam folder…';
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
  function foundRow(kind, main, sub, extra, wide) {
    var ic = kind === 'ok' ? 'check' : (kind === 'warn' ? 'alert' : 'minus');
    return h('li', { class: (kind === 'none' ? 'f-none' : '') + (wide ? ' f-wide' : '') },
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

  function renderNotes(r) {
    var uw = r.uwagi || [];
    var box = $('#notes'), nl = $('#notes-list');
    nl.replaceChildren();
    uw.forEach(function (u) {
      var warn = (u && u.typ) !== 'info';
      nl.appendChild(h('li', { class: warn ? 'warn' : 'info' }, icon(warn ? 'alert' : 'info'), h('span', { text: txt(u) })));
    });
    box.hidden = !uw.length;
  }

  /* Lewa kolumna dla gotowej prezentacji: ile slajdów, akapitów, grafik, tabel i wykresów, rozdziały. */
  function renderFoundPptx(r) {
    $('#h-opcje').textContent = r.produkt || 'Prezentacja';
    var list = $('#found-list');
    list.replaceChildren();
    state.packFiles = [];
    state.packs = {};
    list.appendChild(foundRow('ok', h('strong', { text: num(r.slajdy | 0, 'slajd', 'slajdy', 'slajdów') }), r.nazwa_pliku || null));
    list.appendChild(foundRow('ok', h('strong', { text: num(r.akapity | 0, 'akapit', 'akapity', 'akapitów') }),
      'cały tekst i notatki trafią do nowej prezentacji, na końcu sprawdzę każdy akapit'));
    var g = r.grafiki | 0;
    list.appendChild(g ? foundRow('ok', h('strong', { text: num(g, 'grafika', 'grafiki', 'grafik') }), 'przeniosę je w całości, bez przycinania')
      : foundRow('none', h('span', { text: 'Grafiki: brak' })));
    var t = r.tabele | 0, w = r.wykresy | 0;
    if (t || w) {
      var parts = [];
      if (t) parts.push(num(t, 'tabela', 'tabele', 'tabel'));
      if (w) parts.push(num(w, 'wykres', 'wykresy', 'wykresów'));
      list.appendChild(foundRow('ok', h('strong', { text: parts.join(' i ') }), w ? 'wykresy zostaną edytowalne' : null));
    } else {
      list.appendChild(foundRow('none', h('span', { text: 'Tabele i wykresy: brak' })));
    }
    var rz = r.rozdzialy || [];
    list.appendChild(foundRow(rz.length ? 'ok' : 'none', rz.length
      ? h('strong', { text: num(rz.length, 'rozdział', 'rozdziały', 'rozdziałów') }) : h('span', { text: 'Rozdziały: brak' }),
      rz.length ? rz.slice(0, 4).join(', ') + (rz.length > 4 ? '…' : '') : null));
    renderNotes(r);
  }

  function renderFound(r) {
    if (r.tryb === 'pptx') { renderFoundPptx(r); return; }
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
        h('strong', { text: num(smaki.length, 'smak', 'smaki', 'smaków') }), null, [cards, hint], true));
    } else {
      list.appendChild(foundRow('none', h('span', { text: 'Nie znalazłem żadnego smaku' })));
    }

    var karty = r.karty | 0;
    list.appendChild(karty
      ? foundRow('ok', h('strong', { text: num(karty, 'karta wprowadzenia', 'karty wprowadzenia', 'kart wprowadzenia') }))
      : foundRow('none', h('span', { text: 'Brak kart wprowadzenia' })));

    var ak = r.copy_akapity | 0;
    var cp = r.copy_pliki || [], wsz = r.copy_wszystkie | 0, licz = r.copy_liczby | 0;
    if (cp.length) {
      var sub = ak
        ? num(ak, 'akapit', 'akapity', 'akapitów') + ' tekstu' + (licz ? ', ' + num(licz, 'liczba', 'liczby', 'liczb') + ' z badania' : '')
        : 'same liczby i notatki z badania (' + num(wsz, 'akapit', 'akapity', 'akapitów') + '), trafią na slajd z wynikami';
      list.appendChild(foundRow('ok', h('span', null, 'Teksty: ', h('strong', { text: cp.join(', ') }),
        h('span', { class: 'f-sub', text: sub }))));
    } else {
      list.appendChild(foundRow('none', h('span', null, 'Brak pliku z tekstem',
        h('span', { class: 'f-sub', text: 'dodaj plik Word o nazwie zaczynającej się od „Copy”' }))));
    }

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

    renderNotes(r);
  }

  /* ---------- opcje: suwaki ---------- */
  /* Długość: przełącza slajdy budowane z danych folderu (slajdy z szablonu zostają, jak je ustawił użytkownik).
     Ilość tekstu: zmienia treść slajdów (silnik: compose, parametr "tekst"). Skutek obu widać od razu pod suwakiem. */
  var SLIDERS = {
    dlugosc: { root: '#sl-dlugosc', input: '#in-dlugosc', vals: [{ n: 'Krótka' }, { n: 'Standardowa' }, { n: 'Pełna' }] },
    tekst: { root: '#sl-tekst', input: '#in-tekst', vals: [
      { n: 'Mniej', d: 'same tytuły i liczby' }, { n: 'Standardowo', d: 'hasło i zdanie opisu' }, { n: 'Więcej', d: 'pełniejsze opisy' }] }
  };
  var TEXT_EFFECT = [
    'Bez opisów pod zaletami i liczbami. Tekst z copy tylko na jednym slajdzie.',
    'Pod liczbami z badania zdanie opisu. Cały tekst z copy.',
    'Podpis na okładce, % owoców i EAN przy smakach, pod każdą zaletą miejsce na zdanie [w nawiasach].'
  ];
  var effectTimer = null;

  function slideCount() {
    var t = +$('#in-tekst').value;
    return state.secs.reduce(function (n, o) {
      if (!o.checked || !o.avail) return n;
      var k = o.slajdy == null ? 1 : +o.slajdy;
      if (o.id === 'copy' && t === 0) k = Math.min(1, k);
      return n + k;
    }, 0);
  }
  function presetLevel() {  /* który preset odpowiada obecnemu wyborowi slajdów z folderu (-1 = własny) */
    for (var lv = 0; lv < 3; lv++) {
      var set = presetSet(lv), same = state.secs.every(function (o) {
        return o.rodzaj !== 'auto' || !o.avail || o.id === 'koniec' || keepFilm(o) || !!set[o.id] === o.checked;
      });
      if (same) return lv;
    }
    return -1;
  }
  function presetSet(level) {
    var p = state.presety || {}, set = {};
    (p[String(level)] || []).forEach(function (id) { set[id] = 1; });
    return set;
  }

  function syncSlider(key) {
    var c = SLIDERS[key], root = $(c.root), input = $(c.input);
    var v = Math.max(0, Math.min(2, +input.value || 0));
    root.style.setProperty('--pct', (v * 50) + '%');
    $$('.dot', root).forEach(function (d, i) { d.classList.toggle('on', i <= v); });
    $$('.stops button', root).forEach(function (b, i) { b.classList.toggle('on', i === v); });
    var n = c.vals[v].n, d = c.vals[v].d;
    if (key === 'dlugosc' && state.secs) {
      var cnt = slideCount();
      d = '≈ ' + num(cnt, 'slajd', 'slajdy', 'slajdów');
      if (presetLevel() === -1) n = 'Własny wybór';
    }
    $('.slider-value strong', root).textContent = n;
    $('.slider-value span', root).textContent = d || '';
    input.setAttribute('aria-valuetext', n + (d ? ', ' + d : ''));
    if (key === 'tekst') $('#tekst-effect').textContent = TEXT_EFFECT[v];
  }
  function setSlider(key, v) { $(SLIDERS[key].input).value = String(v); syncSlider(key); }

  function refreshCounts() {
    if (!state.secs) return;
    syncSlider('dlugosc');
    var cnt = slideCount();
    $('#bar-count').textContent = state.pptx ? pptxBar() : num(cnt, 'slajd', 'slajdy', 'slajdów');
    (state.groups || []).forEach(function (g) {
      var items = state.secs.filter(function (o) { return o.grupa === g.id; });
      var on = items.filter(function (o) { return o.checked && o.avail; }).length;
      g.count.textContent = on ? on + ' z ' + items.length : items.length + '';
      g.el.classList.toggle('has-on', on > 0);
    });
  }

  function initSliders() {
    Object.keys(SLIDERS).forEach(function (key) {
      var c = SLIDERS[key], input = $(c.input);
      function changed(v) {
        if (key === 'dlugosc') applyPreset(v, true);
        else { syncSlider(key); refreshCounts(); pulse($('#tekst-effect')); }
      }
      input.addEventListener('input', function () { syncSlider(key); changed(+input.value); });
      $$('.stops button', $(c.root)).forEach(function (b) {
        b.addEventListener('click', function () { setSlider(key, +b.getAttribute('data-v')); changed(+b.getAttribute('data-v')); });
      });
      syncSlider(key);
    });
  }
  function pulse(el) { if (!el) return; el.classList.remove('pulse'); void el.offsetWidth; el.classList.add('pulse'); }

  /* ---------- opcje: slajdy (grupy) ---------- */
  var LOCKED = { koniec: 1 };   /* 30.09: okładkę można wyłączyć */

  function filmLink() { return ($('#in-film').value || '').trim(); }
  function keepFilm(o) { return o.id === 'film' && !!filmLink(); }   /* wpisany link: suwak długości nie rusza slajdu z filmem (decyduje przełącznik) */
  function styl() { return ($('input[name="styl"]:checked') || {}).value || 'nowy'; }

  function refreshSec(o) {
    var stary = o.rodzaj === 'szablon' && styl() === 'stary';
    o.avail = !stary && !!(o.locked || o.dostepna || (o.id === 'film' && filmLink()));
    if (o.locked) o.checked = true;
    if (!o.avail) o.input.checked = false;
    o.input.checked = o.checked && o.avail;
    o.input.disabled = !o.avail || o.locked;
    o.row.classList.toggle('is-on', o.checked && o.avail);
    o.row.classList.toggle('is-off', !o.avail);
    o.row.classList.toggle('is-locked', o.locked);
    o.desc.textContent = o.avail ? o.opis : (stary ? 'tylko w nowym stylu'
      : (o.id === 'film' ? 'wpisz link w kroku Dodatki' : (o.powod || 'brak danych w folderze')));
  }

  function secRow(s) {
    var locked = !!LOCKED[s.id], auto = s.rodzaj !== 'szablon';
    var o = { id: s.id, nazwa: s.nazwa, opis: s.opis || '', dostepna: !!s.dostepna, powod: s.powod || '', grupa: s.grupa,
      rodzaj: auto ? 'auto' : 'szablon', slajdy: s.slajdy, locked: locked, checked: !!s.domyslnie || locked };
    var nameId = 'sec-n-' + s.id, descId = 'sec-d-' + s.id;
    o.input = h('input', { type: 'checkbox', role: 'switch', name: 'sekcja', value: s.id, 'aria-labelledby': nameId, 'aria-describedby': descId });
    o.desc = h('span', { class: 'sec-desc', id: descId });
    var noimg = s.rodzaj === 'pptx';   /* rozdziały gotowej prezentacji nie mają miniatur */
    var img = noimg ? null : h('img', { class: 'sec-img', src: s.miniatura || ('img/sekcja-' + s.id + '.png'), alt: '', decoding: 'async', loading: 'lazy' });
    if (img) img.addEventListener('error', function () { img.style.visibility = 'hidden'; });
    /* rozdział prezentacji = jeden wiersz: nazwa i zakres slajdów (bez metki i licznika, zakres mówi to samo) */
    var multi = auto && !noimg && s.slajdy > 1 ? h('span', { class: 'sec-tag' }, num(s.slajdy, 'slajd', 'slajdy', 'slajdów')) : null;
    o.row = h('label', { class: 'sec' + (noimg ? ' sec-noimg sec-line' : ''), 'data-id': s.id },
      img,
      h('span', { class: 'sec-txt' },
        h('span', { class: 'sec-name', id: nameId },
          h('span', { text: s.nazwa }),
          auto && !noimg ? h('span', { class: 'chip chip-auto', text: 'z folderu' }) : null,
          multi,
          locked ? h('span', { class: 'sec-tag' }, icon('lock'), 'zawsze') : null),
        o.desc),
      h('span', { class: 'switch' }, o.input, h('i', { class: 'track' }), h('i', { class: 'knob' }, icon('check'))));
    o.li = h('li', null, o.row);
    o.input.addEventListener('change', function () { o.checked = o.input.checked; refreshSec(o); refreshCounts(); });
    return o;
  }

  function renderSecs(r) {
    var host = $('#secs');
    host.replaceChildren();
    state.presety = r.presety || { 0: [], 1: [], 2: [] };
    var groups = r.grupy && r.grupy.length ? r.grupy : [{ id: '', nazwa: 'Slajdy', opis: '' }];
    host.classList.toggle('one-col', groups.length < 3);
    host.classList.remove('solo');
    state.secs = (r.sekcje || []).map(secRow);
    state.groups = groups.map(function (g) {
      var items = state.secs.filter(function (o) { return (o.grupa || '') === g.id; });
      items.sort(function (a, b) { return (a.rodzaj === 'auto' ? 0 : 1) - (b.rodzaj === 'auto' ? 0 : 1); });
      var count = h('span', { class: 'grp-count' });
      /* grupy startują zwinięte (licznik "3 z 9" mówi, co jest w środku); name = otwarta najwyżej jedna naraz */
      var el = h('details', { class: 'grp', 'data-id': g.id, name: 'grupa-slajdow' },
        h('summary', null,
          h('span', { class: 'grp-name' }, h('strong', { text: g.nazwa }), h('span', { class: 'grp-desc', text: g.opis || '' })),
          count, icon('chevron')),
        h('ul', { class: 'secs-list' }, items.map(function (o) { return o.li; })));
      host.appendChild(el);
      return { id: g.id, el: el, count: count };
    });
    var any = state.secs.some(function (o) { return !o.locked && o.checked && o.dostepna; });
    if (!any) applyPreset(+$('#in-dlugosc').value, false);
    else state.secs.forEach(refreshSec);
    refreshCounts();
  }

  function applyPreset(level, announce) {
    var set = presetSet(level), on = [], off = [];
    state.secs.forEach(function (o) {
      if (o.rodzaj !== 'auto' || o.locked) { refreshSec(o); return; }
      var want = keepFilm(o) ? o.checked : !!set[o.id];
      var was = o.checked && o.avail;
      o.checked = want;
      refreshSec(o);
      var now = o.checked && o.avail;
      if (now !== was) {
        (now ? on : off).push(o.nazwa);
        o.row.classList.remove('flash'); void o.row.offsetWidth; o.row.classList.add('flash');
      }
    });
    refreshCounts();
    if (announce) {
      var e = $('#dlugosc-effect'), parts = [];
      if (on.length) parts.push('Dodano: ' + on.join(', '));
      if (off.length) parts.push('Usunięto: ' + off.join(', '));
      e.textContent = parts.length ? parts.join('. ') + '.' : 'Bez zmian w slajdach z folderu.';
      pulse(e);
      clearTimeout(effectTimer);
      effectTimer = setTimeout(function () { e.textContent = 'Zmienia, które slajdy z danymi z folderu wejdą do prezentacji.'; }, 6000);
    }
  }

  function initFilm() {
    var inp = $('#in-film'), hint = $('#film-hint');
    inp.addEventListener('input', function () {
      var v = filmLink(), o = state.secs.filter(function (s) { return s.id === 'film'; })[0];
      var wasAvail = o ? o.avail : false;
      if (o) {
        refreshSec(o);
        if (o.avail && !wasAvail) { o.checked = true; refreshSec(o); }
        refreshCounts();
      }
      if (!v) { hint.textContent = 'Wklej link, a dodam slajd z filmem.'; hint.style.color = ''; }
      else if (!/^(https?:\/\/)?([\w-]+\.)?(youtube\.com|youtu\.be)\//i.test(v)) {
        hint.textContent = 'To nie wygląda na link do YouTube — sprawdź, czy jest wklejony w całości.';
        hint.style.color = 'var(--amber-ink)';
      } else { hint.textContent = 'Dodam slajd z tym filmem.'; hint.style.color = ''; }
    });
  }

  /* ---------- opcje: cała strona ---------- */
  /* Tryb wyznacza kroki ustawień (PANES). Konwersja gotowej prezentacji: bez suwaków Długość / Tekst (treść zawsze
     w całości), bez dodatków i bez wyboru stylu (zawsze nowy); zamiast slajdów z folderu - rozdziały prezentacji. */
  function setMode(r) {
    var pp = r.tryb === 'pptx';
    state.pptx = pp;
    state.mode = pp ? 'pptx' : 'folder';
    $('#l-found').textContent = pp ? 'Znalazłem w prezentacji' : 'Znalazłem w folderze';
    $('#blk-dlugosc').hidden = pp;
    $('#l-sekcje').hidden = pp;
    $('#sec-lead').hidden = pp;
    $('#blk-cel-slajdy').hidden = true;
    if (pp) { renderCel(r); return; }
    $('#h-slajdy').textContent = 'Ile slajdów';
    $('#slajdy-lead').hidden = true;   /* suwak i nagłówek grup tłumaczą się same */
  }

  /* ---------- konwersja .pptx: cel (zachowaj układ / rozwiń, dokończ / skróć) - 07.10.2026 ----------
     Program zawsze przekłada prezentację slajd w slajd. Cel zmienia to, co dzieje się obok: przy "rozwiń" można
     dołożyć puste slajdy z szablonu, przy "skróć" podaje się, ile slajdów ma zostać. Rozdział wyłączony przełącznikiem
     zostaje w pliku jako slajdy ukryte - w każdym celu (nic nie znika). Zdania niżej stoją nad listą rozdziałów. */
  var CEL_LEAD = {
    wiernie: 'Wyłączony rozdział zostaje w pliku jako slajdy ukryte, nic nie znika.',
    rozwin: 'Włącz puste slajdy z szablonu, które chcesz dołożyć: staną przed zakończeniem.',
    skroc: 'Wyłączone rozdziały zostają w pliku jako slajdy ukryte, pokaz jest krótszy.'
  };

  function pptxCounts() {
    var all = 0, vis = 0, add = 0;
    (state.secs || []).forEach(function (o) {
      if (o.rodzaj === 'auto') { all += (+o.slajdy || 0); if (o.checked && o.avail) vis += (+o.slajdy || 0); }
      else if (state.cel === 'rozwin' && o.checked && o.avail) add += 1;
    });
    return { all: all, vis: vis, add: add };
  }

  /* Cel "Skróć": ile slajdów ma zostać. Puste, za małe albo za duże pole wraca do bezpiecznej wartości. */
  function celSlajdy() {
    var c = pptxCounts(), v = parseInt($('#in-cel-slajdy').value, 10);
    var def = Math.max(3, Math.round(c.all * 0.6)), max = Math.max(3, c.all);
    if (!(v >= 3)) v = def;
    return Math.min(v, max);
  }

  function pptxBar() {
    var c = pptxCounts(), hid = c.all - c.vis;
    if (state.cel === 'skroc') {
      var t = celSlajdy(), hint = $('#cel-slajdy-hint');
      $('#in-cel-slajdy').placeholder = String(Math.max(3, Math.round(c.all * 0.6)));
      $('#in-cel-slajdy').max = String(Math.max(3, c.all));
      hint.textContent = c.vis > t
        ? 'Teraz w pokazie zostaje ' + c.vis + ' z ' + c.all + '. Do celu brakuje ' + (c.vis - t) + ': wyłącz rozdziały niżej albo zostaw to poleceniu dla AI na końcu.'
        : 'W pokazie zostaje ' + c.vis + ' z ' + c.all + '. Cel osiągnięty.';
      return 'Zostaje ' + c.vis + ' z ' + c.all + ', cel: ' + t;
    }
    var base = hid ? c.vis + ' z ' + c.all + ' w pokazie' : num(c.all, 'slajd', 'slajdy', 'slajdów');
    if (state.cel === 'rozwin' && c.add) base += ' + ' + c.add + ' ' + plural(c.add, 'nowy', 'nowe', 'nowych');
    return base;
  }

  function refreshCel() {
    if (!state.pptx) return;
    var cel = state.cel;
    $('#blk-cel-slajdy').hidden = cel !== 'skroc';
    if (cel === 'skroc' && $('#in-cel-slajdy').value === '') $('#in-cel-slajdy').value = String(celSlajdy());
    /* "Zachowaj" i "Skróć": lista rozdziałów jest treścią kroku, więc stoi otwarta. "Rozwiń": dwie grupy zwinięte
       z licznikami (16 pustych slajdów to długa lista - otwiera ją użytkownik). */
    (state.groups || []).forEach(function (g) {
      if (g.id === 'dodatki') { g.el.hidden = cel !== 'rozwin'; g.el.open = false; }
      else g.el.open = cel !== 'rozwin';
    });
    $('#secs').classList.toggle('solo', cel !== 'rozwin');   /* jedyna grupa = lista bez nagłówka */
    $('#slajdy-lead').hidden = false;
    $('#slajdy-lead').textContent = CEL_LEAD[cel] || CEL_LEAD.wiernie;
    $('#h-slajdy').textContent = cel === 'rozwin' ? 'Rozdziały i nowe slajdy' : 'Rozdziały';
    refreshCounts();
  }

  function renderCel(r) {
    var host = $('#cels');
    host.replaceChildren();
    state.cel = r.cel_domyslny || 'wiernie';
    (r.cele || []).forEach(function (c) {
      var inp = h('input', { type: 'radio', name: 'cel', value: c.id, 'aria-describedby': 'cel-d-' + c.id });
      inp.checked = c.id === state.cel;
      inp.addEventListener('change', function () { if (inp.checked) { state.cel = c.id; refreshCel(); } });
      host.appendChild(h('label', { class: 'cel-card', 'data-cel': c.id },
        inp,
        h('span', { class: 'cel-txt' },
          h('span', { class: 'cel-name', text: c.nazwa }),
          h('span', { class: 'cel-desc', id: 'cel-d-' + c.id, text: c.opis })),
        h('span', { class: 'style-tick', 'aria-hidden': 'true' })));
    });
    var wiz = r.wizualizacje || {};
    $('#wiz-row').hidden = !wiz.dostepne;
    $('#blk-wiz').hidden = !wiz.dostepne;
    $('#in-wiz').checked = !!wiz.dostepne;
    $('#in-cel-slajdy').value = '';
  }

  function initCel() {
    var el = $('#in-cel-slajdy');
    el.addEventListener('input', refreshCounts);
    el.addEventListener('change', function () { if (el.value !== '') el.value = String(celSlajdy()); refreshCounts(); });
  }

  function renderOptions(r) {
    renderFound(r);
    setMode(r);
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
    refreshCel();
    syncSlider('tekst');
    $$('.pane-ctx').forEach(function (e) { e.textContent = r.produkt || ''; });   /* nazwa produktu nad tytułem każdego kroku */
    var s = Math.round((+r.szacowany_czas_s || 30) / 5) * 5;
    $('#bar-eta').textContent = 'zwykle ok. ' + num(Math.max(s, 5), 'sekunda', 'sekundy', 'sekund');
  }

  function collectOpts() {
    var styl = state.pptx ? 'nowy' : (($('input[name="styl"]:checked') || {}).value || 'nowy');   /* konwersja: zawsze nowy styl */
    var o = {
      styl: styl,
      dlugosc: +$('#in-dlugosc').value,
      tekst: +$('#in-tekst').value,
      sekcje: state.secs.filter(function (o) { return o.checked && o.avail; }).map(function (o) { return o.id; }),
      film: filmLink(),
      claimy: ($('#in-claimy').value || '').split(/\r?\n/).map(function (l) { return l.trim(); }).filter(Boolean).join('\n'),
      packshoty: JSON.parse(JSON.stringify(state.packs || {}))
    };
    if (state.pptx) {  /* konwersja: cel, wizualizacje; puste slajdy z szablonu (t10...) tylko przy celu "rozwiń" */
      o.cel = state.cel;
      o.wizualizacje = !$('#wiz-row').hidden && $('#in-wiz').checked;
      if (state.cel === 'skroc') o.cel_slajdy = celSlajdy();
      if (state.cel !== 'rozwin') o.sekcje = o.sekcje.filter(function (id) { return !/^t\d+$/.test(id); });
    }
    return o;
  }

  function showOptions(res) {
    state.analyzing = false;
    if (!res || res.ok === false) {
      onError((res && res.blad) || 'Nie udało się odczytać folderu. Sprawdź, czy to folder z produktem.');
      return;
    }
    state.result = res;
    state.paneMax = 0;
    renderOptions(res);            /* ustawia state.mode */
    gotoPane(panes()[0], true);
    goto('opcje');
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
    return STEPS.filter(function (s) { return !(noPP && s[0] === 'qa'); }).map(function (s) {
      return (state.pptx && s[0] === 'folder') ? ['folder', 'Czytam prezentację'] : s;
    });
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
    if (res.ukryte) meta.push('w tym ' + num(res.ukryte | 0, 'ukryty', 'ukryte', 'ukrytych'));
    if (res.nowe && res.nowe.length) meta.push(num(res.nowe.length, 'nowy do uzupełnienia', 'nowe do uzupełnienia', 'nowych do uzupełnienia'));
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
    $('#sec-podglad').hidden = !thumbs.length;   /* bez miniatur nie zostaje sam nagłówek */
    strip.scrollLeft = 0;
    updateStripEdge();

    /* Sprawdzenie: krótkie wiersze (pogrubiona nazwa + zwykły opis). Każde ostrzeżenie jest widoczne od razu;
       pełna lista uwag jest zwinięta i otwiera się sama, gdy cokolwiek wymaga uwagi. */
    var qa = res.qa || {};
    var uw = (res.uwagi || []).map(txt);
    var checked = qa.problemy != null && qa.wykonano !== false;   /* brak liczby = kontrola w PowerPoint się nie wykonała */
    var n = qa.problemy | 0;
    var covTxt = uw.filter(function (x) { return /^Treść:/.test(x); })[0];
    var ukTxt = uw.filter(function (x) { return /^Układ:/.test(x); })[0];
    var covOk = !covTxt || /^Treść: 100%/.test(covTxt);
    var ukOk = !(res.wiernosc && res.wiernosc.usterki && res.wiernosc.usterki.length);
    var todo = uw.filter(function (x) { return !/^(Treść|Układ):/.test(x); });
    if (!checked) todo = todo.filter(function (x) { return !/^Nie sprawdzono w PowerPoint/.test(x); });   /* mówi to już wiersz kontroli */
    var WAZNE = /^(Brakuje|Do sprawdzenia|Nie sprawdzono|PowerPoint nie oddał)/;   /* to, co wymaga działania, idzie na górę listy */
    todo = todo.filter(function (x) { return WAZNE.test(x); }).concat(todo.filter(function (x) { return !WAZNE.test(x); }));
    var alarm = !checked || n > 0 || !covOk || !ukOk || todo.some(function (x) { return /^(Brakuje|Do sprawdzenia)/.test(x); });

    var checks = $('#res-checks');
    checks.replaceChildren();
    function row(cls, ic, label, detail, id) {
      checks.appendChild(h('li', { class: cls, id: id }, icon(ic),
        h('span', null, label ? h('strong', { text: label }) : null, label && detail ? ' ' : null, detail || null)));
    }
    function check(id, ok, t) {   /* "Nazwa: opis" z silnika -> pogrubiona nazwa + zwykły opis */
      var i = t.indexOf(': ');
      row(ok ? 'ok' : 'warn', ok ? 'shield' : 'alert', i > 0 ? t.slice(0, i + 1) : t, i > 0 ? t.slice(i + 2) : '', id);
    }
    if (!checked) row('warn', 'alert', 'Tekst na slajdach:', 'nie sprawdzono w PowerPoint. Otwórz prezentację i przejrzyj slajdy.', 'res-qa');
    else check('res-qa', !n, 'Tekst na slajdach: ' + num(n, 'problem', 'problemy', 'problemów'));
    var det = (qa.szczegoly || []).map(txt);   /* które slajdy i co: od razu pod swoim wierszem */
    if (checked && n && det.length) $('#res-qa > span').appendChild(h('ul', { class: 'qa-details' }, det.map(function (d) { return h('li', { text: d }); })));
    if (covTxt) check('res-cov', covOk, covTxt);
    if (ukTxt) check('res-uklad', ukOk, ukTxt);

    /* najwyżej trzy wskazówki z danych programu: nowe slajdy, slajdy ukryte, slajdy do obejrzenia najpierw, wstawione paczki */
    var nowe = res.nowe || [], spr = res.sprawdz || [], ukr = res.ukryte | 0;
    var wiz = (res.wizualizacje || []).map(function (w) { return w && w.slajd; }).filter(Boolean);
    function nums(a) {
      return a.length > 5 ? a.slice(0, 5).join(', ') + ' i ' + (a.length - 5) + ' ' + plural(a.length - 5, 'inny', 'inne', 'innych') : a.join(', ');
    }
    if (nowe.length) row('tip', 'info', '', 'Uzupełnij ' + num(nowe.length, 'nowy slajd', 'nowe slajdy', 'nowych slajdów') + ' (nr ' + nums(nowe) + '): teksty w [nawiasach].');
    if (ukr) row('tip', 'info', '', num(ukr, 'slajd jest ukryty', 'slajdy są ukryte', 'slajdów jest ukrytych') + '. Przed wysłaniem pliku poza firmę usuń je albo zapisz PDF.');
    if (spr.length) row('tip', 'info', '', 'Zajrzyj najpierw na ' + (spr.length === 1 ? 'slajd' : 'slajdy') + ' oryginału nr ' + nums(spr) + ': nietypowy układ albo dużo tekstu.');
    if (wiz.length && $$('#res-checks .tip').length < 3) row('tip', 'info', '', 'Wstawiłem paczki z biblioteki produktów na ' + (wiz.length === 1 ? 'slajdzie' : 'slajdach') + ' nr ' + nums(wiz) + ': sprawdź dobór.');

    var tl = $('#res-todo-list');
    tl.replaceChildren();
    todo.forEach(function (u) { tl.appendChild(h('li', { text: u })); });
    var box = $('#res-todo');
    box.hidden = !todo.length;
    /* ścieżka folderu nie ma wskazówek z danych, więc jej uwagi (zwykle 2-4 krótkie) stoją otwarte; przy prezentacji
       długa lista jest zwinięta, chyba że coś wymaga uwagi */
    box.open = alarm || !state.pptx || todo.length <= 3;
    $('#res-todo-label').textContent = 'Uwagi do prezentacji (' + todo.length + ')';
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
    state.pane = 'materialy';
    state.paneMax = 0;
    state.done = null;
    state.secs = [];
    state.building = false;
    state.cancelled = false;
    state.analyzing = false;
  }

  /* ---------- przyciski ---------- */
  function initButtons() {
    $('#btn-back').addEventListener('click', prevPane);
    $('#btn-next').addEventListener('click', nextPane);
    $$('input[name="styl"]').forEach(function (i) {
      i.addEventListener('change', function () { if (state.secs) { state.secs.forEach(refreshSec); refreshCounts(); } });
    });
    /* Enter w polu tekstowym = przycisk główny kroku (Dalej albo Stwórz prezentację).
       Enter na przełączniku, karcie wyboru i suwaku niczego nie przeskakuje. */
    $('#opcje-form').addEventListener('submit', function (e) { e.preventDefault(); nextPane(); });
    $('#opcje-form').addEventListener('keydown', function (e) {
      var t = e.target;
      if (e.key !== 'Enter' || !t || t.tagName !== 'INPUT') return;
      if (e.repeat || /^(checkbox|radio|range)$/.test(t.type)) e.preventDefault();   /* przytrzymany Enter nie przeskakuje kilku kroków */
    });
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
      call('copy_text', t).then(function (ok) {
        /* set_clipboard zwraca False, gdy schowek jest zajęty (np. zablokowany pulpit) - wtedy nie udawaj sukcesu */
        if (ok === false) { toast('Nie udało się skopiować polecenia (schowek zajęty). Spróbuj jeszcze raz za chwilę.', 'error', 12000); return; }
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
      if (t && t.closest && t.closest('button, a, summary, textarea, select, input, [role="button"]')) return;
      if (e.repeat) return;   /* przytrzymany Enter nie przeskakuje kilku kroków */
      if (state.screen === 'start') { e.preventDefault(); pickFolder(); }
      else if (state.screen === 'opcje') { e.preventDefault(); nextPane(); }
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
      var k = document.createElement('script');  /* katalog slajdów dla atrapy (generuje WORK\\mock_katalog.py) */
      k.src = 'mock-katalog.js';
      document.head.appendChild(k);
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
    initCel();
    initStrip();
    initButtons();
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
