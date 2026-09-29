# Format spec JSON - build_dk.py

```json
{"output": "../Nazwa.pptx", "theme": "fresh|shop", "sections": false, "morph": true, "footer": "", "slides": [...]}
```
Ścieżki `image`, `pack`, `path`, `props[]` - względem pliku spec. Każdy slajd może mieć: `morph` (false wyłącza),
`section` (nazwa sekcji PowerPointa od tego slajdu), `label_slide` (opis "do czego służy" - notatki + karteczka poza
slajdem), `hidden` (true = ukryty w pokazie). Kolory: token motywu (`brand`, `card`, ...) albo stały hex.

| type | pola |
|---|---|
| cover | `variant` 1-4 (**4 = wzór usera 29.09**: duże logo na zieleni, "NOWOŚĆ" zielonym Mindsetem, 3 paczki pod tytułem), `kicker`, `title`, `subtitle`, `image` (packshot albo lista 3 = trio), `props[]`, `flavors[]` `{name, dot}`; `kicker_style` display/button/label (okładki domyślnie display) |
| cover_text | `variant` 1-3, `kicker`, `title`, `subtitle`, `meta` (autor/data), `props[]` (wariant 2) |
| agenda | `kicker`, `title`, `items[]` str albo `{title, text}` (do 8) |
| section | `variant` dark/light, `number`, `title`, `subtitle`, opc. `image`, `props` |
| lead | `kicker`, `title`, `lead`, `columns[]` `{title, text}` |
| statement | `kicker`, `text`, `note`, `bg` |
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

Tytuły Mindset łamią się równo (bez sieroty); ręczne łamanie: `
` w tekście (np. `"1 g kreatyny
w każdej kulce"`).
Film/zdjęcie: rogi = geometria `roundRect` na samym obiekcie (`round_picture`), NIE maska - dzięki temu "Zmień obraz" i Malarz formatów przenoszą kształt.

Brak `image` -> placeholder "ZDJĘCIE" / "PACKSHOT" (w PowerPoint: prawy klik > Zmień obraz).
Pełny przykład wszystkich typów: `scripts/make_template.py`. Przykład prezentacji produktu: `examples/kulki-kreatyna/make_specs.py`.
