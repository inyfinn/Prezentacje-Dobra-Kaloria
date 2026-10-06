# -*- coding: utf-8 -*-
"""Jednorazowa migracja tokens.json 1.6.0 -> 2.0.0 ("sklep", runda 4, 06.10.2026).

Źródło wartości: 7 zrzutów sklepu dobrakaloria.pl od usera, próbkowane pikselami (RUNDA-4-SKLEP-2026-10-06.md,
DOWODY-SKLEP.md). Uruchom raz: python migrate_2_0_0.py ; potem python build_tokens.py. Kopia 1.6.0: tokens/tokens-1.6.0.json.
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "tokens", "tokens.json")
BAK = os.path.join(os.path.dirname(HERE), "tokens", "tokens-1.6.0.json")

d = json.load(open(SRC, encoding="utf8"))
if d["meta"]["version"] != "1.6.0":
    raise SystemExit("oczekiwałem 1.6.0, jest %s - nic nie zmieniam" % d["meta"]["version"])
if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)

d["meta"].update({
    "version": "2.0.0",
    "date": "2026-10-06",
    "source": "Sklep dobrakaloria.pl - 7 zrzutów od usera z 06.10.2026 (DOWODY-SKLEP.md), wartości próbkowane pikselami",
    "note": "JEDYNE źródło wartości. tokens.css, tokens_qt.py i tokens.md są GENEROWANE (scripts/build_tokens.py) - nie edytuj ich ręcznie. "
            "Od 2.0.0 (runda 4, 'sklep'): jasne style odtwarzają sklep dobrakaloria.pl - tło strony BIAŁE, panel jasnoszary ciepły, "
            "w panelu znów biała karta, ecru/beż dopiero jako kolejny poziom kafla (drabina jawna: 'surfaces' w wariancie); "
            "tekst i tytuły prawie czarne (#222222), zieleń marki wraca jako akcent: tytuły-akcenty, aktywne zakładki, przycisk "
            "główny, ikony liniowe, kropki, metki, fokus; żółty = przycisk wyróżnionej akcji; przycisk drugorzędny biały z ciemnym "
            "obrysem 1 px; checkbox biały w środku. Reguły 1.6.0 'zero zieleni' i 'tekst brązowy' są UCHYLONE dla stylów jasnych. "
            "Style ciemne (DK1 zieleń ciemny, DK2 krem ciemny) bez zmian - zrzuty sklepu ich nie pokazują."
})

P = d["color"]["primitive"]
P.update({
    # --- 2.0.0: wartości zmierzone na zrzutach sklepu
    "ink-900": "#222222",     # tekst, tytuły Mindset, obrys przycisku drugorzędnego, linia pod zakładkami
    "ink-800": "#333333",     # nagłówki kolumn stopki, nazwy pozycji koszyka
    "ink-600": "#666666",     # tekst pomocniczy ("Dodaj do ulubionych", drobny druk)
    "grey-600": "#6C757D",    # ostatni okruszek
    "grey-500": "#868E96",    # POCHODNA (między #ADB5BD a #6C757D): obrys pola i checkboxa z kontrastem 3:1
    "grey-400": "#ADB5BD",    # obrys checkboxa w stopce sklepu
    "grey-300": "#CED4DA",    # ramka pola ilości w koszyku
    "grey-250": "#DDDDDD",    # linie podziału
    "grey-200": "#E9E9E9",    # nieaktywny krok, tor
    "grey-100": "#F5F5F5",    # kółko pod strzałką karuzeli
    "stone-100": "#F8F7F5",   # panele koszyka (jasnoszary ciepły)
    "stone-150": "#F8F4F1",   # pasek menu
    "stone-200": "#F6F2EF",   # stopka, pasy tabeli
    "ecru-100": "#FDF8EC",    # kafle kategorii na stronie głównej
    "ecru-300": "#F5ECD8",    # POCHODNA: kafel w kaflu ecru (kolejny poziom w głąb)
    "ecru-400": "#F0E6CF",    # POCHODNA: jeszcze głębiej (tylko styl 'krem')
    "ecru-line": "#EADFC6",   # POCHODNA: linia na ecru
    "ecru-line-strong": "#DDD0B4",
    "green-900": "#00642E",   # pasek górny, logo, zielone tytuły i etykiety ikon
    "green-750": "#007936",   # przyciski główne, ikony liniowe, obrys wyszukiwarki
    "green-450": "#47C33D",   # pasek aktywnego kroku koszyka
    "yellow-450": "#FFD821",  # przycisk "ZOBACZ WIĘCEJ"
})

LIGHT = {
    "text": "{ink-900}", "text-muted": "{ink-600}", "label": "{ink-800}",
    "heading": "{ink-900}", "heading-accent": "{green-900}",
    "bg": "{@surface-0}", "surface": "{@surface-1}", "surface-hover": "{stone-200}",
    "overlay": "{white}", "strip": "{stone-150}", "zebra": "{stone-200}",
    "border": "{grey-250}", "border-strong": "{grey-300}", "field-border": "{grey-500}",
    "brand": "{green-750}", "brand-hover": "{green-900}", "brand-soft": "{green-100}", "brand-soft-strong": "{green-200}",
    "on-brand": "{white}", "progress": "{green-450}",
    "cta": "{yellow-450}", "cta-hover": "{yellow-500}", "on-cta": "{ink-900}",
    "disabled-bg": "{grey-100}", "switch-off": "{grey-200}",
    "danger": "{red-700}", "danger-soft": "{red-50}",
    "warning-text": "{amber-950}", "warning-border": "{amber-300}", "warning-bg": "{amber-50}",
    "inverse-bg": "{ink-900}", "on-inverse": "{white}", "focus": "{green-750}",
    "accent": "{green-750}", "accent-hover": "{green-900}", "on-accent": "{white}", "accent-beige": "{tan-400}",
    "icon": "{green-750}", "icon-bg": "{grey-100}",
    "check-bg": "{white}", "check-border": "{grey-500}", "check-border-hover": "{green-750}", "check-mark": "{green-750}",
    "check-disabled-border": "{grey-300}", "check-disabled-mark": "{grey-400}",
    "slider-track": "{grey-200}", "slider-fill": "{green-750}", "slider-thumb": "{white}", "slider-thumb-border": "{green-750}",
    "switch-off-border": "{grey-500}", "switch-on": "{green-750}", "switch-knob": "{white}",
    "btn2-bg": "{white}", "btn2-text": "{ink-900}", "btn2-border": "{ink-900}", "btn2-hover-bg": "{stone-200}",
    "step-active-bg": "{green-750}", "step-active-text": "{white}", "step-idle-border": "{grey-300}",
    "step-idle-text": "{ink-600}", "step-done": "{green-750}",
}
for name in ("semantic", "semantic-zielen-jasny", "semantic-krem-jasny"):
    d["color"][name] = dict(LIGHT)
# style ciemne: tylko nowe role (wartości bez zmian)
for name, acc in (("semantic-dark", "{lime-300}"), ("semantic-krem", "{wheat-200}")):
    r = d["color"][name]
    r.update({"heading": r["text"], "heading-accent": acc, "overlay": "{@surface-4}", "strip": "{@surface-1}",
              "zebra": "{@surface-1}", "progress": acc})

d["radius"].update({"btn": "4px", "sm": "4px", "md": "8px", "lg": "12px", "pill": "999px"})
d["shadow"] = {
    "thumb": "0 1px 2px rgba(34,34,34,.14), 0 4px 10px rgba(34,34,34,.10)",
    "raised": "0 1px 4px rgba(34,34,34,.16)",
    "bar": "0 2px 8px rgba(34,34,34,.08)",
    "toast": "0 10px 30px rgba(34,34,34,.22)",
    "focus-field": "0 0 0 3px rgba(0,121,54,.22)",
}
d["control"].update({"stroke-icon": "2", "focus-width": "2px", "focus-offset": "2px"})
d["qt"].update({"radius-card": "8px", "radius-field": "4px", "radius-btn": "4px", "radius-drop": "12px"})

V = d["ladder"]["variants"]
NAMES_SHOP = ["tło okna (biel)", "panel, sekcja (jasnoszary ciepły)", "karta lub pole w panelu (biel)",
              "kafel w karcie (ecru)", "kafel w kaflu (głębszy beż)"]
NAMES_KREM = ["tło okna (biel)", "kafel, sekcja (ecru)", "karta lub pole w kaflu (biel)",
              "kafel w karcie (beż)", "kafel w kaflu (głębszy beż)"]
SHOP = {"mode": "light", "white_ok": True, "tag_hue": 152,
        "surfaces": ["#FFFFFF", "#F8F7F5", "#FFFFFF", "#FDF8EC", "#F5ECD8"],
        "borders": ["#DDDDDD", "#DDDDDD", "#DDDDDD", "#EADFC6", "#DDD0B4"], "level_names": NAMES_SHOP}
V["program"] = dict(SHOP, name="Sklep Dobra Kaloria (domyślny): biel, szary panel, biała karta", roles="semantic")
V["zielen-jasny"] = dict(SHOP, name="Dobra Kaloria 1 · zieleń, jasny (= sklep)", roles="semantic-zielen-jasny")
V["krem-jasny"] = dict(SHOP, name="Dobra Kaloria 2 · krem, jasny (kafle ecru na bieli, jak strona główna sklepu)",
                       roles="semantic-krem-jasny",
                       surfaces=["#FFFFFF", "#FDF8EC", "#FFFFFF", "#F5ECD8", "#F0E6CF"],
                       borders=["#DDDDDD", "#EADFC6", "#DDDDDD", "#DDD0B4", "#D3C5A6"], level_names=NAMES_KREM)
# kolejność wariantów jak dotąd
d["ladder"]["variants"] = {k: V[k] for k in ("program", "krem-jasny", "zielen-jasny", "zielen-ciemny", "krem-ciemny")}
d["ladder"]["note"] = (
    "Od 2.0.0 style jasne mają drabinę JAWNĄ ('surfaces' i 'borders' w wariancie, wartości ze zrzutów sklepu): "
    "L0 białe tło okna, L1 panel jasnoszary ciepły (krem: kafel ecru), L2 biała karta lub pole w panelu, L3 kafel ecru w karcie, "
    "L4 kafel w kaflu (głębszy beż). Nakładki (menu, podpowiedź, modal) = rola 'overlay' (biel + cień), nie poziom drabiny. "
    "Style ciemne liczone wzorem jak w 1.4.0-1.6.0: L_n = L0 + n*dL (OKLCH), L4 = nakładka."
)
d["ladder"]["rules"] = {
    "text": "text i text-muted >= 4.5:1 na każdym poziomie L0-L4",
    "white": "style jasne: L0 = #FFFFFF zawsze; beż/ecru nigdy jako tło okna - dopiero od poziomu kafla",
    "panel": "style jasne: karta lub pole leżące na panelu L1 jest BIAŁE (L2), jak w koszyku sklepu",
    "neutral-text": "style jasne: tekst, tytuł, etykieta neutralne (chroma OKLCH <= 0.02) - nie brązowe",
    "brand": "style jasne: zieleń marki to akcent interfejsu - tytuł-akcent (heading-accent), aktywna zakładka, przycisk główny, "
             "ikony liniowe, kropki list, metki, fokus, suwak, przełącznik, znak checkboxa; brand na L0-L4 >= 4.5:1",
    "step": "style ciemne: skok sąsiadów 0.015-0.045 L (OKLCH), jeden kierunek; L4-L0 >= 0.06. Style jasne: sąsiednie poziomy różne "
            "(kontrast >= 1.03)",
    "no-green-dark-krem": "DK2 krem ciemny: bez zieleni poza brand* (decyzja usera 05.10: zieleń w ciemnych brązach brzydka)",
}
d["tags"]["note"] = (
    "Tag k (1..count): hue = tag_hue wariantu + offsets[k-1] (stopnie OKLCH). Od 2.0.0 style jasne mają tag_hue 152 "
    "(zieleń marki; odcienie 120-184), bo metki sklepu są zielone. Metka pełna (cena, licznik, znaczek) = brand + on-brand. "
    "Kategorie rozróżnia etykieta, nie sam kolor."
)

T = d["themes"]["photo-resizer"]["tokens"]
T.update({
    "@BG_WINDOW@": "{white}", "@BG_PANEL@": "{stone-100}", "@BG_PANEL_ALT@": "{white}", "@BG_INPUT@": "{white}",
    "@BG_BUTTON@": "{white}", "@BG_HOVER@": "{stone-200}", "@FG_TITLE@": "{ink-900}", "@FG_TEXT@": "{ink-900}",
    "@FG_MUTED@": "{ink-600}", "@FG_ACCENT@": "{green-900}", "@ACCENT@": "{green-750}", "@ACCENT_HOVER@": "{green-900}",
    "@BORDER@": "{grey-250}", "@BORDER_FOCUS@": "{green-750}", "@COMBO_BORDER@": "{grey-500}", "@SEP@": "{grey-250}",
    "@FOOTER_CLOSE_HOVER@": "{stone-200}", "@UPDATE_TOAST_BORDER@": "{grey-250}", "@UPDATE_TOAST_TITLE@": "{ink-900}",
    "@UPDATE_TOAST_TEXT@": "{ink-600}", "@UPDATE_TOAST_PROGRESS@": "{green-450}", "@UPDATE_TOAST_INSTALL_BG@": "{yellow-450}",
    "@UPDATE_TOAST_INSTALL_TEXT@": "{ink-900}", "@UPDATE_TOAST_LATER_BG@": "{white}", "@UPDATE_TOAST_LATER_HOVER@": "{stone-200}",
    "@UPDATE_TOAST_LATER_TEXT@": "{ink-900}", "@UPDATE_TOAST_LATER_BORDER@": "{ink-900}",
    "@OVERLAY_SCRIM@": "rgba(34, 34, 34, 0.42)", "@OVERLAY_HINT@": "{ink-600}",
})
M = d["themes"]["dam"]["tokens"]
M.update({
    "--dam-bg": "{white}", "--dam-surface": "{stone-100}", "--dam-surface-muted": "{stone-200}",
    "--dam-surface-sunken": "{stone-200}", "--dam-surface-elevated": "{white}", "--dam-surface-raised": "{white}",
    "--dam-input-bg": "{white}", "--dam-border": "{grey-250}", "--dam-chrome": "{grey-250}", "--dam-text": "{ink-900}",
    "--dam-text-muted": "{ink-600}", "--dam-dark": "{ink-900}", "--dam-danger": "{red-700}",
    "--dam-sidebar-bg": "{stone-100}", "--dam-sidebar-bg-end": "{stone-100}", "--dam-shadow-rgb": "34 34 34",
    "--dam-radius-md": "8px", "--dam-radius-sm": "4px",
})
d["themes-list"][0]["styl"] = "Sklep Dobra Kaloria (domyślny)"

json.dump(d, open(SRC, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=2)
open(SRC, "a", encoding="utf8", newline="\n").write("\n")
print("tokens.json -> 2.0.0 (kopia 1.6.0: %s)" % BAK)
