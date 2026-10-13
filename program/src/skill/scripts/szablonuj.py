# -*- coding: utf-8 -*-
"""szablonuj.py - krok „szablonowanie” konwersji PPTX (13.10.2026, odwrócona inżynieria ręcznej wersji kierownika).

Po tym, jak `pptx_convert._uklad` ułoży slajd w wiersze `uklad` (karty, kafle, cytat, obrazy), ten krok zamienia GOŁY
TEKST w klocki szablonu marki: liczba-bohater (`hero`), nagłówek karty (`h`), pas-wniosek (`band`), kafle z ikoną
(`icon`), etykieta / wartość (`kv`), punkty z ikoną (`li`), karta zielona (`fill: brand`). Reguły S1-S13:
`references/konwersja-pptx.md`, pkt 2b. Żadne słowo nie znika, nie dochodzi i nie zmienia kolejności (jedyny wyjątek jawny:
liczba-bohater powtarza liczbę, która stoi w zdaniu pod nią) - po każdym slajdzie `slowa()` porównuje zestawy słów
i przy różnicy slajd zostaje taki, jaki był.

    stosuj(sp, n) -> (nowy_slajd, decyzje) albo (None, [])      # sp = slajd typu `uklad` (spec, wiersze bez znaczników `_`)

Czego NIE robi (zostaje dla agenta AI): słupki `bars` (etykiet nie da się pewnie wyciąć ze zdania), wybór ikony „po sensie”,
łączenie zdań w pary pytanie / odpowiedź.
"""
import collections
import contextlib
import copy
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
IKONY_JSON = os.path.join(HERE, "..", "assets", "ikony-slowa.json")
KATALOG_JSON = os.path.join(HERE, "..", "assets", "katalog-szablonu.json")  # 65 slajdów szablonu: id, nr, nazwa (worker katalogu)
IKONY_DK = os.path.join(HERE, "..", "assets", "icons", "dk")  # zestaw marki „W stylu DK”: <nazwa>.png
IKONY_STARE = os.path.join(HERE, "..", "assets", "icons", "svg")  # zapas, gdy folderu `dk` jeszcze nie ma: <nazwa>.svg
IKONY_SVG = IKONY_DK if os.path.isdir(IKONY_DK) else IKONY_STARE  # folder ikon, z którego korzysta kontrola słownika
IKONA_EXT = ".png" if IKONY_SVG == IKONY_DK else ".svg"
ABBR = {"r.", "ok.", "np.", "m.in.", "tzw.", "tj.", "wg.", "itd.", "itp.", "mln.", "mld.", "tys.", "godz.", "min.", "ul."}
MAX_SLOW = 45  # S2: jednostka tekstu najwyżej 45 słów
# 13.10 (user): „za dużo Lato, za mało haseł” -> S14 „hasłowanie” (zdanie = hasło Mindset + krótki dopisek Lato) wygrywa z S2 / S5 /
# S11 tam, gdzie się różnią; wszystkie reguły są włączone (WSTRZYMANE = zbiór nazw wyłączonych, np. {"S14"} w testach).
WSTRZYMANE = set()
# S1(e): znaczniki wniosku na początku zdania
ZNACZNIKI = ("ale ", "ważna kwestia", "insight:", "wniosek", "temat do", "dlatego", "czyli")
NEGATYWNE = re.compile(r"ślepy zaułek|odjechał|zła wiadomość|zagroż", re.I)  # wniosek negatywny -> pas czerwony
_JEDN = r"(?:(?:mln|mld|tys\.?)(?:\s?zł)?|%|zł|g/kg|kg|g|lat)"
_LICZBA = re.compile(r"[+~≈]?\d+(?:[.,]\d+)?(?:\s?[–-]\s?\d+(?:[.,]\d+)?)?\s?" + _JEDN + r"(?![\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ/])", re.I)

CALE = 12
HMIN = 4
HMAX = 15
HDLUGIE = 24
SPOJ = ("i", "oraz", "ale", "wobec", "czyli")
_IK = None


def ikona_istnieje(nazwa):
    """Czy ikona o tej nazwie jest w zestawie (dk\\<nazwa>.png albo, bez folderu dk, stare svg\\<nazwa>.svg)."""
    return os.path.isfile(os.path.join(IKONY_SVG, nazwa + IKONA_EXT))


def ikony():
    """(lista (rdzeń, ikona) od najdłuższych rdzeni, słownik całych słów) ze słownika S13."""
    global _IK
    if _IK is None:
        try:
            with open(IKONY_JSON, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            d = {}
        _IK = (sorted((k, v) for k, v in d.get("rdzenie", {}).items() if k.strip() == k),
               dict(d.get("slowa", {})))
        _IK = (sorted(_IK[0], key=lambda kv: -len(kv[0])), _IK[1])
    return _IK


def ikona_dla(tekst, ik=None):
    """S13: pierwsze trafienie w tekście (słowo po słowie od początku): całe słowo ze `slowa` albo słowo zaczynające się
    od rdzenia -> nazwa ikony; brak trafienia -> None."""
    rdzenie, slowa_ = ikony() if ik is None else ik
    for w in re.findall(r"[^\W\d_]+", tekst.lower()):
        if w in slowa_:
            return slowa_[w]
        for rdzen, nazwa in rdzenie:
            if w.startswith(rdzen):
                return nazwa
    return None


# --- tekst: (t, wyr) bez przepisywania -----------------------------------------------------------------------------
def para(b):
    """Blok / wiersz -> (tekst, wyr); wyr tylko, gdy ma tyle znaków co słów."""
    t, w = b.get("t") or "", b.get("wyr")
    if w and len(w) != len(t.split()):
        w = None
    return (t, w)


def zdania(p):
    """(t, wyr) -> [(t, wyr)]: granica = słowo kończące się .!?… i następne z wielkiej litery (bez skrótów)."""
    t, w = p
    toks = t.split()
    out, cur, cf = [], [], []
    for i, tok in enumerate(toks):
        cur.append(tok)
        if w:
            cf.append(w[i])
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        if nxt and tok[-1] in ".!?…" and tok.lower() not in ABBR and \
                (nxt[0].isupper() or nxt[0] in "„\"(" or tok.lower() == "zł."):  # „zł.” w środku zdania nie ma kropki
            out.append((" ".join(cur), "".join(cf) if w else None))
            cur, cf = [], []
    if cur:
        out.append((" ".join(cur), "".join(cf) if w else None))
    return out


def tnij(p, n):
    """Pierwsze n słów | reszta."""
    t, w = p
    toks = t.split()
    return (" ".join(toks[:n]), w[:n] if w else None), (" ".join(toks[n:]), w[n:] if w else None)


def flow(p):
    """Te same słowa bez wymuszonych łamań linii autora (karta łamie tekst sama)."""
    return (" ".join(p[0].split()), p[1])


def sklej(ps):
    if not ps:
        return ("", None)
    w = "".join(p[1] or "-" * len(p[0].split()) for p in ps) if any(p[1] for p in ps) else None
    return (" ".join(p[0] for p in ps), w)


def nslow(p):
    return len(p[0].split())


def blok(k, p, **kw):
    """Blok tekstowy z (t, wyr); `wyr` tylko, gdy coś wyróżnia."""
    t, w = p
    b = {"k": k, "t": t}
    if w and set(w) != {"-"}:
        b["wyr"] = w
    b.update(kw)
    return b


def kolor_bloku(b):
    """Kolor przenoszony na części bloku (całe pole czerwone: color accent)."""
    return {"color": b["color"]} if b.get("color") else {}


def czesc(b, p, k=None):
    """Blok-część: tekst p, rodzaj i kolor jak w b."""
    return blok(k or b["k"], p, **kolor_bloku(b))


def calosc_kolor(b):
    """Blok w całości w kolorze: color accent albo wyr bez słów w kolorze bazowym ('-')."""
    if b.get("color") == "accent":
        return True
    w = b.get("wyr")
    return bool(w) and len(w) == len((b.get("t") or "").split()) and "-" not in w


def liczba_bohater(p):
    """S2 / S14d: liczba z jednostką ze zdania: pierwsza wyróżniona (`wyr` a / i), inaczej pierwsza z jednostką; „z X do Y” ->
    Y (cel). Zwraca tekst liczby (stoi dosłownie w zdaniu) albo None. Rok i liczby porządkowe się nie liczą (brak jednostki)."""
    t, w = p
    starts = [m.start() for m in re.finditer(r"\S+", t)]
    ms = list(_LICZBA.finditer(t))
    if not ms:
        return None
    wyb = None
    if w:
        for m in ms:
            idx = max(i for i, s in enumerate(starts) if s <= m.start())
            if idx < len(w) and w[idx] in "ai":
                wyb = m
                break
    wyb = wyb or ms[0]
    m2 = re.compile(r"\s+do\s+").match(t, wyb.end())
    m3 = _LICZBA.match(t, m2.end()) if m2 else None
    return (m3 or wyb).group(0).strip()


def tekst_karty(item):
    return " ".join(b.get("t", "") for b in item["blocks"] if b["k"] in ("h", "lead", "p", "b", "li", "hero"))


# --- klocki ---------------------------------------------------------------------------------------------------------
def k_icon(name, **kw):
    return dict({"k": "icon", "name": name, "bg": True}, **kw)


def k_karta(*blocks, **kw):
    return dict({"blocks": [b for b in blocks if b]}, **kw)


def k_cols(items, **kw):
    r = {"k": "cols", "items": list(items), "card": True, "kont": True, "valign": "t"}
    r.update(kw)
    return r


def k_band(p, fill="brand", **kw):
    r = {"k": "band", "t": p[0], "fill": fill}
    if p[1] and set(p[1]) != {"-"}:
        r["wyr"] = p[1]
    r.update(kw)
    return r


# --- wzory z katalogu szablonu (13.10): reguła -> slajd szablonu, który naśladuje --------------------------------------------
WZORY = {"fakt-z-liczba": ("t62", "t38"), "jedno-zdanie-kafel": ("t62", "t38"), "kafle-ikony": ("t56",),
         "lista-z-ikona": ("t17",), "etykieta-wartosc": ("t45",), "teza-zielona": ("t14",), "para-kontrast": ("t59", "t21"),
         "cytat": ("t20",), "cytat-wynik": ("t60",), "obrazy-wniosek": ("t63",), "slupki": ("t39",), "haslowanie": ("t61",)}
# pierwszy id z listy, który jest w katalogu (t62 = „Trzy fakty w kartach”; bez niego t38 = „Wskaźniki (KPI)”)
_KAT = {}


def katalog():
    """{id: {"id", "nr", "nazwa"}} z assets/katalog-szablonu.json; brak pliku albo błąd = {} (pole `wzor` puste, bez błędu)."""
    if KATALOG_JSON not in _KAT:
        out = {}
        try:
            with open(KATALOG_JSON, encoding="utf-8") as f:
                for s in json.load(f).get("slajdy", []):
                    out[s["id"]] = {"id": s["id"], "nr": s.get("nr"), "nazwa": s.get("nazwa", "")}
        except (OSError, ValueError, KeyError, TypeError):
            out = {}
        _KAT[KATALOG_JSON] = out
    return _KAT[KATALOG_JSON]


def wzor(wzorzec):
    """Slajd szablonu, który naśladuje reguła (klucz z WZORY): {"id": "t62", "nr": 62, "nazwa": "..."} albo None (brak
    mapowania / katalogu). Z kilku id bierze pierwszy, który jest w katalogu."""
    kat = katalog()
    for i in WZORY.get(wzorzec, ()):
        if i in kat:
            return kat[i]
    return None


def opis_wzorow(decyzje, limit=12):
    """Uwaga dla użytkownika: „slajd 18: Liczby w kaflach (wzór: slajd 38 szablonu)”; do `limit` pozycji, reszta „…i N innych”."""
    wid, widziane = [], set()
    inne = {d["slajd"] for d in decyzje if d.get("wzor") and d["wzor"]["id"] != "t61"}  # „Akapit w karcie” tylko gdy nic lepszego
    for d in decyzje:
        w = d.get("wzor")
        if not w or (d["slajd"], w["id"]) in widziane or (w["id"] == "t61" and d["slajd"] in inne):
            continue
        widziane.add((d["slajd"], w["id"]))
        wid.append("slajd %s: %s (wzór: slajd %s szablonu)" % (d["slajd"], w["nazwa"], w["nr"]))
    if not wid:
        return ""
    reszta = len(wid) - limit
    return "; ".join(wid[:limit]) + ("; …i %d innych (decyzje-szablon.json)" % reszta if reszta > 0 else "")


def _placeholder(sp):
    """Slajd z placeholderami szablonu: jakikolwiek tekst z „[” albo „]” (prezentacja „onlien”: „[Tytuł z hasłem]”). Taki slajd
    zostaje jak przed szablonowaniem - nic nie hasłujemy, nie robimy z tego kafli ani liczb."""
    def tk(o):
        if isinstance(o, str):
            return ("[" in o) or ("]" in o)
        if isinstance(o, dict):
            return any(tk(v) for k, v in o.items() if k in ("t", "title", "kicker", "label", "author", "items", "rows", "blocks"))
        if isinstance(o, list):
            return any(tk(x) for x in o)
        return False
    return tk({"title": sp.get("title"), "kicker": sp.get("kicker"), "rows": sp.get("rows", [])})


# =====================================================================================================================
def _opcje_st(opcje):
    """Opcje wariantu (osie kandydatów, 9b) -> znaczniki w zbiorze `st`. Brak klucza = decyduje reguła (domyślny wariant).
    ikony: True / False (ikony na kartach zawsze / nigdy), siatka: "rzad" / "siatka" (4-6 kart w jednym rzędzie / w siatce),
    h_wiersz: True / False (nagłówek do myślnika jako wiersz nad kartami / w karcie), zdania: "dopisek" / "li" (kolejne zdania
    akapitu jako dopisek / jako punkty `li`; wyłącza S15), pad: mnożnik paddingu kart (np. 0.75)."""
    st, o = set(), opcje or {}
    if o.get("ikony") is True:
        st.add("IKONY-TAK")
    elif o.get("ikony") is False:
        st.add("BEZ-IKON")
    if o.get("siatka"):
        st.add("SIATKA:" + o["siatka"])
    if o.get("h_wiersz") is True:
        st.add("H-WIERSZ-TAK")
    elif o.get("h_wiersz") is False:
        st.add("H-WIERSZ-NIE")
    if o.get("zdania") == "dopisek":
        st.add("ZDANIA-DOPISEK")
    elif o.get("zdania") == "li":
        st.add("ZDANIA-LI")
    if o.get("pad"):
        st.add("PAD:%s" % o["pad"])
    return st


def stosuj(sp, n=0, wstrzymane=None, ikony_kart=True, opcje=None):
    """Szablonowanie jednego slajdu `uklad`. Zwraca (nowy slajd, decyzje) albo (None, []) gdy nic się nie zmienia / słowa
    się nie zgadzają. wstrzymane: zbiór nazw reguł wyłączonych (S2, S5, S11, S14, S15); ikony_kart=False: karty tekstowe bez
    ikon; opcje: wariant układu (`_opcje_st`) - kandydaci slajdu to `stosuj` z różnymi opcjami (`kandydaci`)."""
    if sp.get("type") != "uklad" or not sp.get("rows") or _placeholder(sp):
        return None, []
    dec = []
    st = set(WSTRZYMANE if wstrzymane is None else wstrzymane) | _opcje_st(opcje)
    if not ikony_kart:
        st.add("BEZ-IKON")

    def note(wz, opis, wz_wzor=None):
        dec.append({"slajd": n, "wzorzec": wz, "wzor": wzor(wz_wzor or wz), "opis": opis})

    new = copy.deepcopy(sp)
    rows = copy.deepcopy(sp["rows"])
    rows = _s3(new, rows, note)
    rows = _s4_kafle(rows, note)
    rows = _s6_kv(rows, note)
    rows = _s1_wiersze(rows, note)
    rows = _karty(new, rows, note, st)
    if not dec:
        return None, []
    if ikony_kart and "IKONY-TAK" not in st and "BEZ-IKON" not in st and len(rows) >= 4:
        # 13.10: slajd z >= 4 wierszami (nagłówek + karty + kv + pas, s37): karty bez ikon od razu (wariant „ikony tak” to wymusza)
        return stosuj(sp, n, wstrzymane, ikony_kart=False, opcje=opcje)
    rows = _siatka_rows(rows, st)
    rows = _pad_rows(rows, st)
    new["rows"] = rows
    new["valign"] = "t"  # S12: treść startuje pod tytułem, wolne miejsce zostaje na dole (jak s21 / s38 szablonu)
    if slowa(sp) != slowa(new):
        return None, []
    return new, dec


# --- kontrola: zadne slowo nie zginelo i nie doszlo (poza liczba-bohaterem, ikonami i slupkami) ------------------------
def slowa(sp):
    out = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("k") in ("hero", "bars", "icon", "img"):
                return
            for kk, v in o.items():
                if kk in ("t", "title", "kicker", "author", "label") and isinstance(v, str):
                    out.extend(v.replace("•", " ").replace("\xa0", " ").split())
                elif kk in ("rows", "items", "blocks"):
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                out.extend(x.replace("\xa0", " ").split()) if isinstance(x, str) else walk(x)

    walk({"title": sp.get("title"), "kicker": sp.get("kicker"), "rows": sp.get("rows", [])})
    return sorted(w.lower() for w in out)


# --- S3: nagłówek slajdu na tytuł --------------------------------------------------------------------------------------
def _s3(sp, rows, note):
    """Pierwszy wiersz to goły `h` (<= 14 słów) nad pics / chips / cols, slajd ma `title` z belki i nie ma `kicker`:
    kicker = dawny title, title = tekst `h`, wiersz `h` znika."""
    if not rows or rows[0]["k"] != "h" or len(rows) < 2 or rows[1]["k"] not in ("pics", "chips", "cols"):
        return rows
    h = rows[0]
    if not sp.get("title") or sp.get("kicker") or len(h["t"].split()) > 14:
        return rows
    sp["kicker"], sp["title"] = sp["title"], " ".join(h["t"].split())
    note("naglowek-na-tytul", "belka + nagłówek nad obrazami / kaflami -> belka = kicker, nagłówek = TYTUŁ")
    return rows[1:]


# --- S4: kafle z ikoną -------------------------------------------------------------------------------------------------
def _kafle(teksty, ik, note_txt=None):
    """Wiersze `cols` z kaflami: ikona w kółku + hasło ink na środku. 4 pozycje = 2 x 2, 2-3 i 5 = jeden rząd, 6 = 2 x 3."""
    n = len(teksty)
    ile = {4: 2, 6: 3}.get(n, n)
    d, pt, pad = {2: (2.2, 24, 1.2), 3: (2.2, 24, 1.2), 4: (2.0, 28, 0.8), 5: (1.3, 18, 0.5), 6: (1.6, 22, 0.7)}[n]
    out = []
    for a in range(0, n, ile):
        items = []
        for p in teksty[a:a + ile]:
            nazwa = ikona_dla(p[0], ik) or "sparkles"
            items.append(k_karta(k_icon(nazwa, align="c", d=d), blok("lead", flow(p), align="c", color="ink", pt=pt),
                                 align="c"))
        out.append(k_cols(items, pad=pad, rwane_ok=True))
    return out


def _s4_kafle(rows, note):
    """Wiersz `chips` albo 2-6 kolejnych wierszy `b` / `li` po <= 6 słów -> kafle z ikoną (S4)."""
    ik = ikony()
    out, i = [], 0
    while i < len(rows):
        r = rows[i]
        if r["k"] == "chips" and 2 <= len(r["items"]) <= 6:
            out += _kafle([(t, None) for t in r["items"]], ik)
            note("kafle-ikony", "%d haseł (kafle) -> kafle z ikoną i hasłem ink" % len(r["items"]))
            i += 1
            continue
        if r["k"] in ("b", "li") and r.get("li", r["k"] == "li"):
            j = i
            while j < len(rows) and rows[j]["k"] in ("b", "li") and len(rows[j]["t"].split()) <= 6:
                j += 1
            if 2 <= j - i <= 6:
                out += _kafle([para(x) for x in rows[i:j]], ik)
                note("kafle-ikony", "lista %d krótkich punktów -> kafle z ikoną i hasłem ink" % (j - i))
                i = j
                continue
        out.append(r)
        i += 1
    return out


# --- S6: etykieta / wartość --------------------------------------------------------------------------------------------
_KV = re.compile(r"^(CT|TA)\s*:\s*(.*)$", re.I)


def _s6_kv(rows, note):
    out = []
    for r in rows:
        if r["k"] in ("h", "lead", "p") and r.get("t"):
            linie = [x for x in r["t"].split("\n") if x.strip()]
            m = [_KV.match(x.strip()) for x in linie]
            if linie and all(m):
                items = [k_karta({"k": "kv", "label": x.group(1) + ":", "t": x.group(2).strip()}) for x in m]
                out.append(k_cols(items, pad=0.7, valign="m"))
                note("etykieta-wartosc", "linie CT: / TA: -> %d kafle etykieta / wartość" % len(items))
                continue
        out.append(r)
    return out


# --- S1: wniosek-pas (wiersze) -----------------------------------------------------------------------------------------
def _s1_wiersze(rows, note):
    """(a) wiersz `sub` pod `pics`; (b) wiersz z `po_kartach`; goły wiersz „Insight: …” (ikona żarówki)."""
    out = []
    for i, r in enumerate(rows):
        k, t = r["k"], r.get("t") or ""
        poprz = rows[i - 1]["k"] if i else None
        kol = "accent" if (r.get("color") == "accent" or calosc_kolor(r) and r.get("color") == "accent") else None
        if k == "sub" and poprz == "pics":
            fill = "accent" if (r.get("color") == "accent" or NEGATYWNE.search(t)) else "brand"
            out.append(k_band(para(r), fill))
            note("wniosek-pas", "podpis pod obrazami -> pas %s" % ("czerwony" if fill == "accent" else "zielony"), "obrazy-wniosek")
        elif r.get("po_kartach") and k in ("lead", "p", "h", "sub", "b"):
            out.append(k_band(para(r), "accent" if NEGATYWNE.search(t) else "brand"))
            note("wniosek-pas", "komentarz pod kartami -> pas")
        elif k in ("h", "lead", "p") and re.match(r"(?i)^insight\s*:", t.strip()):
            out.append(k_band(flow(para(r)), "brand", icon="lightbulb"))
            note("wniosek-pas", "„Insight: …” -> pas z ikoną żarówki")
        else:
            out.append(r)
    return out


# --- karty ------------------------------------------------------------------------------------------------------------
def _karta_tekstowa(row):
    """Wiersz `cols` kart (z kartami: `card` nie jest False), w którym są tylko bloki tekstu (bez obrazów, tagów i metek)."""
    if row["k"] != "cols" or not row.get("card", True):
        return False
    return all(b["k"] in ("h", "lead", "p", "b") for it in row["items"] for b in it["blocks"]) and         not any(it.get("tag") or it.get("meta") for it in row["items"])


def _karty(sp, rows, note, st=frozenset()):
    rows = _wniosek_zadan(rows, note)
    if "S2" not in st:
        rows = _scal_stos(rows, note)
    wiele = len(rows) >= 3  # S14h: slajd z >= 3 wierszami (karty + kv + pas)
    out = []
    tylko = sum(1 for r in rows if r["k"] not in ("pics",)) == 1  # slajd = jeden wiersz tekstu
    i = 0
    while i < len(rows):
        r = rows[i]
        nx = rows[i + 1] if i + 1 < len(rows) else None
        if r["k"] == "h" and (r.get("t") or "").rstrip().endswith(":") and nx is not None and _karta_tekstowa(nx) and \
                2 <= len(nx["items"]) <= 3 and all(len(it["blocks"]) == 1 and it["blocks"][0]["k"] == "lead" and
                                                   nslow(para(it["blocks"][0])) <= 12 for it in nx["items"]):
            # S14f (s10): nagłówek z „:” + 2-3 pozycje-hasła -> jeden wiersz: karta zielona z nagłówkiem + karty-hasła obok siebie
            cards = [k_karta(blok("lead", flow(para(r)), pt=24), fill="brand", w=0.8)] + \
                [k_karta(blok("lead", flow(para(it["blocks"][0])), color="ink", pt=22)) for it in nx["items"]]
            out.append(k_cols(cards, pad=0.8, valign="m", rwane_ok=True))
            note("lista-pod-naglowkiem", "nagłówek z „:” + %d pozycje-hasła -> karta zielona z nagłówkiem + karty obok siebie" %
                 len(nx["items"]))
            i += 2
            continue
        if _karta_tekstowa(r):
            out += _wiersz_kart(r, tylko, note, st, wiele)
        elif r["k"] == "cols" and not r.get("card", True) and len(r["items"]) >= 2:
            out.append(_kolumny_z_lista(r, note))
        else:
            out.append(r)
        i += 1
    return out


def _kolumny_z_lista(row, note):
    """S7 w kolumnach bez kart (s15: „Osoby” + obraz | „Wartości odżywcze” + lista z punktorami): kolumna z listą staje się
    kartą z punktami `li`, cały wiersz dostaje karty (obraz zostaje w całości w swojej karcie)."""
    r = copy.deepcopy(row)
    zm = []
    for it in r["items"]:
        przed = json.dumps(it["blocks"], ensure_ascii=False)
        _lista_karty(it, lambda wz, opis: zm.append(wz))
        if json.dumps(it["blocks"], ensure_ascii=False) != przed:
            note("lista-z-ikona", "kolumna „nagłówek + lista z punktorami” -> karta z punktami z ikoną")
    if not zm:
        return row
    r["card"], r["pad"], r["valign"] = True, 0.9, "t"
    return r


def _bez_ostatniego(blocks, ostatni):
    return blocks[:-1] + ([ostatni] if ostatni else [])


def _wniosek_zadan(rows, note):
    """S1 (c)-(g): wniosek z ostatniej karty ostatniego wiersza kart -> pas pod kartami. (e) także z dowolnej karty wiersza (S14g:
    ostatnie zdanie od „To ” - wniosek z danych)."""
    idx = [i for i, r in enumerate(rows) if _karta_tekstowa(r)]
    if not idx:
        return rows
    i = idx[-1]
    r = copy.deepcopy(rows[i])
    item = r["items"][-1]
    bl = item["blocks"]
    last = bl[-1]
    band = None
    t = last.get("t", "")
    zd = zdania(para(last)) if last["k"] in ("p", "lead") else []
    inna = len(r["items"]) > 1 or len(bl) > 1 or any(_karta_tekstowa(x) for j, x in enumerate(rows) if j != i)

    def e1():
        for it in reversed(r["items"]):
            lb = it["blocks"][-1]
            if lb["k"] != "p":
                continue
            z = zdania(para(lb))
            if len(z) >= 2 and (_marker(z[-1][0]) or z[-1][0].startswith("To ")) and nslow(z[-1]) <= 14:
                return it, lb, z
        return None

    hit = e1()
    if last["k"] in ("p", "lead", "b") and t.startswith("="):  # (d)
        band = para(last)
        bl.pop()
    elif last["k"] in ("p", "lead", "b") and len(bl) >= 2 and calosc_kolor(last) and len(t.split()) <= 14 and \
            not (last.get("wyr") and set(last["wyr"]) == {"-"}):  # (c)
        band = para(last)
        bl.pop()
    elif last["k"] == "p" and len(bl) >= 3 and nslow(para(last)) <= 20 and not _etykieta(t) and \
            re.match(r"(?i)^(dla|zatem|podsumowując|wniosek)\b", t.strip()):  # (g) ostatni akapit karty z >= 3 akapitami
        band = para(last)
        bl.pop()
    elif hit is not None:  # (e) ostatnie zdanie karty (znacznik wniosku albo „To ”)
        it, lb, z = hit
        band = z[-1]
        it["blocks"][-1] = czesc(lb, sklej(z[:-1]))
    elif zd and len(zd) == 1 and _marker(t) and nslow(zd[0]) <= 14 and inna and len(r["items"]) > 1 and \
            len(bl) == 1:  # (e) ostatnia karta-zdanie
        band = zd[0]
        r["items"].pop()
    elif zd and len(zd) == 1 and _marker(t) and nslow(zd[0]) <= 14 and len(r["items"]) == 1 and len(bl) == 1 and \
            sum(1 for j in idx) >= 2:  # (e) ostatnia karta-zdanie w stosie kart (osobne wiersze)
        band = zd[0]
        rows = rows[:i] + rows[i + 1:]
        r = None
    elif zd and len(zd) == 2 and len(r["items"]) == 1 and len(bl) == 1 and nslow(zd[1]) <= 12 and \
            len(idx) == 1 and not _marker(zd[0][0]):  # (f) karta-artykuł z 2 zdaniami, drugie krótkie
        band = zd[1]
        bl[-1] = czesc(last, zd[0])
    if band is None:
        return rows
    fill = "accent" if (NEGATYWNE.search(band[0])) else "brand"
    if r is not None:
        rows = rows[:i] + [r] + [k_band(band, fill)] + rows[i + 1:]
    else:
        rows = rows[:i] + [k_band(band, fill)] + rows[i:]
    note("wniosek-pas", "ostatnie zdanie / akapit wnioskujący -> pas %s pod kartami" % ("czerwony" if fill == "accent" else "zielony"),
         "cytat-wynik" if band[0].startswith("=") else None)
    return rows


def _marker(t):
    tl = t.strip().lower()
    return any(tl.startswith(m) for m in ZNACZNIKI)


def _scal_stos(rows, note):
    """2-4 kolejne wiersze po jednej karcie z jednym akapitem (<= 45 słów) -> jeden wiersz kart OBOK siebie."""
    out, i = [], 0
    while i < len(rows):
        j = i
        while j < len(rows) and _karta_tekstowa(rows[j]) and len(rows[j]["items"]) == 1 and \
                len(rows[j]["items"][0]["blocks"]) == 1 and rows[j]["items"][0]["blocks"][0]["k"] == "p" and \
                nslow(para(rows[j]["items"][0]["blocks"][0])) <= MAX_SLOW:
            j += 1
        if 2 <= j - i <= 4:
            items = [copy.deepcopy(x["items"][0]) for x in rows[i:j]]
            r0 = copy.deepcopy(rows[i])
            r0["items"] = items
            out.append(r0)
            note("karty-obok", "%d karty z jednym zdaniem pod sobą -> równe karty obok siebie" % (j - i))
            i = j
        else:
            out.append(rows[i])
            i += 1
    return out


# --- jeden wiersz kart --------------------------------------------------------------------------------------------------
def _wiersz_kart(row, tylko, note, st=frozenset(), wiele=False):
    ik = ikony()
    items = copy.deepcopy(row["items"])
    pad = row.get("pad", 1.0)
    przed = []  # wiersze przed wierszem kart (pas-temat S10, nagłówek do myślnika S14h)
    # S10b / S14f: nagłówek z „:” + 2-3 pozycje listy w jednej karcie -> karta zielona z nagłówkiem + karty-hasła obok siebie
    if len(items) == 1 and _lista_pod_naglowkiem(items[0]) and 2 <= len(items[0]["blocks"]) - 1 <= 3:
        bl = items[0]["blocks"]
        cards = [k_karta(blok("lead", flow(para(bl[0])), pt=24), fill="brand", w=0.8)] + \
            [k_karta(blok("lead", flow(para(b)), color="ink", pt=22)) for b in bl[1:]]
        note("lista-pod-naglowkiem", "nagłówek z „:” + %d pozycje -> karta zielona z nagłówkiem + %d karty-hasła obok siebie" %
             (len(bl) - 1, len(bl) - 1))
        return [k_cols(cards, pad=0.8, valign="m", rwane_ok=True)]
    # S8: teza -> karta zielona; jedno hasło -> karta z ikoną
    if len(items) == 1 and all(b["k"] == "lead" for b in items[0]["blocks"]) and tylko:
        bl = items[0]["blocks"]
        if len(bl) >= 2 and sum(len(b["t"].split()) for b in bl) <= 16:
            cards = [k_karta(*[dict(b, align="c") for b in bl], fill="brand", align="c")]
            note("teza-zielona", "slajd z jedną tezą (hasła Mindset) -> karta pełna zielona, biały tekst")
            return [k_cols(cards, pad=1.6, valign="m", min_h=8.5)]
        if len(bl) == 1 and len(bl[0]["t"].split()) <= 12:
            nazwa = ikona_dla(bl[0]["t"], ik)
            if nazwa:
                cards = [k_karta(k_icon(nazwa, align="c"), dict(bl[0], align="c"), align="c")]
                note("haslo-z-ikona", "pojedyncze hasło -> karta z ikoną nad hasłem")
                return [k_cols(cards, pad=1.6, valign="m", min_h=8.5)]
    # S9: para kontrastu (dwie karty „Prefiks – reszta”)
    if len(items) == 2 and all(len(it["blocks"]) == 2 and it["blocks"][0]["k"] == "h" and it["blocks"][0].get("one_line") and
                               it["blocks"][1]["k"] == "lead" for it in items):
        for it in items:
            h, ld = it["blocks"]
            tl = h["t"].lower()
            ic = "trending-up" if "dobr" in tl else "trending-down" if ("zł" in tl or "zła" in tl) else None
            ld["color"] = "ink"
            it["blocks"] = ([k_icon(ic)] if ic else []) + [h, ld]
        note("para-kontrast", "dwie karty „Prefiks – reszta”: ikona kierunku, nagłówek w kolorze, hasło INK (nie zielone na zielonym)")
        return [k_cols(items, pad=1.4, valign="m", min_h=8.5)]
    # --- pojedyncza karta z akapitami: S10 (pas-temat), S5c (etykiety), S2 (podział na karty) ---
    if len(items) == 1:
        nowe = _rozbij_jedna(items[0], przed, note, st)
        if nowe is not None:
            items = nowe
    # --- S15: jedno zdanie = jeden kafel (rząd kart-faktów); 4 kafle = siatka 2 x 2 ---
    siatka = False
    if "S15" not in st and "ZDANIA-DOPISEK" not in st and "ZDANIA-LI" not in st:
        items, siatka = _s15(items, note)
    wiele_eff = ("H-WIERSZ-TAK" in st) or (wiele and "H-WIERSZ-NIE" not in st)  # S14h (oś `h_wiersz`)
    # --- S5: nagłówki kart; S7: listy; S14: hasłowanie; S5b: karta zielona; S2 / S14d: liczby-bohaterowie; ikony; S11 ---
    if "S5" not in st:
        for it in items:
            _naglowek_karty(it, note, wiele_eff)
    for it in items:
        _lista_karty(it, note)
    if "S14" not in st:
        for it in items:
            _haslowanie_karty(it, len(items) >= 3, note, st)
    gotowe = []
    # S14h: karty obok nagłówka-wiersza bez ikon (ikony zabierały wysokość); wariant „ikony tak” to znosi
    bez_ikon = any("_h_wiersz" in it for it in items) and "IKONY-TAK" not in st
    for it in items:
        hw = it.pop("_h_wiersz", None)
        zl = it.pop("_zielona", None)
        if hw:
            przed.append(hw)
        gotowe.append(it)
        if zl is not None:  # S5b: ostatnie zdanie-zalecenie = osobna karta zielona (hasło + dopisek, ikona ze słownika)
            z = _haslowanie_bloku(zl, False) if "S14" not in st else [blok("lead", para(zl))]
            z = [dict(b, pt=24) if b["k"] == "lead" else b for b in z]
            nazwa = ikona_dla(zl["t"], ik)
            gotowe.append(k_karta(*(([k_icon(nazwa)] if nazwa and "BEZ-IKON" not in st else []) + z), fill="brand"))
    items = gotowe
    he = set()
    if "S2" not in st:
        he = _bohaterowie(items, note)
        _ikony_kart(items, he, st | {"BEZ-IKON"} if bez_ikon else st)
    if "S11" not in st:
        for it in items:
            _s11(it, len(items))
    for it in items:  # znaczniki robocze (_s14) nie trafiają do specu
        for b in it["blocks"]:
            for k in [k for k in b if k.startswith("_")]:
                del b[k]
    if siatka and len(items) == 4:  # S15: siatka 2 x 2, kolejność czytania wierszami = kolejność źródła
        return przed + [k_cols(items[:2], pad=0.9, valign="t", rwane_ok=True, min_h=5.0),
                        k_cols(items[2:], pad=0.9, valign="t", rwane_ok=True, min_h=5.0)]
    r = k_cols(items, pad=pad if pad != 1.0 else (1.1 if len(items) >= 3 else 1.3), valign="t", rwane_ok=True)
    if len(items) == 1:
        r["valign"] = "m"
    if row.get("pad") is not None and len(items) == 1:
        r["pad"] = min(row["pad"], 1.4)
    return przed + [r]


S15_MAKS, S15_KAFLE = 16, 4  # kolejne zdanie <= 16 słów = samodzielna myśl; po rozdzieleniu najwyżej 4 kafle


def _s15(items, note):
    """S15 „jedno zdanie = jeden kafel”: w rzędzie kart-faktów (co najmniej jedno zdanie z liczbą z jednostką) karta z jednym
    akapitem `p` o 2-3 zdaniach, w której pierwsze zdanie ma >= 5 słów (krótsze to nagłówek karty, S5) a kolejne <= 16 słów
    (samodzielna myśl), rozpada się na osobne kafle - o ile po rozdzieleniu kafli jest <= 4. Karty z nagłówkiem-etykietą
    (S14e) i z kilkoma blokami zostają. Zwraca (karty, siatka): siatka = True, gdy wyszły 4 kafle (układ 2 x 2)."""
    if not 1 <= len(items) <= S15_KAFLE:
        return items, False
    zd = []
    for it in items:
        bl = it["blocks"]
        z = zdania(para(bl[0])) if len(bl) == 1 and bl[0]["k"] == "p" else None
        ok = bool(z) and 2 <= len(z) <= 3 and nslow(z[0]) >= 5 and all(nslow(x) <= S15_MAKS for x in z[1:])
        zd.append(z if ok else None)
    if not any(zd):
        return items, False
    if not any(liczba_bohater(x) for it, z in zip(items, zd) for x in (z or [para(b) for b in it["blocks"] if b["k"] == "p"])):
        return items, False
    razem = sum(len(z) if z else 1 for z in zd)
    if razem > S15_KAFLE:
        return items, False
    nowe = []
    for it, z in zip(items, zd):
        if not z:
            nowe.append(it)
            continue
        b = it["blocks"][0]
        for x in z:
            nowe.append(dict(it, blocks=[czesc(b, x)]))
    note("jedno-zdanie-kafel", "karta z %d zdaniami -> osobne kafle (razem %d%s)" % (
        max(len(z) for z in zd if z), razem, ", siatka 2 x 2" if razem == 4 else ""))
    return nowe, razem == 4


def _lista_pod_naglowkiem(item):
    """Karta: `h` z „:” + >= 2 bloki `lead` / `p` (pozycje listy; ostatni kolorowy blok idzie osobno jako pas)."""
    bl = item["blocks"]
    if len(bl) < 3 or bl[0]["k"] != "h" or not bl[0]["t"].rstrip().endswith(":"):
        return False
    return all(b["k"] in ("lead", "p") and "\n" not in b["t"] and len(b["t"].split()) <= 12 for b in bl[1:])


def _rozbij_jedna(item, przed, note, st=frozenset()):
    """Jedna karta -> kilka kart: S10 (pas-temat + zdania), S5c (akapity z etykietą „Słowo:”), S2 (akapity z liczbą)."""
    bl = item["blocks"]
    ps = [b for b in bl if b["k"] == "p"]
    # S10: jedyny akapit zaczyna się wyróżnionym fragmentem + „–” albo wyróżnionym pierwszym zdaniem <= 4 słowa
    if len(bl) == 1 and bl[0]["k"] == "p":
        p = para(bl[0])
        t, w = p
        toks = t.split()
        lab = None
        if w and toks:
            if len(toks) > 2 and w[0] == "a" and toks[1] in ("–", "—", "-") and "a" not in w[2:3]:
                lab, rest = tnij(p, 2)
            else:
                zd = zdania(p)
                if len(zd) >= 3 and nslow(zd[0]) <= 4 and zd[0][1] and set(zd[0][1]) == {"a"}:
                    lab, rest = zd[0], sklej(zd[1:])
        if lab is not None and nslow(rest) >= 20:
            zr = zdania(rest)
            if 2 <= len(zr) <= 4 or (len(zr) == 1 and lab):
                if len(zr) == 1:
                    zr = [rest]
                ik = ikona_dla(lab[0] + " " + rest[0])
                przed.append(k_band((lab[0], None), "brand", icon=ik, align="l") if ik else k_band((lab[0], None), "brand", align="l"))
                note("temat-pas", "akapit zaczyna się wyróżnionym fragmentem -> pas-temat nad kartami, każde zdanie = karta")
                cards = [k_karta(blok("p", z, **kolor_bloku(bl[0]))) for z in zr]
                return cards
    # S5c: akapity zaczynające się od etykiety „Słowo:” = osobne karty obok siebie
    if "S5" not in st and len(ps) >= 2 and len(bl) >= 3:
        grupy, cur = [], []
        for b in bl:
            if b["k"] == "p" and cur and _etykieta(b["t"]) and any(x["k"] == "p" for x in cur):
                grupy.append(cur)
                cur = []
            cur.append(b)
        grupy.append(cur)
        if 2 <= len(grupy) <= 4:
            cards = []
            for g in grupy:
                slow = sum(len(b.get("t", "").split()) for b in g)
                udzial = slow / max(1, sum(len(b.get("t", "").split()) for b in bl)) * len(grupy)  # 1,0 = równy udział słów
                cards.append(k_karta(*g, w=max(0.9, min(1.6, round(0.7 + 0.5 * udzial, 2)))))  # nie węższa niż 0,9 (s41: 1 słowo w linii)
            note("etykieta-z-dwukropkiem", "akapit zaczyna się od „Słowo:” -> osobne karty obok siebie")
            return cards
    # S2: karta bez nagłówka z 2-4 akapitami, w tym z liczbą -> osobne karty obok siebie
    if "S2" not in st and 2 <= len(ps) <= 4 and len(ps) == len(bl) and all(nslow(para(b)) <= MAX_SLOW for b in ps) and \
            any(liczba_bohater(para(b)) for b in ps):
        note("karty-obok", "%d akapity jednej karty (jest liczba) -> równe karty obok siebie" % len(ps))
        return [k_karta(b) for b in ps]
    return None


def _etykieta(t):
    """Akapit zaczyna się od etykiety „Słowo:” (jedno słowo kończące się dwukropkiem)."""
    pierwsze = t.split(None, 1)[0] if t.strip() else ""
    return pierwsze.endswith(":") and len(pierwsze) > 2 and not re.match(r"^\d", pierwsze)


# --- S5: nagłówek karty -------------------------------------------------------------------------------------------------
def _naglowek_karty(item, note, wiele=False):
    """S5: pierwszy akapit karty bez `h`: początek jest nagłówkiem, gdy (i) pierwsze zdanie <= 4 słowa (także pytanie),
    (ii) pierwsze słowo kończy się „:”, (iii) tekst do „ – ” ma <= 9 słów i reszta >= 5, (iv) tekst do „np.” <= 6 słów (karta zielona).
    S14h: (iii) na slajdzie z >= 3 wierszami -> nagłówek jako goły wiersz `h` NAD kartami (`_h_wiersz`). S5b: nagłówek + 2 krótkie
    zdania, ostatnie „Najlepiej / Warto …” -> osobna karta zielona (`_zielona`)."""
    bl = item["blocks"]
    if not bl or bl[0]["k"] != "p" or any(b["k"] in ("h", "icon", "hero") for b in bl):
        return
    b = bl[0]
    p = para(b)
    t, w = p
    toks = t.split()
    if len(toks) < 4:
        return
    zd = zdania(p)
    head = rest = None
    kreska = False
    if len(zd) >= 2 and nslow(zd[0]) <= 4:  # (i)
        head, rest = zd[0], sklej(zd[1:])
    elif toks[0].endswith(":") and len(toks[0]) > 2 and not re.match(r"^\d", toks[0]):  # (ii)
        head, rest = tnij(p, 1)
    elif "–" in toks:  # (iii)
        k = toks.index("–")
        if 1 <= k <= 9 and len(toks) - k - 1 >= 5:
            head, rest = tnij(p, k + 1)
            kreska = True
    if head is None and "np." in toks:  # (iv)
        k = toks.index("np.")
        if 1 <= k <= 6 and len(toks) - k >= 3:
            head, rest = tnij(p, k)
            item["fill"] = "brand"
    if head is None:
        return
    hb = blok("h", head, **kolor_bloku(b))
    if item.get("fill") == "brand":
        hb["color"] = "white"
    if kreska and wiele:  # S14h
        item["_h_wiersz"] = dict(hb, align="l", color="brand", pt=28, gap=0.5)
        item["blocks"] = [blok("p", rest, **kolor_bloku(b))] + bl[1:]
        note("naglowek-do-myslnika", "nagłówek do „ – ” na slajdzie z >= 3 wierszami -> goły wiersz h nad kartami (karty bez ikon)")
        return
    zr = zdania(rest)
    if len(bl) == 1 and len(zr) == 2 and nslow(rest) <= 20 and not item.get("fill") and nslow(zr[1]) <= 12 and \
            _zalecenie(zr[1][0]):
        item["blocks"] = [hb, blok("p", zr[0], **kolor_bloku(b))]
        item["_zielona"] = blok("lead", zr[1])
        note("naglowek-karty", "pierwsze krótkie zdanie -> nagłówek karty; ostatnie zdanie (zalecenie) -> karta zielona obok")
        return
    item["blocks"] = [hb, blok("p", rest, **kolor_bloku(b))] + bl[1:]
    note("naglowek-karty", "początek akapitu -> nagłówek karty (zielony), reszta jako hasło / dopisek")


def _zalecenie(t):
    """Zdanie-zalecenie: zaczyna się od przysłówka / rozkaźnika („Najlepiej …”, „Warto …”, „Zalecamy …”, „Unikaj …”)."""
    return bool(re.match(r"(?i)^(najlepiej|warto|zalecamy|polecamy|unikaj|pamiętaj|należy|trzeba)\b", t.strip()))


# --- S7: lista z ikoną -------------------------------------------------------------------------------------------------
def _lista_karty(item, note):
    """Karta: `h` + >= 3 krótkie akapity-linie (<= 12 słów) albo blok `p` z liniami „• ” -> `h` + bloki `li` (ikona check)."""
    bl = item["blocks"]
    if not bl or bl[0]["k"] != "h":
        return
    rest = bl[1:]
    if len(rest) == 1 and rest[0]["k"] == "p" and "•" in rest[0]["t"]:
        linie = [x.replace("•", "").replace("\xa0", " ").strip() for x in rest[0]["t"].split("\n") if x.strip()]
        if len(linie) >= 3:
            item["blocks"] = [bl[0]] + [{"k": "li", "t": x, "icon": "check"} for x in linie]
            note("lista-z-ikona", "nagłówek + lista z punktorami -> punkty z ikoną")
        return
    if len(rest) >= 3 and all(b["k"] == "p" and len(b["t"].split()) <= 12 and "\n" not in b["t"] for b in rest):
        nowe = []
        for b in rest:
            li = {"k": "li", "t": b["t"], "icon": "check"}
            if b.get("wyr") and len(b["wyr"]) == len(b["t"].split()):
                li["wyr"] = b["wyr"]
            if b.get("color") == "accent":
                li["wyr"] = "a" * len(b["t"].split())
            nowe.append(li)
        item["blocks"] = [bl[0]] + nowe
        note("lista-z-ikona", "nagłówek + %d krótkie zdania-linie -> punkty z ikoną" % len(nowe))


# --- S2: liczba-bohater -------------------------------------------------------------------------------------------------
def _bohaterowie(items, note):
    """S2 + S14d: 2-4 karty obok siebie (każda <= 45 słów: `h` / `lead` / `p`, bez list `li`), w co najmniej jednej HASŁO (pierwszy
    `lead`) zawiera liczbę z jednostką -> w tych kartach blok `hero` (liczba z hasła) tuż przed hasłem. Karta z nagłówkiem-liczbą
    (`_liczba_h`) hero już ma. Zwraca zbiór numerów kart z `hero` (albo z liczbą w nagłówku)."""
    he = {k for k, it in enumerate(items) if _liczba_h(it)}
    n = len(items)
    if not 2 <= n <= 4:
        return he
    for it in items:
        if any(b["k"] not in ("h", "lead", "p", "icon") for b in it["blocks"]):
            return he
        if sum(nslow(para(b)) for b in it["blocks"] if b["k"] != "icon") > MAX_SLOW:
            return he
    wybor = []
    for k, it in enumerate(items):
        liczba = None
        for b in it["blocks"]:
            if b["k"] == "lead" and k not in he:
                liczba = liczba_bohater(para(b))
                break
        wybor.append(liczba)
    if not any(wybor):
        return he
    for k, (it, liczba) in enumerate(zip(items, wybor)):
        if not liczba:
            continue
        i = next(j for j, b in enumerate(it["blocks"]) if b["k"] == "lead")
        it["blocks"].insert(i, {"k": "hero", "t": liczba})
        he.add(k)
    note("fakt-z-liczba", "%d karty obok siebie, liczba z jednostką w haśle %d -> liczba-bohater nad hasłem" % (n, len(he)))
    return he


# --- S13 / ikony kart -------------------------------------------------------------------------------------------------
def _ikony_kart(items, he, st):
    """S13: karty bez `hero` / ikony dostają ikonę ze słownika (pierwsze trafienie w tekście karty), gdy: (a) w rzędzie 2-4 kart
    któraś ma `hero`, albo (b) wszystkie karty rzędu to zwykły tekst (`h` / `lead` / `p`, bez etykiety z „:”), albo (c) rząd ma jedną
    kartę bez nagłówka. Brak trafienia = karta bez ikony. Wariant „BEZ-IKON” (slajd ciasny, S14h) pomija ikony kart."""
    if "BEZ-IKON" in st:
        return

    def etykieta(it):
        return bool(it["blocks"]) and it["blocks"][0]["k"] == "h" and it["blocks"][0]["t"].rstrip().endswith(":")

    def zwykla(it):
        return all(b["k"] in ("h", "lead", "p", "icon") for b in it["blocks"]) and not etykieta(it)

    n = len(items)
    if n >= 2:
        if not (he or all(zwykla(it) for k, it in enumerate(items) if k not in he)):
            return
    elif not (zwykla(items[0]) and not any(b["k"] == "h" for b in items[0]["blocks"]) and
              any(b.get("_s14") for b in items[0]["blocks"])):  # jedna karta: tylko hasło zrobione ze zdania (nie stos haseł R5, s7)
        return
    for k, it in enumerate(items):
        if k in he or not zwykla(it) or any(b["k"] == "icon" for b in it["blocks"]):
            continue
        nazwa = ikona_dla(tekst_karty(it))
        if nazwa:
            it["blocks"] = [k_icon(nazwa)] + it["blocks"]


def _s11(item, n):
    """S11: `lead` w karcie z `h` albo `icon` - kolor ink (nie zielony na zielonym nagłówku); każde zielone hasło w karcie kremowej
    też idzie ink (kolor bazowy pola to nie wyróżnienie - user 13.10: „zielone napisy, źle się to czyta”); wymuszone łamania autora
    zdjęte w kartach węższych niż 60% slajdu (>= 2 karty obok siebie)."""
    bl = item["blocks"]
    if item.get("fill") == "brand":
        return
    ink = any(b["k"] in ("h", "icon") for b in bl)
    for b in bl:
        if b["k"] == "lead" and (ink or b.get("color") == "brand"):
            b["color"] = "ink"
    if n >= 2:
        for b in bl:
            if b["k"] == "lead" and "\n" in b["t"]:
                b["t"] = " ".join(b["t"].split())


def haslo_cut(p):
    """S14a: zdanie (t, wyr) -> (hasło, reszta albo None). Do CALE słów całe zdanie jest hasłem; dłuższe dzieli się po
    pierwszym przecinku stojącym po HMIN..HMAX słowach, a gdy go nie ma - przed pierwszym spójnikiem (i / oraz / ale / wobec /
    czyli) na pozycji HMIN..HMAX. Bez granicy: całe zdanie (reszta None)."""
    toks = p[0].split()
    if len(toks) <= CALE:
        return p, None
    for i in range(HMIN, min(HMAX, len(toks) - 2) + 1):
        if toks[i - 1].endswith(","):
            return tnij(p, i)
    for i in range(HMIN, min(HMAX, len(toks) - 2) + 1):
        if toks[i] in SPOJ:
            return tnij(p, i)
    return p, None


def _haslowanie_bloku(b, jako_li):
    """S14a-S14b, S14e: blok `p` (akapit) -> [lead (hasło z pierwszego zdania), p (dopisek: reszta zdania + kolejne zdania,
    max_pt 18)]; jako_li (S14e: karta z nagłówkiem-etykietą i akapitem >= 4 zdań): kolejne zdania to bloki `li`. Hasło: ink,
    a gdy >= 80% jego słów było w kolorze (czerwone hasło) - bez `wyr` (wyróżnienie wszystkiego = brak wyróżnienia).
    Zdanie dłuższe niż HDLUGIE słów bez żadnej granicy zostaje akapitem `p` (hasło Mindset nie ma >= 25 słów)."""
    ss = zdania(para(b))
    h, r = haslo_cut(ss[0])
    if r is None and nslow(h) > HDLUGIE:
        return [b]
    wyr = h[1]
    if wyr and wyr.count("a") >= 0.8 * len(wyr):
        wyr = None
    lead = {"k": "lead", "t": h[0], "color": "ink", "_s14": True}
    if wyr and set(wyr) != {"-"}:
        lead["wyr"] = wyr
    out = [lead]
    kol = kolor_bloku(b)
    if jako_li:
        if r:
            out.append(blok("p", r, max_pt=18, **kol))
        for z in ss[1:]:
            li = {"k": "li", "t": z[0], "icon": "check"}
            if z[1] and set(z[1]) != {"-"}:
                li["wyr"] = z[1]
            out.append(li)
        return out
    rest = ([r] if r else []) + ss[1:]
    if rest:
        out.append(blok("p", sklej(rest), max_pt=18, **kol))
    return out


def _haslowanie_karty(item, blokuj, note, st=frozenset()):
    """S14a-c, e, f: każdy akapit `p` karty -> hasło + dopisek. S14c: karta, która ma już nagłówek-hasło (`h` >= 3 słowa), w rzędzie
    >= 3 kart (blokuj) - reszta akapitu zostaje samym dopiskiem `p` max_pt 18 (bez drugiego hasła). `h`-etykieta (1-2 słowa albo
    zakończona „:”) nie blokuje hasła. Karta z >= 5 akapitami (lista, nie myśl) zostaje bez zmian - 5 haseł Mindset jedno pod drugim
    to nie prezentacja."""
    bl = item["blocks"]
    if sum(1 for b in bl if b["k"] == "p") >= 5:
        return
    h_haslo = any(b["k"] == "h" and nslow(para(b)) >= 3 and not b["t"].rstrip().endswith(":") for b in bl)
    jako_li = any(b["k"] == "h" for b in bl)
    nowe, zm = [], False
    dopisek, li_wymus = "ZDANIA-DOPISEK" in st, "ZDANIA-LI" in st  # oś `zdania` (9b): kolejne zdania jako dopisek / punkty li
    for b in bl:
        if b["k"] != "p":
            nowe.append(b)
            continue
        if h_haslo and blokuj:
            nowe.append(dict(b, max_pt=18))
            zm = True
            continue
        nz = len(zdania(para(b)))
        czesci = _haslowanie_bloku(b, (not dopisek) and ((jako_li and nz >= 4) or (li_wymus and nz >= 2)))
        zm = zm or czesci != [b]
        nowe.extend(czesci)
    item["blocks"] = nowe
    if zm:
        note("haslowanie", "zdanie w karcie -> hasło Mindset (lead) + krótki dopisek Lato (S14a-c, e, f)")


def miara_slow(slides):
    """Ile słów w kartach (`cols`) stoi w Mindset (lead + h) i w Lato (p + li): {lead, h, p, li, hero}; liczba-bohater (hero) osobno."""
    c = collections.Counter()
    for sp in slides:
        for r in sp.get("rows", []):
            if r.get("k") != "cols":
                continue
            for it in r["items"]:
                for b in it["blocks"]:
                    if b["k"] in ("lead", "h", "p", "li", "hero"):
                        c[b["k"]] += len((b.get("t") or "").split())
    return dict(c)


def _liczba_h(it):
    """Karta zaczyna się nagłówkiem-liczbą („11 g”, „0%”, „82%”): to już jest liczba-bohater autora - bez drugiego `hero` i bez ikony."""
    bl = it["blocks"]
    if not bl or bl[0]["k"] != "h":
        return False
    toks = bl[0]["t"].split()
    return 1 <= len(toks) <= 3 and any(c.isdigit() for c in bl[0]["t"]) and \
        sum(1 for c in bl[0]["t"] if c.isalpha()) <= 4


# --- S12: wysokość kart -------------------------------------------------------------------------------------------------
def rozloz(sp, build_dk):
    """S12: `valign: t` (ustawione w stosuj) i `min_h` kart tak, by karty + pasy zajęły >= 65% pola treści (bez rozciągania
    kart z obrazami). Zwraca slajd z `min_h` albo ten sam, gdy układ się nie mieści / nie ma czego rozciągać."""
    ms, f = build_dk.uklad_layout(sp)
    if ms is None:
        return sp
    avail = build_dk.CB - build_dk.uklad_top(sp) - (build_dk.cm(0.25) if sp.get("source") else 0)
    total = sum(m["h"] for m in ms) + sum(m["gap"] for m in ms[1:])
    cel = 0.65 * avail
    if total >= cel:
        return sp
    idx = [i for i, (m, r) in enumerate(zip(ms, sp["rows"]))
           if r["k"] == "cols" and r.get("kont") and r.get("card", True) and
           not any(b["k"] == "img" for it in r["items"] for b in it["blocks"])]
    if not idx:
        return sp
    brak = cel - total
    for proba in (1.0, 0.6, 0.3):
        s2 = copy.deepcopy(sp)
        for i in idx:
            m = ms[i]
            nowa = min(m["h"] + brak * proba / len(idx), build_dk.cm(9.5))
            s2["rows"][i]["min_h"] = round(max(s2["rows"][i].get("min_h") or 0, nowa / build_dk.cm(1) / min(1.0, f)), 1)
        ms2, f2 = build_dk.uklad_layout(s2)
        if ms2 is not None and f2 >= f - 1e-9:
            return s2
    return sp


# =====================================================================================================================
# 9a-9c. SAMOOCENA UKŁADU (bez PowerPointa), KANDYDACI I WYBÓR WARIANTU (13.10.2026)
# User: „każda prezentacja to trochę coś innego… program nie będzie mieć LLM, dlatego trzeba umieć tak zbudować program, by on
# umiał patrzeć na to, co widzi, i podejmować decyzje.” Decyzje układu z POMIARU (miary z `build_dk.uklad_layout`), nie z reguł
# uszytych pod jedną prezentację: dla slajdu generujemy kandydatów (osie: ikony, siatka, nagłówek, zdania, pad), każdemu
# liczymy `ocena`, wybieramy najlepszego; po renderze `inny_wariant` podmienia slajd na następnego kandydata.
# =====================================================================================================================
# Wagi (stałe): punkty = PUNKTY_BAZA + premie (ciągłe) - kary (kody). Wyższe = lepiej.
PUNKTY_BAZA = 100.0
PREMIA = {"haslo": 8.0, "dopisek": 6.0, "wypelnienie": 6.0, "mindset": 6.0}  # maks. punktów za pismo hasła / dopisku, wypełnienie, udział Mindset
KARY = {"HASLO_MALE": 14.0, "DOPISEK_MALY": 8.0, "HASLO_MNIEJSZE": 6.0, "SLOWO_PO_SLOWIE": 10.0, "HASLO_DLUGIE": 5.0,
        "PUSTY_DOL": 8.0, "KARTA_PUSTA": 6.0, "KARTY_NIEROWNE": 5.0, "ZA_DUZO_LATO": 6.0, "AKAPIT_BEZ_HASLA": 7.0,
        "PLYWAJACA_TRESC": 9.0}
PUNKTY_NIE_MIESCI = -1000.0  # kod NIE_MIESCI_SIE
HASLO_MIN_PT, HASLO_MIN_PT_WASKIE = 16.0, 14.0  # hasło < 16 pt = HASLO_MALE; w rzędzie 5-6 kart 14 pt jest dopuszczalne
DOPISEK_MIN_PT = 13.0
HASLO_MAX_LINII = 5
SLOWO_PO_SLOWIE_LINII = 3  # tyle kolejnych jednowyrazowych linii hasła
PUSTY_DOL_UL = 0.30  # wolne > 30% pola treści przy piśmie poniżej górnych granic
KARTA_PUSTA_UL = 0.50
KARTY_NIEROWNE_UL = 2.5
LATO_UL = 0.60  # udział słów Lato (p + li) w słowach kart; od 20 słów Lato
AKAPIT_LINII = 3
PROG_REMISU = 10.0  # kandydaci w granicach PROG_REMISU od najlepszego są „równorzędni”: wygrywa ten bliższy kolejności reguł
TOLERANCJA_PO_RENDERZE = 6.0  # inny_wariant: kandydat nie gorszy niż o tyle punktów od obecnego
MAX_KANDYDATOW = 12
# kolejność osi = od najmniej inwazyjnej (sam odstęp kart) do zmieniającej strukturę treści (kolejne zdania); przy równorzędnych
# kandydatach wygrywa wcześniejszy, więc wzorzec reguł zmieniamy możliwie najmniej
OSIE = (("pad", (0.75,)), ("ikony", (True, False)), ("siatka", ("rzad", "siatka")), ("h_wiersz", (True, False)),
        ("zdania", ("dopisek", "li")))
PLYWA_PAS = 0.18  # PLYWAJACA_TRESC: pusty pas pod tytułem i pod treścią >= 18% wysokości slajdu...
PLYWA_TRESC_MAX = 0.50  # ...a treść zajmuje <= 50% wysokości (główna wada odrzuconej wersji 1.2.0: treść „pływa” w pustym polu)
KODY_OCENY = tuple(KARY) + ("NIE_MIESCI_SIE",)
OSIE_PO_RENDERZE = frozenset({"pad", "ikony", "siatka", "h_wiersz"})  # po renderze zmieniamy wygląd, nie podział treści (osi `zdania`)


def _bd():
    import build_dk
    return build_dk


def _slow(lines):
    return sum(len(x.split()) for x in lines)


def _kolejne_jednowyrazowe(lines):
    """Najdłuższy ciąg kolejnych linii z jednym słowem (łamanie słowo po słowie)."""
    best = cur = 0
    for x in lines:
        cur = cur + 1 if len(x.split()) == 1 else 0
        best = max(best, cur)
    return best


def ocena(sp, build_dk=None):
    """Samoocena slajdu `uklad` z miar układu (`build_dk.uklad_layout`: rozmiary pisma, wysokości, linie) - bez PowerPointa i bez
    obrazu. Zwraca {"punkty": float, "miary": {...}, "usterki": [{"kod", "opis"}]}. Kody: HASLO_MALE, DOPISEK_MALY,
    HASLO_MNIEJSZE, SLOWO_PO_SLOWIE, HASLO_DLUGIE, PUSTY_DOL, NIE_MIESCI_SIE, KARTA_PUSTA, KARTY_NIEROWNE, ZA_DUZO_LATO,
    AKAPIT_BEZ_HASLA. Punkty = PUNKTY_BAZA + premie (większe hasło, większy dopisek, wypełnienie pola, udział Mindset) - kary."""
    bd = build_dk or _bd()
    ms, f = bd.uklad_layout(sp)
    if ms is None:
        return {"punkty": PUNKTY_NIE_MIESCI, "miary": {},
                "usterki": [{"kod": "NIE_MIESCI_SIE", "opis": "treść nie mieści się na slajdzie nawet najmniejszym pismem"}]}
    cmv = bd.cm
    avail = bd.CB - bd.uklad_top(sp) - (cmv(0.25) if sp.get("source") else 0)
    total = sum(m["h"] for m in ms) + sum(m["gap"] for m in ms[1:])
    wyp = max(0.0, min(1.0, total / avail)) if avail > 0 else 1.0
    haslo_pt, dop_pt, slowa_m, slowa_l = [], [], 0, 0
    pod_gora = False  # któryś blok ma pismo poniżej górnej granicy (KONT_PT) - da się jeszcze rosnąć
    kary = collections.defaultdict(int)
    opisy = {}
    chs_all, pusta_max = [], 0.0

    def zgloś(kod, opis):
        kary[kod] += 1
        opisy.setdefault(kod, opis)

    for m, r in zip(ms, sp["rows"]):
        if m["kind"] == "text":
            if r["k"] in ("lead", "h", "big", "sub"):
                haslo_pt.append(m["pt"])
                if m["pt"] < HASLO_MIN_PT:
                    zgloś("HASLO_MALE", "hasło ma %.1f pt (< %d pt)" % (m["pt"], HASLO_MIN_PT))
            continue
        if m["kind"] != "cols":
            continue
        ncol = len(m["cols"])
        lim = HASLO_MIN_PT_WASKIE if ncol >= 5 else HASLO_MIN_PT
        karty = m.get("cards", True)  # kolumny bez kart (obraz + tekst, s15) nie mają „pustej karty” ani „nierównych kart”
        if ncol >= 2 and karty:
            chs = [c for c in m["chs"] if c > 0]
            if len(chs) >= 2 and min(chs) > 0 and max(chs) / min(chs) > KARTY_NIEROWNE_UL:
                zgloś("KARTY_NIEROWNE", "treść kart w rzędzie różni się %.1f x" % (max(chs) / min(chs)))
            chs_all += chs
        for i, (parts, iw) in enumerate(m["cols"]):
            inner = m["hs"][i] - 2 * m["pad"] - m["tag_h"] - m["meta_h"]
            if ncol >= 2 and karty and inner > 0 and (1 - m["chs"][i] / inner) > KARTA_PUSTA_UL:
                zgloś("KARTA_PUSTA", "karta jest pusta w %d%%" % round(100 * (1 - m["chs"][i] / inner)))
                pusta_max = max(pusta_max, 1 - m["chs"][i] / inner)
            ma_haslo = False
            hp, dp = [], []
            for kind, _y, _h, d in parts:
                if kind == "txt":
                    k = d.get("k")
                    if k in ("lead", "h"):
                        ma_haslo = True
                        hp.append(d["pt"])
                        haslo_pt.append(d["pt"])
                        slowa_m += _slow(d["lines"])
                        if d["pt"] < lim:
                            zgloś("HASLO_MALE", "hasło ma %.1f pt (< %d pt)" % (d["pt"], lim))
                        if len(d["lines"]) > HASLO_MAX_LINII:
                            zgloś("HASLO_DLUGIE", "hasło ma %d linii" % len(d["lines"]))
                        if _kolejne_jednowyrazowe(d["lines"]) >= SLOWO_PO_SLOWIE_LINII:
                            zgloś("SLOWO_PO_SLOWIE", "hasło łamie się słowo po słowie („%s”)" % " / ".join(d["lines"][:4]))
                        if d["pt"] < bd.KONT_PT.get(k, 99) * 0.95:
                            pod_gora = True
                    elif k in ("p", "b"):
                        dp.append(d["pt"])
                        dop_pt.append(d["pt"])
                        slowa_l += _slow(d["lines"])
                        if d["pt"] < DOPISEK_MIN_PT:
                            zgloś("DOPISEK_MALY", "dopisek ma %.1f pt (< %d pt)" % (d["pt"], DOPISEK_MIN_PT))
                        if d["pt"] < bd.KONT_PT.get(k, 99) * 0.95:
                            pod_gora = True
                        if len(d["lines"]) > AKAPIT_LINII and not any(
                                x[0] in ("hero",) or (x[0] == "txt" and x[3].get("k") in ("lead", "h")) for x in parts):
                            zgloś("AKAPIT_BEZ_HASLA", "akapit Lato ma %d linii i nie ma hasła" % len(d["lines"]))
                elif kind == "hero":
                    ma_haslo = True
                elif kind == "li":
                    dop_pt.append(d["pt"])
                    dp.append(d["pt"])
                    slowa_l += _slow(d["lines"])
                    if d["pt"] < DOPISEK_MIN_PT:
                        zgloś("DOPISEK_MALY", "punkt ma %.1f pt (< %d pt)" % (d["pt"], DOPISEK_MIN_PT))
            if hp and dp and min(hp) < max(dp):
                zgloś("HASLO_MNIEJSZE", "hasło (%.1f pt) mniejsze od dopisku (%.1f pt)" % (min(hp), max(dp)))
    if slowa_l >= 20 and slowa_l / max(1, slowa_l + slowa_m) > LATO_UL:
        kary["ZA_DUZO_LATO"] += 1
        opisy["ZA_DUZO_LATO"] = "Lato to %d%% słów w kartach (próg %d%%)" % (round(100.0 * slowa_l / (slowa_l + slowa_m)), round(100 * LATO_UL))
    if avail > 0 and (avail - total) / avail > PUSTY_DOL_UL and pod_gora:
        kary["PUSTY_DOL"] += 1
        opisy["PUSTY_DOL"] = "%d%% pola treści pod kartami jest puste" % round(100.0 * (avail - total) / avail)
    H = getattr(bd, "H", None)
    if H and avail > 0:  # PLYWAJACA_TRESC: treść wyśrodkowana w pustym polu (valign m), mała w stosunku do slajdu
        valign = sp.get("valign") or ("t" if all(r["k"] in ("p", "b", "small") for r in sp["rows"]) else "m")
        wolne = max(0.0, avail - total)
        gora = wolne / 2 if valign == "m" else 0.0
        dol = wolne - gora + max(0.0, H - bd.CB)
        if total <= PLYWA_TRESC_MAX * H and gora >= PLYWA_PAS * H and dol >= PLYWA_PAS * H:
            kary["PLYWAJACA_TRESC"] += 1
            opisy["PLYWAJACA_TRESC"] = "treść zajmuje %d%% wysokości i pływa w pustym polu (pas pod tytułem %d%%, pod treścią %d%%)" % (
                round(100.0 * total / H), round(100.0 * gora / H), round(100.0 * dol / H))
    udzial_m = slowa_m / max(1, slowa_m + slowa_l)
    miary = {"f": round(f, 2), "wypelnienie": round(wyp, 3), "slowa_mindset": slowa_m, "slowa_lato": slowa_l,
             "udzial_mindset": round(udzial_m, 3), "min_pt_hasla": min(haslo_pt) if haslo_pt else None,
             "min_pt_dopisku": min(dop_pt) if dop_pt else None, "karta_pusta_max": round(pusta_max, 3),
             "gestosc": round((slowa_m + slowa_l) / max(1.0, total / bd.cm(1) / 10.0), 2)}
    pkt = PUNKTY_BAZA
    if haslo_pt:
        pkt += PREMIA["haslo"] * min(1.0, (sum(haslo_pt) / len(haslo_pt)) / 26.0)
    if dop_pt:
        pkt += PREMIA["dopisek"] * min(1.0, min(dop_pt) / 16.0)
    pkt += PREMIA["wypelnienie"] * min(1.0, wyp / 0.9)
    pkt += PREMIA["mindset"] * udzial_m
    cap = {"SLOWO_PO_SLOWIE": 3, "KARTA_PUSTA": 3, "HASLO_MALE": 3, "HASLO_DLUGIE": 3, "AKAPIT_BEZ_HASLA": 3, "DOPISEK_MALY": 3}
    for kod, ile in kary.items():
        pkt -= KARY[kod] * min(ile, cap.get(kod, 1))
    return {"punkty": round(pkt, 2), "miary": miary,
            "usterki": [{"kod": k, "opis": opisy[k]} for k in KODY_OCENY if kary.get(k)]}


# --- osie wariantu: siatka i pad (przekształcenia gotowych wierszy) ----------------------------------------------------
def _karty_wiersz(r):
    return r["k"] == "cols" and r.get("kont") and r.get("card", True) and \
        not any(b["k"] == "img" for it in r["items"] for b in it["blocks"])


def _siatka_rows(rows, st):
    """Oś `siatka` (znaczniki SIATKA:rzad / SIATKA:siatka): 4-6 kafli w jednym rzędzie albo w siatce (4 = 2 x 2, 5 = 3 + 2,
    6 = 3 + 3). Kolejność czytania wierszami = kolejność źródła. Brak znacznika = rząd(y) tak, jak ułożyła reguła."""
    tryb = next((x.split(":", 1)[1] for x in st if x.startswith("SIATKA:")), None)
    if not tryb:
        return rows
    out, i = [], 0
    while i < len(rows):
        r = rows[i]
        # siatka z reguły (kilka sąsiednich rzędów o tych samych parametrach) -> spłaszczamy do jednego rzędu na życzenie
        j = i
        while _karty_wiersz(r) and j + 1 < len(rows) and _karty_wiersz(rows[j + 1]) and \
                all(rows[j + 1].get(k) == r.get(k) for k in ("pad", "min_h", "valign")) and \
                not any(it.get("fill") for rr in rows[i:j + 2] for it in rr["items"]):
            j += 1
        grupa = rows[i:j + 1]
        wszystkie = [it for rr in grupa for it in rr["items"]] if _karty_wiersz(r) else []
        if _karty_wiersz(r) and 4 <= len(wszystkie) <= 6 and not any(it.get("fill") for it in wszystkie):
            n = len(wszystkie)
            if tryb == "rzad":
                podzial = [wszystkie]
            else:
                a = {4: 2, 5: 3, 6: 3}[n]
                podzial = [wszystkie[:a], wszystkie[a:]]
            for k, czesc in enumerate(podzial):
                nr = dict(r, items=czesc)
                if tryb != "rzad" and r.get("min_h"):
                    nr["min_h"] = round(r["min_h"] * 0.6, 1)
                out.append(nr)
            i = j + 1
        else:
            out.append(r)
            i += 1
    return out


def _pad_rows(rows, st):
    """Oś `pad` (znacznik PAD:x): mnożnik paddingu kart-pojemników (np. 0.75 = karty ciaśniejsze, więcej miejsca na pismo)."""
    x = next((float(s.split(":", 1)[1]) for s in st if s.startswith("PAD:")), None)
    if not x:
        return rows
    return [dict(r, pad=round(max(0.5, r.get("pad", 1.0) * x), 2)) if _karty_wiersz(r) else r for r in rows]


# --- kandydaci i wybór ---------------------------------------------------------------------------------------------------------
def _klucz(sl):
    return json.dumps({k: sl.get(k) for k in ("title", "kicker", "rows", "valign")}, sort_keys=True, ensure_ascii=False)


def _nazwa(opcje):
    if not opcje:
        return "domyślny"
    t = {"ikony": lambda v: "ikony na kartach: %s" % ("tak" if v else "nie"), "siatka": lambda v: "kafle: %s" % ("rząd" if v == "rzad" else "siatka"),
         "h_wiersz": lambda v: "nagłówek: %s" % ("wiersz nad kartami" if v else "w karcie"),
         "zdania": lambda v: "kolejne zdania: %s" % ("dopisek" if v == "dopisek" else "punkty"), "pad": lambda v: "pad kart x%s" % v}
    return "; ".join(t[k](opcje[k]) for k in ("ikony", "siatka", "h_wiersz", "zdania", "pad") if k in opcje)


@contextlib.contextmanager
def _layout_memo(bd):
    """Na czas generowania kandydatów `build_dk.uklad_layout` pamięta wyniki (klucz: JSON slajdu): `rozloz`, `ocena` i bramka
    mieszczenia liczą ten sam układ wielokrotnie, a jeden pomiar kosztuje do ~1,5 s (długi tekst, wiele kroków pisma)."""
    orig, cache = bd.uklad_layout, {}

    def pamietaj(sp):
        k = json.dumps(sp, sort_keys=True, ensure_ascii=False, default=str)
        if k not in cache:
            cache[k] = orig(sp)
        return cache[k]
    bd.uklad_layout = pamietaj
    try:
        yield
    finally:
        bd.uklad_layout = orig


def kandydaci(sp, n=0, build_dk=None, dopusc=None, wstrzymane=None):
    bd = build_dk or _bd()
    with _layout_memo(bd):
        return _kandydaci(sp, n, bd, dopusc, wstrzymane)


def _kandydaci(sp, n, build_dk, dopusc, wstrzymane):
    """Kandydaci układu slajdu `uklad` (9b): wariant domyślny (kolejność reguł) + warianty z osi OSIE, które NAPRAWDĘ zmieniają
    slajd (oś bez wpływu odpada; wynik bez duplikatów). Każdy: {"nazwa", "opcje", "slajd", "decyzje", "ocena", "dopuszczony"}.
    `dopusc(slajd) -> bool` = dodatkowa bramka mieszczenia (pptx_convert._miesci); kandydat bez niej nie bywa wybrany.
    Kolejność deterministyczna: domyślny pierwszy, potem iloczyn osi w kolejności OSIE. Brak szablonowania = []."""
    bd = build_dk
    pamiec = {}

    def zrob(opcje):
        k = json.dumps(opcje, sort_keys=True)
        if k not in pamiec:
            sl, dec = stosuj(sp, n, wstrzymane, opcje=opcje)
            pamiec[k] = (rozloz(sl, bd), dec) if sl is not None else (None, [])
        return pamiec[k]
    dom, dec0 = zrob({})
    if dom is None:
        return []
    k0 = _klucz(dom)
    poziomy = []  # (oś, [wartości, które zmieniają slajd])
    for os_, wart in OSIE:
        dzialaja = []
        for v in wart:
            sl, _d = zrob({os_: v})
            if sl is not None and _klucz(sl) != k0:
                dzialaja.append(v)
        if dzialaja:
            poziomy.append((os_, dzialaja))
    # kandydaci: domyślny, pojedyncze zmiany osi, a każdy z nich jeszcze z ciaśniejszym paddingiem (pełny iloczyn osi byłby
    # kosztowny, a poza padem osie rzadko się dodają); kolejność = bliskość kolejności reguł (mniej zmian = wcześniej)
    inne = [{os_: v} for os_, wart in poziomy if os_ != "pad" for v in wart]
    pad = [{"pad": v} for os_, wart in poziomy if os_ == "pad" for v in wart]
    pad_z = [dict(w, pad=p["pad"]) for p in pad for w in inne]
    wyniki, widziane = [], set()
    for opcje in ([{}] + pad + inne + pad_z)[:MAX_KANDYDATOW * 2]:
        sl, dec = (dom, dec0) if not opcje else zrob(opcje)
        if sl is None or _klucz(sl) in widziane:
            continue
        widziane.add(_klucz(sl))
        oc = ocena(sl, bd)
        wyniki.append({"nazwa": _nazwa(opcje), "opcje": dict(opcje), "slajd": sl, "decyzje": dec, "ocena": oc,
                       "dopuszczony": oc["punkty"] > PUNKTY_NIE_MIESCI / 2 and (dopusc is None or bool(dopusc(sl)))})
        if len(wyniki) >= MAX_KANDYDATOW:
            break
    return wyniki


def wybierz(kand):
    """Indeks wybranego kandydata (albo None, gdy żaden nie jest dopuszczony). Najlepszy to najwięcej punktów; ale kandydaci
    w granicach PROG_REMISU od najlepszego są równorzędni i wygrywa spośród nich NAJBLIŻSZY KOLEJNOŚCI REGUŁ (najniższy indeks:
    domyślny, potem pojedyncze zmiany, potem złożone). Jedna lekka usterka domyślnego wariantu nie uzasadnia więc odejścia od
    reguł (wzorzec zaakceptowany przez usera zostaje), a ciężka (np. dopisek < 13 pt) tak. Deterministyczne."""
    dop = [i for i, k in enumerate(kand) if k["dopuszczony"]]
    if not dop:
        return None
    best = max(kand[i]["ocena"]["punkty"] for i in dop)
    return min(i for i in dop if kand[i]["ocena"]["punkty"] >= best - PROG_REMISU)


def zapis_wariantow(kand, wybrany, n, czesc=0):
    """Rekord do `warianty-szablon.json`: kandydaci z punktami i PEŁNYM slajdem (do podmiany po renderze, `inny_wariant`)."""
    return {"zrodlo": n, "czesc": czesc, "wybrany": wybrany,
            "kandydaci": [{"nazwa": k["nazwa"], "opcje": k["opcje"], "punkty": k["ocena"]["punkty"], "miary": k["ocena"]["miary"],
                           "usterki": k["ocena"]["usterki"], "dopuszczony": k["dopuszczony"], "slajd": k["slajd"]} for k in kand]}


def opis_wariantow(kand, wybrany):
    """Pole `warianty` decyzji: [{nazwa, punkty, usterki: [kody], wybrany, dopuszczony}] (bez pełnych slajdów)."""
    return [{"nazwa": k["nazwa"], "punkty": k["ocena"]["punkty"], "usterki": [u["kod"] for u in k["ocena"]["usterki"]],
             "wybrany": i == wybrany, "dopuszczony": k["dopuszczony"]} for i, k in enumerate(kand)]


# --- po renderze: inny wariant ---------------------------------------------------------------------------------------------
KODY_MNIEJ_TRESCI = {"PRZEPELNIENIE", "KOLIZJA", "PRZY_KRAWEDZI", "GESTO"}  # kontrola po renderze: za ciasno -> mniej / luźniej
KODY_WIECEJ_TRESCI = {"PUSTY_DOL", "MALO_TRESCI", "PLYWAJACA_TRESC"}  # za pusto -> więcej wypełnienia


def _kierunek_ok(kody, cur, nowy):
    """Kody, których `ocena` nie liczy (po renderze), wymagają zmiany miary w dobrą stronę: za ciasno (PRZEPELNIENIE, KOLIZJA,
    PRZY_KRAWEDZI, GESTO) = mniejsze wypełnienie albo mniejsza gęstość; za pusto (PUSTY_DOL, MALO_TRESCI) = większe wypełnienie."""
    if not cur or not nowy:
        return True
    if kody & KODY_MNIEJ_TRESCI and not (nowy.get("wypelnienie", 1) < cur.get("wypelnienie", 1) - 0.02 or
                                         nowy.get("gestosc", 99) < cur.get("gestosc", 99) - 0.3):
        return False
    if kody & KODY_WIECEJ_TRESCI and not nowy.get("wypelnienie", 0) > cur.get("wypelnienie", 0) + 0.02:
        return False
    return True


def _rekord(spec, nr, warianty):
    """Rekord wariantów slajdu WYNIKU nr (1-based): po (zrodlo, czesc = który z kolei slajd tego źródła)."""
    sl = spec["slides"]
    if not 1 <= nr <= len(sl):
        return None
    zr = sl[nr - 1].get("zrodlo")
    czesc = sum(1 for x in sl[:nr - 1] if x.get("zrodlo") == zr)
    for r in (warianty or {}).get("slajdy", []):
        if r["zrodlo"] == zr and r["czesc"] == czesc:
            return r
    return None


def inny_wariant(spec, nr_slajdu, kody, warianty=None):
    """Po renderze (9c): podmienia w specu slajd WYNIKU nr_slajdu (1-based) na następnego kandydata, który według `ocena` nie ma
    usterek z `kody` (kody z `oko.py` i z kontroli PowerPointa: PUSTY_DOL, KARTA_PUSTA, KARTY_NIEROWNE, PRZY_KRAWEDZI, GESTO,
    MALO_TRESCI, PLYWAJACA_TRESC, SIEROTA, ZAWIESZKA, PRZEPELNIENIE, KOLIZJA), jest dopuszczony, nie jest gorszy niż o
    TOLERANCJA_PO_RENDERZE punktów, różni się od obecnego tylko osiami z OSIE_PO_RENDERZE (wygląd; podział treści na kafle -
    oś `zdania` - zostaje) i dla kodów liczonych tylko po renderze zmienia miarę w dobrą stronę (`_kierunek_ok`). Kandydaci: `warianty`
    (słownik z `warianty-szablon.json`) albo `spec["warianty"]`. Zwraca True, gdy podmieniono (zapisuje nowy indeks w rekordzie
    i dopisuje do `spec["poprawki_ukladu"]`), False, gdy nie ma lepszego kandydata. Zestaw słów slajdu nie zmienia się."""
    war = warianty if warianty is not None else spec.get("warianty")
    rek = _rekord(spec, nr_slajdu, war)
    if not rek or len(rek["kandydaci"]) < 2 or rek.get("wybrany") is None:
        return False
    kody, kand, idx = set(kody or ()), rek["kandydaci"], rek["wybrany"]
    cur = kand[idx]
    najlepszy = None
    for i, k in sorted(enumerate(kand), key=lambda x: (-x[1]["punkty"], x[0])):
        if i == idx or not k["dopuszczony"] or {u["kod"] for u in k["usterki"]} & kody:
            continue
        if not set(k.get("opcje") or {}) <= OSIE_PO_RENDERZE:  # nie zmieniamy podziału treści (np. s12: 3 kafle ze wzorca zostają)
            continue
        if k["punkty"] < cur["punkty"] - TOLERANCJA_PO_RENDERZE or not _kierunek_ok(kody, cur["miary"], k["miary"]):
            continue
        if _klucz(k["slajd"]) == _klucz(spec["slides"][nr_slajdu - 1]):
            continue
        najlepszy = i
        break
    if najlepszy is None:
        return False
    spec["slides"][nr_slajdu - 1] = copy.deepcopy(kand[najlepszy]["slajd"])
    rek["wybrany"] = najlepszy
    spec.setdefault("poprawki_ukladu", []).append({"slajd": nr_slajdu, "kody": sorted(kody), "bylo": cur["nazwa"],
                                                    "jest": kand[najlepszy]["nazwa"]})
    return True


if __name__ == "__main__":  # python szablonuj.py <spec.json> - pomiar układu PRZED renderem: pismo, usterki, miara słów
    import sys as _sys
    _spec = json.load(open(_sys.argv[1], encoding="utf8"))
    _zle = 0
    for _n, _sp in enumerate(_spec.get("slides", []), 1):
        if _sp.get("type") != "uklad":
            continue
        try:
            _o = ocena(_sp)
        except Exception as _e:  # slajd, którego nie da się zmierzyć, nie przerywa przeglądu
            print("slajd %02d: nie zmierzono (%s)" % (_n, _e))
            continue
        _m = _o.get("miary", {})
        _u = "; ".join("%s (%s)" % (x["kod"], x["opis"]) for x in _o["usterki"])
        _zle += bool(_o["usterki"])
        print("slajd %02d: hasło %s pt, dopisek %s pt | %s" % (_n, _m.get("min_pt_hasla", "-"), _m.get("min_pt_dopisku", "-"),
                                                             _u or "bez usterek"))
    _ms = miara_slow(_spec.get("slides", []))
    print("slajdów z usterką: %d | słowa w kartach: Mindset %d, Lato %d" % (
        _zle, _ms.get("lead", 0) + _ms.get("h", 0), _ms.get("p", 0) + _ms.get("li", 0)))
