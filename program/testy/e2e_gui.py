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
a = ap.parse_args()
OUT = os.path.join(HERE, "e2e-shots")
os.makedirs(OUT, exist_ok=True)
env = dict(os.environ, DK_DEBUG_PORT="9333")
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
        print("opcje OK")
        if a.styl == "stary":
            el = page.query_selector("text=Stary styl")
            if el:
                el.click()
        page.click("#btn-build")
        t0 = time.time()
        last = ""
        while time.time() - t0 < 240:
            txt = page.evaluate("document.body.innerText")
            if "GOTOWE" in txt.upper() and "Otwórz prezentację" in txt:
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
        print("zrzuty:", OUT)
finally:
    proc.kill()
    # plik startowy uruchamia osobny proces program.exe - samo proc.kill() zostawiało otwarte okno (29.09)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process -Name program -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '%s\\*' } | "
                    "Stop-Process -Force -Confirm:$false" % os.path.dirname(a.exe).replace("'", "''")])
