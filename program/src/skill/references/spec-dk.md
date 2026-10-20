# Format spec JSON - build_dk.py

```json
{"output": "../Nazwa.pptx", "theme": "fresh|shop", "sections": false, "morph": true, "footer": "", "slides": [...]}
```
Ścieżki `image`, `pack`, `path`, `props[]` - względem pliku spec. Każdy slajd może mieć: `morph` (false wyłącza),
`section` (nazwa sekcji PowerPointa od tego slajdu), `label_slide` (opis "do czego służy" - notatki + karteczka poza
slajdem), `hidden` (true = ukryty w pokazie), `notes` (notatki prelegenta; konwersja gotowej prezentacji przenosi nimi
notatki źródła). Kolory: token motywu (`brand`, `card`, ...) albo stały hex.

| type | pola |
|---|---|
| cover | `variant` 1-4 (**4 = wzór usera 29.09**: duże logo na zieleni, "NOWOŚĆ" zielonym Mindsetem, 3 paczki pod tytułem), `kicker`, `title`, `subtitle`, `image` (packshot albo lista 3 = trio), `props[]`, `flavors[]` `{name, dot}`; `kicker_style` display/button/label (okładki domyślnie display) |
| cover_text | `variant` 1-3, `kicker`, `title`, `subtitle`, `meta` (autor/data), `props[]` (wariant 2), opcjonalne `logo` (PNG obcej marki: do 3,5 cm wysokości, w całości, bez cienia i obrotu) |
| agenda | `kicker`, `title`, `items[]` str albo `{title, text}` (do 8) |
| section | `variant` dark/light, `number` (`""` = bez numeru; konwersja nie dopisuje numerów), `label` (zamiast numeru: nagłówek ze starej belki), `title`, `subtitle`, opc. `image`, `props` |
| lead | `kicker`, `title`, `lead`, `columns[]` `{title, text}` |
| statement | `kicker`, `text`, `note`, `bg`, opc. `max_pt` (górny rozmiar pisma, domyślnie 60 - konwerter zmniejsza przy wielu liniach) |
| longtext | `kicker`, `title`, `columns` [[akapity], [akapity]] |
| bullets | `kicker`, `title`, `items[]` `{title, text}`, `with_image` / `image` |
| steps | `kicker`, `title`, `items[]` `{title, text}` (3-5) |
| quote | `kicker`, `quote`, `author`, `role` |
| two_cols | `kicker`, `title`, `columns[2]` `{title, items[]}` |
| text_image | `side` right/left, `kicker`, `title`, `text`, `items[]`, `image` albo `pack` + `props` |
| full_image | `image`, opc. `title`, `caption` |
| gallery | `kicker`, `title`, `items[]` `{image, caption}` (2-6) |
| product_hero | `kicker`, `title`, `image`, `props`, `items[4]` `{title, text}` |
| flavor | `key`, `kicker`, `name`, `text`, `facts[3]` `{value, label}`, `ean`, `tint`, `deep`, `image`, `props`, `rot` |
| line | `title`, `items[]` `{key, name, title (pełna nazwa na karcie), meta (metka), image, props, text?, badge?}` - bez `badge`/`text` karta jest czysta jak w wersji usera (większa paczka) |
| nutrition | `kicker`, `title`, `image`, `props`, `head[3]`, `rows[][3]`, `note` |
| tiles | `title`, `items[]` `{title, text?, image, rot}` (3-4) - bez `text`: węższe kafle na środku, nagłówki wyśrodkowane |
| hero_stat | `kicker`, `title`, `value`, `label`, `items[]` (1-2), `image`, `props`, `source` |
| kpis | `kicker`, `title`, `items[]` `{value, label, note}`, `highlight` |
| bars | `kicker`, `title`, `items[]` `{label, value}`, `highlight[]`, `insight`, `max`, `source` |
| segments | `kicker`, `title`, `groups[]` `{name, desc, metrics[] {value, label}}`, `source` |
| table | `kicker`, `title`, `head[]`, `rows[][]`, `widths[]` |
| timeline | `kicker`, `title`, `items[]` `{date, title, text}`, `current` |
| split | `kicker`, `title`, `a` `{value, label}`, `b`, `note`, `source` |
| reasons | `kicker`, `title`, `items[]` `{value, title, text}` |
| facts | `kicker`, `title`, `items[]` `{label, value}` (4-8) |
| cards_images | `kicker`, `title`, `items[]` `{image, badge, title, text}` |
| contact | `kicker`, `title`, `name`, `role`, `image`, `lines[]` [etykieta, wartość] |
| end | `variant` brand/light, `hashtag`, `title`, `subtitle`, `contact` |
| icon_list | `kicker`, `title`, `items[]` `{icon, title, text}` (3-4), `pack` + `props` albo `image`, `button` (żółty przycisk) |
| icon_grid | `kicker`, `title`, `items[]` `{icon, title, text}` (3-6), opc. `pack`, `source` |
| media | **claim + film** (29.09): `title`, `claim_image`, `claim_title`, `text`, `media_title`, oraz `link` (URL YouTube -> prawdziwe wideo online przez `online_video.ps1`) ALBO `video` (mp4) + `poster` - film zawsze zaokrąglony i odtwarzany w slajdzie |
| article | **akapit w karcie** (29.09): `title` (pytanie), `paragraphs[]` (1-3, wyjustowane, rozmiar sam maleje 16->13 pt), `props[]` (do 4 drobnych owoców przy krawędziach) |
| video | `variant` full/text, opc. `link` (YouTube -> prawdziwe wideo online), `title`, `caption`, `kicker`, `text`, `items[]`, opc. `video` (mp4 - osadzony) + `poster`; bez pliku ramka z instrukcją |
| before_after | `kicker`, `title`, `items[2]` `{image, caption, badge}` |
| donut | `kicker`, `title`, `center`, `center_label`, `items[]` `{label, value, text, note}` - wykres EDYTOWALNY |
| columns | `kicker`, `title`, `categories[]`, `series[]` `{name, values[]}`, `insight`, `number_format`, opcjonalne `stacked` (kolumny skumulowane) i `percent` (skumulowane do 100%) - wykres EDYTOWALNY |
| price | `kicker`, `title`, `image` (1 paczka lub lista 3), `props`, `price`, `price_label`, `price_note`, `facts[4]` `{label, value}` |
| compare_table | `kicker`, `title`, `columns[]` (pierwsza = nasz produkt), `rows[]` [cecha, True/False/tekst, ...] |
| occasions | `kicker`, `title`, `items[4]` `{icon, time, title, text}` |
| social | `kicker`, `title`, `items[3]` `{image, channel, result}` |
| next_steps | `kicker`, `title`, `items[]` `{task, who, when, done}` |
| instructions | `kicker`, `title`, `columns[2]` [[nagłówek, treść], ...] |
| flow | **tekst bez limitu długości** (konwersja, 06.10): `kicker`, `title`, `blocks[]` `{k, t, url?}` (`k`: `p` akapit, `li` punkt - prawdziwe wypunktowanie, `h` podtytuł, `small` / `url` drobny tekst; ukośnik-n (backslash n) w `t` = łamanie wiersza), `images[]` `{image, caption}` (1-2 obrazy w całości z prawej), `source`. Pismo samo 20 -> 13 pt; mieszczenie sprawdza `flow_layout(blocks, w, h)` |
| text_cols | 2-4 kolumny w kartach (konwersja): `kicker`, `title`, `columns[]` `{title?, blocks[]}` (bloki jak w `flow`), `source`. Mieszczenie: `text_cols_layout(columns, has_title)` |
| pics | zdjęcia / zrzuty **w całości, bez przycinania** (konwersja): `kicker`, `title`, `items[]` `{image, caption}` (1-6), `note` (wspólny podpis pod spodem), `source` |
| uklad | **układ 1:1 ze starego slajdu** (konwersja, 07.10): `kicker`, `title`, `bg` (`paper` / `card`), `valign` (`m` / `t`), `max_f` (np. 1.2 = pismo do 120%), `source`, `rows[]` w kolejności góra-dół: tekst `{k: big / h / lead / sub (Mindset) albo p / b / small (Lato), t, align, color, pt, w, li, gap}`; kolumny `{k: cols, items[] {blocks[] {k: img (image, h w cm, round) albo h / lead / p / b / small}, tag (czerwony znacznik, np. „Zmiana nazwy”), meta (zielona metka na dole, np. „Segment 1 & 3”), w (waga), fill}, card, grow}`; kafle haseł `{k: chips, items[], per_row}`; obrazy w całości `{k: pics, items[] {image, caption}, layout: "1+siatka", split, rows_h}`. Dodatki z 07.10 (automat): w wierszu tekstu i w bloku kolumny `wyr` = kolor słowo po słowie (`"a--i-"`: `a` akcent, `i` zieleń marki, `-` kolor wiersza); w `pics` `h` / `min_h` (cm) i `ws` (udziały szerokości komórek - mały obraz zostaje mały); w bloku `img` `name` (nazwa kształtu, np. lista plików wizualizacji). Sam zmniejsza pismo co 5%, aż wszystko się mieści; `ValueError`, gdy się nie da (wtedy podziel slajd i powiedz o tym). Przed budową: `build_dk.uklad_fit(spec)` (współczynnik pisma albo `None`) i `uklad_layout(spec)`. **Klocki z szablonu marki (13.10.2026)** w `cols.items[].blocks[]`: `{k: hero, t, color: brand|accent|ink}` (liczba-bohater: Mindset 44 pt x f w granicach 30-60, jedna linia, zmniejszana do szerokości karty; na karcie zielonej biała), `{k: icon, name, d (cm, domyślnie 1.8), bg (kółko pod ikoną, domyślnie true), align: l|c}` (ikona z zestawu marki „W stylu DK” `assets/icons/dk/<nazwa>.png` - te same nazwy co Lucide, kolorowana w locie przez `build_dk.icon()`, pamięć podręczna `%LOCALAPPDATA%/DobraKaloria/ikony`; nazwa Lucide, której zestaw nie ma, ma zamiennik w `IKONA_ALIAS`, w ostateczności zapas `assets/icons/<kolor>/`; kółko białe na kremowej karcie, kremowe na bieli, na zieleni jaśniejsza zieleń; brak pliku -> `leaf` + ostrzeżenie na stderr, nie wyjątek), `{k: kv, label, t}` (etykieta wersalikami Lato bold 13 pt x f, min 12, kolor `tan`, pod nią wartość Mindset 22 pt x f), `{k: bars, items[] {label, value, t}, max}` (poziome słupki w szerokości karty: podpis Lato po lewej, kolumna do 45% szerokości, tor zaokrąglony, wypełnienie `brand`, wartość `t` po prawej), `{k: li, t, icon (domyślnie check), wyr}` (punkt z ikoną 0,55 cm, druga linia pod tekstem); `h` i `lead` przyjmują `align` i `color`. Karta (`items[]`): `fill` `brand` (zielona: wszystkie teksty i ikony białe, `wyr` a = żółty, bo czerwień na zieleni jest nieczytelna) albo `white` (biała z linią 0,75 pt), `align: c` (cała treść karty na środku), `valign: t|m` na kartę (domyślnie z wiersza). Wiersz `{k: band, t, fill: brand|card|accent, icon, align: c|l, wyr}` (pas-wniosek na całą szerokość: Mindset 24 pt, granice 18-30, do 3 linii, wysokość = tekst + 2 x 0,55 cm, odstęp od poprzedniego wiersza stały 0,5 cm; ikona biała na brand / accent; align domyślnie `l` z ikoną, `c` bez). Rama: tytuł do 3 linii (dłuższy dostaje mniejsze pismo, do 26 pt), treść zaczyna się pod faktycznym końcem tytułu + 0,6 cm (nie wyżej niż CT 5,3 cm); `title_size` / `title_w` w slajdzie. Dopasowanie pisma: długie słowo w `h` / `lead` / `kv` zmniejsza pismo tylko tego bloku (do 55% bazowego, min 13 pt), nie f całego slajdu; klocki `h` / `lead` / `hero` / `kv` na tej samej pozycji (i z tym samym żądanym pt) w wierszu kafli mają jeden rozmiar - najmniejszy z dopasowanych; akapity `p` / `b` / `li` w kartach nie mniejsze niż 15 pt, gdy slajd mieści się z takim pismem (inaczej jak dawniej, skalowane z f); w karcie-pojemniku (`kont`) `h` <= 1,6 x `p`; za ostatnim hero / icon / kv / bars / li nie ma odstępu, kafel `kv` ma pad >= 0,55 cm. Wiersz `cols`: `rwane_ok: true` = nie szukaj mniejszego pisma tylko po to, by uniknąć „rwanych” linii w kartach-pojemnikach (większe pismo, krótsze linie); `min_h` (cm) to minimum przy f = 1 i nie rośnie z f. Twarda spacja U+00A0 w tekście Lato (np. „Gen Z”, „500 zł”) nie jest punktem łamania i zostaje w tekście slajdu. **Pozostałe pola** (docstring `build_dk.s_uklad`): wiersz cytatu `{k: quote, t, author, wyr, color}` (wzór t20 Cytat / opinia); wiersz `cols`: `pad` (cm, domyślnie 0.75), `grow`, `kont: true` (karta-pojemnik: pismo rośnie do 1,6 x), `valign` (treść w karcie); wiersz tekstu i blok karty: `max_pt` (górna granica pisma; dopisek `p` w karcie ma `max_pt: 18`), `po_kartach: true` (komentarz pod kartami: pismo najwyżej o 2 pt większe niż tekst kart); slajd: `valign` (`t` = treść od góry, `m` = na środku; domyślnie `m`, a gdy wszystkie wiersze to tekst Lato - `t`), `links: [{t, url}]` (hiperłącze na tych słowach, bez dopisanego tekstu), `source` (stopka źródła). Zasady i wzory z katalogu (t62 Trzy fakty w kartach, t56 Okazje spożycia, t59 Dwie karty…): `konwersja-pptx.md` 2a-2b, `katalog-szablonu.md`, metoda: `dopracowanie.md` |

## Klucze specu konwersji (poza polami slajdów)

Spec z `pptx_convert.py` (`spec_konwersja.json`, w programie `spec_program.json`) ma obok `slides` klucze, które czyta konwerter, kontrole i agent AI; `build_dk.py` je pomija. Każdy slajd `uklad` z konwersji ma też `zrodlo` (numer slajdu źródła).

| klucz | zawartość |
|---|---|
| `cel`, `mapa`, `uwagi`, `sprawdz`, `wizualizacje`, `litery`, `biblioteka`, `output` | cel konwersji; mapa slajd źródła -> slajdy wyniku; uwagi dla człowieka i AI; numery slajdów „Sprawdź najpierw”; wstawione wizualizacje; liczba zmian wielkości liter; biblioteka produktów; plik wynikowy |
| `szablon` | decyzje szablonowania (S1-S15) na slajd: `[{slajd, wzorzec, wzor {id, nr, nazwa}, opis}]`; to samo co `decyzje-szablon.json`; `wzor` z `assets/katalog-szablonu.json` |
| `bledy_tekstu` | ostrzeżenia lintu o ewidentnych błędach tekstu źródła: `[{slajd, rodzaj, jest, propozycja, kontekst, pewnosc}]`; program ich nie poprawia |
| `poprawki` | jawne poprawki tekstu źródła: `[{slajd, bylo, jest, powod}]` (`slajd` = numer slajdu ŹRÓDŁA). Deklarację wpisuje agent AI; kontrola treści przyjmuje tylko zmiany w granicach (`konwersja-pptx.md` 2c, `dopracowanie.md` pkt 4) |

Tytuły Mindset łamią się równo (bez sieroty); ręczne łamanie: `
` w tekście (np. `"1 g kreatyny
w każdej kulce"`).
Film/zdjęcie: rogi = geometria `roundRect` na samym obiekcie (`round_picture`), NIE maska - dzięki temu "Zmień obraz" i Malarz formatów przenoszą kształt.

Brak `image` -> placeholder "ZDJĘCIE" / "PACKSHOT" (w PowerPoint: prawy klik > Zmień obraz).
Pełny przykład wszystkich typów: `scripts/make_template.py`. Przykład prezentacji produktu: `examples/kulki-kreatyna/make_specs.py`.
