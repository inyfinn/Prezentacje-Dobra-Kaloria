#!/usr/bin/env bash
# Instalacja skilli dla agenta AI (Mac / Linux): /prezentacje i /ui-ux-pro-max - kopiowanie bez kasowania.
#   bash zainstaluj-skille.sh [katalog skilli]      domyślnie ~/.claude/skills (Codex: ~/.codex/skills, Gemini: ~/.gemini/skills)
# Źródła: każdy folder skille/<nazwa>/ z SKILL.md obok tego pliku.
# Skill już zainstalowany i taki sam -> pomija. Inny -> stary PRZENOSI do <katalog>/_poprzednie/<nazwa>-<data>, potem kopiuje.
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"
KAT="${1:-$HOME/.claude/skills}"
case "$KAT" in /*) ;; *) echo "BLAD: podaj pełną ścieżkę katalogu skilli"; exit 1 ;; esac
[ "$KAT" = "/" ] || [ "$KAT" = "$HOME" ] && { echo "BLAD: zły katalog skilli: $KAT"; exit 1; }
STAMP="$(date +%Y-%m-%d_%H%M%S)"
mkdir -p "$KAT"
for zr in "$R"/skille/*/; do
  zr="${zr%/}"; nazwa="$(basename "$zr")"
  [ -f "$zr/SKILL.md" ] || continue
  cel="$KAT/$nazwa"
  if [ -f "$cel/SKILL.md" ] && cmp -s "$zr/SKILL.md" "$cel/SKILL.md" \
     && [ "$(find "$zr" -type f | wc -l)" -eq "$(find "$cel" -type f | wc -l)" ]; then
    echo "[$nazwa] już zainstalowany i aktualny - pomijam ($cel)"; continue
  fi
  if [ -f "$cel/SKILL.md" ] && [ -f "$zr/PACZKA-LEKKA.txt" ] && [ ! -f "$cel/PACZKA-LEKKA.txt" ]; then
    echo "[$nazwa] jest już pełna wersja - nie nadpisuję jej lekką z paczki ($cel)"; continue
  fi
  if [ -e "$cel" ]; then
    mkdir -p "$KAT/_poprzednie"
    mv "$cel" "$KAT/_poprzednie/$nazwa-$STAMP"
    echo "[$nazwa] poprzednia wersja przeniesiona do: $KAT/_poprzednie/$nazwa-$STAMP"
  fi
  cp -R "$zr" "$cel"
  [ -f "$cel/SKILL.md" ] || { echo "BLAD: [$nazwa] kopia nie powiodła się"; exit 1; }
  echo "[$nazwa] zainstalowano -> $cel"
done
echo "Agent zobaczy skille po nowej sesji albo po wczytaniu SKILL.md z tych katalogów."
