# -*- coding: utf-8 -*-
"""Ścieżki programu "Stwórz prezentację".

Trzy foldery (od 1.3 wierzch jest czysty: Prezentacje.exe, Prezentacje na Maca.dmg, paczka dla AI i folder WORK):
  * ROOT      - wierzch, folder programu "— SZABLON AI - skrypt" (tam leży Prezentacje.exe); obejmuje też WORK
  * WORK_DIR  - folder z zależnościami: "pliki programu\\", skill-prezentacje\\, skill-ds-dobra-kaloria\\, AGENTS.md itd.
                (nowy układ: ROOT\\WORK; stary układ, kopie na M:/G: i wydania do 1.2.x: ten sam folder co ROOT)
  * CONTENTS  - "pliki programu" (sys._MEIPASS); wersja konsolowa dla AI leży WEWNĄTRZ (zawartość obok siebie)
Dwa tryby:
  * deweloperski  - kod w WORK\\src (app\\, ui\\, skill\\); WORK_DIR = WORK
  * spakowany     - PyInstaller: "pliki programu\\program.exe"; WORK_DIR = folder nadrzędny "pliki programu"
Program może stać na dysku sieciowym (G:) - NIC nie zapisuje do własnego folderu; cache i logi idą do USER_DIR.
"""
import os
import sys

import platforma


def uklad_wdrozenia(contents):
    """(WORK_DIR, ROOT) dla programu spakowanego, którego pliki leżą w `contents` ("pliki programu").
    Nowy układ <ROOT>\\WORK\\pliki programu -> (<ROOT>\\WORK, <ROOT>). Stary <ROOT>\\pliki programu -> (<ROOT>, <ROOT>)."""
    nad = os.path.dirname(os.path.abspath(contents))
    if os.path.basename(nad).upper() == "WORK":
        return nad, os.path.dirname(nad)
    return nad, nad


FROZEN = bool(getattr(sys, "frozen", False))
if FROZEN:
    CONTENTS = sys._MEIPASS                                   # ...\WORK\pliki programu (stary układ: ...\pliki programu)
    APP_DIR = os.path.join(CONTENTS, "app")                   # ui\, skill\, app\render_app.ps1
    WORK_DIR, ROOT = uklad_wdrozenia(CONTENTS)
    if platforma.mac():
        WORK_DIR = ROOT = CONTENTS    # w pakiecie .app instrukcje (AGENTS.md) i wersja.txt leżą w zasobach, nie obok programu
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # WORK\src
    CONTENTS = APP_DIR
    WORK_DIR = os.path.dirname(APP_DIR)                                     # WORK (w repozytorium: program)
    ROOT = os.path.dirname(WORK_DIR)                                        # — SZABLON AI - skrypt

UI_DIR = os.path.join(APP_DIR, "ui")
SKILL_DIR = os.path.join(APP_DIR, "skill")
SKILL_SCRIPTS = os.path.join(SKILL_DIR, "scripts")
RENDER_PS = os.path.join(APP_DIR, "app", "render_app.ps1")
VERIFY_PS = os.path.join(SKILL_SCRIPTS, "verify.ps1")
USER_DIR = platforma.katalog_uzytkownika()      # Windows: %LOCALAPPDATA%\Dobra Kaloria\Stworz prezentacje; macOS: ~/Library/Application Support/...
LOG_DIR = os.path.join(USER_DIR, "logi")
AGENTS_MD = os.path.join(WORK_DIR, "AGENTS.md")
# Wersja konsolowa dla AI. Windows: osobny stworz-cli.exe w "pliki programu". macOS: ten sam plik wykonywalny co okno
# (Contents/MacOS/stworz-prezentacje); z argumentami (folder albo opcja zaczynająca się od "-") działa jak wiersz poleceń (main_gui.py).
CLI_EXE = sys.executable if (FROZEN and platforma.mac()) else os.path.join(WORK_DIR, "pliki programu", "stworz-cli.exe")


def version():
    for p in (os.path.join(CONTENTS, "wersja.txt"), os.path.join(WORK_DIR, "wersja.txt")):
        try:
            return open(p, encoding="utf8").read().strip()
        except OSError:
            pass
    return "dev"


def ensure_user_dirs():
    for d in (USER_DIR, LOG_DIR, os.path.join(USER_DIR, "cache")):
        os.makedirs(d, exist_ok=True)
