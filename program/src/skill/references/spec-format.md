# Format spec JSON

Wspólne: `{"output": "../Nazwa.pptx", "slides": [ ... ]}`. Ścieżki (`path`, `image`) względem pliku spec.
Jednostki geometrii: cm (slajd 33,87 × 19,05), obrót w stopniach. Liczby jako tekst ("59%", "11 g").

## build_deck.py (styl szablon)

| type | pola |
|---|---|
| cover | `variant`: "product" (domyślny) \| "template"; product: `kicker`, `title`, `subtitle` (str lub lista), `alternate` (naprzemienne kolory linii - raport); template: `title`, `title2`, `subtitle` |
| product | `title`, `bullets[]`, `images[]` (packshoty), `props[]`, `callouts[]`, opc. `text_x`, `text_w`, `size`, `region` [x0,y0,x1,y1] |
| bullets | `title`, `bullets[]` (styl wzoru: zielone kropki, 32 pt) |
| arrows | `title`, `items[]`: str albo `{text, slim}` |
| stats | `title`, `lead`, `items[]`: `{value, label, note}` (2-4), opc. `images[]`, `source` |
| compare | `title`, `items[]`: `{path, value, label, sub}` (`value` "" = bez liczby), `highlight` (indeks), `source` |
| bars | `title`, `lead`, `items[]`: `{label, value 0-100, text?}`, `highlight[]`, opc. `images[]`, `source` |
| gallery | `title`, `images[]`, `cols`, `caption` (tekst obok), `frame` (ramka telefonu) |
| free | `title`, `images[]` `{path,x,y,h|w,rot,shadow}`, `texts[]` `{text,x,y,w,size,font,color,align}` |
| skus | `title`, `items[]` `{name, meta, ean, color, path?, shadow_color}` - nazwa w ramce-pędzlu; bez `path` koło w kolorze smaku |
| end | opc. `hashtag` |

`images[]` (packshoty): `{path, h?, x?, y?, rot?, scale?, shadow (true), shadow_color}` - bez x/y układ automatyczny:
1 = centralnie, 2 = kaskada, 3 = trójkąt (dwa z tyłu, jeden z przodu), 4+ = rząd.
`props[]` (rekwizyty): `{path, w, x, y, rot}` albo `{path, w, anchor: tl|tr|bl|br|l|r|b, dx, dy, behind}`.
`callouts[]`: `{kind: banner|round|box|bubble|speech|polska, x, y, w, h?, text, size, font}`.

## build_fresh.py (styl fresh)

Globalnie: `accent` (hex koloru produktu), `footer` (domyślna stopka). Każdy slajd treści: `kicker`, `title`, `source`.

| type | pola |
|---|---|
| cover | `kicker`, `title`, `subtitle`, `tag` (pigułka), `image`, `image_h`, `rot` |
| section | `title`, `subtitle`, opc. `number` (domyślnie nr strony), `image`, `image_h`, `rot` |
| features | `image`, `items[]` (4): `{title, text}` |
| hero_stat | `value`, `label`, `items[]` (1-3) `{value,label}`, `image` |
| segments | `lead`, `groups[]`: `{name, desc, metrics[] {value,label}}` |
| compare | `items[]` `{path, value, label, sub}`, `highlight`, `badge` |
| split | `a` `{value,label}`, `b` `{value,label}`, `groups_title`, `groups[]` `{value,label}`, `note` |
| bars | `items[]` `{label,value}`, `highlight[]`, `insight` (karta wniosku), `image` |
| reasons | `items[]` (3-4) `{value, title, text}` - pierwsza karta zielona |
| skus | `items[]` `{name, meta, ean, color, path?}` - bez `path` rysuje koło w kolorze smaku |
| end | `hashtag`, `contact` |
