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
import folder_prez  # noqa: E402
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


def get_clipboard():
    """Tekst ze schowka (CF_UNICODETEXT) albo None. Tylko odczyt: niczego nie zmienia ani nie czyści. Gdy schowek jest chwilowo
    zajęty przez inny program - None (okno zapyta za sekundę); tekst ponad 1 MB pomijamy."""
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
        if not h or k32.GlobalSize(h) > (1 << 20):
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


def _korzen_dysku(d):
    """Korzeń dysku (np. cały dysk D:) nie jest „folderem, w którym był plik” - nie otwieramy go."""
    d = os.path.abspath(d)
    return os.path.dirname(d) == d


class Api:
    def __init__(self):
        self._window = None
        self.folder = None
        self._pliki = []        # pełne ścieżki plików z ostatniej analizy pakietu (kopiowane do Źródeł w create_folder)
        self._limit = None      # limit slajdów z ostatniego polecenia dla AI (suwak) - do kontroli scenariusza
        self._cancel = threading.Event()

    # --- wywołania z JS ---------------------------------------------------------------------------------------
    def get_info(self):
        engine._log_file("most JS<->Python gotowy po %.1f s od startu" % (time.time() - T0))
        return {"wersja": paths.version(), "powerpoint": engine.powerpoint_available(), "szablony": ["nowy", "stary"],
                "root": paths.ROOT}

    def _start_dir(self):
        """Katalog startowy okien wyboru: ostatni folder (przy konwersji - folder pliku .pptx)."""
        f = self.folder or ""
        return os.path.dirname(f) if os.path.isfile(f) else f

    def pick_folder(self):
        r = self._window.create_file_dialog(webview.FileDialog.FOLDER, directory=self._start_dir())
        return r[0] if r else None

    def pick_file(self):
        """Plik, z którego powstanie prezentacja: gotowa prezentacja do przełożenia na styl DK (.pptx, .ppsx) albo dokument
        (.docx, .doc, .rtf, .odt, .pdf, .txt, .md - lista z silnika). Zwraca ścieżkę pliku albo None."""
        wzorce = ["*.pptx", "*.ppsx"] + ["*" + e for e in engine.dok_ext()]
        r = self._window.create_file_dialog(webview.FileDialog.OPEN, directory=self._start_dir(), allow_multiple=False,
                                            file_types=("Prezentacje i dokumenty (%s)" % ";".join(wzorce), "Wszystkie pliki (*.*)"))
        return r[0] if r else None

    pick_pptx = pick_file   # stara nazwa (mock, testy)

    def pick_files(self):
        """Wybór JEDNEGO ALBO WIELU plików do nowej prezentacji: dokumenty, prezentacje, obrazy i zrzuty. Lista ścieżek albo None."""
        wzorce = ["*.pptx", "*.ppsx"] + ["*" + e for e in engine.dok_ext()] + ["*" + e for e in folder_prez.OBRAZ_EXT]
        r = self._window.create_file_dialog(webview.FileDialog.OPEN, directory=self._start_dir(), allow_multiple=True,
                                            file_types=("Dokumenty, prezentacje i obrazy (%s)" % ";".join(wzorce), "Wszystkie pliki (*.*)"))
        return list(r) if r else None

    def pick_parent(self):
        """Wybór folderu, w którym powstanie folder prezentacji (baza). Ścieżka albo None."""
        baza = folder_prez.baza_domyslna()[0]
        r = self._window.create_file_dialog(webview.FileDialog.FOLDER, directory=baza if os.path.isdir(baza) else "")
        return r[0] if r else None

    def analyze(self, path):
        try:
            t = time.time()
            res = engine.analyze(path)
            engine._log_file("analiza: %.1f s (%s)" % (time.time() - t, res.get("plik") or res["folder"]))
            self.folder = res.get("plik") or res["folder"]  # konwersja i dokument: ścieżką jest plik
            self._last_est = res["szacowany_czas_s"]
            return res
        except Exception as e:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "blad": engine.komunikat_bledu(e, engine.BLAD_PLIKU)}   # nigdy surowy wyjątek w oknie

    def analyze_many(self, paths):
        """Analiza listy ścieżek (upuszczonych albo wybranych): jeden folder produktu / .pptx / folder prezentacji = jak `analyze` (+ "tryb");
        inne pliki = "tryb": "pakiet" z propozycją folderu prezentacji (folder powstaje dopiero w create_folder)."""
        try:
            t = time.time()
            res = engine.analyze_many(paths)
            engine._log_file("analiza (%d): %.1f s (%s)" % (len(paths or []), time.time() - t, res.get("tryb")))
            self._pliki = [x["sciezka"] for x in res.get("pliki") or [] if x.get("sciezka")] if res.get("tryb") == "pakiet" else []
            if res.get("tryb") == "pakiet" and not res.get("istnieje"):
                self.folder = None     # folderu jeszcze nie ma: budowa wymaga create_folder
            else:
                self.folder = res.get("plik") or res["folder"]    # konwersja i dokument: ścieżką jest plik; folder prezentacji: folder
            self._last_est = res["szacowany_czas_s"]
            return res
        except Exception as e:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "blad": engine.komunikat_bledu(e, engine.BLAD_PLIKU)}   # nigdy surowy wyjątek w oknie

    def create_folder(self, opts):
        """Tworzy folder prezentacji i KOPIUJE do niego pliki (Źródła). opts: {"baza", "nazwa", "pliki" (ścieżki albo wiersze z analizy;
        domyślnie pliki z ostatniej analizy)}. Zajęta nazwa dostaje „ (2)”. Zapamiętuje bazę. {"ok", "folder", "zrodla", "skopiowano", "blad"}."""
        opts = opts or {}
        try:
            baza = str(opts.get("baza") or folder_prez.baza_domyslna()[0])
            nazwa = folder_prez.oczysc_tytul(opts.get("nazwa") or "", 80)
            pliki = [x.get("sciezka") if isinstance(x, dict) else x for x in (opts.get("pliki") or self._pliki)]
            pliki = [p for p in pliki if p]
            if not os.path.isabs(baza):
                return {"ok": False, "folder": None, "zrodla": None, "blad": "Wskaż folder, w którym ma powstać prezentacja."}
            if not pliki:
                return {"ok": False, "folder": None, "zrodla": None, "blad": "Nie ma plików do skopiowania - wybierz je jeszcze raz."}
            folder, kopie = folder_prez.utworz_folder(baza, nazwa, pliki)
        except FileNotFoundError as e:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "folder": None, "zrodla": None,
                    "blad": "Nie znajduję pliku „%s” - został przeniesiony albo usunięty. Wybierz pliki jeszcze raz." % os.path.basename(str(e.filename or e))}
        except OSError:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "folder": None, "zrodla": None,
                    "blad": "Nie mogę utworzyć folderu w tym miejscu (brak dostępu albo dysk niedostępny). Wybierz inną lokalizację przez »Zmień…«."}
        folder_prez.zapisz_ustawienie("baza_prezentacji", baza)
        engine.zapisz_polecenie(folder)
        self.folder = folder
        engine._log_file("folder prezentacji: %s (skopiowano %d plików)" % (folder, len(kopie)))
        return {"ok": True, "folder": folder, "zrodla": os.path.join(folder, folder_prez.ZRODLA),
                "skopiowano": [os.path.basename(p) for p in kopie], "blad": ""}

    def build(self, opts):
        if not self.folder:
            return {"started": False, "blad": "Najpierw utwórz folder prezentacji." if self._pliki else "Najpierw wskaż folder."}
        self._cancel.clear()
        opts = dict(opts or {})
        opts.setdefault("szacowany_czas_s", getattr(self, "_last_est", 40))

        def run():
            res = engine.safe_build(self.folder, opts, progress=self._progress, log=lambda t: self._js("App.onLog", t),
                                    cancel=self._cancel)
            if res.get("ok"):
                self._js("App.onDone", res)
            else:
                if res.get("traceback"):   # szczegóły techniczne tylko w „Pokaż szczegóły” i w logu, nie w komunikacie
                    self._js("App.onLog", res["traceback"])
                self._js("App.onError", res.get("blad") or engine.BLAD_TWORZENIA)

        threading.Thread(target=run, daemon=True).start()
        return {"started": True}

    def cancel(self):
        self._cancel.set()
        return True

    def open_path(self, p):
        """Otwiera plik prezentacji. Zwraca {"ok": bool, "komunikat": zdanie dla człowieka lub ""}: przeniesiony albo
        usunięty plik nie kończy się surowym wyjątkiem, tylko zdaniem i (gdy się da) otwarciem folderu, w którym był."""
        p = str(p or "")
        if os.path.exists(p):
            try:
                os.startfile(p)
                return {"ok": True, "komunikat": ""}
            except OSError:
                engine._log_file(traceback.format_exc())
                return {"ok": False, "komunikat": "Nie mogę otworzyć tego pliku. Otwórz go ręcznie z folderu z prezentacją."}
        return self._brak_pliku(p, "pliku prezentacji")

    def open_folder(self, p):
        """Pokazuje folder (albo zaznacza plik w jego folderze). Zwraca {"ok", "komunikat"} jak open_path."""
        p = str(p or "")
        try:
            if os.path.isfile(p):
                subprocess.Popen(["explorer", "/select,", p])
                return {"ok": True, "komunikat": ""}
            if os.path.isdir(p):
                os.startfile(p)
                return {"ok": True, "komunikat": ""}
        except OSError:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "komunikat": "Nie mogę otworzyć folderu. Otwórz go ręcznie w Eksploratorze."}
        return self._brak_pliku(p, "pliku prezentacji" if p.lower().endswith((".pptx", ".ppsx", ".potx", ".pptm")) else "folderu z prezentacją")

    def _brak_pliku(self, p, co):
        """Brak pliku / folderu (przeniesiony albo usunięty): zdanie po ludzku i, gdy istnieje folder, w którym był (bezpośredni
        nadrzędny, nie korzeń dysku), jego otwarcie. Nie szukamy wyżej: wyższy folder to nie „folder, w którym był”."""
        d = os.path.dirname(p.rstrip(chr(92) + "/"))
        if d and os.path.isdir(d) and not _korzen_dysku(d):
            try:
                os.startfile(d)
                return {"ok": True, "komunikat": "Nie znajduję %s - został przeniesiony albo usunięty. Otwieram folder, w którym był." % co}
            except OSError:
                engine._log_file(traceback.format_exc())
        return {"ok": False, "komunikat": "Nie znajduję %s - został przeniesiony albo usunięty. Zrób prezentację jeszcze raz." % co}

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
            except Exception:
                engine._log_file(traceback.format_exc())
                self._js("App.onUpdate", {"blad": "Nie udało się zaktualizować programu. Spróbuj jeszcze raz za chwilę albo poproś "
                                                  "opiekuna programu o nową wersję."})

        threading.Thread(target=run, daemon=True).start()
        return {"started": True}

    def copy_text(self, t):
        return set_clipboard(t or "")

    def open_ai(self, ktory, t):
        """Kopiuje polecenie do schowka i otwiera wybrany czat w przeglądarce. Adres tylko z listy AI_CHATS."""
        if ktory not in engine.AI_CHATS:
            return {"ok": False, "blad": "Nieznany czat."}
        return self._otworz_czat(ktory, t)

    def _otworz_czat(self, ktory, t):
        nazwa, url, app = engine.AI_CHATS[ktory]
        skopiowano = bool(set_clipboard(t or ""))
        appid = engine.find_app(app)
        try:
            if appid:  # aplikacja na komputerze ma dostęp do plików, przeglądarka nie
                subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + appid])
            else:
                os.startfile(engine.adres_czatu(ktory, url, t))
        except OSError:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "blad": "Nie udało się otworzyć czatu %s. Otwórz go ręcznie%s." % (
                nazwa, " - polecenie jest już skopiowane, wystarczy wkleić" if skopiowano else "")}
        gdzie = "aplikacja" if appid else "przegladarka"
        engine._log_file("otwieram %s (%s, schowek: %s, %d znaków)" % (nazwa, gdzie, skopiowano, len(t or "")))
        return {"ok": True, "nazwa": nazwa, "klucz": ktory, "skopiowano": skopiowano, "gdzie": gdzie}

    # --- folder prezentacji: polecenia dla AI i scenariusz ---------------------------------------------------------
    def ai_targets(self):
        """[{"id", "nazwa", "dostepny", "ostatni"}]: Claude, ChatGPT, Gemini i (gdy `claude` jest w PATH) Claude Code; "ostatni" = zapamiętany wybór."""
        return engine.ai_cele()

    def prepare_ai(self, ktory, opts=None):
        """Polecenie „źródła -> scenariusz” do schowka + otwarcie czatu (albo Claude Code w folderze). opts: {"slajdy": N}.
        {"ok", "nazwa", "gdzie", "skopiowano", "blad", ...}."""
        return self._ai(ktory, opts, False)

    def improve_ai(self, ktory, opts=None):
        """Jak prepare_ai, ale polecenie poprawki scenariusza po budowie (uwagi i plansze z ostatniego raportu); bez scenariusza - jak prepare_ai."""
        return self._ai(ktory, opts, True)

    def _ai(self, ktory, opts, poprawka):
        try:
            opts = opts or {}
            folder = self.folder
            if not folder or not folder_prez.czy_folder_prezentacji(folder):
                return {"ok": False, "blad": "Najpierw utwórz folder prezentacji."}
            cele = {c["id"]: c for c in engine.ai_cele()}
            if ktory not in cele:
                return {"ok": False, "blad": "Nieznany czat."}
            p = (engine.polecenie_poprawki_ai(folder, opts.get("slajdy")) if poprawka else None) or \
                engine.polecenie_przygotowania_ai(folder, opts.get("slajdy"))
            self._limit = p["slajdy"]
            folder_prez.zapisz_ustawienie("ostatni_ai", ktory)
            engine.zapisz_polecenie(folder)    # POLECENIE.md w folderze: Claude Code i inni agenci czytają je z dysku
            self._prep_t = time.time()   # od tej chwili nowy scenariusz zapisany w folderze przez agenta = odpowiedź (peek_clipboard)
            if ktory in ("claude_cowork", "claude_code") and not (ktory == "claude_code" and engine.uruchom_claude_code(folder)):
                # aplikacja Claude Desktop: nowa sesja Cowork / Code z krótkim poleceniem i folderem; pełne polecenie zostaje w schowku
                skopiowano = bool(set_clipboard(p["tekst"]))
                rodzaj = "cowork" if ktory == "claude_cowork" else "code"
                try:
                    os.startfile(engine.adres_claude(rodzaj, engine.POLECENIE_CLAUDE_CODE, folder))
                except OSError:
                    engine._log_file(traceback.format_exc())
                    return {"ok": False, "blad": "Nie udało się otworzyć aplikacji Claude. Otwórz ją ręcznie%s." % (
                        " - polecenie jest w schowku, wystarczy wkleić" if skopiowano else "")}
                res = {"ok": True, "nazwa": "Claude " + ("Cowork" if rodzaj == "cowork" else "Code"), "klucz": ktory,
                       "skopiowano": skopiowano, "gdzie": "aplikacja"}
                engine.zapisz_polecenie(folder)
                return dict(res, blad="", zalaczniki=[], uwagi=p["uwagi"], slajdy=p["slajdy"], katalog=p["katalog"], folder=True)
            if ktory == "claude_code":
                res = {"ok": True, "nazwa": "Claude Code", "klucz": ktory, "skopiowano": False, "gdzie": "terminal"}
            else:
                res = self._otworz_czat(ktory, p["tekst"])
                if not res.get("ok"):
                    return res
            if p["do_zalaczenia"] and os.path.isdir(p["katalog"]):    # obrazy, zrzuty i PDF-y czat dostaje od użytkownika
                try:
                    os.startfile(p["katalog"])
                except OSError:
                    engine._log_file(traceback.format_exc())
            res.update(blad="", zalaczniki=p["do_zalaczenia"], uwagi=p["uwagi"], slajdy=p["slajdy"], katalog=p["katalog"])
            return res
        except Exception as e:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "blad": engine.komunikat_bledu(e, engine.BLAD_TWORZENIA)}

    def peek_clipboard(self):
        """Scenariusz ze schowka albo None: tylko tekst, który po białych znakach (i ewentualnym ```markdown) zaczyna się od „# SCENARIUSZ DK”.
        Niczego nie zapisuje do schowka (polecenie, które sam tam wstawiłem, tak się nie zaczyna)."""
        try:
            t = get_clipboard()
            if folder_prez.wyglada_na_scenariusz(t):
                return engine.scenariusz_modul().wyciagnij(t)
            # agent z dostępem do folderu (Claude Cowork / Code) zapisał scenariusz sam: plik nowszy niż otwarcie czatu, nie ruszany od 3 s
            od = getattr(self, "_prep_t", None)
            if od and self.folder and os.path.isdir(self.folder):
                sc, _nr = folder_prez.najnowszy_scenariusz(self.folder)
                if sc and od < os.path.getmtime(sc) < time.time() - 3:
                    with open(sc, encoding="utf-8-sig") as f:
                        md = engine.scenariusz_modul().wyciagnij(f.read())
                    if md:
                        self._prep_t = None    # raz; kolejny zapis agenta wykryje się po kolejnym otwarciu czatu
                        return md
            return None
        except Exception:
            engine._log_file(traceback.format_exc())
            return None

    def save_scenario(self, text):
        """Odpowiedź czatu -> sprawdzenie -> nowa wersja scenariusza w folderze prezentacji. {"ok", "plik", "slajdy", "uwagi", "blad"}."""
        if not self.folder or not folder_prez.czy_folder_prezentacji(self.folder):
            return {"ok": False, "plik": None, "slajdy": 0, "uwagi": [], "blad": "Najpierw utwórz folder prezentacji."}
        try:
            res = engine.zapisz_scenariusz(self.folder, text or "", self._limit)
        except Exception as e:
            engine._log_file(traceback.format_exc())
            return {"ok": False, "plik": None, "slajdy": 0, "uwagi": [], "blad": engine.komunikat_bledu(e, engine.BLAD_TWORZENIA)}
        if res.get("ok"):
            self._last_est = res["szacowany_czas_s"]
            engine._log_file("scenariusz zapisany: %s (%d slajdów)" % (res["plik"], res["slajdy"]))
        return res

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
        sciezki = [f.get("pywebviewFullPath") for f in files if f.get("pywebviewFullPath")]
        if sciezki:
            self._js("App.analyzeMany", sciezki)    # zawsze lista (jeden plik = lista z jednym elementem)
        else:
            self._js("App.onError", "Nie udało się odczytać upuszczonego pliku - użyj przycisku „Wybierz folder”.")


WIN_W, WIN_H = 1160, 820        # docelowy rozmiar okna (piksele logiczne), gdy ekran pozwala
MIN_W, MIN_H = 980, 700


def _work_area():
    """Obszar roboczy monitora z kursorem (ekran bez paska zadań) w pikselach LOGICZNYCH: (x, y, szer, wys, skala).
    pywebview mnoży szerokość/wysokość/x/y przez skalę DPI okna (winforms.py: Size = initial_width * _scale,
    Location = initial_x * _scale; skala = GetDpiForWindow/96 = systemowy DPI, bo proces jest 'system DPI aware'),
    więc tu liczymy to samo: piksele fizyczne / skala systemowa. Wyjątek = błąd wykrycia (wywołujący wraca do 1160x820)."""
    from ctypes import wintypes
    u32 = ctypes.windll.user32
    u32.SetProcessDPIAware()  # to samo wywołuje pywebview przy starcie; bez tego rcWork bywa już przeskalowany
    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT), ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]
    pt = wintypes.POINT()
    u32.GetCursorPos(ctypes.byref(pt))
    u32.MonitorFromPoint.restype = ctypes.c_void_p
    u32.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
    hmon = u32.MonitorFromPoint(pt, 1)  # MONITOR_DEFAULTTOPRIMARY
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    u32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
    if not u32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
        raise OSError("GetMonitorInfoW")
    scale = u32.GetDpiForSystem() / 96.0
    rc = mi.rcWork
    return (rc.left / scale, rc.top / scale, int((rc.right - rc.left) / scale), int((rc.bottom - rc.top) / scale), scale)


def _window_geometry():
    """(x, y, szer, wys, min_szer, min_wys) w pikselach logicznych: nigdy większe niż obszar roboczy, wyśrodkowane.
    DK_TEST_WORKAREA=1366x720 podmienia wymiary obszaru (test małych ekranów); błąd wykrycia = stare 1160x820."""
    try:
        x, y, ww, wh, scale = _work_area()
        zrodlo = "wykryty"
        t = os.environ.get("DK_TEST_WORKAREA", "")
        if t:
            ww, wh = [int(v) for v in t.lower().split("x")]
            zrodlo = "wymuszony DK_TEST_WORKAREA"
        w, h = min(WIN_W, ww), min(WIN_H, wh)
        px, py = int(x + (ww - w) / 2), int(y + (wh - h) / 2)
        engine._log_file("okno: obszar roboczy %dx%d od (%d,%d) [%s], skala %.2f, rozmiar okna %dx%d, pozycja (%d,%d)"
                         % (ww, wh, x, y, zrodlo, scale, w, h, px, py))
        return px, py, w, h, min(MIN_W, w), min(MIN_H, h)
    except Exception:
        engine._log_file("okno: nie wykryto obszaru roboczego, zostaje %dx%d\n%s" % (WIN_W, WIN_H, traceback.format_exc()))
        return None, None, WIN_W, WIN_H, MIN_W, MIN_H


def run():
    if os.environ.get("DK_DEBUG_PORT"):  # test automatyczny (WORK\logs\e2e_gui.py): Playwright łączy się przez CDP
        webview.settings["REMOTE_DEBUGGING_PORT"] = int(os.environ["DK_DEBUG_PORT"])
    api = Api()
    gx, gy, gw, gh, gminw, gminh = _window_geometry()
    window = webview.create_window("Stwórz prezentację - Dobra Kaloria", url=os.path.join(paths.UI_DIR, "index.html"),
                                   js_api=api, width=gw, height=gh, x=gx, y=gy, min_size=(gminw, gminh), text_select=False,
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
    # Okno zamknięte = koniec programu. Zamknięcie przed załadowaniem strony zostawiało proces w tle (wątek czekał
    # na 'loaded', 30.09) - taki proces blokuje aktualizację i kolejne uruchomienia.
    engine._log_file("okno zamknięte po %.1f s - koniec programu" % (time.time() - T0))
    os._exit(0)


if __name__ == "__main__":
    run()
