# Styl DK 2026 (build_dk.py) - motywy "fresh" (B) i "shop" (C)

Zastępuje styl-fresh.md (plamy organiczne i Nunito są WYCOFANE 28.09.2026).

## Motywy - wartości slotów PowerPointa

| Slot (PowerPoint) | Token w kodzie | fresh (B, naturalny) | shop (C, sklep) | Rola |
|---|---|---|---|---|
| Tekst 1 (dk1) | ink | 1F3A24 | 1F1F1F | nagłówki, tekst |
| Tło 1 (lt1) | white | FFFFFF | FFFFFF | karty wyróżnione, tekst na zieleni |
| Tekst 2 (dk2) | - | 006400 | 0F763E | - |
| Tło 2 (lt2) | paper | FAF6EF | FFFFFF | tło slajdów |
| Akcent 1 | brand | 006400 | 0F763E | zieleń marki: panele, liczby, słupki |
| Akcent 2 | accent | D6232A | DA272D | kropka kickera, kolor produktu |
| Akcent 3 | card | F1ECE2 | FDF8EC | karty |
| Akcent 4 | sage | C9DABB | E9F2EC | tła pomocnicze, duże numery |
| Akcent 5 | tan (sage2 w kodzie motywu) | AD8767 | AD8767 | beż "pod tło": etykiety nad tytułem (14 pt bold), podpisy ≥18 pt |
| Akcent 6 | sun | F2C94C | FFD42A | żółty (metki w sklepie, kropki na zieleni) |
| - | muted | Akcent 5 -30% jasności (#7D5E44) | jw. | opisy, stopki (kontrast ≥4,87:1 na każdym tle) |
| - | brand_soft | Akcent 1 +55% | jw. | drugorzędne słupki, kropki |
| - | line | Akcent 3 -10% | jw. | linie podziału |
| - | on_brand | Tło 1 -12% | jw. | tekst drugorzędny na zieleni |

Kolory smaków (tła kart smaku, kropki etykiet) są STAŁE (hex w specu) - to kolory produktu, nie motywu.

Zmiana globalna przez użytkownika: Projektowanie > Warianty > Kolory > Dostosuj kolory / Czcionki.
Czcionki motywu: nagłówki **Mindset** (osadzony w DK_WZOR), treść **Lato** (osadzana przez `render.ps1 -EmbedFonts`).

## Kształty i elementy ze sklepu (28.09)
- Przycisk żółty: prostokąt, rogi ~0,12 cm (`tag(style="button")`) - NIE ścięty.
- Metka ceny/gramatury: zielona, ścięta tylko z lewej (`style="price"`).
- Znaczek NOWOŚĆ / BESTSELLER: ostre końce (`style="badge"`).
- Ikony: Lucide, kreska 1,6, kolor marki (`assets/icons/<kolor>/<nazwa>.png`, nowe: `scripts/make_icons.py`).
- Światło: MX 2,4 cm, CT 5,3 cm, CB = H-1,75 cm, GAP 0,7 cm - zmieniaj stałe, nie liczby w funkcjach.

## Zasady kompozycji
1. **Zero plam za produktem.** Paczka stoi na tle slajdu albo w karcie (shop). Cień pod paczką (softEdge) zostaje.
2. `scene()`: paczka + 3-6 MAŁYCH elementów smaku (12-21% wysokości paczki), część za paczką, część przed,
   lekko nachodzą na krawędź - jak karty produktów na dobrakaloria.pl.
3. Okładki (`cover` 1-3 z produktem, `cover_text` 1-3 bez produktu) zawsze z dużym logo na zieleni.
4. Rama slajdu: kicker w beżu AD8767, 14 pt bold, wersaliki (fresh: z czerwoną kropką; shop: sam tekst; żółty
   przycisk tylko jako "NOWOŚĆ" na okładce sklepu i CTA) -> tytuł Mindset -> treść; logo prawy górny róg;
   stopka źródła lewy dół; numer strony prawy dół.
5. Karty zaokrąglone ~0,45 cm, bez cieni; wyróżnienie = karta w kolorze marki albo cienka linia.
6. Shop: kafle "zalet" (zielone, biały tekst, obrazek składnika), karty produktu jak listing sklepu (metka NOWOŚĆ,
   nazwa Lato Bold, zielona metka z gramaturą), kicker jako żółta metka.
7. Tekst: łamanie tylko na spacjach, ochrona przed sierotami; min. 12,5 pt opisy, 10,5 pt stopka.
8. Morph na każdym slajdzie; wspólne obiekty mają nazwy `!!logo`, `!!title`, `!!kicker`, `!!panel`, `!!pack`,
   `!!pack_<smak>`, `!!image` - nie zmieniaj ich w PowerPoint (Okienko zaznaczenia).
