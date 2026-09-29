# -*- mode: python ; coding: utf-8 -*-
# PyInstaller: okno programu "program.exe" z zawartością OBOK SIEBIE (całość trafia do "pliki programu").
# Na wierzchu leży osobny plik startowy (src\launcher\launcher.cs). Buduje build.ps1.
import os

SRC = os.path.join(SPECPATH, "src")
datas = [
    (os.path.join(SRC, "ui"), "app/ui"),
    (os.path.join(SRC, "skill", "scripts"), "app/skill/scripts"),
    (os.path.join(SRC, "skill", "assets"), "app/skill/assets"),
    (os.path.join(SRC, "skill", "references"), "app/skill/references"),
    (os.path.join(SRC, "app", "render_app.ps1"), "app/app"),
    (os.path.join(SPECPATH, "wersja.txt"), "."),
]
EXCLUDES = ["tkinter", "matplotlib", "cv2", "scipy", "pandas", "IPython", "jupyter", "notebook", "PyQt5", "PyQt6",
            "PySide2", "PySide6", "playwright", "pytest", "sphinx", "customtkinter", "test", "unittest"]
HIDDEN = ["openpyxl", "tifffile", "clr", "webview.platforms.edgechromium", "webview.platforms.winforms",
          "webview.dom", "PIL.ImageFont", "PIL.ImageDraw", "PIL.ImageFilter", "pptx", "lxml.etree", "lxml._elementpath"]

a = Analysis([os.path.join(SRC, "app", "main_gui.py")], pathex=[os.path.join(SRC, "app"), os.path.join(SRC, "skill", "scripts")],
             binaries=[], datas=datas, hiddenimports=HIDDEN, hookspath=[], runtime_hooks=[], excludes=EXCLUDES,
             noarchive=False)
pyz = PYZ(a.pure)
# UWAGA: bez Splash() - ekran powitalny PyInstallera (Tcl/Tk) blokował start okna WebView2 i zostawał na wierzchu
# (zgłoszenie usera 29.09 13:40, potwierdzone pomiarem: 1 z 3 startów nie wstał w 40 s). Nie przywracać.
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="program", debug=False, bootloader_ignore_signals=False,
          strip=False, upx=False, console=False, icon=os.path.join(SRC, "ikona.ico"),
          contents_directory=".")
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="program")
