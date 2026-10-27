# -*- mode: python ; coding: utf-8 -*-
# PyInstaller (macOS): pakiet "Stwórz prezentację.app" z oknem (pywebview/WKWebView) i silnikiem Pythona.
# Jeden plik wykonywalny Contents/MacOS/stworz-prezentacje: bez argumentów otwiera okno, z folderem albo opcją
# zaczynającą się od "-" działa jak wiersz poleceń dla AI (main_gui.py). Bez skryptów .ps1 i bez pliku startowego C#.
# Buduje buduj-mac.sh (GitHub Actions: .github/workflows/mac.yml). Ścieżki liczone od tego pliku:
#   <program>/mac/stworz_mac.spec, <program>/src, <program>/wersja.txt  (w WORK: WORK/mac, WORK/src, WORK/wersja.txt)
import os
import posixpath

PROG = os.path.dirname(SPECPATH)
SRC = os.path.join(PROG, "src")
WERSJA = open(os.path.join(PROG, "wersja.txt"), encoding="utf8").read().strip()
ICNS = os.environ.get("DK_ICNS") or os.path.join(SPECPATH, "ikona.icns")   # tworzy ją buduj-mac.sh z src/ikona.ico
NAZWA_APP = "Stwórz prezentację"


def pliki(katalog, cel, pomin_rozszerzenia=(".ps1", ".pyc"), pomin_prefiks=()):
    """Wszystkie pliki katalogu jako (źródło, folder docelowy) dla datas; bez skryptów Windows (.ps1), cache i testów."""
    wynik = []
    for root, dirs, files in os.walk(katalog):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".cache", ".pytest_cache")]
        rel = os.path.relpath(root, katalog).replace(os.sep, "/")
        dst = cel if rel == "." else posixpath.join(cel, rel)
        for f in files:
            if f.lower().endswith(pomin_rozszerzenia) or f.startswith(pomin_prefiks) or f == ".DS_Store":
                continue
            wynik.append((os.path.join(root, f), dst))
    return wynik


datas = (pliki(os.path.join(SRC, "ui"), "app/ui")
         + pliki(os.path.join(SRC, "skill", "scripts"), "app/skill/scripts", pomin_prefiks=("test_",))
         + pliki(os.path.join(SRC, "skill", "assets"), "app/skill/assets")
         + pliki(os.path.join(SRC, "skill", "references"), "app/skill/references")
         + [(os.path.join(PROG, "wersja.txt"), ".")])
# python-pptx: szablony XML (notes.xml, default.pptx…) – bez nich budowa pada na notatkach (smoke Actions 27.10.2026)
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files("pptx") + collect_data_files("openpyxl") + collect_data_files("webview")
# SKILL.md obok skryptów (agent AI instaluje skill z tego folderu) i instrukcja AGENTS.md, gdy leży w repo (dla-uzytkownika) / w WORK
for p, cel in ((os.path.join(SRC, "skill", "SKILL.md"), "app/skill"),
               (os.path.join(os.path.dirname(PROG), "dla-uzytkownika", "AGENTS.md"), "."),
               (os.path.join(PROG, "AGENTS.md"), ".")):       # w folderze źródłowym AGENTS.md leży w WORK (od 1.3)
    if os.path.isfile(p):
        datas.append((p, cel))

EXCLUDES = ["tkinter", "matplotlib", "cv2", "scipy", "pandas", "IPython", "jupyter", "notebook", "PyQt5", "PyQt6",
            "PySide2", "PySide6", "playwright", "pytest", "sphinx", "customtkinter", "test", "unittest",
            "clr", "pythonnet", "clr_loader", "qtpy"]
HIDDEN = ["openpyxl", "tifffile", "webview.platforms.cocoa", "webview.dom", "PIL.ImageFont", "PIL.ImageDraw", "PIL.ImageFilter",
          "pptx", "lxml.etree", "lxml._elementpath", "numpy", "lzma", "hashlib", "fitz", "pymupdf", "pypdf",
          # pyobjc: pywebview ładuje cocoa.py dynamicznie
          "objc", "AppKit", "Foundation", "WebKit", "Quartz", "Security", "UniformTypeIdentifiers", "CoreFoundation",
          "PyObjCTools", "PyObjCTools.AppHelper"]

a = Analysis([os.path.join(SRC, "app", "main_gui.py")], pathex=[os.path.join(SRC, "app"), os.path.join(SRC, "skill", "scripts")],
             binaries=[], datas=datas, hiddenimports=HIDDEN, hookspath=[], runtime_hooks=[], excludes=EXCLUDES,
             noarchive=False,
             # python-pptx otwiera szablony ścieżką pptx/oxml/../templates: na macOS folder pptx/oxml musi istnieć na dysku
             # (Windows skraca „..” bez sprawdzania folderu) - moduły pptx także jako pliki .py obok archiwum
             module_collection_mode={"pptx": "pyz+py"})
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="stworz-prezentacje", debug=False, bootloader_ignore_signals=False,
          strip=False, upx=False, console=False, argv_emulation=False, target_arch=None, codesign_identity=None,
          entitlements_file=None)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="stworz-prezentacje")
app = BUNDLE(coll, name=NAZWA_APP + ".app", icon=ICNS, bundle_identifier="pl.dobrakaloria.stworz-prezentacje", version=WERSJA,
             info_plist={
                 "CFBundleVersion": WERSJA,
                 "CFBundleShortVersionString": WERSJA,
                 "LSMinimumSystemVersion": "11.0",
                 "NSHighResolutionCapable": True,
                 # przy pierwszym "Claude Code" system pyta o zgodę na sterowanie Terminalem (osascript); tekst pytania:
                 "NSAppleEventsUsageDescription": "Program otwiera Terminal, żeby uruchomić w nim Claude Code w folderze prezentacji.",
                 "NSDesktopFolderUsageDescription": "Program czyta pliki źródłowe prezentacji i zapisuje gotową prezentację.",
                 "NSDocumentsFolderUsageDescription": "Program tworzy folder prezentacji w Dokumentach i zapisuje w nim wynik.",
                 "NSDownloadsFolderUsageDescription": "Program czyta pliki źródłowe prezentacji.",
             })
