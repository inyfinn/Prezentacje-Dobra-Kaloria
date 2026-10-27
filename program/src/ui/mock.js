/* Udawany backend do oglądania interfejsu w zwykłej przeglądarce.
   Ładowany przez app.js tylko wtedy, gdy nie ma pywebview (albo przy ?mock=1).
   Adres: index.html            -> mock włączy się sam
          index.html?mock=1     -> wymuś mock
          index.html?mock=0     -> nigdy nie ładuj mocka
          ?speed=3              -> tworzenie 3x szybciej (domyślnie ~9 s)
          ?buildfail=1          -> tworzenie kończy się błędem w połowie
          ?hold=40              -> tworzenie zatrzymuje się na 40% (do zrzutów ekranu)
          ?delay=6000           -> analiza folderu trwa 6 s zamiast 1,8 s
          ?wynik=ostrzezenia    -> ekran Gotowe z ostrzeżeniami (problemy z tekstem, treść < 100%, różnice układu)
          ?wynik=bezpp          -> ekran Gotowe bez kontroli w PowerPoint (brak miniatur, tekst niesprawdzony)
          ?clip=0               -> schowek nigdy nie zwraca odpowiedzi czatu (zrzut pustego kroku Treść)
          ?cc=0                 -> Claude Code niedostępny na liście czatów
   Pakiet plików (1.3): App.analyzeMany(['a.docx', 'zrzut.png', 'b.pdf']) albo „Wybierz pliki” -> Folder -> Treść. Odpowiedź czatu pojawia się
   w schowku po kliknięciu „Otwórz …” / „Popraw w …” (po 2 pustych sprawdzeniach). Nazwa pliku ze słowem "bezm" -> dysk M: niedostępny,
   "istnieje" -> folder prezentacji już jest (bez kroku Folder, ze scenariuszem v2; dodatkowo "zly" = scenariusz z błędami); ?ostatni=chatgpt -> zapamiętany czat; odpowiedź ze słowem BLAD -> save_scenario odmawia, ze słowem UWAGA -> uwagi.
   Nazwa "upuszczonego" pliku ze słowem "blad" -> analiza kończy się błędem,
   ze słowem "brak" -> folder z brakami (bez copy, badania i jednego packshotu),
   ze słowem "duzy" -> dane skrajne: 8 smaków i 5 uwag; plik .pptx ze słowem "dlugi" -> 15 rozdziałów. */
(function () {
  'use strict';
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_info) return;

  var q = new URLSearchParams(location.search);
  var speed = Math.max(0.2, Number(q.get('speed')) || 1);
  var buildFail = q.get('buildfail') === '1';
  var hold = Math.max(0, Math.min(99, Number(q.get('hold')) || 0));
  var analyzeMs = Number(q.get('delay')) || 1800;
  var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms / Math.min(speed, 3)); }); };
  var wynik = q.get('wynik') || '';
  var timer = null;
  var lastFolder = null;
  var lastOpts = null;
  var pakiet = null;      /* pakiet plików: { res, folder, tytul, ver } */
  var clipN = -1;         /* -1 = schowek pusty; po „Otwórz czat” liczy sprawdzenia, odpowiedź po dwóch pustych */
  var clipText = '';

  function log() { try { console.info.apply(console, ['[mock]'].concat([].slice.call(arguments))); } catch (e) { /* nic */ } }

  /* ---- miniatury paczek (packshoty) jako data URI ---- */
  function packUri(color, dark, name) {
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 84 112" width="84" height="112">' +
      '<path d="M8 6h68l4 6-2 88a6 6 0 0 1-6 6H12a6 6 0 0 1-6-6L4 12z" fill="' + color + '"/>' +
      '<path d="M8 6h68l1 8H7z" fill="' + dark + '"/>' +
      '<rect x="14" y="20" width="38" height="20" rx="4" fill="#fff"/>' +
      '<text x="33" y="30" font-family="Arial, sans-serif" font-weight="700" font-size="8" fill="' + color + '" text-anchor="middle">dobra</text>' +
      '<text x="33" y="38" font-family="Arial, sans-serif" font-weight="700" font-size="8" fill="' + color + '" text-anchor="middle">kaloria</text>' +
      '<text x="14" y="58" font-family="Arial Narrow, Arial, sans-serif" font-weight="700" font-size="11" fill="#fff">KULKI</text>' +
      '<text x="14" y="70" font-family="Arial Narrow, Arial, sans-serif" font-weight="700" font-size="11" fill="#fff">KREATYNA</text>' +
      '<rect x="8" y="88" width="34" height="14" rx="2" fill="#f7a81b"/>' +
      '<text x="25" y="98" font-family="Arial, sans-serif" font-weight="700" font-size="6.5" fill="#3B2A20" text-anchor="middle">' + name + '</text>' +
      '<circle cx="62" cy="80" r="9" fill="rgba(255,255,255,.28)"/></svg>';
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }
  var PACKS = [
    { plik: 'KREATYNA - Znak wodny (2).png', miniatura: packUri('#2a9d4b', '#1c7a37', 'ARBUZ') },
    { plik: 'KREATYNA - Znak wodny (3).png', miniatura: packUri('#c8232c', '#9b1a21', 'COLA LEMON') },
    { plik: 'KREATYNA - Znak wodny (4).png', miniatura: packUri('#7b2d8b', '#5b1f68', 'MANGO') }
  ];

  /* ---- dane ---- */
  function fullResult(name) {
    return {
      ok: true,
      folder: 'D:\\Marketing\\- POLSKA\\09 - PREZENTACJE\\' + name,
      produkt: 'Kulki z kreatyną',
      smaki: [
        { nazwa: 'Arbuz', masa: '65 g', ean: '5903548004828', packshot: true, packshot_plik: PACKS[0].plik, miniatura: PACKS[0].miniatura, elementy: 5 },
        { nazwa: 'Cola Lemon', masa: '65 g', ean: '5903548004835', packshot: true, packshot_plik: PACKS[1].plik, miniatura: PACKS[1].miniatura, elementy: 6 },
        { nazwa: 'Mango i marakuja', masa: '65 g', ean: '5903548004842', packshot: false, packshot_plik: null, miniatura: null, elementy: 4 }
      ],
      packshoty_pliki: PACKS.map(function (x) { return { plik: x.plik, miniatura: x.miniatura }; }),
      karty: 3,
      copy_akapity: 8,
      badania: ['OMNIBUS_KULKI KREATYNA.xlsx'],
      grafiki: { packshoty: 2, elementy: 44, pominiete: 2 },
      uwagi: [
        { typ: 'ostrzezenie', tekst: 'Brak zdjęcia opakowania dla smaku „Mango i marakuja”. Użyję samych elementów smaku.' },
        { typ: 'info', tekst: 'Dwa pliki graficzne pominąłem, bo nie pasują do żadnego smaku.' }
      ],
      sekcje: [
        { id: 'okladka', nazwa: 'Okładka', opis: 'Duże logo, nazwa produktu i opakowania', dostepna: true, domyslnie: true },
        { id: 'smaki', nazwa: 'Linia smaków', opis: 'Wszystkie smaki na jednym slajdzie', dostepna: true, domyslnie: true },
        { id: 'wyroznia', nazwa: 'Co wyróżnia produkt', opis: 'Trzy–cztery główne zalety', dostepna: true, domyslnie: true },
        { id: 'sklad', nazwa: 'Dobry skład', opis: 'Z czego jest zrobiony', dostepna: true, domyslnie: true },
        { id: 'wartosci', nazwa: 'Wartości odżywcze', opis: 'Tabela na 100 g', dostepna: false, domyslnie: false },
        { id: 'karty_smakow', nazwa: 'Karta każdego smaku', opis: 'Osobny slajd dla każdego smaku', dostepna: true, domyslnie: false },
        { id: 'copy', nazwa: 'Tekst z copy', opis: 'Opis produktu z dokumentu Word', dostepna: true, domyslnie: true },
        { id: 'badanie', nazwa: 'Wyniki badania', opis: 'Liczby z pliku badania', dostepna: true, domyslnie: true },
        { id: 'film', nazwa: 'Film / podcast', opis: 'Slajd z linkiem do filmu', dostepna: false, domyslnie: false },
        { id: 'koniec', nazwa: 'Zakończenie', opis: 'Kontakt i podziękowanie', dostepna: true, domyslnie: true }
      ].map(function (s) {  /* grupy i liczby slajdów z prawdziwego katalogu */
        var k = ((window.MOCK_KATALOG || {}).sekcje || []).filter(function (x) { return x.id === s.id; })[0];
        return k ? Object.assign({}, k, s) : s;
      }).concat(((window.MOCK_KATALOG || {}).sekcje || []).filter(function (x) { return x.rodzaj === 'szablon'; })),
      domyslne: { styl: 'nowy', dlugosc: 1, tekst: 1 },
      grupy: (window.MOCK_KATALOG || {}).grupy, presety: (window.MOCK_KATALOG || {}).presety,
      szacowany_czas_s: 35
    };
  }

  /* gotowa prezentacja (.pptx) do przełożenia na styl DK - dane jak z prawdziwego programu dla pliku testowego */
  function pptxResult(name) {
    var rz = [['Początek', 7, '1-7'], ['Zaczynamy!', 3, '8-10'], ['Jadalne beauty', 6, '11-16'], ['Starzejące się społeczeństwo', 10, '17-26'],
      ['Choroby cywilizacyjne', 3, '27-29'], ['GLP-1', 3, '30-32'], ['Inne trendy oraz wektory zmian', 11, '33-43']];
    if (/dlugi/i.test(name)) {   /* dane skrajne: 15 rozdziałów */
      var from = 1;
      rz = ['Początek', 'Zaczynamy!', 'Jadalne beauty', 'Starzejące się społeczeństwo', 'Choroby cywilizacyjne', 'GLP-1', 'Inne trendy oraz wektory zmian',
        'Rynek i konkurencja', 'Kanały sprzedaży', 'Portfolio na przyszły rok', 'Plan wdrożeń', 'Budżet marketingowy', 'Harmonogram', 'Ryzyka', 'Następne kroki']
        .map(function (n, i) { var k = 3 + (i % 4), x = [n, k, from + '-' + (from + k - 1)]; from += k; return x; });
    }
    var DOD = ['t10', 't11', 't13', 't15', 't17', 't19', 't21', 't42', 't43', 't58', 't38', 't40', 't41', 't20', 't14', 't60'];
    var dod = DOD.map(function (id) { return ((window.MOCK_KATALOG || {}).sekcje || []).filter(function (x) { return x.id === id; })[0]; })
      .filter(Boolean).map(function (x) { return Object.assign({}, x, { grupa: 'dodatki' }); });
    return {
      ok: true, tryb: 'pptx', folder: String(name).replace(/[\\/][^\\/]*$/, ''), plik: name, nazwa_pliku: String(name).split(/[\\/]/).pop(),
      produkt: 'NPD + PORTOFOLiO', slajdy: 43, slajdy_wynik: 43, akapity: 201, grafiki: 15, tabele: 0, wykresy: 0,
      cele: [{ id: 'wiernie', nazwa: 'Zachowaj układ', opis: 'Ten sam slajd w nowym wyglądzie. Te same teksty, kolejność i układ.' },
        { id: 'rozwin', nazwa: 'Rozwiń / dokończ', opis: 'Slajdy z oryginału zostają. Program dołoży puste slajdy z podpowiedziami w [nawiasach]. Treść dopisze AI albo Ty; sam program niczego nie napisze.' },
        { id: 'skroc', nazwa: 'Skróć', opis: 'Nic nie znika: rozdziały, które wyłączysz, zostają w pliku jako slajdy ukryte. Dalszy skrót zrobi AI z gotowego polecenia.' }],
      cel_domyslny: 'wiernie', wizualizacje: { dostepne: q.get('wiz') !== '0', sciezka: 'M:\\- POLSKA\\01 - PRODUKTY\\- DK' },
      rozdzialy: rz.map(function (x) { return x[0]; }),
      sekcje: rz.map(function (x, i) { return { id: 'r0' + (i + 1), nazwa: x[0], opis: 'slajdy ' + x[2] + ' z oryginału', dostepna: true, domyslnie: true, powod: '', grupa: 'rozdzialy', rodzaj: 'pptx', slajdy: x[1] }; })
        .map(function (x, i) { if (i >= 9) x.id = 'r' + (i + 1); return x; }).concat(dod),
      grupy: [{ id: 'rozdzialy', nazwa: 'Rozdziały', opis: '' }, { id: 'dodatki', nazwa: 'Dołóż puste slajdy', opis: 'z szablonu, z podpowiedziami w [nawiasach]' }],
      presety: { 0: [], 1: [], 2: [] }, smaki: [], karty: 0,
      uwagi: [{ typ: 'info', tekst: 'Pominięto 85 obrazów powtarzających się na slajdach (logo, ozdobniki) albo mniejszych niż 160 px.' },
        { typ: 'info', tekst: 'Cały tekst zostanie przeniesiony. Na końcu sprawdzę każdy akapit i pokażę wynik.' }],
      domyslne: { styl: 'nowy', dlugosc: 1, tekst: 1 }, szacowany_czas_s: 30, powerpoint: true
    };
  }

  /* plik .pptx już w stylu marki (nazwa ze słowem "szablon", "dopracowan" albo "nowy styl"): przegląd jak z silnika (analyze_dopracowanie) */
  function jestDopr(name) { return /\.(pptx|ppsx|potx)$/i.test(String(name)) && /(szablon|dopracowan|nowy styl)/i.test(String(name)); }
  function doprResult(name) {
    var szab = /szablon/i.test(name), n = String(name).split(/[\\/]/).pop();
    return {
      ok: true, tryb: 'dopracowanie', rodzaj: szab ? 'szablon_dk' : 'wynik_programu', folder: String(name).replace(/[\\/][^\\/]*$/, ''),
      plik: name, nazwa_pliku: n, produkt: n.replace(/\.[^.]+$/, '').replace(/ - (nowy styl|dopracowana).*$/, ''),
      slajdy: szab ? 7 : 43, podpowiedzi: szab ? 46 : 0, bledy_tekstu_liczba: szab ? 0 : 1, spec: null,
      powod: szab ? 'To szablon z podpowiedziami w nawiasach - sprawdzam go i przygotowuję polecenie; treść wpisz sam albo zleć AI.'
        : 'To prezentacja zrobiona już przez ten program (nowy styl Dobra Kaloria) - nie przerabiam slajdów, sprawdzam je i przygotowuję polecenie do dopracowania.',
      uwagi: [{ typ: 'info', tekst: szab ? 'To szablon z podpowiedziami w nawiasach - sprawdzam go i przygotowuję polecenie; treść wpisz sam albo zleć AI.'
        : 'To prezentacja zrobiona już przez ten program (nowy styl Dobra Kaloria) - nie przerabiam slajdów, sprawdzam je i przygotowuję polecenie do dopracowania.' }],
      sekcje: [], grupy: [], cele: [], smaki: [], karty: 0, presety: { 0: [], 1: [], 2: [] },
      domyslne: { styl: 'nowy', dlugosc: 1, tekst: 1 }, szacowany_czas_s: szab ? 25 : 60, powerpoint: true
    };
  }
  function doprDone(name) {
    var szab = /szablon/i.test(name), n = String(name).split(/[\\/]/).pop(), sl = szab ? 7 : 43;
    var bl = szab ? [] : ['Możliwe błędy w tekście prezentacji: 1 (program ich nie poprawia - popraw w pliku albo zleć AI)',
      'Slajd 12: „komunikacjaod” wygląda na sklejone słowa - może „komunikacja od”?'];
    return {
      ok: true, tryb: 'dopracowanie', rodzaj: szab ? 'szablon_dk' : 'wynik_programu', pptx: name, nazwa: n, slajdy: sl, ukryte: 0, nowe: [],
      podpowiedzi: szab ? 46 : 0, plik_bez_zmian: true, czas_s: 24, miniatury: wynik === 'bezpp' ? [] : thumbs(Math.min(sl, 13)),
      qa: wynik === 'bezpp' ? { problemy: null, szczegoly: [], wykonano: false } : { problemy: 0, szczegoly: [], wykonano: true },
      bledy_tekstu: szab ? [] : [{ slajd: 12 }], bledy_okno: bl,
      oko: { uruchomione: true, pozostale: szab ? [{ slajd: 3, kod: 'PUSTY_DOL', waga: 1, opis: 'pusty dół slajdu' }] : [] },
      uwagi: bl.concat(szab ? ['Sprawdź najpierw: slajd 3 - pusty dół slajdu', 'Podpowiedzi w nawiasach kwadratowych: 46 pól na 7 slajdach - do wypełnienia przez człowieka albo AI (przykład: „[Nazwa produktu]”).'] : [])
        .concat(wynik === 'bezpp' ? ['Nie sprawdzono w PowerPoint (brak PowerPointa na tym komputerze).'] : []),
      wiernosc: { usterki: [] }, sprawdz: [], wizualizacje: [],
      folder_pokaz: 'C:\\Users\\Marta\\AppData\\Local\\Dobra Kaloria\\Stworz prezentacje\\konwersje\\plansze',
      plansze_folder: wynik === 'bezpp' ? null : 'C:\\Users\\Marta\\AppData\\Local\\Dobra Kaloria\\Stworz prezentacje\\konwersje\\plansze',
      prompt_agent: 'KROK 0: sprawdź skill /prezentacje… Dopracuj prezentację „' + n + '” według AGENTS.md (sekcja 3b).',
      prompt_ai: 'Prezentacja „' + n + '” jest już w stylu marki Dobra Kaloria. Program niczego w niej nie zmienił. Twoje zadanie to DOPRACOWANIE, nie przebudowa.'
    };
  }

  /* dokument (docx, pdf, txt...): jak z silnika (analyze_dokument); nazwa ze słowem "krotki" = bez nagłówków i mały zakres */
  function dokumentResult(name) {
    var krotki = /krotki/i.test(name), n = String(name).split(/[\\/]/).pop();
    var sw = krotki ? { slajdy: { min: 2, max: 2, domyslnie: 2 }, rozdzialy: { max: 0, domyslnie: 0 } }
      : { slajdy: { min: 4, max: 60, domyslnie: 14 }, rozdzialy: { max: 7, domyslnie: 3 } };
    return {
      ok: true, tryb: 'dokument', folder: String(name).replace(/[\\/][^\\/]*$/, ''), plik: name, nazwa_pliku: n,
      produkt: krotki ? 'Notatka z rozmowy' : 'Strategia produktowa 2027', tytul: 'Strategia produktowa 2027',
      slowa: krotki ? 180 : 4200, akapity: krotki ? 5 : 96, naglowki: krotki ? {} : { '1': 7, '2': 18, '3': 4 },
      tabele: krotki ? 0 : 3, obrazy: krotki ? 0 : 5, suwaki: sw, czas: { stale: 12, na_slajd: 1.2 },
      uwagi: [{ typ: 'ostrzezenie', tekst: 'Pominąłem numery stron i powtarzające się nagłówki stron (12 wierszy).' },
        { typ: 'info', tekst: 'Cały tekst dokumentu trafi na slajdy - niczego nie dopiszę i nie pominę. Na końcu sprawdzę każdy akapit.' }],
      sekcje: [], grupy: [], cele: [], presety: { 0: [], 1: [], 2: [] }, smaki: [], karty: 0,
      domyslne: { styl: 'nowy', dlugosc: 1, tekst: 1 }, szacowany_czas_s: 30, powerpoint: true
    };
  }

  /* dane skrajne do zrzutów: 8 smaków, 5 uwag (nazwa folderu ze słowem "duzy") */
  function bigResult(name) {
    var r = fullResult(name);
    r.produkt = 'Batony proteinowe z kremem';
    var nazwy = ['Arbuz', 'Cola Lemon', 'Mango i marakuja', 'Słony karmel z orzeszkami', 'Czarna porzeczka', 'Brownie', 'Kokos i biała czekolada', 'Pistacja'];
    r.smaki = nazwy.map(function (n, i) {
      var pk = i === 2 ? null : PACKS[i % PACKS.length];
      return { nazwa: n, masa: '65 g', ean: '59035480048' + (10 + i), packshot: !!pk, packshot_plik: pk ? pk.plik : null, miniatura: pk ? pk.miniatura : null, elementy: 4 };
    });
    r.karty = 8;
    r.uwagi = r.uwagi.concat([
      { typ: 'ostrzezenie', tekst: 'Karta smaku „Pistacja” nie ma gramatury. Wpisz ją ręcznie na slajdzie ze smakami.' },
      { typ: 'ostrzezenie', tekst: 'Zdjęcia opakowań mają znak wodny DEMO.' },
      { typ: 'info', tekst: 'Liczby z badania wziąłem z pierwszego arkusza pliku OMNIBUS.' }
    ]);
    return r;
  }

  /* błędy tekstu oryginału: blok z engine.uwagi_okno (nagłówek, najwyżej 5 linii, reszta w poleceniu dla AI) */
  var BLEDY_OKNO = [
    'Możliwe błędy w tekście oryginału: 7 (program ich nie poprawia - popraw w pliku albo zleć AI)',
    'Slajd 12: „komunikacjaod” wygląda na sklejone słowa - może „komunikacja od”?',
    'Slajd 2: „zbudowanie” wygląda na błąd odmiany - może „zbudowania”?',
    'Slajd 9: „na na” - powtórzone słowo',
    'Slajd 17: „odwrotem o węglowodanów” - może „odwrotem od węglowodanów”?',
    'Slajd 21: brak spacji po przecinku: „wzrost,spadek”',
    '…i 2 kolejnych w poleceniu dla AI'];

  /* uwagi wyniku dla gotowej prezentacji, jak z prawdziwego programu (kolejność i brzmienie z engine.py) */
  function uwagiPptx(opts) {
    var bad = wynik === 'ostrzezenia';
    var u = [bad ? 'Treść: 97% akapitów (195/201) przeniesionych' : 'Treść: 100% akapitów (201/201) przeniesionych',
      bad ? 'Układ: osobne napisy 78 z 80, kolejność góra-dół bez zmian, liczby 94 z 95, slajdów tyle samo (43)'
        : 'Układ: osobne napisy 80 z 80, kolejność góra-dół bez zmian, liczby 95 z 95, slajdów tyle samo (43)'];
    u.push.apply(u, BLEDY_OKNO);
    u.push('Po obejrzeniu zrzutów poprawiłem układ slajdów: 12, 31', 'Sprawdź najpierw: slajd 12 - karta ma 62% wysokości pusta pod tekstem, a obok stoi wypełniona');
    if (opts.cel === 'rozwin') u.push('Slajdy 43, 44 mają podpowiedzi w nawiasach - uzupełnij je albo usuń');   /* jak z silnika: liczone z gotowego pliku */
    u.push('Pominięto 85 obrazów powtarzających się na slajdach (logo, ozdobniki) albo mniejszych niż 160 px.',
      'Slajd 4: dodałem wizualizacje z biblioteki produktów - Pralinowe: słownik: Pralinowe = deserowe (Banoffee kakao, Tiramisu czekolada kakao); Owocowe: linia owocowe (Czarna porzeczka, Figa z makiem, Malina). Sprawdź dobór.',
      'Slajd 5: dodałem wizualizacje z biblioteki produktów - Protein: słownik: Protein = IG (Proteina banoffee, Proteina karmel z mct). Sprawdź dobór.',
      'Grafiki: przeniesiono 15 (całe, bez przycinania). Tekst na zrzutach ekranu zostaje obrazem - nie jest przepisywany automatycznie.',
      'Oryginał jest pisany wersalikami: ustawiłem zwykłą wielkość liter w 63 wierszach (np. „WSTĘP” -> „Wstęp”). Sprawdź nazwy własne i skróty - pełna lista: wielkosc-liter.txt.',
      'Sprawdź najpierw slajdy oryginału nr 4, 5 - mają nietypowy układ albo dużo tekstu.',
      'Animacje, przejścia i tła slajdów z oryginału nie są przenoszone - to kwestia stylu, nie treści.');
    if (bad) u.push('Brakuje (slajd 12 oryginału): Rynek suplementów beauty rośnie o 9,2 mln rocznie', 'Do sprawdzenia - slajd 12: liczba 9,2 mln nie została znaleziona');
    if (wynik === 'bezpp') u.push('Nie sprawdzono w PowerPoint (brak PowerPointa na tym komputerze).');
    return u;
  }

  function thinResult(name) {
    var r = fullResult(name);
    r.produkt = 'Baton proteinowy Wanilia';
    r.smaki = [{ nazwa: 'Wanilia', masa: '50 g', ean: '5903548001111', packshot: false, packshot_plik: null, miniatura: null, elementy: 0 }];
    r.packshoty_pliki = [];
    r.karty = 1;
    r.copy_akapity = 0;
    r.badania = [];
    r.grafiki = { packshoty: 0, elementy: 6, pominiete: 0 };
    r.uwagi = [
      { typ: 'ostrzezenie', tekst: 'Nie znalazłem pliku z copy (docx). Slajd z tekstem będzie pominięty.' },
      { typ: 'ostrzezenie', tekst: 'Brak zdjęcia opakowania — okładka będzie bez paczki.' }
    ];
    r.sekcje.forEach(function (s) {
      if (['copy', 'badanie', 'wartosci', 'karty_smakow'].indexOf(s.id) >= 0) { s.dostepna = false; s.domyslnie = false; }
    });
    return r;
  }

  /* ---- miniatury slajdów jako data URI (SVG, bez canvasa: działa też z file://) ---- */
  function svgUri(body, bg) {
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 180" width="320" height="180">' +
      '<rect width="320" height="180" fill="' + bg + '"/>' + body + '</svg>';
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }
  var T = function (x, y, size, fill, s, anchor) {
    return '<text x="' + x + '" y="' + y + '" font-family="Arial Narrow, Arial, sans-serif" font-weight="700" font-size="' + size +
      '" fill="' + fill + '"' + (anchor ? ' text-anchor="' + anchor + '"' : '') + '>' + s + '</text>';
  };
  function pouch(x, y, w, h, c) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="8" fill="' + c + '"/>' +
      '<rect x="' + (x + w * .14) + '" y="' + (y + h * .1) + '" width="' + (w * .56) + '" height="' + (h * .2) + '" rx="3" fill="#fff"/>';
  }
  function slideThumb(i, n) {
    var G = '#0F763E', C = '#FDF8EC', S = '#E9F2EC', K = '#3B2A20';
    var kinds = [
      function () { return svgUri('<rect width="160" height="180" fill="' + G + '"/><rect x="26" y="62" width="108" height="56" rx="6" fill="#fff"/>' + T(80, 92, 18, G, 'dobra', 'middle') + T(80, 111, 18, G, 'kaloria', 'middle') + T(178, 60, 13, G, 'NOWOŚĆ') + T(178, 84, 22, K, 'KULKI Z') + T(178, 108, 22, K, 'KREATYNĄ') + pouch(200, 116, 34, 52, '#c8232c') + pouch(236, 122, 30, 46, '#2a9d4b'), '#fff'); },
      function () { return svgUri(T(20, 40, 24, K, 'LINIA SMAKÓW') + pouch(50, 62, 62, 96, '#2a9d4b') + pouch(126, 54, 68, 108, '#c8232c') + pouch(208, 62, 62, 96, '#7b2d8b'), '#fff'); },
      function () { return svgUri(T(20, 40, 24, K, 'CO WYRÓŻNIA PRODUKT') + [0, 1, 2, 3].map(function (k) { return '<rect x="' + (20 + k * 74) + '" y="70" width="66" height="84" rx="8" fill="' + G + '"/><circle cx="' + (53 + k * 74) + '" cy="98" r="12" fill="#fff" opacity=".9"/><rect x="' + (30 + k * 74) + '" y="124" width="46" height="5" rx="2" fill="#fff"/><rect x="' + (36 + k * 74) + '" y="135" width="34" height="5" rx="2" fill="#fff" opacity=".7"/>'; }).join(''), '#fff'); },
      function () { return svgUri(T(20, 40, 24, K, 'DOBRY SKŁAD') + [0, 1, 2].map(function (k) { return '<rect x="20" y="' + (62 + k * 36) + '" width="' + (240 - k * 40) + '" height="26" rx="6" fill="' + S + '"/><rect x="28" y="' + (70 + k * 36) + '" width="' + (90 + k * 20) + '" height="10" rx="3" fill="' + G + '"/>'; }).join(''), '#fff'); },
      function () { return svgUri(T(20, 40, 24, K, 'WARTOŚCI ODŻYWCZE') + pouch(24, 60, 70, 104, '#c8232c') + [0, 1, 2, 3, 4].map(function (k) { return '<rect x="120" y="' + (62 + k * 22) + '" width="180" height="18" fill="' + (k % 2 ? '#fff' : C) + '"/>'; }).join(''), '#fff'); },
      function () { return svgUri('<rect x="0" y="0" width="320" height="180" fill="' + C + '"/>' + T(20, 40, 24, K, 'ARBUZ') + pouch(190, 30, 92, 132, '#2a9d4b') + '<circle cx="90" cy="120" r="30" fill="#e0525b"/><circle cx="90" cy="120" r="24" fill="#f6a5a9"/>', C); },
      function () { return svgUri(T(20, 40, 24, K, 'O PRODUKCIE') + [0, 1, 2, 3].map(function (k) { return '<rect x="20" y="' + (62 + k * 26) + '" width="' + (260 - (k % 2) * 60) + '" height="8" rx="3" fill="#cfc6b3"/>'; }).join('') + '<rect x="230" y="110" width="70" height="54" rx="8" fill="' + G + '"/>', '#fff'); },
      function () { return svgUri(T(20, 40, 24, K, 'WYNIKI BADANIA') + [0, 1, 2, 3].map(function (k) { return '<rect x="' + (34 + k * 66) + '" y="' + (150 - (40 + k * 18)) + '" width="44" height="' + (40 + k * 18) + '" rx="4" fill="' + G + '"/>'; }).join(''), S); },
      function () { return svgUri('<rect width="320" height="180" fill="' + G + '"/><rect x="100" y="56" width="120" height="68" rx="6" fill="#fff"/>' + T(160, 88, 20, G, 'dobra', 'middle') + T(160, 110, 20, G, 'kaloria', 'middle') + T(160, 150, 15, '#fff', 'DZIĘKUJEMY', 'middle'), G); }
    ];
    var k = i === 0 ? 0 : (i === n - 1 ? 8 : 1 + ((i - 1) % 7));
    return kinds[k]();
  }
  function thumbs(n) { var a = []; for (var i = 0; i < n; i++) a.push(slideThumb(i, n)); return a; }

  /* ---- postęp ---- */
  var STAGES = [
    { until: 8, krok: 'folder', opis: function () { return 'Czytam folder'; }, log: ['Czytam karty wprowadzenia (3)…', 'Czytam copy: 8 akapitów.'] },
    { until: 40, krok: 'grafiki', opis: function (p) { return 'Przygotowuję grafiki (' + Math.max(1, Math.round((p - 8) / 32 * 44)) + '/44)'; }, log: ['Wycinam elementy smaku…', 'Dopasowuję packshoty do smaków…'] },
    { until: 62, krok: 'slajdy', opis: function () { return 'Układam slajdy'; }, log: ['Układam slajdy według stylu.'] },
    { until: 84, krok: 'budowa', opis: function () { return 'Buduję prezentację'; }, log: ['Składam plik PPTX…'] },
    { until: 95, krok: 'qa', opis: function () { return 'Sprawdzam w PowerPoint'; }, log: ['Otwieram prezentację w PowerPoint…', 'Sprawdzam, czy teksty mieszczą się w ramkach.'] },
    { until: 101, krok: 'zapis', opis: function () { return 'Zapisuję plik'; }, log: ['Zapisuję plik…'] }
  ];

  function runBuild(opts) {
    clearInterval(timer);
    var total = 9000 / speed, t0 = Date.now(), lastStage = -1, failed = false;
    var slides = [6, 9, 13][opts.dlugosc == null ? 1 : opts.dlugosc];
    timer = setInterval(function () {
      var el = Date.now() - t0;
      var pct = Math.min(hold || 100, el / total * 100);
      if (buildFail && pct >= 50 && !failed) {
        failed = true; clearInterval(timer);
        window.App.onLog('BŁĄD: nie mogę zapisać pliku (jest otwarty w PowerPoint).');
        window.App.onError('Nie mogę zapisać prezentacji, bo plik o tej nazwie jest otwarty w PowerPoint. Zamknij go i spróbuj jeszcze raz.');
        return;
      }
      var si = STAGES.findIndex(function (s) { return pct < s.until; });
      if (si < 0) si = STAGES.length - 1;
      if (si !== lastStage) { lastStage = si; STAGES[si].log.forEach(function (l) { window.App.onLog(l); }); }
      if (pct >= 100) {
        clearInterval(timer);
        window.App.onProgress({ krok: 'zapis', opis: 'Zapisuję plik', procent: 100, eta_s: 0 });
        if (pakiet) { var pd = pakietDone(opts); window.App.onLog('Gotowe: ' + pd.nazwa); window.App.onDone(pd); return; }
        if (jestDopr(lastFolder)) { window.App.onLog('Sprawdzone: ' + String(lastFolder).split(/[\\/]/).pop()); window.App.onDone(doprDone(lastFolder)); return; }
        var dk = /\.(docx?|rtf|odt|pdf|txt|md)$/i.test(String(lastFolder));   /* dokument: wynik jak z silnika (tryb dokument) */
        var pp = dk || /\.(pptx|ppsx)$/i.test(String(lastFolder));
        var celSuf = { rozwin: ' - rozwinięta', skroc: ' - skrót' }[opts.cel] || '';
        var name = pp ? String(lastFolder).split(/[\\/]/).pop().replace(/\.[^.]+$/, '') + (dk ? ' - prezentacja' : ' - nowy styl' + celSuf) + '.pptx'
          : 'Kulki z kreatyną - ' + (opts.styl === 'stary' ? 'stary' : 'nowy') + ' styl.pptx';
        window.App.onLog('Gotowe: ' + name);
        window.App.onDone({
          ok: true,
          pptx: 'D:\\Marketing\\- POLSKA\\09 - PREZENTACJE\\Kulki z kreatyną\\' + name,
          nazwa: name,
          slajdy: dk ? (opts.slajdy || 14) + 4 : pp ? 43 + (opts.cel === 'rozwin' ? (opts.sekcje || []).filter(function (x) { return /^t/.test(x); }).length : 0) : slides,
          ukryte: pp ? [7, 3, 6, 10, 3, 3, 11].reduce(function (n, k, i) { return n + ((opts.sekcje || []).indexOf('r0' + (i + 1)) < 0 ? k : 0); }, 0) : 0,
          nowe: pp && opts.cel === 'rozwin' ? (opts.sekcje || []).filter(function (x) { return /^t/.test(x); }).map(function (x, i) { return 43 + i; }) : [],
          sprawdz: pp ? [4, 5] : [],
          wizualizacje: pp && opts.wizualizacje ? [{ slajd: 4, kolumny: [] }, { slajd: 5, kolumny: [] }] : [],
          wiernosc: { usterki: wynik === 'ostrzezenia' ? ['slajd 12: liczba 9,2 mln nie została znaleziona'] : [] },
          czas_s: 31,
          miniatury: wynik === 'bezpp' ? [] : thumbs(slides),
          qa: wynik === 'bezpp' ? { problemy: null, szczegoly: [], wykonano: false }
            : (wynik === 'ostrzezenia' ? { problemy: 2, szczegoly: ['s07 SIEROTA: „kosmetyczne” samo w ostatniej linii', 's12 KOLIZJA: tekst nachodzi na grafikę'], wykonano: true }
              : { problemy: 0, szczegoly: [], wykonano: true }),
          uwagi: pp ? uwagiPptx(opts) : [
            'Sprawdź nazwę smaku „Mango i marakuja” na slajdzie ze smakami: brakowało zdjęcia opakowania.',
            'Wartości odżywcze wpisz ręcznie, jeśli chcesz mieć je w prezentacji.',
            'Slajdy z szablonu (1) mają podpowiedzi w [nawiasach] - uzupełnij je albo użyj przycisku Claude / ChatGPT / Gemini.'
          ].concat(wynik === 'bezpp' ? ['Nie sprawdzono w PowerPoint (brak PowerPointa na tym komputerze).'] : []),
          bledy_okno: pp ? BLEDY_OKNO : [],
          /* najważniejsze wiersze uwag od silnika (engine._uwagi_top): najwyżej 5, reszta pod „Pokaż wszystkie” */
          uwagi_top: pp ? [].concat(opts.cel === 'rozwin' ? [{ typ: 'warn', tekst: 'Slajdy 43, 44 mają podpowiedzi w nawiasach - uzupełnij je albo usuń' }] : [],
            [{ typ: 'warn', tekst: 'Możliwe błędy w tekście: 7 (np. slajd 12 „komunikacjaod” -> „komunikacja od”; slajd 2 „zbudowanie” -> „zbudowania”) - program ich nie poprawia, lista pod „Pokaż wszystkie”' },
              { typ: 'warn', tekst: 'Sprawdź najpierw: slajd 12 - karta ma 62% wysokości pusta pod tekstem, a obok stoi wypełniona' },
              { typ: 'warn', tekst: '…i 1 kolejnych usterek wyglądu - lista pod „Pokaż wszystkie”' },
              { typ: 'info', tekst: 'Wstawiłem paczki z biblioteki produktów na slajdach nr 4, 5: sprawdź dobór.' }]).slice(0, 5) : undefined,
          plansze_folder: pp && wynik !== 'bezpp' ? 'D:\\Marketing\\- POLSKA\\09 - PREZENTACJE\\Kulki z kreatyną\\plansze' : null,
          prompt_agent: 'KROK 0: sprawdź skill /prezentacje… Dopracuj prezentację „' + name + '” według AGENTS.md (sekcja 3b).',
          prompt_ai: 'Mam prezentację PowerPoint „' + name + '” dla produktu Kulki z kreatyną (Dobra Kaloria). ' +
            'Pomóż mi ją dopracować: skróć teksty na slajdach, popraw literówki i zaproponuj mocniejsze nagłówki. ' +
            'Nie zmieniaj liczb ani nazw smaków. Odpowiadaj po polsku, krótko i konkretnie.'
        });
        return;
      }
      var remain = Math.max(1, (total - el) / 1000 * speed);   /* "prawdziwe" ~30 s, nie 9 s */
      var eta = Math.round(remain * (31 / 9));
      window.App.onProgress({ krok: STAGES[si].krok, opis: STAGES[si].opis(pct), procent: Math.round(pct), eta_s: eta });
    }, 250);
  }

  /* ---- pakiet plików (1.3) ---- */
  function typOf(n) {
    return /\.(jpe?g|png|webp|gif|bmp|tiff?)$/i.test(n) ? 'obraz' : (/\.(docx?|rtf|odt|pdf|txt|md)$/i.test(n) ? 'dokument' : (/\.(pptx|ppsx)$/i.test(n) ? 'pptx' : 'inny'));
  }
  function pakietResult(paths) {
    var names = paths.map(function (p) { return String(p).split(/[\\/]/).pop(); });
    var sizes = [184320, 912384, 2411724, 58212, 340100, 1048576, 77824, 640000];
    var txtSize = ['180 KB', '891 KB', '2,3 MB', '57 KB', '332 KB', '1,0 MB', '76 KB', '625 KB'];
    var first = names.filter(function (n) { return typOf(n) === 'dokument'; })[0] || names[0];
    var tytul = first.replace(/\.[^.]+$/, '');
    var m = !/bezm/i.test(paths.join('|'));
    var uw = m ? [{ typ: 'info', tekst: 'Zdjęcia i zrzuty ekranu przeczyta czat, nie program - skopiuję je do folderu „Źródła”.' }]
      : [{ typ: 'ostrzezenie', tekst: 'Dysk M: jest teraz niedostępny, więc zapiszę folder w Dokumentach. Możesz to zmienić przyciskiem „Zmień…”.' }];
    var baza = m ? 'M:\\- POLSKA\\02 - FIRMOWE MATERIAŁY\\PREZENTACJE' : 'C:\\Users\\Marta\\Documents';
    var nazwa = '2026-10-27 - ' + tytul;
    var ist = /istnieje/i.test(paths.join('|'));
    return { res: Object.assign({ ok: true, tryb: 'pakiet', istnieje: ist },
      ist ? { scenariusz: true, scenariusz_wersja: 2, scenariusz_ok: !/zly/i.test(paths.join('|')), wyniki: ['Strategia produktowa 2027.pptx'],
        scenariusz_bledy: /zly/i.test(paths.join('|')) ? ['Slajd 2: brak hasła slajdu.', 'Slajd 5: tabela ma różną liczbę kolumn w wierszach.'] : [] } : {}, {
      pliki: names.map(function (n, i) { return { nazwa: n, sciezka: String(paths[i]), typ: typOf(n), rozmiar: sizes[i % sizes.length], rozmiar_tekst: txtSize[i % txtSize.length] }; }),
      tytul: tytul, baza: baza, nazwa_folderu: nazwa, folder: baza + '\\' + nazwa, m_dostepny: m, uwagi: uw,
      suwaki: { slajdy: { min: 4, max: 40, domyslnie: 12 }, rozdzialy: { max: 5, domyslnie: 2 } }, czas: { stale: 12, na_slajd: 1.2 } }),
      folder: baza + '\\' + nazwa, tytul: tytul, ver: 0 };
  }
  var SCEN = '# SCENARIUSZ DK\ntytuł: Strategia produktowa 2027\npodtytuł: Priorytety portfolio i plan wdrożeń\n\n' +
    '## Rynek rośnie szybciej niż zakładaliśmy\nTrzy trendy napędzają sprzedaż przekąsek białkowych w sklepach i online.\n- Dwucyfrowy wzrost kategorii białkowej\n- Coraz większy udział e-commerce\n- Konsumenci szukają krótkiego składu\n\n' +
    '## Liczba, która robi różnicę\n**42%** konsumentów czyta skład przed zakupem\n\n' +
    '## Co wyróżnia nasze portfolio\nPięć linii, jeden standard jakości.\n- Bez dodatku cukru\n- Źródło białka\n- Krótki skład\n\n' +
    '## Plan wdrożeń 2027\n| Kwartał | Premiera |\n| --- | --- |\n| Q1 | Kulki z kreatyną |\n| Q2 | Baton wanilia |\n\n' +
    '> Smak i skład idą u nas w parze - Dział R&D\n';
  var SCEN2 = SCEN.replace('Strategia produktowa 2027\npodtytuł: Priorytety', 'Strategia produktowa 2027 (wersja po uwagach)\npodtytuł: Priorytety') + '\n## Następne kroki\nTrzy decyzje na najbliższy miesiąc.\n- Zatwierdzić budżet premier\n- Wybrać kanały\n';
  var CZATY = { claude: 'Claude', chatgpt: 'ChatGPT', gemini: 'Gemini', claude_code: 'Claude Code' };
  function pakietDone(opts) {
    var v = ++pakiet.ver, noai = !!(opts && opts.bez_ai);
    var sl = noai ? Math.min((opts.slajdy || 12) + 2, 12) : (v > 1 ? 11 : 10);
    var name = pakiet.tytul + (v > 1 ? ' v' + v : '') + '.pptx';
    return {
      ok: true, tryb: noai ? 'dokument' : 'pakiet', wejscie: 'pakiet', pptx: pakiet.folder + '\\' + name, nazwa: name, slajdy: sl, ukryte: 0, nowe: [], sprawdz: [], wizualizacje: [],
      wiernosc: { usterki: [] }, czas_s: 28, miniatury: thumbs(sl), qa: { problemy: 0, szczegoly: [], wykonano: true },
      uwagi: [], bledy_okno: [], folder_pokaz: pakiet.folder, plansze_folder: pakiet.folder + '\\plansze',
      prompt_agent: 'Przeczytaj POLECENIE.md w folderze „' + pakiet.folder + '” i popraw scenariusz.',
      prompt_ai: 'Mam prezentację PowerPoint „' + name + '” zrobioną z dokumentów (bez AI). Pomóż mi ją dopracować: skróć teksty, popraw literówki.'
    };
  }

  /* ---- API ---- */
  var api = {
    get_info: function () { return sleep(80).then(function () { return { wersja: '1.0.0', powerpoint: true, szablony: ['nowy', 'stary'] }; }); },
    pick_file: function () { log('pick_file'); return sleep(400).then(function () { return 'D:\\Marketing\\- POLSKA\\02 - FIRMOWE MATERIAŁY\\Strategia produktowa 2027.docx'; }); },
    pick_pptx: function () { log('pick_pptx'); return sleep(400).then(function () { return 'D:\\Marketing\\- POLSKA\\02 - FIRMOWE MATERIAŁY\\PREZENTACJE\\06.10.2026 - strategia\\DK_co_dalej_update.pptx'; }); },
    pick_folder: function () { log('pick_folder'); return sleep(400).then(function () { return 'D:\\Marketing\\- POLSKA\\09 - PREZENTACJE\\Kulki z kreatyną'; }); },
    pick_files: function () {
      log('pick_files');
      return sleep(400).then(function () { return ['D:\\Marketing\\Strategia produktowa 2027.docx', 'D:\\Marketing\\Zrzut ekranu 2026-10-20 123456.png', 'D:\\Marketing\\Badanie konsumenckie Q3.pdf']; });
    },
    pick_parent: function () { log('pick_parent'); return sleep(400).then(function () { return 'D:\\Marketing\\- POLSKA\\02 - FIRMOWE MATERIAŁY\\PREZENTACJE'; }); },
    analyze_many: function (paths) {
      paths = [].concat(paths || []);
      log('analyze_many', paths.length);
      if (paths.length === 1 && typOf(String(paths[0])) !== 'obraz') return api.analyze(paths[0]);   /* jedno wejście: jak dawniej */
      lastFolder = paths[0];
      return sleep(analyzeMs).then(function () {
        if (paths.some(function (p) { return /blad/i.test(p); })) return { ok: false, blad: 'Nie mogę odczytać tych plików. Sprawdź, czy nie są otwarte w innym programie.' };
        pakiet = pakietResult(paths);
        return pakiet.res;
      });
    },
    create_folder: function (o) {
      log('create_folder', JSON.stringify(o));
      return sleep(700).then(function () {
        if (/blad/i.test(o.nazwa)) return { ok: false, blad: 'Nie mogę zapisać w tym miejscu. Wybierz inne przyciskiem „Zmień…”.' };
        pakiet.folder = String(o.baza).replace(/[\\/]+$/, '') + '\\' + o.nazwa;
        return { ok: true, folder: pakiet.folder, zrodla: pakiet.folder + '\\Źródła', blad: '' };
      });
    },
    ai_targets: function () {
      return sleep(100).then(function () {
        var last = q.get('ostatni') || 'claude';
        return [{ id: 'claude', nazwa: 'Claude', dostepny: true }, { id: 'chatgpt', nazwa: 'ChatGPT', dostepny: true },
          { id: 'gemini', nazwa: 'Gemini', dostepny: true }, { id: 'claude_code', nazwa: 'Claude Code', dostepny: q.get('cc') !== '0' }]
          .map(function (t) { return Object.assign(t, { ostatni: t.id === last }); });
      });
    },
    prepare_ai: function (ktory, o) {
      log('prepare_ai', ktory, JSON.stringify(o));
      clipN = 0; clipText = SCEN;
      return sleep(300).then(function () { return { ok: true, nazwa: CZATY[ktory] || ktory, gdzie: 'aplikacja', skopiowano: true, blad: '' }; });
    },
    improve_ai: function (ktory) {
      log('improve_ai', ktory);
      clipN = 0; clipText = SCEN2;
      return sleep(300).then(function () { return { ok: true, nazwa: CZATY[ktory] || ktory, gdzie: 'aplikacja', skopiowano: true, blad: '' }; });
    },
    peek_clipboard: function () {
      var on = clipN >= 0 && q.get('clip') !== '0';
      if (on) clipN++;
      return sleep(10).then(function () { return on && clipN > 2 ? clipText : null; });
    },
    save_scenario: function (text) {
      log('save_scenario', String(text).length + ' znaków');
      return sleep(400).then(function () {
        if (/BLAD/.test(text)) return { ok: false, plik: '', slajdy: 0, blad: 'W odpowiedzi brakuje nagłówka „# SCENARIUSZ DK” w pierwszej linii.', uwagi: ['Slajd 3: pusta linia „##” - brak hasła slajdu.'] };
        return { ok: true, plik: ((pakiet && pakiet.folder) || '') + '\\scenariusz.md', slajdy: 8, blad: '',
          uwagi: /UWAGA/.test(text) ? ['Slajd 4 miał 6 punktów - zostawiłem pierwsze 4.'] : [] };
      });
    },
    analyze: function (path) {
      log('analyze', path);
      pakiet = null;
      lastFolder = path;
      var name = String(path);
      return sleep(analyzeMs).then(function () {
        if (/blad/i.test(name)) return { ok: false, blad: 'Nie mogę odczytać tego folderu. Sprawdź, czy nie jest pusty i czy masz do niego dostęp.' };
        if (/skan/i.test(name)) return { ok: false, blad: 'To skan bez tekstu - program nie czyta obrazów. Zapisz dokument z tekstem (np. .docx) i upuść go jeszcze raz.' };
        if (/folder.programu/i.test(name)) return { ok: false, blad: 'To folder programu. Upuść folder produktu albo plik z prezentacją lub dokumentem.' };
        if (/\.(docx?|rtf|odt|pdf|txt|md)$/i.test(name)) return dokumentResult(name);
        if (jestDopr(name)) return doprResult(name);
        if (/\.(pptx|ppsx)$/i.test(name)) return pptxResult(name);
        if (/duzy/i.test(name)) return bigResult(name);
        if (/brak/i.test(name)) return thinResult(name);
        return fullResult(name);
      });
    },
    build: function (opts) { log('build', JSON.stringify(opts)); lastOpts = opts; if (opts && opts.packshoty) window.App.onLog('Paczki: ' + Object.keys(opts.packshoty).map(function (k) { return k + ' = ' + opts.packshoty[k]; }).join('; ')); runBuild(opts); return sleep(50).then(function () { return { started: true }; }); },
    open_path: function (p) { log('open_path', p); return sleep(50).then(function () { return true; }); },
    open_folder: function (p) { log('open_folder', p); return sleep(50).then(function () { return true; }); },
    copy_text: function (t) {
      log('copy_text', String(t).slice(0, 60) + '…');
      try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).catch(function () { /* bez uprawnień - pomijamy */ }); } catch (e) { /* nic */ }
      return sleep(50).then(function () { return true; });
    },
    check_update: function () {
      var on = q.get('update') === '1';
      return sleep(300).then(function () { return on ? { jest: true, wersja: '1.0.9', obecna: '1.0.0', sam: true, powod: '', strona: '' } : { jest: false, obecna: '1.0.0' }; });
    },
    apply_update: function () {
      var p = 0, t = setInterval(function () { p += 12; window.App.onUpdate({ procent: Math.min(100, p), restart: p >= 100 }); if (p >= 100) clearInterval(t); }, 250);
      return sleep(50).then(function () { return { started: true }; });
    },
    open_ai: function (k, t) {
      log('open_ai', k, String(t).length + ' znaków');
      var n = { claude: 'Claude', chatgpt: 'ChatGPT', gemini: 'Gemini' }[k];
      return sleep(50).then(function () { return n ? { ok: true, nazwa: n, klucz: k, skopiowano: true, gdzie: k === 'gemini' ? 'przegladarka' : 'aplikacja' } : { ok: false, blad: 'Nieznany czat.' }; });
    },
    cancel: function () { log('cancel'); clearInterval(timer); return sleep(50).then(function () { return true; }); }
  };

  window.pywebview = { mock: true, api: api, _lastFolder: function () { return lastFolder; }, _lastOpts: function () { return lastOpts; } };
})();
