# -*- coding: utf-8 -*-
"""Warstwa platformy (Windows / macOS): wszystko, co różni się między systemami, w jednym miejscu.

Windows: kod bez zmian (ctypes, os.startfile, explorer, Get-StartApps, winreg). macOS: pbcopy/pbpaste, `open`, `open -R`,
/Applications/<Nazwa>.app, osascript + Terminal.app. Reszta programu pyta tylko tę warstwę. Moduł niczego nie importuje z programu
(paths, engine, gui importują jego), żeby nie robić pętli. Kto chce przetestować macOS na Windows, podmienia mac() i windows()
(patrz WORK\\logs\\test_platforma.py).
"""
import ctypes
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

NAZWA_FIRMY = "Dobra Kaloria"
NAZWA_PROGRAMU = "Stworz prezentacje"
LIMIT_SCHOWKA = 1 << 20           # tekst ze schowka większy niż 1 MB pomijamy
CREATE_NO_WINDOW = 0x08000000


def windows():
    return sys.platform == "win32"


def mac():
    return sys.platform == "darwin"


# --- ścieżki -------------------------------------------------------------------------------------------------------------
def katalog_uzytkownika():
    """Ustawienia, logi i cache programu. Windows: %LOCALAPPDATA%\\Dobra Kaloria\\Stworz prezentacje.
    macOS: ~/Library/Application Support/Dobra Kaloria/Stworz prezentacje."""
    if mac():
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", NAZWA_FIRMY, NAZWA_PROGRAMU)
    return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), NAZWA_FIRMY, NAZWA_PROGRAMU)


def dysk_lokalny(sciezka):
    """True, gdy ścieżka leży na dysku stałym (Windows: GetDriveTypeW == 3). Poza Windows: True (aktualizacja i tak jest wyłączona)."""
    if not windows():
        return True
    drive = os.path.splitdrive(sciezka)[0] + "\\"
    return ctypes.windll.kernel32.GetDriveTypeW(drive) == 3


# --- schowek -------------------------------------------------------------------------------------------------------------
def _srodowisko_utf8():
    """pbcopy/pbpaste czytają i piszą w kodowaniu z LANG; aplikacja uruchomiona z Findera nie ma LANG i dostałaby MacRoman."""
    env = dict(os.environ)
    env["LANG"] = "en_US.UTF-8"
    env["LC_ALL"] = "en_US.UTF-8"
    return env


def schowek_ustaw(text):
    """Tekst do schowka. True/False."""
    text = text or ""
    if mac():
        try:
            r = subprocess.run(["pbcopy"], input=text.encode("utf-8"), env=_srodowisko_utf8(), capture_output=True, timeout=10)
            return r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
    CF_UNICODETEXT, GMEM_MOVEABLE = 13, 0x0002
    k32, u32 = ctypes.windll.kernel32, ctypes.windll.user32
    # Typy muszą być podane jawnie: bez nich ctypes obcina 64-bitowy uchwyt do 32 bitów
    # ("access violation writing 0x0" przy dłuższym tekście - błąd z 29.09.2026)
    k32.GlobalAlloc.restype = ctypes.c_void_p
    k32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [ctypes.c_void_p]
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    k32.GlobalFree.argtypes = [ctypes.c_void_p]
    u32.OpenClipboard.argtypes = [ctypes.c_void_p]
    u32.SetClipboardData.restype = ctypes.c_void_p
    u32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    data = text.encode("utf-16-le") + b"\x00\x00"
    for _ in range(10):  # schowek bywa chwilowo zajęty przez inny program
        if u32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        return False
    try:
        u32.EmptyClipboard()
        h = k32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not h:
            return False
        p = k32.GlobalLock(h)
        if not p:
            k32.GlobalFree(h)
            return False
        ctypes.memmove(p, data, len(data))
        k32.GlobalUnlock(h)
        if not u32.SetClipboardData(CF_UNICODETEXT, h):
            k32.GlobalFree(h)
            return False
        return True
    finally:
        u32.CloseClipboard()


def schowek_pobierz():
    """Tekst ze schowka albo None. Tylko odczyt: niczego nie zmienia ani nie czyści. Gdy schowek jest chwilowo zajęty przez inny
    program albo nie ma w nim tekstu - None (okno zapyta za sekundę); tekst ponad 1 MB pomijamy."""
    if mac():
        try:
            r = subprocess.run(["pbpaste"], env=_srodowisko_utf8(), capture_output=True, timeout=3)
        except (OSError, subprocess.SubprocessError):
            return None
        if r.returncode != 0 or not r.stdout or len(r.stdout) > LIMIT_SCHOWKA:
            return None
        return r.stdout.decode("utf-8", "replace")
    CF_UNICODETEXT = 13
    k32, u32 = ctypes.windll.kernel32, ctypes.windll.user32
    k32.GlobalLock.restype = ctypes.c_void_p
    k32.GlobalLock.argtypes = [ctypes.c_void_p]
    k32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    k32.GlobalSize.restype = ctypes.c_size_t
    k32.GlobalSize.argtypes = [ctypes.c_void_p]
    u32.OpenClipboard.argtypes = [ctypes.c_void_p]
    u32.GetClipboardData.restype = ctypes.c_void_p
    u32.GetClipboardData.argtypes = [ctypes.c_uint]
    if not u32.IsClipboardFormatAvailable(CF_UNICODETEXT):   # bez otwierania schowka: zwykle nie ma tekstu
        return None
    for _ in range(3):
        if u32.OpenClipboard(None):
            break
        time.sleep(0.03)
    else:
        return None
    try:
        h = u32.GetClipboardData(CF_UNICODETEXT)
        if not h or k32.GlobalSize(h) > LIMIT_SCHOWKA:
            return None
        p = k32.GlobalLock(h)
        if not p:
            return None
        try:
            return ctypes.wstring_at(p)
        finally:
            k32.GlobalUnlock(h)
    finally:
        u32.CloseClipboard()


# --- otwieranie plików, folderów i adresów ------------------------------------------------------------------------------
def otworz(cel):
    """Plik, folder albo adres (http://, claude://) w programie domyślnym systemu. Niepowodzenie = OSError (jak os.startfile)."""
    if mac():
        r = subprocess.run(["open", cel], capture_output=True, timeout=30)
        if r.returncode != 0:
            raise OSError("open zwrócił kod %d dla %s" % (r.returncode, cel))
        return
    os.startfile(cel)


def pokaz_w_folderze(plik):
    """Otwiera folder pliku i zaznacza go (Windows: explorer /select, macOS: open -R)."""
    if mac():
        subprocess.Popen(["open", "-R", plik])
    else:
        subprocess.Popen(["explorer", "/select,", plik])


# --- aplikacje ------------------------------------------------------------------------------------------------------------
def znajdz_aplikacje(nazwa):
    """Windows: AppID aplikacji z menu Start o dokładnie tej nazwie. macOS: ścieżka /Applications/<Nazwa>.app albo ~/Applications/<Nazwa>.app.
    None, gdy aplikacji nie ma."""
    if not nazwa or not re.fullmatch(r"[A-Za-z0-9 ]+", nazwa):
        return None
    if mac():
        for d in ("/Applications", os.path.join(os.path.expanduser("~"), "Applications")):
            p = os.path.join(d, nazwa + ".app")
            if os.path.isdir(p):
                return p
        return None
    try:
        cmd = "(Get-StartApps | Where-Object { $_.Name -eq '%s' } | Select-Object -First 1).AppID" % nazwa
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
                           capture_output=True, text=True, timeout=15, creationflags=CREATE_NO_WINDOW)
        app = (r.stdout or "").strip().splitlines()
        return app[0].strip() if app and app[0].strip() else None
    except Exception:
        return None


def uruchom_aplikacje(appid):
    """Uruchamia aplikację znalezioną przez znajdz_aplikacje."""
    if mac():
        subprocess.Popen(["open", appid])
    else:
        subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + appid])


def powerpoint_dostepny():
    """PowerPoint do zrzutów i kontroli tekstu (COM) jest tylko na Windows. Na Macu zawsze False: program niczego tam nie renderuje."""
    if not windows():
        return False
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"PowerPoint.Application\CurVer"))
        return True
    except OSError:
        return False


def schemat_claude():
    """True, gdy system zna schemat claude:// (Windows: wpis w rejestrze; macOS: jest Claude.app)."""
    if mac():
        return znajdz_aplikacje("Claude") is not None
    try:
        import winreg
        winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "claude"))
        return True
    except OSError:
        return False


def znajdz_claude():
    """Pełna ścieżka polecenia `claude` (Claude Code) albo None. Aplikacja z Findera nie dziedziczy PATH z terminala, więc na Macu
    sprawdzamy jeszcze typowe miejsca instalacji."""
    p = shutil.which("claude")
    if p or not mac():
        return p
    dom = os.path.expanduser("~")
    for d in (os.path.join(dom, ".local", "bin"), os.path.join(dom, ".claude", "local"), "/opt/homebrew/bin", "/usr/local/bin",
              os.path.join(dom, ".npm-global", "bin")):
        k = os.path.join(d, "claude")
        if os.path.isfile(k) and os.access(k, os.X_OK):
            return k
    return None


def polecenie_terminala(folder, claude, polecenie):
    """Linia wpisywana w Terminalu na Macu: cd '<folder>' && '<claude>' '<polecenie>'. Każdy element przez shlex.quote
    (spacje, polskie litery i apostrofy w ścieżce są bezpieczne)."""
    return "cd %s && %s %s" % (shlex.quote(folder), shlex.quote(claude), shlex.quote(polecenie))


def argumenty_osascript(linia):
    """Lista argumentów osascript: skrypt w kilku -e, a linia powłoki przychodzi jako `argv` (bez wklejania jej do tekstu AppleScript,
    więc bez drugiej warstwy cytowania)."""
    return ["osascript",
            "-e", "on run argv",
            "-e", 'tell application "Terminal"',
            "-e", "activate",
            "-e", "do script (item 1 of argv)",
            "-e", "end tell",
            "-e", "end run",
            linia]


def uruchom_claude_code(folder, polecenie):
    """Nowe okno terminala w folderze prezentacji z `claude` i krótkim poleceniem. Windows: Windows Terminal (wt), a gdy go nie ma -
    zwykła konsola. macOS: Terminal.app przez osascript (przy pierwszym użyciu system pyta o zgodę na sterowanie Terminalem).
    Lista argumentów, jedna powłoka, bez zagnieżdżonych cudzysłowów. False, gdy `claude` nie jest zainstalowany albo folder nie istnieje."""
    claude = znajdz_claude()
    if not claude or not os.path.isdir(folder):
        return False
    if mac():
        try:
            r = subprocess.run(argumenty_osascript(polecenie_terminala(folder, claude, polecenie)), capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return False
        return r.returncode == 0
    wt = shutil.which("wt")
    if wt:
        subprocess.Popen([wt, "-d", folder, claude, polecenie])
    else:
        subprocess.Popen(["cmd.exe", "/k", "claude", polecenie], cwd=folder, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return True
