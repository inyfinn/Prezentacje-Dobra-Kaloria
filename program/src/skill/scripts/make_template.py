# -*- coding: utf-8 -*-
"""
Szablon prezentacji Dobra Kaloria dla handlowców i pracowników (46 slajdów, 8 sekcji).

    python make_template.py [katalog_wyjściowy]

Tworzy dwa pliki (ta sama treść, dwa motywy): "DK - szablon prezentacji (naturalny).pptx" i "(sklep).pptx".
Każdy slajd ma opis "do czego służy" w notatkach i na żółtej karteczce POZA obszarem slajdu.
"""
import json
import os
import sys

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_dk  # noqa: E402

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "demo")


def e(name):
    return os.path.join(D, name)


PACK = e("pack_cola.png")
PROPS = [e("p_kulka_ugryz.png"), e("p_cola_cytryna_plaster.png"), e("p_kulka.png"),
         e("p_cola_cytryna_cwiartka.png"), e("p_kulka.png"), e("p_kulka_ugryz.png")]
MIX = [e("p_kulka_ugryz.png"), e("p_arbuz_klin1.png"), e("p_mango_kostka.png"), e("p_marakuja_pol1.png"),
       e("p_cola_cytryna_plaster.png"), e("p_kulka.png")]
DOTS = [{"name": "Arbuz", "dot": "E0525C"}, {"name": "Cola lemon", "dot": "A3302A"},
        {"name": "Mango & marakuja", "dot": "F2A33A"}]
SRC = "[Źródło: kto, kiedy, próba - np. badanie, raport sprzedaży]"
EX_FILM = "https://www.youtube.com/watch?v=Jk7RAkFN4vk"  # przykładowy film (podcast o kreatynie): miniatura + link, klik otwiera YouTube

INSTR = [[
    ("Jak korzystać z szablonu", "Wybierz slajd pasujący do treści, skopiuj go (Ctrl+C, Ctrl+V w panelu slajdów) i podmień "
     "teksty. Żółta karteczka po prawej stronie slajdu opisuje, do czego slajd służy - jest poza kadrem, więc nie "
     "widać jej w pokazie. Ten sam opis jest w notatkach."),
    ("Zdjęcia i packshoty", "Kliknij obraz prawym przyciskiem > Zmień obraz > Z pliku. Packshoty tylko PNG bez tła. "
     "Drobne elementy smaku (owoce, kulki) bierz z biblioteki marki: 99 - WYMIANA > Materiały - Dobra kaloria - "
     "Brand - elementy > Liście i owoce - warzywa."),
    ("Kolory globalnie", "Projektowanie > Warianty > strzałka > Kolory > Dostosuj kolory. Akcent 1 = zieleń marki, "
     "Akcent 2 = kolor produktu, Akcent 3 = karty, Akcent 5 = beż etykiet i opisów (AD8767), "
     "Akcent 6 = żółty. Zmiana przemaluje całą prezentację."),
], [
    ("Czcionki globalnie", "Projektowanie > Warianty > Czcionki. Nagłówki: Mindset, treść: Lato. Nie zmieniaj "
     "czcionki ręcznie na pojedynczych slajdach - wtedy zmiana globalna przestaje działać."),
    ("Teksty w nawiasach", "Każdy tekst w [nawiasach kwadratowych] to podpowiedź: zaznacz go razem z nawiasami i wpisz swoją treść. Tytuł slajdu = wniosek, nie temat. Szablon nie ma animacji - niczego nie trzeba ustawiać."),
    ("Zasady treści", "Jeden slajd = jedna myśl. Tytuł mówi wniosek, nie temat. Każda liczba ma źródło w stopce. "
     "Claimy produktowe tylko z karty wprowadzenia. Przed wysłaniem na zewnątrz usuń slajdy nieużywane i ten slajd."),
]]
INSTR2 = [[
    ("Film z YouTube", "Film to zaokrąglona miniatura z przyciskiem play i podpisem 'Kliknij - film otworzy się "
     "na YouTube'. W pokazie jedno kliknięcie otwiera film w przeglądarce (w edycji: Ctrl + klik). Swój film: "
     "prawy klik na miniaturze > Edytuj link > wklej adres; to samo na przycisku i podpisie. Nowa miniatura: "
     "prawy klik > Zmień obraz (rogi zostają). Wideo wstawione jako 'Wideo online' NIE działa - YouTube "
     "blokuje je w PowerPoincie (błąd 153)."),
    ("Własny plik mp4", "Wstawianie > Wideo > To urządzenie. Kliknij miniaturę filmu w szablonie > Malarz formatów "
     "(pędzelek) > kliknij nowy film - dostanie te same zaokrąglone rogi. Taki film gra w slajdzie bez internetu."),
], [
    ("Co jest czym", "Narzędzia główne > Zaznacz > Okienko zaznaczenia (Alt+F10): każdy obiekt ma nazwę, która "
     "mówi, co z nim zrobić (np. 'Packshot - prawy klik: Zmień obraz'). Paczka z owocami to jedna grupa - "
     "przesuwasz całość; kliknij dwa razy, żeby zmienić pojedynczy obraz."),
    ("Za długi tekst", "Pola tekstowe same zmniejszają czcionkę, gdy tekst się nie mieści. Jeśli zrobi się za "
     "mały - skróć tekst albo podziel treść na dwa slajdy."),
]]


def spec(theme):
    s = []

    def add(_section, _opis, **sl):
        if _section:
            sl["section"] = _section
        sl["label_slide"] = _opis
        s.append(sl)

    add("Instrukcja", "Instrukcja szablonu - slajd UKRYTY (nie pokazuje się w pokazie). Usuń go przed wysłaniem.",
        type="instructions", kicker="Szablon Dobra Kaloria", title="Jak korzystać z szablonu", columns=INSTR,
        hidden=True)
    add(None, "Instrukcja cz. 2: film z zaokrąglonymi rogami i nazwy obiektów - slajd UKRYTY. Usuń go przed wysłaniem.",
        type="instructions", kicker="Szablon Dobra Kaloria", title="Film i łatwa edycja", columns=INSTR2, hidden=True)
    # --- Powitanie z produktem
    T1, SUB = "[Nazwa produktu]", "[Jedno zdanie: główny claim z karty wprowadzenia]"
    FL = [{"name": "[Smak 1]"}, {"name": "[Smak 2]"}, {"name": "[Smak 3]"}]
    TRIO = [e("pack_arbuz.png"), PACK, e("pack_mango.png")]
    add("Powitanie", "Powitanie Z PRODUKTEM, wariant 4 (wzór z 29.09): duże logo na zieleni, 'NOWOŚĆ' i nazwa "
        "zielonym i czarnym Mindsetem, pod spodem cała linia (3 paczki). Najlepsze wejście dla nowej linii smaków.",
        type="cover", variant=4, kicker="[Nowość]", title=T1, image=TRIO, props=MIX[:4])
    add(None, "Powitanie Z PRODUKTEM, wariant 1: paczka na granicy zieleni i tła. Najmocniejsze wejście "
        "dla nowości. Podmień packshot (prawy klik > Zmień obraz) i elementy smaku.", type="cover", variant=1,
        kicker="[Nowość]", title=T1, subtitle=SUB, image=PACK, props=MIX, flavors=FL)
    add(None, "Powitanie Z PRODUKTEM, wariant 2: tytuł biały na zieleni, paczka po jasnej stronie. Dobre do "
        "prezentacji dla sieci handlowej.", type="cover", variant=2, kicker="[Nowość]", title=T1, subtitle=SUB,
        image=PACK, props=MIX, flavors=FL)
    add(None, "Powitanie Z PRODUKTEM, wariant 3: klasyczny podział 50/50 jak dawny wzór (duże logo na środku "
        "zieleni). Najbezpieczniejszy wybór.", type="cover", variant=3, kicker="[Nowość]", title=T1,
        image=PACK, props=MIX, flavors=FL)
    # --- Powitanie bez produktu
    add(None, "Powitanie BEZ PRODUKTU, wariant 1: podział 50/50 z logo. Spotkania, raporty, prezentacje firmowe.",
        type="cover_text", variant=1, kicker="[Rodzaj spotkania]", title="[Tytuł prezentacji]",
        subtitle="[Czego dotyczy spotkanie i dla kogo]", meta="[Imię Nazwisko]  ·  [dział]  ·  [data]")
    add(None, "Powitanie BEZ PRODUKTU, wariant 2: cała zieleń marki, duży biały tytuł, drobne owoce przy krawędzi. "
        "Na otwarcie konferencji, szkolenia, eventu.", type="cover_text", variant=2, kicker="[Rodzaj wydarzenia]",
        title="[Tytuł prezentacji]", subtitle="[Data i miejsce]", props=MIX)
    add(None, "Powitanie BEZ PRODUKTU, wariant 3: jasne tło, zielony pas z logo, bardzo duży tytuł. Raporty, "
        "podsumowania kwartału, prezentacje wewnętrzne.", type="cover_text", variant=3, kicker="[Raport]",
        title="[Tytuł prezentacji]", subtitle="[Zakres, okres, odbiorca]", meta="[Imię Nazwisko]  ·  [data]")
    # --- Struktura i tekst
    add("Struktura i tekst", "Agenda / spis treści: 3-8 punktów. Od 5 punktów układ sam dzieli się na dwie kolumny.",
        type="agenda", kicker="[Plan spotkania]", title="Agenda",
        items=[{"title": "[Punkt %d]" % i, "text": "[krótko, czego dotyczy]"} for i in range(1, 7)])
    add(None, "Przerywnik rozdziału - ciemny. Rozdziela główne części prezentacji; daje oddech między slajdami "
        "z treścią.", type="section", variant="dark", number="[Rozdział 01]", title="[Tytuł rozdziału]",
        subtitle="[Jedno zdanie: co będzie w tej części]")
    add(None, "Przerywnik rozdziału - jasny z dużym numerem. Alternatywa dla ciemnego; nie używaj obu naprzemiennie.",
        type="section", variant="light", number="02", title="[Tytuł rozdziału]",
        subtitle="[Jedno zdanie: co będzie w tej części]")
    add(None, "Wstęp: duży akapit otwierający (2-3 zdania) + trzy krótkie rozwinięcia. Na początek prezentacji albo "
        "rozdziału.", type="lead", kicker="[Wstęp]", title="[Tytuł wstępu]",
        lead="[Akapit otwierający: 2-3 zdania, najważniejsza myśl całej prezentacji.]",
        columns=[{"title": "[Hasło %d]" % i, "text": "[1-2 zdania rozwinięcia]"} for i in range(1, 4)])
    add(None, "Tekst krótki: jedno zdanie-hasło na środku slajdu. Do mocnej tezy, wniosku albo cytatu z badania.",
        type="statement", kicker="[Etykieta]", text="[Jedno zdanie - najważniejsza teza]",
        note="[Opcjonalny podpis pod hasłem]")
    add(None, "Tekst długi: dwie kolumny akapitów, maksymalnie ok. 180 słów. Opis rynku, historii, strategii.",
        type="longtext", kicker="[Etykieta]", title="[Tytuł: wniosek w 3-6 słowach]",
        columns=[["[Akapit 1: najważniejsza informacja. Krótkie zdania, jedna myśl w akapicie.]",
                  "[Akapit 2: rozwinięcie albo przykład. Więcej tekstu? Podziel na dwa slajdy.]"],
                 ["[Akapit 3: kontekst rynkowy albo dane, które wspierają tytuł.]",
                  "[Akapit 4: wniosek i czego oczekujemy od odbiorcy.]"]])
    add(None, "AKAPIT W KARCIE (wzór z 29.09, 'Dlaczego warto dbać o błonnik'): tytuł-pytanie i 1-3 akapity "
        "edukacyjne w kremowej karcie, drobne owoce przy krawędziach. Tekst sam się zmniejszy, gdy nie zmieści się "
        "w karcie.", type="article", title="[Tytuł-pytanie: dlaczego warto ...?]",
        paragraphs=["[Akapit 1: fakt edukacyjny o składniku - 2-3 zdania, ze źródłem wiedzy (np. zalecenia "
                    "żywieniowe). Pisz prosto, bez obietnic zdrowotnych, których nie ma w karcie produktu.]",
                    "[Akapit 2: dodatkowy kontekst albo wniosek dla odbiorcy.]"],
        props=[e("p_arbuz_klin1.png"), e("p_marakuja_pol1.png"), e("p_kulka_ugryz.png"), e("p_mango_kostka.png")])
    add(None, "Punkty: 3-6 haseł z krótkim rozwinięciem. Klasyczna lista zalet, warunków, ustaleń.",
        type="bullets", kicker="[Etykieta]", title="[Tytuł listy]",
        items=[{"title": "[Hasło %d]" % i, "text": "[Jedno zdanie rozwinięcia]"} for i in range(1, 5)])
    add(None, "Punkty + zdjęcie po prawej. Gdy lista potrzebuje kontekstu wizualnego (np. półka, event).",
        type="bullets", kicker="[Etykieta]", title="[Tytuł listy]", with_image=True,
        items=[{"title": "[Hasło %d]" % i, "text": "[Jedno zdanie rozwinięcia]"} for i in range(1, 4)])
    add(None, "Kroki / proces: 3-5 etapów w kolejności (wdrożenie, zamówienie, kampania).", type="steps",
        kicker="[Proces]", title="[Tytuł procesu]",
        items=[{"title": "[Etap %d]" % i, "text": "[Co się dzieje na tym etapie]"} for i in range(1, 5)])
    add(None, "Cytat / opinia: klient, partner, konsument, influencer. Zawsze z autorem.", type="quote",
        kicker="[Opinia]", quote="[Treść cytatu - krótka, konkretna, najlepiej z liczbą albo emocją]",
        author="[Imię Nazwisko]", role="[funkcja, firma]")
    add(None, "Dwie kolumny - porównanie: 'dziś' kontra 'nasza propozycja'. Prawa kolumna jest wyróżniona.",
        type="two_cols", kicker="[Porównanie]", title="[Tytuł porównania]",
        columns=[{"title": "[Dziś]", "items": ["[Obserwacja %d]" % i for i in range(1, 4)]},
                 {"title": "[Z nami]", "items": ["[Korzyść %d]" % i for i in range(1, 4)]}])
    # --- Tekst i grafika
    TXT = "[Opis: 2-4 zdania. Zdjęcie podmień: prawy klik > Zmień obraz.]"
    add("Tekst i grafika", "Tekst po lewej, ZDJĘCIE po prawej (do krawędzi). Opis produktu, kampanii, eventu.",
        type="text_image", side="right", kicker="[Etykieta]", title="[Tytuł slajdu]", text=TXT,
        items=["[Punkt 1]", "[Punkt 2]", "[Punkt 3]"])
    add(None, "ZDJĘCIE po lewej, tekst po prawej. Lustrzane odbicie poprzedniego - używaj na zmianę dla rytmu.",
        type="text_image", side="left", kicker="[Etykieta]", title="[Tytuł slajdu]", text=TXT,
        items=["[Punkt 1]", "[Punkt 2]", "[Punkt 3]"])
    add(None, "Tekst po lewej, PRODUKT po prawej (na kremowym tle z drobnymi elementami smaku).",
        type="text_image", side="right", kicker="[Produkt]", title="[Tytuł slajdu o produkcie]",
        text="[Opis produktu - claimy tylko z karty wprowadzenia.]", pack=PACK, props=PROPS,
        items=["[Claim 1]", "[Claim 2]", "[Claim 3]"])
    add(None, "Lista zalet z ikonami + ZDJĘCIE w zaokrąglonej karcie (jak 'Lecimy w kulki!' w sklepie). "
        "3-4 pozycje; ikony z assets/icons (Lucide).", type="icon_list", kicker="[Etykieta]",
        title="[Tytuł z hasłem]",
        items=[{"icon": ic, "title": "[Zaleta %d]" % (i + 1), "text": "[1-2 zdania opisu zalety]"}
               for i, ic in enumerate(["sparkles", "smile-plus", "thumbs-up", "heart-pulse"])])
    add(None, "Tylko grafika: zdjęcie na cały slajd + karta z podpisem. Kadr z kampanii, półka w sklepie, event.",
        type="full_image", title="[Podpis zdjęcia]", caption="[Jedno zdanie: gdzie, kiedy, co widać]")
    add(None, "Tylko grafika bez podpisu. Na zdjęcie, które mówi samo za siebie.", type="full_image")
    add(None, "Galeria 3 zdjęć z podpisami (półki, POS, materiały).", type="gallery", kicker="[Galeria]",
        title="[Tytuł galerii]", items=[{"caption": "[Podpis %d]" % i} for i in range(1, 4)])
    add(None, "Galeria 6 zdjęć (2 x 3): relacja z eventu, materiały od twórców, zdjęcia ekspozycji.",
        type="gallery", kicker="[Galeria]", title="[Tytuł galerii]",
        items=[{"caption": "[Podpis %d]" % i} for i in range(1, 7)])
    # --- Produkt
    CL = [{"icon": ic, "title": "[Claim %d]" % (i + 1), "text": "[krótkie rozwinięcie]"}
          for i, ic in enumerate(["dumbbell", "smile-plus", "citrus", "sparkles"])]
    add("Produkt", "Anatomia produktu: paczka w centrum, 4 claimy wokół. Główny slajd produktowy.",
        type="product_hero", kicker="[Produkt]", title="[Co wyróżnia produkt]", image=PACK, props=PROPS, items=CL)
    add(None, "Lista zalet z ikonami + PRODUKT w kremowej karcie (styl sklepu). Najlepszy slajd 'dlaczego ten "
        "produkt' - claimy z karty wprowadzenia, każdy z ikoną.", type="icon_list", kicker="[Produkt]",
        title="[Co wyróżnia produkt]", pack=PACK, props=PROPS, items=CL)
    add(None, "Siatka ikon (jak 'Skład produktu' w sklepie): 3-6 cech z ikoną, zielonym nagłówkiem i opisem. "
        "Skład, oświadczenia żywieniowe, wartości marki.", type="icon_grid", kicker="[Skład]",
        title="[Tytuł slajdu]",
        items=[{"icon": ic, "title": "[Cecha %d]" % (i + 1), "text": "[wartość lub opis z karty]"}
               for i, ic in enumerate(["candy-off", "leaf", "earth", "wheat", "apple", "hand-heart"])])
    add(None, "Karta smaku: jeden smak na slajd - nazwa, opis z karty, 3 twarde dane, EAN. Tło w odcieniu smaku "
        "(kolor wpisany na stałe, nie z motywu).", type="flavor", key="cola", kicker="[Smak 1/3]",
        name="[Nazwa smaku]", text="[Nazwa prawna z karty wprowadzenia i krótki opis smaku]",
        facts=[{"value": "[00%]", "label": "[owoców w składzie]"}, {"value": "[0%]", "label": "[dodatku cukru]"},
               {"value": "[00 g]", "label": "[opakowanie]"}], ean="[EAN]", tint="F7E6DE", deep="A3302A",
        image=PACK, props=PROPS)
    add(None, "Linia produktów / portfolio: 2-4 SKU obok siebie - packshot, nazwa, metka z gramaturą (bez znaczków "
        "i opisów, jak w wersji z 29.09). Znaczek NOWOŚĆ / opis dodasz w specu polami badge / text.", type="line",
        kicker="[Portfolio]", title="[Tytuł linii]",
        items=[{"key": "a", "name": "[Smak 1]", "meta": "[00 g]", "title": "[Nazwa produktu, smak 1]", "image": e("pack_arbuz.png"),
                "props": [e("p_arbuz_klin1.png"), e("p_kulka_ugryz.png"), e("p_arbuz_lisc1.png")]},
               {"key": "b", "name": "[Smak 2]", "meta": "[00 g]", "title": "[Nazwa produktu, smak 2]", "image": PACK,
                "props": PROPS[:3]},
               {"key": "c", "name": "[Smak 3]", "meta": "[00 g]", "title": "[Nazwa produktu, smak 3]", "image": e("pack_mango.png"),
                "props": [e("p_mango_kostka.png"), e("p_kulka_ugryz.png"), e("p_marakuja_pol1.png")]}])
    NUT = ["Wartość energetyczna", "Tłuszcz", "w tym kwasy nasycone", "Węglowodany", "w tym cukry", "Błonnik",
           "Białko", "Sól"]
    add(None, "Wartości odżywcze: packshot + tabela 100 g / opakowanie przepisana z karty wprowadzenia.",
        type="nutrition", kicker="[Skład]", title="Wartości odżywcze", image=PACK, props=PROPS,
        rows=[[n, "[wartość]", "[wartość]"] for n in NUT], head=["Wartość odżywcza", "100 g", "[porcja]"],
        note="[Przepisz wartości z karty wprowadzenia]")
    add(None, "Zalety jako zielone kafle (jak sekcja 'Zalety naszych produktów' w sklepie). 3-4 claimy z obrazkiem.",
        type="tiles", kicker="[Zalety]", title="[Tytuł slajdu]",
        items=[{"title": "[Zaleta 1]", "text": "[krótki opis]", "image": e("p_kulka_ugryz.png")},
               {"title": "[Zaleta 2]", "text": "[krótki opis]", "image": e("p_arbuz_klin1.png"), "rot": -10},
               {"title": "[Zaleta 3]", "text": "[krótki opis]", "image": e("p_mango_kostka.png")},
               {"title": "[Zaleta 4]", "text": "[krótki opis]", "image": e("p_cola_cytryna_plaster.png"), "rot": 12}])
    # --- Dane
    add("Dane", "Liczba-bohater: jedna duża liczba + opis + 1-2 liczby pomocnicze. Najważniejszy wynik.",
        type="hero_stat", kicker="[Wynik]", title="[Tytuł: wniosek]", value="00%",
        label="[Czego dotyczy liczba i w jakiej grupie]", image=PACK, props=PROPS,
        items=[{"value": "00%", "label": "[liczba pomocnicza]"}, {"value": "00%", "label": "[liczba pomocnicza]"}],
        source=SRC)
    add(None, "KPI: 3-4 wskaźniki obok siebie. Jeden można wyróżnić (highlight).", type="kpis", kicker="[Wyniki]",
        title="[Tytuł: wniosek]", highlight=0,
        items=[{"value": "00", "label": "[wskaźnik %d]" % i, "note": "[krótki komentarz]"} for i in range(1, 5)],
        source=SRC)
    add(None, "Wykres słupkowy poziomy: 3-7 pozycji. Długość słupka zmienisz szerokością kształtu; liczba to tekst.",
        type="bars", kicker="[Dane]", title="[Tytuł: wniosek]",
        items=[{"label": "[Pozycja %d]" % (i + 1), "value": v, "text": "00%"} for i, v in enumerate([80, 66, 55, 51, 39])],
        highlight=[0, 1], insight="[Wniosek z wykresu w 1-2 zdaniach]", source=SRC)
    add(None, "Dwie grupy obok siebie (segmenty, kanały, regiony), w każdej 2-4 wyniki.", type="segments",
        kicker="[Badanie]", title="[Tytuł: wniosek]",
        groups=[{"name": "[Grupa %d]" % g, "desc": "[Krótki opis grupy]",
                 "metrics": [{"value": "00%", "label": "[opis wyniku]"}, {"value": "00%", "label": "[opis wyniku]"}]}
                for g in (1, 2)], source=SRC)
    add(None, "A kontra B jednym paskiem: preferencja, udział, podział głosów. Długość paska zmienisz ręcznie.",
        type="split", kicker="[Porównanie]", title="[Tytuł: wniosek]",
        a={"value": "00%", "label": "[Opcja A]", "share": 0.67}, b={"value": "00%", "label": "[Opcja B]"},
        note="[Komentarz do wyniku]", source=SRC)
    add(None, "Tabela: asortyment, cennik, indeksy. Liczby same wyrównują się do prawej.", type="table",
        kicker="[Asortyment]", title="[Tytuł tabeli]", head=["Produkt", "Indeks", "EAN", "Gramatura", "Karton"],
        widths=[3, 1.2, 2, 1.2, 1.2],
        rows=[["[Produkt %d]" % i, "[indeks]", "[EAN]", "[00 g]", "[szt.]"] for i in range(1, 4)])
    add(None, "Oś czasu: 3-6 etapów (wprowadzenie produktu, plan kampanii). Wypełnione kółko = bieżący etap.",
        type="timeline", kicker="[Plan]", title="[Tytuł harmonogramu]", current=1,
        items=[{"date": "[Termin %d]" % i, "title": "[Etap %d]" % i, "text": "[krótki opis]"} for i in range(1, 5)])
    # --- Handel
    add("Handel", "Argumenty dla handlu: 3-4 powody, żeby wprowadzić produkt. Pierwsza karta wyróżniona.",
        type="reasons", kicker="[Dla handlu]", title="[Dlaczego warto mieć na półce]",
        items=[{"value": "00%", "title": "[Argument %d]" % i, "text": "[Uzasadnienie z liczbą i źródłem]"}
               for i in range(1, 5)])
    add(None, "Logistyka / fakty: siatka 4-8 kart wartość + etykieta (karton, paleta, termin, przechowywanie).",
        type="facts", kicker="[Logistyka]", title="Informacje logistyczne",
        items=[{"label": lb, "value": "[wartość]"} for lb in ["Gramatura", "Karton", "Paleta", "Termin",
                                                            "Przechowywanie", "Indeks", "EAN", "Dostępność"]])
    add(None, "Karty ze zdjęciem: wsparcie marketingowe, materiały POS, kanały komunikacji.", type="cards_images",
        kicker="[Wsparcie]", title="[Tytuł slajdu]",
        items=[{"badge": "[Kanał %d]" % i, "title": "[Działanie %d]" % i, "text": "[Krótki opis działania]"}
               for i in range(1, 4)])
    add(None, "Osoba kontaktowa: zdjęcie, imię, rola, telefon, e-mail. Na koniec spotkania handlowego.",
        type="contact", kicker="[Kontakt]", title="Porozmawiajmy", name="[Imię Nazwisko]", role="[Stanowisko]",
        lines=[["Telefon", "[+48 000 000 000]"], ["E-mail", "[imie.nazwisko@dobrakaloria.pl]"],
               ["WWW", "dobrakaloria.pl"]])
    # --- Multimedia i specjalne (28.09.2026)
    add("Multimedia i specjalne", "FILM na cały slajd: spot, film produktowy, relacja z eventu. W pokazie film "
        "odtworzy się po kliknięciu. Wstaw: Wstawianie > Wideo > To urządzenie, rozciągnij na cały slajd, usuń "
        "przykładową miniaturę. Film z YouTube: prawy klik > Edytuj link.",
        type="video", variant="full", title="[Tytuł filmu]", caption="[Jedno zdanie: co pokazuje film]",
        link=EX_FILM)
    add(None, "CLAIM + FILM (wzór z 29.09, 'Co dobrego w kreatynie'): po lewej element produktu, zielony claim i "
        "opis; po prawej tytuł i film YouTube (zaokrąglona miniatura, play, podpis) - w pokazie klik otwiera film. "
        "Swój film: prawy klik > Edytuj link na miniaturze, przycisku i podpisie; miniatura: Zmień obraz.", type="media",
        title="[Tytuł: co dobrego w składniku]", claim_image=e("p_kulka_ugryz.png"),
        claim_title="[Claim: np. 1 g składnika w porcji]",
        text="[1-2 zdania: dlaczego ten składnik jest ważny dla odbiorcy.]",
        media_title="[Zaproszenie do filmu / podcastu: tytuł i o czym jest]", link=EX_FILM)
    add(None, "FILM + TEKST: film 16:9 w zaokrąglonej ramce po prawej, opis i punkty po lewej. "
        "Gdy film trzeba skomentować (kampania, proces produkcji, reklama). Swój film: Edytuj link (YouTube) "
        "albo wstaw mp4 i Malarz formatów z miniatury na film - rogi się przeniosą.", type="video", variant="text", kicker="[Film]",
        title="[Tytuł slajdu]", text="[2-3 zdania: co widać w filmie i po co go pokazujemy]", link=EX_FILM,
        items=["[Punkt 1]", "[Punkt 2]", "[Punkt 3]"])
    add(None, "PRZED / PO: dwa zdjęcia obok siebie (półka przed i po wprowadzeniu, stare i nowe opakowanie, "
        "ekspozycja). Znaczki 'Przed' / 'Po' możesz przepisać.", type="before_after", kicker="[Zmiana]",
        title="[Tytuł: co się zmieniło]", items=[{"caption": "[Opis stanu przed]"}, {"caption": "[Opis stanu po]"}])
    add(None, "Wykres PIERŚCIENIOWY (udział, struktura sprzedaży, podział grupy). EDYTOWALNY: prawy klik na wykresie "
        "> Edytuj dane. Liczbę w środku wpisz ręcznie.", type="donut", kicker="[Udział]", title="[Tytuł: wniosek]",
        center="00%", center_label="[czego dotyczy]",
        items=[{"label": "[Kategoria %d]" % i, "value": v, "text": "00%", "note": "[krótki opis]"}
               for i, v in ((1, 55), (2, 25), (3, 20))], source=SRC)
    add(None, "Wykres KOLUMNOWY - trend w czasie (sprzedaż, dystrybucja, zasięg). EDYTOWALNY: prawy klik > Edytuj "
        "dane - wpisz swoje miesiące i wartości.", type="columns", kicker="[Trend]", title="[Tytuł: wniosek]",
        categories=["[Mies. 1]", "[Mies. 2]", "[Mies. 3]", "[Mies. 4]", "[Mies. 5]", "[Mies. 6]"],
        series=[{"name": "[Seria]", "values": [20, 28, 35, 41, 52, 60]}],
        insight="[Wniosek z wykresu w 1-2 zdaniach]", source=SRC)
    add(None, "CENA I MARŻA dla handlu: produkt, rekomendowana cena detaliczna w metce, 4 karty warunków.",
        type="price", kicker="[Warunki]", title="[Cena i marża]", image=PACK, props=PROPS[:3],
        price="[0,00 zł]", price_note="[np. cena za 100 g, cena promocyjna]",
        facts=[{"label": "Cena zakupu", "value": "[0,00 zł]"}, {"label": "Marża", "value": "[00%]"},
               {"label": "Promocja", "value": "[mechanizm]"}, {"label": "Min. zamówienie", "value": "[szt.]"}])
    add(None, "PORÓWNANIE z konkurencją / innymi produktami: cechy w wierszach, ✓ lub ✗. Pierwsza kolumna "
        "(nasz produkt) jest wyróżniona. Ikonę ✓/✗ zmienisz kopiując z innej komórki.", type="compare_table",
        kicker="[Porównanie]", title="[Tytuł: przewaga]",
        columns=["[Nasz produkt]", "[Konkurent A]", "[Konkurent B]"],
        rows=[["[Cecha 1]", True, False, False], ["[Cecha 2]", True, True, False], ["[Cecha 3]", True, False, True],
              ["[Cecha 4]", True, False, False], ["[Cena]", "[0,00 zł]", "[0,00 zł]", "[0,00 zł]"]])
    add(None, "OKAZJE SPOŻYCIA / momenty dnia: kiedy i po co sięgnąć po produkt (4 momenty z ikonami).",
        type="occasions", kicker="[Kiedy]", title="[Tytuł: okazje spożycia]",
        items=[{"icon": ic, "time": "[Pora %d]" % (i + 1), "title": "[Okazja %d]" % (i + 1),
                "text": "[1-2 zdania, dlaczego wtedy]"} for i, ic in enumerate(["sunrise", "dumbbell", "coffee", "moon"])])
    add(None, "SOCIAL MEDIA: 3 telefony z postami / reelsami kampanii; pod każdym kanał i wynik. Zrzuty ekranu "
        "podmień: prawy klik > Zmień obraz.", type="social", kicker="[Kampania online]", title="[Tytuł kampanii]",
        items=[{"channel": "[Kanał %d]" % i, "result": "[wynik: zasięg, wyświetlenia]"} for i in range(1, 4)])
    add(None, "NASTĘPNE KROKI: checklista ustaleń po spotkaniu - zadanie, kto, termin. Zaznaczony kwadrat = "
        "zrobione (skopiuj ikonę z pierwszego wiersza).", type="next_steps", kicker="[Ustalenia]",
        title="Następne kroki",
        items=[{"task": "[Zadanie %d]" % i, "who": "[Osoba]", "when": "[Termin]", "done": i == 1} for i in range(1, 6)])
    # --- Pojemniki konwersji (08.10): te same karty, których używa automat przy przekładaniu cudzej prezentacji
    add("Karty z konwersji", "DWIE KARTY: dobra / zła wiadomość (albo dwie strony jednej sprawy). Każda karta: nagłówek "
        "(zieleń albo czerwień) i jedno zdanie pod nim. Automat używa tego wzoru, gdy stary slajd ma dwie krótkie "
        "myśli typu 'Dobra wiadomość - ... / Zła wiadomość - ...'.", type="uklad", kicker="[Wstęp]",
        title="[Tytuł: dwie strony tej samej sprawy]", valign="t",
        rows=[{"k": "cols", "card": True, "kont": True, "pad": 1.2, "min_h": 5.0, "items": [
            {"blocks": [{"k": "h", "t": "[Dobra wiadomość]", "one_line": True},
                        {"k": "lead", "t": "[jedno zdanie: co rośnie]"}]},
            {"blocks": [{"k": "h", "t": "[Zła wiadomość]", "color": "accent", "one_line": True},
                        {"k": "lead", "t": "[jedno zdanie: co nas hamuje]"}]}]}])
    add(None, "CYTAT + WNIOSEK: cytat z autorem (kursywa, linia marki), pod nim karta z 2-3 wyśrodkowanymi hasłami. "
        "Słowa w kolorze zostają kolorem także w cytacie.", type="uklad", kicker="[Wstęp]",
        title="[Tytuł: skąd ta teza]", valign="t",
        rows=[{"k": "quote", "t": "[Cytat w jednym zdaniu, np. z badania albo od eksperta]",
               "author": "[Imię Nazwisko, firma]", "wyr": "--aa------"},
              {"k": "cols", "card": True, "kont": True, "pad": 1.6, "min_h": 0, "valign": "m", "items": [{"blocks": [
                  {"k": "lead", "t": "[Hasło 1]", "align": "c", "pt": 26},
                  {"k": "lead", "t": "[Hasło 2 - najważniejsze]", "align": "c", "pt": 34},
                  {"k": "lead", "t": "= [Wniosek]", "align": "c", "pt": 26, "color": "accent"}]}]}])
    add(None, "AKAPIT W KARCIE Z WYRÓŻNIENIEM: 1-3 akapity Lato w kremowej karcie; 2-3 najważniejsze słowa w kolorze "
        "(czerwień = akcent, zieleń = marka). Dla tekstu, który musi zostać zdaniami, nie hasłami.", type="uklad",
        title="[Tytuł: wniosek, nie temat]", valign="t",
        rows=[{"k": "cols", "card": True, "kont": True, "pad": 1.6, "min_h": 8.0, "valign": "m", "items": [{"blocks": [
            {"k": "p", "t": "[Akapit 1: 2-3 zdania z liczbą i jej źródłem w stopce.]", "wyr": "-----a-----"},
            {"k": "p", "t": "[Akapit 2: dopowiedzenie albo skutek dla marki.]"}]}]}], source=SRC)
    add(None, "TRZY FAKTY W KARTACH: trzy równe karty, w każdej jedno zdanie Lato z liczbą w środku zdania (liczba "
        "nie wychodzi do osobnego kafla). Pod kartami wniosek jednym hasłem.", type="uklad",
        title="[Tytuł: wniosek z trzech faktów]", valign="t",
        rows=[{"k": "cols", "card": True, "kont": True, "pad": 1.2, "min_h": 5.0, "valign": "t", "items": [
            {"blocks": [{"k": "p", "t": "[Fakt %d: zdanie z liczbą, np. 7,7 mln osób to 20,6%% ludności.]" % i}]}
            for i in (1, 2, 3)]},
              {"k": "lead", "t": "[Wniosek jednym hasłem]", "gap": 0.9}], source=SRC)
    add(None, "ZRZUTY W CAŁOŚCI + WNIOSEK: dwa obrazy bez kadrowania (zrzuty ekranu, wykresy) i pod nimi jedno zdanie "
        "Mindsetem w zieleni. Źródło zostaje drobnym drukiem w stopce.", type="uklad",
        title="[Tytuł: co pokazują zrzuty]",
        rows=[{"k": "pics", "min_h": 4.0, "h": 6.5, "items": [{"image": PACK, "caption": ""}, {"image": PACK, "caption": ""}]},
              {"k": "sub", "t": "[Wniosek pod zrzutami jednym zdaniem]", "color": "brand"}], source=SRC)
    # --- Zakończenie
    add("Zakończenie", "Zakończenie: zieleń marki, logo, #zawszedobra. Standardowy ostatni slajd.", type="end",
        variant="brand", contact="halo@dobrakaloria.pl  ·  dobrakaloria.pl")
    add(None, "Zakończenie z podziękowaniem i kontaktem. Gdy chcesz zostawić dane na ekranie podczas rozmowy.",
        type="end", variant="light", title="Dziękujemy", subtitle="[Jedno zdanie na pożegnanie]",
        contact="[Imię Nazwisko]  ·  [telefon]  ·  [e-mail]")
    for sl in s:  # etykiety nad tytułem tylko tam, gdzie niosą informację (lekcja A19, 29.09)
        if sl["type"] not in KEEP_KICKER:
            sl.pop("kicker", None)
    return {"theme": theme, "sections": True, "slides": s}


KEEP_KICKER = {"cover", "cover_text", "instructions", "segments", "hero_stat", "kpis", "bars", "donut", "columns",
               "split", "quote", "statement", "flavor"}


# --- łatwa edycja (29.09): nazwy w Okienku zaznaczenia, produkt jako grupa, tekst sam się dopasowuje -------------
def _nm(sh):
    return sh.name or ""


def group_elements(slide, members, name):
    """Przenosi kształty (ciągłe w kolejności Z) do jednej grupy o podanej nazwie; kolejność warstw zostaje."""
    from pptx.oxml import parse_xml
    els = [m._element for m in members]
    tree = els[0].getparent()
    xs = [(int(m.left), int(m.top), int(m.left + m.width), int(m.top + m.height)) for m in members]
    x0, y0 = min(a[0] for a in xs), min(a[1] for a in xs)
    x1, y1 = max(a[2] for a in xs), max(a[3] for a in xs)
    nid = max(int(e.get("id")) for e in tree.iter("{*}cNvPr")) + 1
    g = parse_xml(
        '<p:grpSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:nvGrpSpPr><p:cNvPr id="%d" name="%s"/>'
        '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/>'
        '<a:chOff x="%d" y="%d"/><a:chExt cx="%d" cy="%d"/></a:xfrm></p:grpSpPr></p:grpSp>'
        % (nid, name, x0, y0, x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0))
    els[0].addprevious(g)
    for e in els:
        g.append(e)


def easy_edit(path):
    """Szablon ma być bardzo łatwy w edycji: każdy obiekt ma nazwę mówiącą, co z nim zrobić; paczka z owocami
    i cieniem to jedna grupa; pola tekstowe = jeden akapit, który PowerPoint sam łamie i zmniejsza przy przepełnieniu."""
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    from pptx.oxml.ns import qn
    prs = Presentation(path)
    for slide in prs.slides:
        shapes = list(slide.shapes)
        # 1) grupy produktu: kolejne kształty !!pack* / Cien (scena jednej paczki albo trio)
        runs, cur = [], []
        for sh in shapes:
            if _nm(sh).startswith("!!pack") or _nm(sh) == "Cien":
                cur.append(sh)
            else:
                if len(cur) > 1:
                    runs.append(cur)
                cur = []
        if len(cur) > 1:
            runs.append(cur)
        for run in runs:
            group_elements(slide, run, "Produkt z owocami (grupa) - przesuwaj całość; kliknij 2x, by zmienić obraz")
        # 2) nazwy i tekst
        for sh in slide.shapes:
            items = list(sh.shapes) if sh.shape_type == MSO_SHAPE_TYPE.GROUP else [sh]
            for it in items:
                n = _nm(it)
                if n.startswith(("OPIS", "tlo", "ONLINE|", "Film")):  # film: nazwy z generatora zostają  # opis poza slajdem i ozdobniki tła zostają (verify.ps1 je pomija)
                    continue
                if n == "Cien":
                    it.name = "Cień pod paczką"
                elif "_el" in n and n.startswith("!!"):
                    it.name = "Owoc / element smaku - prawy klik: Zmień obraz albo Delete"
                elif n.startswith("!!pack"):
                    it.name = "Packshot - prawy klik: Zmień obraz (PNG bez tła)"
                elif n.startswith("!!logo"):
                    it.name = "Logo marki"
                elif n == "!!panel":
                    it.name = "Tło - zieleń marki (kolor: Projektowanie > Warianty > Kolory)"
                elif n == "!!title":
                    it.name = "Tytuł slajdu"
                elif n == "!!kicker":
                    it.name = "Etykieta nad tytułem (można usunąć)"
                elif n == "!!image" or (it.shape_type == MSO_SHAPE_TYPE.PICTURE and not n.startswith("Film")
                                         and it.width > 1500000):
                    it.name = "Zdjęcie - prawy klik: Zmień obraz (rogi i rozmiar zostają)"
                elif it.shape_type == MSO_SHAPE_TYPE.PICTURE and not n.startswith("Film"):
                    it.name = "Ikona / grafika - prawy klik: Zmień obraz"
                if it.has_text_frame and it.shape_type == MSO_SHAPE_TYPE.TEXT_BOX:
                    tf = it.text_frame
                    # linie łamane przez generator -> jeden akapit; prawdziwe akapity (kończą się "]" "." "?" "!")
                    # zostają osobno, żeby nie zlepić np. dwóch akapitów tekstu albo punktów listy
                    display = "+mj-lt" in it._element.xml  # nagłówki Mindset zostają łamane jak z generatora
                    i = 1
                    while i < len(tf.paragraphs) and not display:
                        prev, cur_p = tf.paragraphs[i - 1], tf.paragraphs[i]
                        if prev.runs and cur_p.runs and not prev.text.rstrip().endswith(("]", ".", "?", "!", ":")):
                            prev.runs[-1].text = prev.runs[-1].text.rstrip() + " " + cur_p.text.lstrip()
                            cur_p._p.getparent().remove(cur_p._p)
                        else:
                            i += 1
                    if not display:  # po scaleniu linii: twarde spacje od nowa dla całego akapitu (typografia PL)
                        for para in tf.paragraphs:
                            if len(para.runs) == 1:
                                para.runs[0].text = build_dk.bd.typo_nbsp(para.runs[0].text.replace("\u00a0", " "))
                    bp = tf._txBody.find(qn("a:bodyPr"))
                    for c in list(bp):
                        if c.tag in (qn("a:spAutoFit"), qn("a:noAutofit"), qn("a:normAutofit")):
                            bp.remove(c)
                    etree.SubElement(bp, qn("a:normAutofit"))  # za długi tekst -> PowerPoint sam go zmniejszy
                    if not n.startswith(("Tytuł", "Etykieta")) and it.name == n:
                        t = " ".join(tf.text.split())
                        it.name = "Numer slajdu" if t.isdigit() else "Tekst: " + (t[:40] or "pole tekstowe")
                elif it.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE and it.name == n:
                    it.name = "Punktor" if it.width < 400000 else "Karta / tło (kolor z motywu)"
    prs.save(path)


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    for theme, label in (("shop", None),):  # jeden szablon (28.09): motywy różniły się tylko kolorem tła
        out = os.path.join(out_dir, "DK - szablon prezentacji.pptx")
        n = build_dk.build(spec(theme), out)
        out = build_dk.build.last_out  # guard.py mógł przekierować do "(nowa wersja)"
        easy_edit(out)
        import guard
        guard.record(out)
        build_dk.bd.online_videos(out)  # prawdziwe wideo YouTube w slotach filmu
        print("OK", out, n, "slajdow")
