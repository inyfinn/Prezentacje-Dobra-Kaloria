#!/usr/bin/env bash
# Budowa "Stwórz prezentację.app" i obrazu "Prezentacje na Maca.dmg" na macOS (lokalnie albo w GitHub Actions).
#   bash buduj-mac.sh
# Wymaga: macOS, Python 3.12 z pakietami z requirements-mac.txt (pip install -r requirements-mac.txt).
# Wynik: <ten folder>/_wynik/dist/Stwórz prezentację.app oraz _wynik/Prezentacje na Maca.dmg.
# Niczego nie kasuje: kolejne budowy nadpisują ten sam wynik (PyInstaller sam czyści swój folder roboczy).
set -euo pipefail

MAC="$(cd "$(dirname "$0")" && pwd)"
PROG="$(dirname "$MAC")"                     # program/ w repozytorium, WORK/ w folderze źródłowym
PY="${PYTHON:-python3}"
OUT="${DK_MAC_OUT:-$MAC/_wynik}"
APP_NAME="Stwórz prezentację.app"
DMG_NAME="Prezentacje na Maca.dmg"
EXE_NAME="stworz-prezentacje"

[ "$(uname -s)" = "Darwin" ] || { echo "BŁĄD: ten skrypt buduje paczkę dla macOS i musi działać na Macu (uname: $(uname -s))." >&2; exit 1; }
[ -f "$PROG/wersja.txt" ] || { echo "BŁĄD: brak $PROG/wersja.txt" >&2; exit 1; }
VER="$(tr -d '[:space:]' < "$PROG/wersja.txt")"
echo "== Stwórz prezentację $VER, macOS ($(uname -m)), $("$PY" --version) =="
mkdir -p "$OUT"

# 1. ikona .icns z istniejącej ikony src/ikona.ico
export DK_ICNS="$OUT/ikona.icns"
"$PY" "$MAC/ikona_icns.py" "$PROG/src/ikona.ico" "$DK_ICNS"

# 2. kontrola importów ze źródeł (szybciej niż cała budowa)
PYTHONPATH="$PROG/src/app:$PROG/src/skill/scripts" "$PY" -c "import engine, gui, platforma; assert platforma.mac(); assert not engine.powerpoint_available(); print('import OK')"

# 3. PyInstaller
"$PY" -m PyInstaller --noconfirm --clean --distpath "$OUT/dist" --workpath "$OUT/praca" "$MAC/stworz_mac.spec"
APP="$OUT/dist/$APP_NAME"
[ -d "$APP" ] || { echo "BŁĄD: nie powstał $APP" >&2; exit 1; }

# 4. test dymny: ten sam plik wykonywalny z argumentem "--help" działa jak wiersz poleceń (kod 0, jest tekst pomocy)
POMOC="$("$APP/Contents/MacOS/$EXE_NAME" --help 2>&1)" || { echo "BŁĄD: --help zwróciło niezerowy kod" >&2; echo "$POMOC" >&2; exit 1; }
sed -n 1,3p <<<"$POMOC"
grep -q "stworz-cli" <<<"$POMOC" || { echo "BŁĄD: brak tekstu pomocy w wyniku --help" >&2; exit 1; }
if codesign --verify --deep --strict "$APP"; then echo "podpis (ad hoc) poprawny"; else echo "UWAGA: podpis ad hoc niepoprawny - aplikacja może nie wystartować" >&2; fi

# 5. obraz DMG: aplikacja + skrót do Programów (przeciągnij, żeby zainstalować)
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/dk-dmg.XXXXXX")"
ditto "$APP" "$STAGE/$APP_NAME"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "Prezentacje" -srcfolder "$STAGE" -ov -format UDZO "$OUT/$DMG_NAME"
echo "tymczasowy folder obrazu (można usunąć): $STAGE"
ls -la "$OUT/$DMG_NAME"
echo "OK $VER"
