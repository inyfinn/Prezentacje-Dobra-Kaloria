# -*- coding: utf-8 -*-
"""Okno programu "Stwórz prezentację": pywebview (WebView2) + interfejs HTML z ui\\. Logika w engine.py."""
import ctypes
import json
import os
import subprocess
import threading
import time
import traceback

T0 = time.time()  # start procesu (przed importem ciężkich bibliotek) - do pomiaru czasu uruchamiania

import webview  # noqa: E402

import engine  # noqa: E402
import update  # noqa: E402
import paths  # noqa: E402




def set_clipboard(text):
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


class Api:
    def __init__(self):
        self._window = None
        self.folder = None
        self._cancel = threading.Event()

    # --- wywołania z JS ---------------------------------------------------------------------------------------
    def get_info(self):
        engine._log_file("most JS<->Python gotowy po %.1f s od startu" % (time.time() - T0))
        return {"wersja": paths.version(), "powerpoint": engine.powerpoint_available(), "szablony": ["nowy", "stary"],
                "root": paths.ROOT}

    def pick_folder(self):
        r = self._window.create_file_dialog(webview.FileDialog.FOLDER, directory=self.folder or "")
        return r[0] if r else None

    def analyze(self, path):
        try:
            t = time.time()
            res = engine.analyze(path)
            engine._log_file("analiza folderu: %.1f s (%s)" % (time.time() - t, res["folder"]))
            self.folder = res["folder"]
            self._last_est = res["szacowany_czas_s"]
            return res
        except Exception as e:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "blad": str(e)}

    def build(self, opts):
        if not self.folder:
            return {"started": False, "blad": "Najpierw wskaż folder."}
        self._cancel.clear()
        opts = dict(opts or {})
        opts.setdefault("szacowany_czas_s", getattr(self, "_last_est", 40))

        def run():
            res = engine.safe_build(self.folder, opts, progress=self._progress, log=lambda t: self._js("App.onLog", t),
                                    cancel=self._cancel)
            if res.get("ok"):
                self._js("App.onDone", res)
            else:
                self._js("App.onError", res.get("blad", "Nieznany błąd"))

        threading.Thread(target=run, daemon=True).start()
        return {"started": True}

    def cancel(self):
        self._cancel.set()
        return True

    def open_path(self, p):
        os.startfile(p)
        return True

    def open_folder(self, p):
        if os.path.isfile(p):
            subprocess.Popen(["explorer", "/select,", p])
        else:
            os.startfile(p)
        return True

    def check_update(self):
        r = update.check()
        engine._log_file("aktualizacja: %s" % {k: v for k, v in r.items() if k != "url"})
        self._upd = r if r.get("jest") else None
        return {k: v for k, v in r.items() if k in ("jest", "wersja", "obecna", "sam", "powod", "strona")}

    def apply_update(self):
        info = getattr(self, "_upd", None)
        if not info:
            return {"started": False, "blad": "Nie ma nowszej wersji."}

        def run():
            try:
                src = update.download(info, progress=lambda p: self._js("App.onUpdate", {"procent": p}))
                update.apply(src)
                engine._log_file("aktualizacja pobrana (%s) - zamykam program" % info["wersja"])
                self._js("App.onUpdate", {"procent": 100, "restart": True})
                time.sleep(1.2)
                self._window.destroy()
            except Exception as e:
                engine._log_file(traceback.format_exc())
                self._js("App.onUpdate", {"blad": "Nie udało się zaktualizować: %s" % e})

        threading.Thread(target=run, daemon=True).start()
        return {"started": True}

    def copy_text(self, t):
        return set_clipboard(t or "")

    def open_ai(self, ktory, t):
        """Kopiuje polecenie do schowka i otwiera wybrany czat w przeglądarce. Adres tylko z listy AI_CHATS."""
        if ktory not in engine.AI_CHATS:
            return {"ok": False, "blad": "Nieznany czat."}
        nazwa, url, app = engine.AI_CHATS[ktory]
        skopiowano = bool(set_clipboard(t or ""))
        appid = engine.find_app(app)
        if appid:  # aplikacja na komputerze ma dostęp do plików, przeglądarka nie
            subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + appid])
        else:
            os.startfile(url)
        gdzie = "aplikacja" if appid else "przegladarka"
        engine._log_file("otwieram %s (%s, schowek: %s, %d znaków)" % (nazwa, gdzie, skopiowano, len(t or "")))
        return {"ok": True, "nazwa": nazwa, "klucz": ktory, "skopiowano": skopiowano, "gdzie": gdzie}

    # --- z Pythona do JS ------------------------------------------------------------------------------------------
    def _js(self, fn, arg):
        try:
            self._window.evaluate_js("%s(%s)" % (fn, json.dumps(arg, ensure_ascii=False)))
        except Exception:
            pass

    def _progress(self, step, opis, pct, eta):
        self._js("App.onProgress", {"krok": step, "opis": opis, "procent": pct, "eta_s": eta})

    def on_drop(self, e):
        files = (e.get("dataTransfer") or {}).get("files") or []
        path = next((f.get("pywebviewFullPath") for f in files if f.get("pywebviewFullPath")), None)
        if path:
            self._js("App.analyze", path)
        else:
            self._js("App.onError", "Nie udało się odczytać upuszczonego pliku - użyj przycisku „Wybierz folder”.")


def run():
    if os.environ.get("DK_DEBUG_PORT"):  # test automatyczny (WORK\logs\e2e_gui.py): Playwright łączy się przez CDP
        webview.settings["REMOTE_DEBUGGING_PORT"] = int(os.environ["DK_DEBUG_PORT"])
    api = Api()
    window = webview.create_window("Stwórz prezentację - Dobra Kaloria", url=os.path.join(paths.UI_DIR, "index.html"),
                                   js_api=api, width=1160, height=820, min_size=(980, 700), text_select=False,
                                   background_color="#FFFFFF")
    api._window = window  # PRYWATNE: pywebview przegląda publiczne pola API w głąb - publiczne 'window' wieszało start (29.09)

    def after_start(w):
        """Osobny wątek po starcie GUI (wzorzec z dokumentacji pywebview). Rejestracja w handlerze 'loaded'
        blokowała most JS<->Python na ~15 s (evaluate_js czeka na to samo zdarzenie 'loaded')."""
        w.events.loaded.wait()
        engine._log_file("okno załadowane po %.1f s od startu (wersja %s, %s)" % (time.time() - T0, paths.version(), paths.ROOT))
        try:
            el = w.dom.get_element("#dropzone")
            if el is not None:
                el.events.drop += api.on_drop
            engine._log_file("drop: zarejestrowano na #dropzone")
        except Exception:
            engine._log_file(traceback.format_exc())

    # Ekran powitalny zamykamy PRZED startem okna: trzymany dłużej (do 'loaded') blokował start WebView2 (29.09)
    engine._log_file("start: biblioteki wczytane po %.1f s, zamykam ekran powitalny i otwieram okno" % (time.time() - T0))

    webview.start(after_start, window, gui="edgechromium")  # tryb prywatny: każdy start ma własny, tymczasowy profil WebView2


if __name__ == "__main__":
    run()
