# -*- coding: utf-8 -*-
"""Ostrzezenia o EWIDENTNYCH bledach tekstu slajdow (offline, tylko stdlib).

    import lint_tekst
    uwagi = lint_tekst.sprawdz([(12, ["... komunikacjaod anti-agingu ..."]), ...])
    for u in uwagi: print(lint_tekst.opis(u))

Program NIE poprawia tekstu (zasada 1:1) - tylko ostrzega; poprawia czlowiek albo AI.
Zasada nadrzedna: falszywy alarm jest gorszy niz pominiecie. Dlatego:
  * slowo jest "poprawne", gdy jest na liscie czestych form, w filtrze Blooma ze WSZYSTKIMI formami slownika sjp.pl
    albo na liscie slow angielskich (blad filtra = slowo uznane za poprawne = pominiecie, nigdy alarm),
  * `wysoka` pewnosc tylko dla wzorcow prawie bez wyjatkow, `srednia` dla reszty,
  * nazwy wlasne, skroty, slowa z cyfra / lacznikiem / adresy, biala lista, zdania obce i slowa powtarzane
    w prezentacji (autor pisze tak celowo) nigdy nie sa literowkami.
Slownik: assets/slownik/ (licencje: LICENCJA.txt), buduje go assets/slownik/buduj_slownik.py.

Kontrakt (staly):
    sprawdz(slajdy) -> [{"slajd", "rodzaj", "jest", "propozycja", "kontekst", "pewnosc"}]
      slajdy:  [(nr_slajdu, [tekst, ...]), ...]
      rodzaj:  sklejone | literowka | powtorzenie | interpunkcja | spacje | nawias
      pewnosc: wysoka | srednia
    opis(u) -> zdanie po polsku do pokazania uzytkownikowi / wklejenia do polecenia dla AI
"""
import collections
import hashlib
import lzma
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# szukamy slownika obok skilla (skill/scripts + skill/assets) i w kilku ukladach "splaszczonych" (program, PyInstaller)
_KAND = [os.path.join(HERE, "..", "assets", "slownik"), os.path.join(HERE, "assets", "slownik"),
         os.path.join(HERE, "slownik"), os.path.join(getattr(sys, "_MEIPASS", HERE), "assets", "slownik")]
DIR = next((d for d in _KAND if os.path.exists(os.path.join(d, "czeste.xz"))), _KAND[0])

# --- dane (leniwie: import kosztuje ~0, pierwsze sprawdz() ~0.1 s) -----------------------------------------------
_S = {}


def _dane():
    if _S:
        return _S
    with lzma.open(os.path.join(DIR, "czeste.xz"), "rt", encoding="utf-8") as f:
        pl, obce, ang = f.read().split("\n\n")
    with open(os.path.join(DIR, "forms.bloom"), "rb") as f:
        raw = f.read()
    _S["rank"] = {w: i for i, w in enumerate(pl.split("\n"))}
    _S["obce"] = set(obce.split())
    _S["ang"] = set(ang.split())
    _S["m"] = int.from_bytes(raw[:4], "little")
    _S["k"] = raw[4]
    _S["bits"] = memoryview(raw)[5:]
    return _S


def _bloom(w):
    S = _dane()
    m, bits = S["m"], S["bits"]
    d = hashlib.blake2b(w.encode("utf-8"), digest_size=16).digest()
    h1, h2 = int.from_bytes(d[:8], "little") % m, (int.from_bytes(d[8:], "little") | 1) % m or 1
    for i in range(S["k"]):
        b = (h1 + i * h2) % m
        if not bits[b >> 3] & (1 << (b & 7)):
            return False
    return True


# Biala lista: slowa obce i marketingowe, ktore autor pisze celowo
BIALA = set("""beauty snack snacking snacks trial insight insights target targeting premium well-being wellbeing longevity
anti-aging antiaging lifestyle fit fitness vege vegan bio clean label glp gen millenials millennials millennial matcha
protein proteinowy proteinowe shot shoty shots healthy superfood superfoods smoothie foodtech food-tech
dobrakaloria kubara kubary kubarze mindset lato online offline e-commerce ecommerce marketing brand branding storytelling
packshot packshoty display mix mixy box boxy bar bary baton batony hype trend trendy
b2b b2c retail horeca fmcg kpi roi okr crm seo sem pr creatine kreatyna kreatyny kolagen zero keto paleo low carb high
logo layout banner slajd slajdy slajdów""".split())

# Slowa funkcyjne 2-3 literowe, ktore wolno uznac za czesc sklejonego wyrazu
FUNC = set("od do na po za ze we bez pod nad przy dla oraz lub czy jak ale że się nie to przez ponad wśród też tak już "
           "jest są ma co aby gdy".split())
FUNC_KONIEC = set("od do na po za ze we dla oraz lub czy jak ale że się".split())  # po nich sklejenie to prawie zawsze blad
FUNC_POCZATEK = set("dla oraz lub ale czy jak się".split())  # nie bywaja przedrostkiem ("do-stepny", "pod-naglowek" bywaja)
KONCOWKI_PEWNE = set("od dla oraz lub czy jak się ale".split())  # po slowie czestym: sklejenie prawie na pewno
POWT_OK = set("nie tak ha he hi ho no bla la to co bardzo mniam da ra ta ma".split())  # powtorzenia bywaja celowe
POWT_WYSOKA = set("na w z do od po za ze we i o u a że się oraz lub jest są dla przy bez pod nad przez".split())
STOP_ANG = set("the and of with that this for you your are is was our we from have has will can not but when which their "
               "they more about into than how what".split())
KSZTALT_ANG = re.compile(r"th|wh|sh|gh|ph|ck|oo|ee|[qvx]|ing$|ed$|ies$|ness|tion|ly$|ers$|ors$")

ALFABET = "abcdefghijklmnopqrstuvwxyząćęłńóśźż"
POLSKIE = re.compile(r"^[a-ząćęłńóśźż]+$")
SPECJALNE = re.compile(r"[\d@/\\#_%&=+<>|~^*]|https?:|www\.|\.[a-z]{2,4}\b", re.I)
KONIEC_ZDANIA = (".", "!", "?", "…", ":", ";")
BULLETY = {"•", "-", "–", "—", "·", "*", "▪", "►", "→", "✓", "✔"}
_OGONKI = str.maketrans("ąćęłńóśźż", "acelnoszz")
_PRZYCIECIE = " \t\r\n.,;:!?…()[]{}„”“\"'«»‘’–—"
_CHUNK = re.compile(r"\S+")


def _poprawne(w):
    """Czy slowo (male litery) jest znane: biala lista, lista czestych, slowa z napisow, angielskie, filtr Blooma."""
    if len(w) <= 2 or w in BIALA:
        return True
    S = _dane()
    if w in S["rank"] or w in S["obce"] or w in S["ang"] or _bloom(w):
        return True
    return w.startswith("nie") and len(w) > 5 and _poprawne(w[3:])  # przedrostek nie- (formy z nie- nie sa w filtrze)


def _angielskie(w):
    S = _dane()
    return len(w) >= 4 and w in S["ang"] and w not in S["rank"] and not _bloom(w)


def _dobry_czlon(w):
    return w in FUNC or (len(w) >= 4 and w in _dane()["rank"])


def _wielkosc(wzor, tekst):
    if len(wzor) > 1 and wzor.isupper():
        return tekst.upper()
    if wzor[:1].isupper():
        return tekst[:1].upper() + tekst[1:]
    return tekst


# --- tokeny -----------------------------------------------------------------------------------------------------
def _linie(tekst):
    pos = 0
    for ln in re.split(r"(\n)", tekst):
        if ln != "\n":
            yield pos, ln
        pos += len(ln)


def _tokeny(tekst):
    """(rdzen, start, koniec, poczatek_zdania) dla kazdego fragmentu miedzy spacjami, bez interpunkcji z brzegow."""
    out = []
    for ln_start, ln in _linie(tekst):
        prev, pierwszy = "", True
        for m in _CHUNK.finditer(ln):
            ch = m.group()
            s = ch.lstrip(_PRZYCIECIE)
            r = s.rstrip(_PRZYCIECIE)
            if r:
                start = ln_start + m.start() + len(ch) - len(s)
                poczatek = pierwszy or prev.endswith(KONIEC_ZDANIA) or prev in BULLETY or (
                    prev.endswith(")") and len(prev) <= 3)
                out.append((r, start, start + len(r), poczatek))
                pierwszy = False
            prev = ch
    return out


def _norm(t):
    return t.replace("\x1f", " ").replace("\x0b", "\n").replace("\r", "\n").replace("\xa0", " ").replace("​", "")


def _ctx(tekst, a, b, n=30):
    l, r = max(0, a - n), min(len(tekst), b + n)
    return ("…" if l else "") + " ".join(tekst[l:r].split()) + ("…" if r < len(tekst) else "")


def _zwykle(r):
    """Rdzen to jedno zwykle slowo z liter polskiego alfabetu (bez cyfr, lacznikow, adresow)?"""
    return POLSKIE.match(r.lower()) is not None and not SPECJALNE.search(r)


def _licz(slajdy):
    c = collections.Counter()
    for _, teksty in slajdy:
        for t in teksty:
            for r, *_ in _tokeny(t):
                if _zwykle(r):
                    c[r.lower()] += 1
    return c


# --- slowa: sklejone / literowki ---------------------------------------------------------------------------------
def _edits1(w):
    sp = [(w[:i], w[i:]) for i in range(len(w) + 1)]
    out = {a + b[1:] for a, b in sp if b}
    out |= {a + b[1] + b[0] + b[2:] for a, b in sp if len(b) > 1}
    out |= {a + c + b[1:] for a, b in sp if b for c in ALFABET}
    out |= {a + c + b for a, b in sp for c in ALFABET}
    out.discard(w)
    return out


def _sklejone(w, ostro):
    """(A, B, pewnosc) albo None. w: male litery, slowo spoza slownika. ostro: tylko wzorzec z przyimkiem."""
    rank = _dane()["rank"]
    najlepsze = None
    for i in range(2, len(w) - 1):
        a, b = w[:i], w[i:]
        fa, fb = a in FUNC, b in FUNC
        if fa and fb or not _dobry_czlon(b) or not (
                _dobry_czlon(a) or (b in KONCOWKI_PEWNE and len(a) >= 6 and _poprawne(a))):
            continue
        if fb:  # slowo + przyimek ("komunikacjaod")
            if len(a) < 5:
                continue
            wys = b in FUNC_KONIEC
        elif fa:  # przyimek + slowo ("dlaklientow"); "do/od/na/po/za/pod/przy..." bywaja przedrostkiem - pomijamy
            if a not in FUNC_POCZATEK or len(b) < 5:
                continue
            wys = True
        else:  # dwa zwykle slowa: tylko bardzo pewne czlony i dlugie slowo, nigdy na poczatku zdania ani wersalikami
            if ostro or len(w) < 10 or min(len(a), len(b)) < 5 or rank[a] > 20000 or rank[b] > 20000:
                continue
            wys = False
        ocena = (not wys, (0 if fa else rank.get(a, 150000)) + (0 if fb else rank.get(b, 150000)))
        if najlepsze is None or ocena < najlepsze[0]:
            najlepsze = (ocena, a, b, "wysoka" if wys else "srednia")
    return None if najlepsze is None else najlepsze[1:]


def _glue_pewne(w):
    """Slowo czeste + spojnik / przyimek ("pokazujeod"): sklejone nawet gdy filtr Blooma przez pomylke uzna je za slowo."""
    rank = _dane()["rank"]
    for b in KONCOWKI_PEWNE:
        if w.endswith(b) and len(w) - len(b) >= 5 and rank.get(w[:-len(b)], 1 << 30) < 30000:
            return w[:-len(b)], b
    return None


def _literowka(w):
    """Najlepsza poprawka: slowo z przywroconymi ogonkami albo jedyne bliskie slowo czeste (1 zmiana), inaczej None."""
    S = _dane()
    rank = S["rank"]
    if "bez_ogonkow" not in S:
        S["bez_ogonkow"] = idx = {}
        for c, r in rank.items():  # przy kilku kandydatach wygrywa najczestszy
            b = c.translate(_OGONKI)
            if b != c and rank.get(idx.get(b), 1 << 30) > r:
                idx[b] = c
    if w in S["bez_ogonkow"]:
        return S["bez_ogonkow"][w]
    sas = [c for c in _edits1(w)
           if c in rank and rank[c] < 100000 and c[0].translate(_OGONKI) == w[0].translate(_OGONKI)
           and c[:-1] != w[:-1] and c != w[:-1] and c[:-1] != w]  # zmiana ostatniej litery = raczej inna forma / obce slowo
    return sas[0] if len(sas) == 1 else None


def _adres_obok(tekst, a, b):
    przed, po = tekst[a - 1:a] if a else "", tekst[b:b + 1]
    return przed in ("@", "#", "/") or po in ("@", "/", "#") or (
        po == "." and tekst[b + 1:b + 2].islower()) or (przed == "." and tekst[a - 2:a - 1].isalpha())


def _wersaliki(tekst):
    lit = [c for c in tekst if c.isalpha()]
    return len(lit) >= 6 and not any(c.islower() for c in lit)


def _slowa(nr, tekst, licz, uw):
    caps_tekst = _wersaliki(tekst)
    kand, nieznane, wszystkie, ang, stop = [], 0, 0, 0, set()
    for r, a, b, poczatek in _tokeny(tekst):
        w = r.lower()
        if w in STOP_ANG:
            stop.add(w)
        if not _zwykle(r) or _adres_obok(tekst, a, b):
            continue
        pomin = False
        if not caps_tekst:  # skrot, camelCase, nazwa wlasna w srodku zdania
            pomin = (len(r) > 1 and r.isupper()) or any(c.isupper() for c in r[1:]) or (r[:1].isupper() and not poczatek)
        znane = _poprawne(w)
        if len(w) >= 4 and not pomin:
            wszystkie += 1
            nieznane += not znane
            ang += _angielskie(w)
        if not pomin and (not znane or (len(w) >= 7 and w not in _dane()["rank"] and w not in BIALA
                                        and w not in _dane()["obce"] and w not in _dane()["ang"] and _glue_pewne(w))):
            kand.append((r, w, a, b, poczatek and (r[:1].isupper() or caps_tekst)))
    if len(stop) >= 2 or ang >= 2 or (nieznane >= 3 and nieznane >= 0.3 * wszystkie):
        return  # zdanie obce (np. cytat po angielsku) albo mieszanka: nie oceniamy
    for r, w, a, b, wielka_poczatek in kand:
        if len(w) >= 6 and licz[w] < 3:
            s = _sklejone(w, ostro=wielka_poczatek or caps_tekst)
            if not s and _glue_pewne(w):
                s = (*_glue_pewne(w), "wysoka")
            if s:
                x, y, pew = s
                uw.append((a, nr, "sklejone", r, _wielkosc(r, x + " " + y), _ctx(tekst, a, b), pew))
                continue
        if len(w) >= 5 and licz[w] < 2 and not KSZTALT_ANG.search(w) and not _poprawne(w):
            n = _literowka(w)
            if n:
                uw.append((a, nr, "literowka", r, _wielkosc(r, n), _ctx(tekst, a, b), "srednia"))


def _powtorzenia(nr, tekst, uw):
    for ln_start, ln in _linie(tekst):
        for m in re.finditer(r"(?<![\w-])([^\W\d_]{2,})([ \t]+)\1(?![\w-])", ln):
            w = m.group(1).lower()
            if w in POWT_OK:
                continue
            uw.append((ln_start + m.start(), nr, "powtorzenie", m.group(0), m.group(1),
                       _ctx(tekst, ln_start + m.start(), ln_start + m.end()), "wysoka" if w in POWT_WYSOKA else "srednia"))


# --- interpunkcja, spacje, nawiasy -------------------------------------------------------------------------------
_ADRES = re.compile(r"(?i:https?://|www\.)\S+|\S+@\S+|\b[\w-]+(?:\.[a-z]{2,4}){1,2}\b(?:/\S*)?")
_MAL = "a-ząćęłńóśźż"
_DUZ = "A-ZĄĆĘŁŃÓŚŹŻ"
_REGULY = [  # (wzorzec miejsca bledu, co wstawic zamiast dopasowania)
    # smak,ale -> smak, ale (przynajmniej jedna strona malymi: "PL,EN" to nie blad)
    (rf"(?:(?<=[{_MAL}]),(?=[{_MAL}{_DUZ}]{{2}})|(?<=[{_DUZ}]),(?=[{_MAL}]{{2}}))", ", "),
    # smaku.Dobre -> smaku. Dobre (nie skroty typu "S.A.")
    (rf"(?<=[{_MAL}]{{2}})\.(?=[{_DUZ}][{_MAL}]{{2}})", ". "),
    # smak , ale -> smak, ale   |   smak . Dobre -> smak. Dobre
    (rf"(?<=[{_MAL}{_DUZ}\d])[ \t]+(?=[,;])", ""),
    (rf"(?<=[{_MAL}{_DUZ}])[ \t]+(?=\.(?!\.)(?:\s|$))", ""),
    # dwie kropki zamiast "…"
    (r"(?<![.])\.\.(?![.])", "…"),
]


def _interpunkcja(nr, tekst, uw):
    t = _ADRES.sub(lambda m: "x" * len(m.group()), tekst)  # kropki w adresach to nie blad
    for rx, wstaw in _REGULY:
        for m in re.finditer(rx, t):
            a = m.start()
            l, r = a, m.end()
            while l > 0 and not t[l - 1].isspace():
                l -= 1
            while r < len(t) and not t[r].isspace():
                r += 1
            uw.append((a, nr, "interpunkcja", tekst[l:r], tekst[l:a] + wstaw + tekst[m.end():r], _ctx(tekst, l, r),
                       "wysoka"))
    for m in re.finditer(r"(\S+)([ ]{2,})(\S+)", tekst):
        uw.append((m.start(), nr, "spacje", m.group(), m.group(1) + " " + m.group(3), _ctx(tekst, m.start(), m.end()),
                   "srednia"))


_EMOT = re.compile(r"[:;]-?[()]")
_MARKER = re.compile(r"(?m)^\s*(?:[a-zA-Z]|\d{1,2})\)")


def _nawiasy(nr, tekst, uw):
    """tekst = wszystkie teksty slajdu: zawijanie wierszy rozcina nawias miedzy kawalki, wiec liczymy na calym slajdzie."""
    t = _MARKER.sub("", _EMOT.sub("", tekst))
    t = re.sub(r'(?m)^\s*[„”"“]\s*$', "", t)  # samotny znak cudzyslowu to ozdoba (duzy cudzyslow przy opinii)
    for o, z in (("(", ")"), ("[", "]")):
        no, nz = t.count(o), t.count(z)
        if no != nz:
            i = t.find(o) if no > nz else t.find(z)
            uw.append((i, nr, "nawias", o if no > nz else z, "", _ctx(tekst, i, i + 1, 25), "srednia"))
    no, nc, st = t.count("„"), t.count("”"), t.count('"')
    if "“" not in t and (no or nc) and no != nc and no != nc + st:
        i = t.find("„") if no > nc else t.find("”")
        uw.append((i, nr, "nawias", "„" if no > nc else "”", "", _ctx(tekst, i, i + 1, 25), "srednia"))
    elif no == nc and st % 2:
        i = t.find('"')
        uw.append((i, nr, "nawias", '"', "", _ctx(tekst, i, i + 1, 25), "srednia"))


# --- API ---------------------------------------------------------------------------------------------------------
def sprawdz(slajdy):
    """slajdy: [(nr_slajdu, [tekst, ...]), ...] -> lista uwag (patrz doc modulu), po slajdach i miejscu w tekscie."""
    slajdy = [(n, [_norm(t) for t in ts if t and t.strip()]) for n, ts in slajdy]
    licz = _licz(slajdy)
    wynik = []
    for nr, teksty in slajdy:
        widziane = set()
        for t, uw in [(t, []) for t in teksty] + [(None, [])]:
            if t is None:  # nawiasy: na calym slajdzie
                _nawiasy(nr, "\n".join(teksty), uw)
            else:
                _slowa(nr, t, licz, uw)
                _powtorzenia(nr, t, uw)
                _interpunkcja(nr, t, uw)
            for _poz, n, rodzaj, jest, prop, kon, pew in sorted(uw, key=lambda x: x[0]):
                if (rodzaj, jest) in widziane:
                    continue
                widziane.add((rodzaj, jest))
                wynik.append({"slajd": n, "rodzaj": rodzaj, "jest": jest, "propozycja": prop, "kontekst": kon,
                              "pewnosc": pew})
    return wynik


def opis(u):
    n, j, p = u["slajd"], u["jest"], u["propozycja"]
    r = u["rodzaj"]
    if r == "sklejone":
        return f"Slajd {n}: „{j}” wygląda na sklejone słowa - może „{p}”?"
    if r == "literowka":
        return f"Slajd {n}: „{j}” wygląda na literówkę - może „{p}”?"
    if r == "powtorzenie":
        return f"Slajd {n}: powtórzone słowo „{j}” - może wystarczy „{p}”?"
    if r == "interpunkcja":
        return f"Slajd {n}: błąd interpunkcji w „{j}” - powinno być „{p}”."
    if r == "spacje":
        return f"Slajd {n}: podwójna spacja w „{j}” - wystarczy jedna."
    return f"Slajd {n}: niedomknięty nawias lub cudzysłów „{j}” w: {u['kontekst']}"
