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
| cover_text | `variant` 1-3, `kicker`, `title`, `subtitle`, `meta` (autor/data), `props[]` (wariant 2) |
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
| columns | `kicker`, `title`, `categories[]`, `series[]` `{name, values[]}`, `insight`, `number_format` - wykres EDYTOWALNY |
| price | `kicker`, `title`, `image` (1 paczka lub lista 3), `props`, `price`, `price_label`, `price_note`, `facts[4]` `{label, value}` |
| compare_table | `kicker`, `title`, `columns[]` (pierwsza = nasz produkt), `rows[]` [cecha, True/False/tekst, ...] |
| occasions | `kicker`, `title`, `items[4]` `{icon, time, title, text}` |
| social | `kicker`, `title`, `items[3]` `{image, channel, result}` |
| next_steps | `kicker`, `title`, `items[]` `{task, who, when, done}` |
| instructions | `kicker`, `title`, `columns[2]` [[nagłówek, treść], ...] |
| flow | **tekst bez limitu długości** (konwersja, 06.10): `kicker`, `title`, `blocks[]` `{k, t, url?}` (`k`: `p` akapit, `li` punkt - prawdziwe wypunktowanie, `h` podtytuł, `small` / `url` drobny tekst; ukośnik-n (backslash n) w `t` = łamanie wiersza), `images[]` `{image, caption}` (1-2 obrazy w całości z prawej), `source`. Pismo samo 20 -> 13 pt; mieszczenie sprawdza `flow_layout(blocks, w, h)` |
| text_cols | 2-4 kolumny w kartach (konwersja): `kicker`, `title`, `columns[]` `{title?, blocks[]}` (bloki jak w `flow`), `source`. Mieszczenie: `text_cols_layout(columns, has_title)` |
| pics | zdjęcia / zrzuty **w całości, bez przycinania** (konwersja): `kicker`, `title`, `items[]` `{image, caption}` (1-6), `note` (wspólny podpis pod spodem), `source` |
| uklad | **układ 1:1 ze starego slajdu** (konwersja, 07.10): `kicker`, `title`, `bg` (`paper` / `card`), `valign` (`m` / `t`), `max_f` (np. 1.2 = pismo do 120%), `source`, `rows[]` w kolejności góra-dół: tekst `{k: big / h / lead / sub (Mindset) albo p / b / small (Lato), t, align, color, pt, w, li, gap}`; kolumny `{k: cols, items[] {blocks[] {k: img (image, h w cm, round) albo h / lead / p / b / small}, tag (czerwony znacznik, np. „Zmiana nazwy”), meta (zielona metka na dole, np. „Segment 1 & 3”), w (waga), fill}, card, grow}`; kafle haseł `{k: chips, items[], per_row}`; obrazy w całości `{k: pics, items[] {image, caption}, layout: "1+siatka", split, rows_h}`. Dodatki z 07.10 (automat): w wierszu tekstu i w bloku kolumny `wyr` = kolor słowo po słowie (`"a--i-"`: `a` akcent, `i` zieleń marki, `-` kolor wiersza); w `pics` `h` / `min_h` (cm) i `ws` (udziały szerokości komórek - mały obraz zostaje mały); w bloku `img` `name` (nazwa kształtu, np. lista plików wizualizacji). Sam zmniejsza pismo co 5%, aż wszystko się mieści; `ValueError`, gdy się nie da (wtedy podziel slajd i powiedz o tym). Przed budową: `build_dk.uklad_fit(spec)` (współczynnik pisma albo `None`) i `uklad_layout(spec)`. Zasady: `konwersja-pptx.md` |

Tytuły Mindset łamią się równo (bez sieroty); ręczne łamanie: `
` w tekście (np. `"1 g kreatyny
w każdej kulce"`).
Film/zdjęcie: rogi = geometria `roundRect` na samym obiekcie (`round_picture`), NIE maska - dzięki temu "Zmień obraz" i Malarz formatów przenoszą kształt.

Brak `image` -> placeholder "ZDJĘCIE" / "PACKSHOT" (w PowerPoint: prawy klik > Zmień obraz).
Pełny przykład wszystkich typów: `scripts/make_template.py`. Przykład prezentacji produktu: `examples/kulki-kreatyna/make_specs.py`.
