# -*- coding: utf-8 -*-
"""Wejście "Stwórz prezentację.exe": bez argumentów = okno; z folderem/argumentami = wiersz poleceń (dla AI)."""
import os
import sys


def main():
    args = sys.argv[1:]
    if args and (args[0].startswith("-") or os.path.exists(args[0].strip('"'))):
        try:  # tryb wiersza poleceń: ekran powitalny niepotrzebny
            import pyi_splash
            pyi_splash.close()
        except Exception:
            pass
        import cli
        sys.exit(cli.main(args))
    import gui
    gui.run()


if __name__ == "__main__":
    main()
