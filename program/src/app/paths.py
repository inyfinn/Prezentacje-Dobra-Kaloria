# -*- coding: utf-8 -*-
"""Ścieżki programu "Stwórz prezentację".

Dwa tryby:
  * deweloperski  - kod w WORK\src (app\, ui\, skill\)
  * spakowany     - PyInstaller: "Stwórz prezentację.exe" + "pliki programu\" (sys._MEIPASS); wersja konsolowa
                    dla AI leży WEWNĄTRZ "pliki programu" (zawartość obok siebie), więc ROOT liczymy ostrożnie.
Program może stać na dysku sieciowym (G:) - NIC nie zapisuje do własnego folderu; cache i logi idą do USER_DIR.
"""
import os
import sys

import platforma

FROZEN = bool(getattr(sys, "frozen", False))
if FROZEN:
    CONTENTS = sys._MEIPASS                                   # ...\pliki programu
    APP_DIR = os.path.join(CONTENTS, "app")                   # ui\, skill\, app\render_app.ps1
    _exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    ROOT = _exe_dir if os.path.isdir(os.path.join(_exe_dir, "pliki programu")) else os.path.dirname(CONTENTS)
    if platforma.mac():
        ROOT = CONTENTS       # w pakiecie .app instrukcje (AGENTS.md) i wersja.txt leżą w zasobach, nie obok programu
else:
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # WORK\src
    CONTENTS = APP_DIR
    ROOT = os.path.dirname(os.path.dirname(APP_DIR))                        # — SZABLON AI - skrypt

UI_DIR = os.path.join(APP_DIR, "ui")
SKILL_DIR = os.path.join(APP_DIR, "skill")
SKILL_SCRIPTS = os.path.join(SKILL_DIR, "scripts")
RENDER_PS = os.path.join(APP_DIR, "app", "render_app.ps1")
VERIFY_PS = os.path.join(SKILL_SCRIPTS, "verify.ps1")
USER_DIR = platforma.katalog_uzytkownika()      # Windows: %LOCALAPPDATA%\Dobra Kaloria\Stworz prezentacje; macOS: ~/Library/Application Support/...
LOG_DIR = os.path.join(USER_DIR, "logi")
AGENTS_MD = os.path.join(ROOT, "AGENTS.md")
# Wersja konsolowa dla AI. Windows: osobny stworz-cli.exe w "pliki programu". macOS: ten sam plik wykonywalny co okno
# (Contents/MacOS/stworz-prezentacje); z argumentami (folder albo opcja zaczynająca się od "-") działa jak wiersz poleceń (main_gui.py).
CLI_EXE = sys.executable if (FROZEN and platforma.mac()) else os.path.join(ROOT, "pliki programu", "stworz-cli.exe")


def version():
    for p in (os.path.join(CONTENTS, "wersja.txt"), os.path.join(ROOT, "WORK", "wersja.txt")):
        try:
            return open(p, encoding="utf8").read().strip()
        except OSError:
            pass
    return "dev"


def ensure_user_dirs():
    for d in (USER_DIR, LOG_DIR, os.path.join(USER_DIR, "cache")):
        os.makedirs(d, exist_ok=True)
