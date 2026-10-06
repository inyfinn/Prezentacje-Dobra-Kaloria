# -*- coding: utf-8 -*-
"""Zrzuty wzorca 2.0 (preview/sklep.html) w obu jasnych stylach.

    python scripts/zrzuty_sklep.py     # preview/shots/70-sklep-<styl>.png (cała strona) i 71-sklep-<sekcja>.png
"""
import os
import pathlib

from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(BASE, "preview", "shots")


def main():
    url = pathlib.Path(BASE, "preview", "sklep.html").as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 900}, device_scale_factor=1)
        pg.on("pageerror", lambda e: print("BLAD JS:", e))
        pg.on("console", lambda m: m.type == "error" and print("KONSOLA:", m.text))
        pg.goto(url)
        pg.wait_for_selector("html[data-ready='1']", state="attached", timeout=8000)
        for theme, name in ((None, "sklep"), ("dobra-kaloria-krem-jasny", "krem-jasny")):
            if theme:
                pg.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
            path = os.path.join(SHOTS, "70-sklep-%s.png" % name)
            pg.screenshot(path=path, full_page=True)
            print(path)
        pg.evaluate("document.documentElement.removeAttribute('data-theme')")
        for sec in ("s-poziomy", "s-koszyk", "s-kontrolki"):
            path = os.path.join(SHOTS, "71-sklep-%s.png" % sec[2:])
            pg.query_selector("#" + sec).screenshot(path=path)
            print(path)
        b.close()


if __name__ == "__main__":
    main()
