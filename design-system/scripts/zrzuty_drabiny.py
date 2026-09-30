# -*- coding: utf-8 -*-
"""Zrzuty drabiny i tagów z preview/drabina.html (headless Chromium, Playwright dla Pythona).

    python scripts/zrzuty_drabiny.py      # zapisuje preview/shots/50-drabina-<wariant>.png i 51-tagi.png

Strona otwierana z dysku (file://) - bez serwera HTTP.
"""
import os
import pathlib

from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(BASE, "preview", "shots")


def main():
    os.makedirs(SHOTS, exist_ok=True)
    url = pathlib.Path(BASE, "preview", "drabina.html").as_uri()
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 900}, device_scale_factor=1)
        pg.on("pageerror", lambda e: print("BLAD JS:", e))
        pg.goto(url)
        pg.wait_for_selector("html[data-ready='1']", state="attached", timeout=8000)
        pg.evaluate("document.fonts.ready")
        for sec in pg.query_selector_all("section.variant"):
            name = sec.get_attribute("data-theme").replace("dobra-kaloria-", "").replace("dobra-kaloria", "program")
            path = os.path.join(SHOTS, "50-drabina-%s.png" % name)
            sec.screenshot(path=path)
            out.append(path)
        path = os.path.join(SHOTS, "51-tagi.png")
        pg.screenshot(path=path, full_page=True)
        out.append(path)
        b.close()
    print("\n".join(out))


if __name__ == "__main__":
    main()
