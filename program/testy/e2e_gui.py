# -*- coding: utf-8 -*-
"""Test end-to-end SPAKOWANEGO programu: uruchamia "Stwórz prezentację.exe" z portem CDP, przez Playwright
przeklikuje prawdziwe okno (WebView2): analiza folderu TEST -> ustawienia -> Stwórz -> Gotowe, zrzuty każdego ekranu.
    python e2e_gui.py [--exe <ścieżka exe>] [--folder <folder produktu>]
"""
import argparse
import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ap = argparse.ArgumentParser()
ap.add_argument("--exe", default=os.path.join(ROOT, "Stwórz prezentację.exe"))
ap.add_argument("--folder", default=r"D:\Marketing\- POLSKA\02 - FIRMOWE MATERIAŁY\PREZENTACJE\24.09.2026 - KULKI z kreatyną TEST")
ap.add_argument("--styl", default="nowy")
ap.add_argument("--ai", action="store_true", help="kliknij też Claude / ChatGPT / Gemini (otwiera je na ekranie)")
a = ap.parse_args()
OUT = os.path.join(HERE, "e2e-shots")
os.makedirs(OUT, exist_ok=True)
env = dict(os.environ, DK_DEBUG_PORT="9333")
busy = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process -Name program -ErrorAction SilentlyContinue | Measure-Object).Count"],
                      capture_output=True, text=True).stdout.strip()
if busy not in ("", "0"):  # port debugowania trafiłby w stare okno i test oceniałby nie ten program
    sys.exit("Najpierw zamknij otwarte okna programu (%s)" % busy)
proc = subprocess.Popen([a.exe], env=env)
print("exe pid", proc.pid, "->", a.exe)
try:
    with sync_playwright() as pw:
        browser = None
        for _ in range(120):  # czekaj na okno (start z dysku sieciowego może trwać)
            try:
                browser = pw.chromium.connect_over_cdp("http://127.0.0.1:9333")
                break
            except Exception:
                time.sleep(1)
        assert browser, "brak połączenia CDP - okno nie wstało?"
        page = browser.contexts[0].pages[0]
        page.wait_for_function("window.pywebview && window.pywebview.api && typeof window.pywebview.api.analyze === 'function' && window.App",
                               timeout=180000)
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUT, "1-start.png"))
        print("start OK:", page.title(), "|", page.url)
        print("logo:", page.evaluate("(() => { const i = document.querySelector('img.logo'); return i ? i.naturalWidth : 'brak'; })()"),
              "| fonty:", page.evaluate("[...document.fonts].map(f => f.family + ':' + f.status).join(', ')"))
        page.evaluate("p => App.analyze(p)", a.folder)
        page.wait_for_selector("body[data-screen='opcje']", timeout=180000)
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUT, "2-opcje.png"), full_page=True)
        print("opcje OK | paczki:", page.evaluate("[...document.querySelectorAll('.flav')].map(f => f.innerText.split('\\n')[0] + '=' + (f.querySelector('img') ? f.querySelector('img').getAttribute('alt') || 'obraz' : 'brak')).join(', ')"),
              "| pasek:", page.evaluate("document.querySelector('#bar-count').textContent"))
        # slajd z szablonu (grupa Cytaty) - sprawdza drogę "do uzupełnienia" w prawdziwym programie
        page.click(".grp[data-id='cytaty'] > summary")
        page.click(".sec[data-id='t20'] .switch")
        print("dodano cytat z szablonu | pasek:", page.evaluate("document.querySelector('#bar-count').textContent"))
        if a.styl == "stary":
            el = page.query_selector("text=Stary styl")
            if el:
                el.click()
        page.click("#btn-build")
        t0 = time.time()
        last = ""

        def document_screen(pg):
            return pg.evaluate("document.body.dataset.screen")

        while time.time() - t0 < 240:
            txt = page.evaluate("document.body.innerText")
            # od 1.1.5 przyciski główne są wersalikami (CSS), a innerText zwraca tekst tak, jak go widać - porównanie bez wielkości liter
            if document_screen(page) == "wynik" and "OTWÓRZ PREZENTACJĘ" in txt.upper():
                break
            cur = [l for l in txt.splitlines() if "%" in l or "jeszcze" in l][:2]
            if cur != last:
                print("  ", " | ".join(cur))
                last = cur
                page.screenshot(path=os.path.join(OUT, "3-praca.png"))
            if "Nie udało się" in txt:
                page.screenshot(path=os.path.join(OUT, "3-blad.png"))
                raise SystemExit("BŁĄD w oknie: " + txt[:500])
            time.sleep(1.5)
        else:
            page.screenshot(path=os.path.join(OUT, "3-timeout.png"))
            raise SystemExit("timeout")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(OUT, "4-wynik.png"), full_page=True)
        txt = page.evaluate("document.body.innerText")
        print("WYNIK:", " | ".join(l for l in txt.splitlines() if l.strip())[:600])
        # kliknięcie w PRAWDZIWYM oknie: kopiowanie polecenia dla AI (lekcja 29.09: schowek wywalał się tylko w exe)
        page.screenshot(path=os.path.join(OUT, "4-wynik-okno.png"))
        page.click("#btn-copy-ai")
        time.sleep(1.5)
        toasts = page.evaluate("[...document.querySelectorAll('.toast')].map(t => t.className + ': ' + t.innerText.trim())")
        guide = page.evaluate("(() => { const g = document.querySelector('#guide'); return g && !g.hidden ? g.innerText.replace(/\\s+/g, ' ').trim() : ''; })()")
        print("KOPIUJ -> instrukcja:", guide[:160], "| komunikaty:", toasts)
        page.screenshot(path=os.path.join(OUT, "5-kopiuj.png"))
        if not guide or any("error" in t for t in toasts):
            raise SystemExit("BLAD kopiowania do schowka")
        if a.ai:  # prawdziwe kliknięcie: otwiera aplikacje / przeglądarkę na ekranie użytkownika
            logp = os.path.join(os.environ["LOCALAPPDATA"], "Dobra Kaloria", "Stworz prezentacje", "logi", "ostatni.log")
            for key in ("claude", "chatgpt", "gemini"):
                page.keyboard.press("Escape")
                n0 = len(open(logp, encoding="utf8").read().splitlines())
                page.click("[data-ai='%s']" % key)
                time.sleep(3)
                title = page.evaluate("document.querySelector('#guide-title').textContent")
                step2 = page.evaluate("document.querySelector('#guide-s2-t').textContent")
                new = [l for l in open(logp, encoding="utf8").read().splitlines()[n0:] if "otwieram" in l]
                print("AI %s -> okno: %s | krok 2: %s | log: %s" % (key, title, step2, new[-1][9:] if new else "BRAK"))
                page.screenshot(path=os.path.join(OUT, "6-ai-%s.png" % key))
            page.keyboard.press("Escape")
        print("zrzuty:", OUT)
finally:
    proc.kill()
    # plik startowy uruchamia osobny proces program.exe - samo proc.kill() zostawiało otwarte okno (29.09)
    # realpath: ścieżka z TEMP bywa krótka (KRZYSZ~1.WIE), a proces zgłasza długą - bez tego okno zostawało (30.09)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process -Name program -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '%s\\*' } | "
                    "Stop-Process -Force -Confirm:$false" % os.path.dirname(os.path.realpath(a.exe)).replace("'", "''")])
