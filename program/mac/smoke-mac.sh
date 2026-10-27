#!/usr/bin/env bash
# Prawdziwy test dymny na macOS: zbudowaną binarką zrób prezentację ze scenariusza (wzór ze skilla), bez PowerPointa,
# i sprawdź, że powstał poprawny plik .pptx ze slajdami.
#   bash smoke-mac.sh ["<ścieżka do Stwórz prezentację.app>"]      (domyślnie: wynik buduj-mac.sh)
# Tymczasowy folder prezentacji powstaje w $TMPDIR i zostaje (system sprząta go sam); skrypt niczego nie kasuje.
set -euo pipefail

MAC="$(cd "$(dirname "$0")" && pwd)"
PROG="$(dirname "$MAC")"
PY="${PYTHON:-python3}"
APP="${1:-$MAC/_wynik/dist/Stwórz prezentację.app}"
BIN="$APP/Contents/MacOS/stworz-prezentacje"
WZOR="$PROG/src/skill/assets/scenariusz-wzor.md"

[ "$(uname -s)" = "Darwin" ] || { echo "BŁĄD: smoke test jest dla macOS (uname: $(uname -s))" >&2; exit 1; }
[ -x "$BIN" ] || { echo "BŁĄD: brak pliku wykonywalnego $BIN" >&2; exit 1; }
[ -f "$WZOR" ] || { echo "BŁĄD: brak wzoru scenariusza $WZOR" >&2; exit 1; }

D="$(mktemp -d "${TMPDIR:-/tmp}/dk-smoke.XXXXXX")"
mkdir -p "$D/Źródła"
cp "$WZOR" "$D/scenariusz.md"
# wzór odwołuje się do obrazu Źródła/baton-przyklad.jpg - atrapa
"$PY" -c 'import sys; from PIL import Image; Image.new("RGB", (900, 600), (40, 140, 70)).save(sys.argv[1])' "$D/Źródła/baton-przyklad.jpg"
echo "folder prezentacji: $D"

# CLI: ten sam plik wykonywalny co okno, z argumentami (kod 0 = gotowe). Na Macu nie ma PowerPointa, więc bez zrzutów i kontroli tekstu.
set +e
WYNIK="$("$BIN" "$D" --scenariusz "$D/scenariusz.md" --wyjscie "$D" 2>&1)"
KOD=$?
set -e
printf '%s\n' "$WYNIK" | tail -15
[ "$KOD" -eq 0 ] || { echo "BŁĄD: budowa ze scenariusza zwróciła kod $KOD" >&2; exit 1; }

PPTX="$(ls -t "$D"/*.pptx 2>/dev/null | head -1 || true)"
[ -n "$PPTX" ] && [ -s "$PPTX" ] || { echo "BŁĄD: w $D nie powstał plik .pptx" >&2; ls -la "$D" >&2; exit 1; }
# poprawny plik .pptx = zip z co najmniej 3 slajdami
SLAJDY="$("$PY" -c 'import sys, zipfile; z = zipfile.ZipFile(sys.argv[1]); print(len([n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]))' "$PPTX")"
[ "$SLAJDY" -ge 3 ] || { echo "BŁĄD: $PPTX ma $SLAJDY slajdów" >&2; exit 1; }
echo "OK: $PPTX ($(wc -c < "$PPTX" | tr -d ' ') B, $SLAJDY slajdów)"
