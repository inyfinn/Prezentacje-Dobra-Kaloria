# -*- coding: utf-8 -*-
"""Wejście "stworz-cli.exe" (wersja konsolowa w "pliki programu" - dla AI i skryptów)."""
import sys

import cli

if __name__ == "__main__":
    sys.exit(cli.main(sys.argv[1:]))
