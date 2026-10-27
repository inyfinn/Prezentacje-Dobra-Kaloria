# -*- coding: utf-8 -*-
"""Wejście programu (program.exe, uruchamiany przez Prezentacje.exe; na macOS plik w .app): bez argumentów = okno;
z folderem/argumentami = wiersz poleceń (dla AI)."""
import os
import sys


def main():
    args = sys.argv[1:]
    if args and (args[0].startswith("-") or os.path.exists(args[0].strip('"'))):
        import cli
        sys.exit(cli.main(args))
    import gui
    gui.run()


if __name__ == "__main__":
    main()
