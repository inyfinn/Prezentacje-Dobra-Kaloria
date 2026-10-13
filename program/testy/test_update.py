# -*- coding: utf-8 -*-
"""Test logiki "co zrobic z szablonem" w skrypcie aktualizacji (update.PS_SZABLON): uruchamia prawdziwy PowerShell na
plikach tymczasowych.   python -m pytest -p no:cacheprovider WORK\\logs\\test_update.py -q"""
import hashlib
import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src", "app"))
import update  # noqa: E402

PS = shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PS, reason="brak PowerShella")
NAZWA = "DK - szablon prezentacji.pptx"
SKROT_1_2_0 = "3EFF7B42A42B0782ACA9D777DA2AF188A9112A3141D2A1A5B64A90853AE18349"


def _sha(b):
    return hashlib.sha256(b).hexdigest().upper()


def _uruchom(tmp_path, src_bytes, dst_bytes, stare):
    src, root = tmp_path / "src", tmp_path / "root"
    src.mkdir()
    root.mkdir()
    if src_bytes is not None:
        (src / NAZWA).write_bytes(src_bytes)
    if dst_bytes is not None:
        (root / NAZWA).write_bytes(dst_bytes)
    log = tmp_path / "log.txt"
    skrypt = tmp_path / "t.ps1"
    with open(skrypt, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write('param([string]$Src, [string]$Root, [string]$Log, [string]$Stare)\n'
                'function L($t) { $t | Out-File -LiteralPath $Log -Append -Encoding utf8 }\n'
                + update.PS_SZABLON + 'Wgraj-Szablon $Src $Root @($Stare -split ",")\n')
    r = subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(skrypt), "-Src", str(src), "-Root", str(root),
                        "-Log", str(log), "-Stare", ",".join(stare)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    wpisy = log.read_text(encoding="utf-8-sig").splitlines() if log.exists() else []
    dst = (root / NAZWA).read_bytes() if (root / NAZWA).exists() else None
    return dst, [w.strip() for w in wpisy]


def test_brak_pliku_wgrywa_nowy(tmp_path):
    dst, log = _uruchom(tmp_path, b"nowy", None, [])
    assert dst == b"nowy" and log == ["szablon wgrany (nie było pliku)"]


def test_niezmieniona_stara_wersja_jest_podmieniana(tmp_path):
    dst, log = _uruchom(tmp_path, b"nowy 7 slajdow", b"stary 65 slajdow", [_sha(b"stary 65 slajdow")])
    assert dst == b"nowy 7 slajdow" and log == ["szablon podmieniony (stara niezmieniona wersja)"]


def test_zmieniony_recznie_zostaje(tmp_path):
    dst, log = _uruchom(tmp_path, b"nowy", b"poprawiony przez Ole", [_sha(b"stary 65 slajdow")])
    assert dst == b"poprawiony przez Ole" and log == ["szablon zmieniony ręcznie - zostawiam"]


def test_ten_sam_plik_bez_zmian_nawet_gdy_nie_ma_go_na_liscie(tmp_path):
    dst, log = _uruchom(tmp_path, b"ten sam", b"ten sam", [])
    assert dst == b"ten sam" and log == ["szablon bez zmian"]


def test_brak_szablonu_w_wydaniu_nic_nie_robi(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    dst, log = _uruchom(tmp_path / "a", None, b"cokolwiek", [_sha(b"cokolwiek")])
    assert dst == b"cokolwiek" and log == []
    dst, log = _uruchom(tmp_path / "b", None, None, [])
    assert dst is None and log == []


def test_pusta_lista_starych_nigdy_nie_podmienia(tmp_path):
    dst, log = _uruchom(tmp_path, b"nowy", b"stary", [])
    assert dst == b"stary" and log == ["szablon zmieniony ręcznie - zostawiam"]


def test_skrypt_ma_znany_skrot_i_sie_parsuje(tmp_path):
    assert update.STARE_SZABLONY == (SKROT_1_2_0,)
    ps1 = update.skrypt_ps1()
    assert "@@STARE@@" not in ps1 and "Wgraj-Szablon $Src $Root @('%s')" % SKROT_1_2_0 in ps1
    assert "-not (Test-Path -LiteralPath (Join-Path $Root $t))" not in ps1       # stary warunek "tylko gdy nie ma pliku"
    plik = tmp_path / "zastosuj.ps1"
    with open(plik, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write(ps1)
    kod = ("$e = $null; [void][System.Management.Automation.Language.Parser]::ParseFile('%s', [ref]$null, [ref]$e); "
           "if ($e.Count) { $e | ForEach-Object { $_.Message }; exit 1 }" % str(plik).replace("'", "''"))
    r = subprocess.run([PS, "-NoProfile", "-Command", kod], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
