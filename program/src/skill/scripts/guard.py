# -*- coding: utf-8 -*-
"""
Blokada nadpisania plików edytowanych przez ludzi (lekcja 28.09.2026: dwa razy nadpisałem ręczne poprawki usera).

Każdy zapis generatora (build_dk, build_deck, render.ps1 -EmbedFonts) zapisuje SHA-256 pliku do
~/.claude/skills/prezentacje/.cache/wygenerowane.json. Przed kolejnym zapisem:
  - plik nie istnieje                       -> zapis OK
  - suma na dysku == ostatnio zapisana przez nas -> zapis OK (nikt nie ruszał)
  - suma inna (człowiek edytował) albo plik nieznany -> NIE nadpisujemy; wynik idzie do "<nazwa> (nowa wersja).pptx"
  - plik otwarty w PowerPoint (plik blokady ~$) -> NIE nadpisujemy

    python guard.py record <plik>     # zapisz sumę (render.ps1 woła po ponownym zapisie)
    python guard.py check <plik>      # 0 = można nadpisać, 1 = nie wolno
"""
import hashlib
import json
import os
import sys

CACHE = os.environ.get("DK_GUARD_CACHE") or os.path.join(  # program portable (G:) ustawia katalog per użytkownik
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "wygenerowane.json")


def _load():
    try:
        return json.load(open(CACHE, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _key(path):
    return os.path.normcase(os.path.abspath(path))


def lock_file(path):
    d, n = os.path.split(os.path.abspath(path))
    return os.path.join(d, "~$" + n)


def can_overwrite(path):
    """(True, '') gdy wolno nadpisać; (False, powód) gdy nie."""
    if not os.path.exists(path):
        return True, ""
    if os.path.exists(lock_file(path)):
        return False, "plik jest otwarty w PowerPoint (plik blokady ~$)"
    rec = _load().get(_key(path))
    if rec is None:
        return False, "plik nie pochodzi z generatora (brak zapisanej sumy) - mógł go utworzyć lub edytować człowiek"
    if rec != _sha(path):
        return False, "plik zmieniono po ostatnim zapisie generatora (ręczna edycja)"
    return True, ""


def safe_target(path):
    """Ścieżka, pod którą wolno zapisać: oryginał albo '(nowa wersja)' obok. Wypisuje powód odmowy."""
    ok, why = can_overwrite(path)
    if ok:
        return path
    base, ext = os.path.splitext(path)
    alt = base + " (nowa wersja)" + ext
    n = 2
    while os.path.exists(alt) and not can_overwrite(alt)[0]:
        alt = "%s (nowa wersja %d)%s" % (base, n, ext)
        n += 1
    print("UWAGA: nie nadpisuję '%s' - %s. Zapisuję jako '%s'." % (os.path.basename(path), why, os.path.basename(alt)))
    return alt


def record(path):
    data = _load()
    data[_key(path)] = _sha(path)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(data, open(CACHE, "w", encoding="utf8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    cmd, target = sys.argv[1], sys.argv[2]
    if cmd == "record":
        record(target)
    elif cmd == "check":
        ok, why = can_overwrite(target)
        print("OK" if ok else "NIE: " + why)
        sys.exit(0 if ok else 1)
