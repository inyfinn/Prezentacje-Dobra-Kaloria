# -*- coding: utf-8 -*-
"""Samoaktualizacja z najnowszego wydania na GitHubie (repo publiczne, bez haseł).

Przebieg: check() -> użytkownik klika "Zaktualizuj" -> download() pobiera zip do folderu użytkownika, sprawdza
rozmiar i sumę SHA-256 (gdy GitHub ją podaje), rozpakowuje -> apply() uruchamia mały skrypt, który czeka na
zamknięcie programu, kopiuje nowe pliki NA stare (bez kasowania czegokolwiek) i uruchamia program ponownie.

Program stojący na dysku sieciowym (wspólny folder, wielu użytkowników naraz) nie aktualizuje się sam -
tam nową wersję wgrywa opiekun (WORK\\wydaj.ps1).
"""
import hashlib
import json
import os
import re
import subprocess
import urllib.request
import zipfile

import paths
import platforma

REPO = "inyfinn/Prezentacje-Dobra-Kaloria"
API = "https://api.github.com/repos/%s/releases/latest" % REPO
HOSTS = ("https://github.com/", "https://api.github.com/", "https://objects.githubusercontent.com/",
         "https://release-assets.githubusercontent.com/")
STRONA_MAC = "https://github.com/%s" % REPO     # macOS: nowa wersja z tej strony (program nie podmienia swoich plików)
UPD_DIR = os.path.join(paths.USER_DIR, "aktualizacja")
LAUNCHER = "Stwórz prezentację.exe"
CREATE_NO_WINDOW = 0x08000000
# bez DETACHED_PROCESS: PowerShell bez konsoli kończył się od razu (test 29.09, brak wpisu w logu)
DETACHED = 0x00000200 | CREATE_NO_WINDOW


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or "")[:3]) or (0,)


def _get(url, timeout=8):
    if not url.startswith(HOSTS):
        raise ValueError("niedozwolony adres: " + url)
    req = urllib.request.Request(url, headers={"User-Agent": "Stworz-prezentacje/" + paths.version(),
                                               "Accept": "application/vnd.github+json"})
    return urllib.request.urlopen(req, timeout=timeout)


def can_self_update():
    """Tylko program spakowany, na dysku lokalnym, w folderze z prawem zapisu. macOS: nigdy (nowa wersja = pobranie ze strony)."""
    if platforma.mac():
        return False, "na Macu nową wersję pobierasz ręcznie ze strony %s" % STRONA_MAC
    if not paths.FROZEN:
        return False, "wersja deweloperska"
    if not platforma.dysk_lokalny(paths.ROOT):  # Windows: GetDriveTypeW == 3 (dysk stały)
        return False, "program stoi na dysku wspólnym"
    probe = os.path.join(paths.ROOT, "pliki programu", "~zapis.tmp")
    try:
        open(probe, "w").close()
        os.remove(probe)
    except OSError:
        return False, "brak prawa zapisu w folderze programu"
    return True, ""


def check():
    """{'jest': bool, 'wersja', 'obecna', 'url', 'rozmiar', 'sha256', 'sam': bool, 'powod'}; błąd sieci = jest False."""
    out = {"jest": False, "obecna": paths.version()}
    try:
        with _get(API) as r:
            rel = json.loads(r.read().decode("utf8"))
        tag = rel.get("tag_name", "")
        zips = [a for a in rel.get("assets", []) if a.get("name", "").lower().endswith(".zip")
                and "windows" in a.get("name", "").lower()]
        if platforma.mac():     # wydanie na GitHubie ma tylko paczkę Windows: dla Maca liczy się sam numer wersji, nic się nie pobiera
            if vtuple(tag) <= vtuple(out["obecna"]):
                return out
            out.update(jest=True, wersja=tag.lstrip("v"), sam=False, powod=can_self_update()[1], mac=True, strona=STRONA_MAC)
            return out
        if not zips or vtuple(tag) <= vtuple(out["obecna"]):
            return out
        a = zips[0]
        sam, powod = can_self_update()
        dig = a.get("digest") or ""
        out.update(jest=True, wersja=tag.lstrip("v"), url=a["browser_download_url"], rozmiar=int(a.get("size") or 0),
                   sha256=dig.split(":", 1)[1] if dig.startswith("sha256:") else "", sam=sam, powod=powod,
                   strona=rel.get("html_url", ""))
    except Exception as e:  # brak internetu, limit zapytań - program działa dalej bez aktualizacji
        out["blad"] = "%s: %s" % (type(e).__name__, e)
    return out


def download(info, progress=None):
    """Pobiera i rozpakowuje wydanie. Zwraca folder z rozpakowanym programem."""
    os.makedirs(UPD_DIR, exist_ok=True)
    ver = re.sub(r"[^0-9.]", "", info["wersja"])
    zp = os.path.join(UPD_DIR, "%s.zip" % ver)
    h = hashlib.sha256()
    got = 0
    with _get(info["url"], timeout=30) as r, open(zp, "wb") as f:
        while True:
            chunk = r.read(262144)
            if not chunk:
                break
            f.write(chunk)
            h.update(chunk)
            got += len(chunk)
            if progress and info.get("rozmiar"):
                progress(min(95, int(got * 95 / info["rozmiar"])))
    if info.get("rozmiar") and got != info["rozmiar"]:
        raise IOError("pobrano %d B, powinno być %d B" % (got, info["rozmiar"]))
    if info.get("sha256") and h.hexdigest().lower() != info["sha256"].lower():
        raise IOError("suma kontrolna pliku się nie zgadza")
    dst = os.path.join(UPD_DIR, ver)
    os.makedirs(dst, exist_ok=True)
    base = os.path.realpath(dst)
    with zipfile.ZipFile(zp) as z:
        for m in z.infolist():
            name = m.filename
            try:  # zip z Windows bez flagi UTF-8 zapisuje polskie litery w cp437
                if not m.flag_bits & 0x800:
                    name = name.encode("cp437").decode("utf8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
            target = os.path.realpath(os.path.join(dst, name))
            if not (target == base or target.startswith(base + os.sep)):
                raise IOError("niebezpieczna ścieżka w archiwum: " + m.filename)
            if m.is_dir():
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(m) as src, open(target, "wb") as out:
                while True:
                    chunk = src.read(262144)
                    if not chunk:
                        break
                    out.write(chunk)
    for need in (LAUNCHER, os.path.join("pliki programu", "program.exe"), os.path.join("pliki programu", "wersja.txt")):
        if not os.path.isfile(os.path.join(dst, need)):
            raise IOError("w wydaniu brakuje pliku: " + need)
    if progress:
        progress(100)
    return dst


# SHA-256 znanych STARYCH wydań "DK - szablon prezentacji.pptx" (wielkie litery). Plik o takim skrócie nie był ruszany ręcznie,
# więc aktualizacja może go podmienić nowym; inny skrót = poprawiany ręcznie, zostaje nietknięty.
STARE_SZABLONY = (
    "3EFF7B42A42B0782ACA9D777DA2AF188A9112A3141D2A1A5B64A90853AE18349",  # szablon 65 slajdów z 07.10.2026 (wydanie 1.2.0)
)

# Wybór, co zrobić z szablonem; wydzielone, żeby dało się je przetestować (WORK\logs\test_update.py). Zakłada funkcję L (log).
PS_SZABLON = r"""function Wgraj-Szablon($Src, $Root, $Stare) {
    $t = "DK - szablon prezentacji.pptx"
    $s = Join-Path $Src $t
    $d = Join-Path $Root $t
    if (-not (Test-Path -LiteralPath $s)) { return }
    if (-not (Test-Path -LiteralPath $d)) { Copy-Item -LiteralPath $s -Destination $d; L "szablon wgrany (nie było pliku)"; return }
    $h = (Get-FileHash -LiteralPath $d -Algorithm SHA256).Hash.ToUpper()
    if ($h -eq (Get-FileHash -LiteralPath $s -Algorithm SHA256).Hash.ToUpper()) { L "szablon bez zmian"; return }
    if (@($Stare) -contains $h) { Copy-Item -LiteralPath $s -Destination $d -Force; L "szablon podmieniony (stara niezmieniona wersja)" }
    else { L "szablon zmieniony ręcznie - zostawiam" }
}
"""

PS1 = r"""param([string]$Src, [string]$Root, [int]$ProcId, [string]$Log)
# Aktualizacja programu "Stwórz prezentację": kopiuje nowe pliki na stare. Nie kasuje; nadpisuje tylko znane, niezmienione stare wersje.
function L($t) { ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $t) | Out-File -LiteralPath $Log -Append -Encoding utf8 }
""" + PS_SZABLON + r"""L "start: $Src -> $Root (czekam na proces $ProcId)"
foreach ($p in @($Src, $Root)) { if (-not $p -or -not (Test-Path -LiteralPath $p -PathType Container)) { L "BLAD brak folderu: $p"; exit 2 } }
if (-not (Test-Path -LiteralPath (Join-Path $Root "pliki programu\program.exe"))) { L "BLAD to nie jest folder programu: $Root"; exit 2 }
for ($i = 0; $i -lt 120; $i++) {
    $run = @(Get-Process -Name "program", "Stwórz prezentację" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$Root\*" })
    if ($run.Count -eq 0) { break }
    Start-Sleep -Milliseconds 500
}
if ($run.Count -gt 0) { L "BLAD program nadal działa - przerywam"; exit 3 }
robocopy (Join-Path $Src "pliki programu") (Join-Path $Root "pliki programu") /E /R:5 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
$rc = $LASTEXITCODE
L "robocopy kod $rc"
if ($rc -ge 8) { L "BLAD kopiowania"; exit 4 }
# kopie skilli dla AI obok programu: bez nich polecenie dla AI wskazywałoby starą metodę (kopia bez kasowania)
foreach ($d in "skill-prezentacje", "skill-ds-dobra-kaloria") {
    $sd = Join-Path $Src $d
    if (Test-Path -LiteralPath $sd -PathType Container) {
        robocopy $sd (Join-Path $Root $d) /E /R:5 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
        L ("skill " + $d + " - robocopy kod " + $LASTEXITCODE)
    }
}
foreach ($f in "Stwórz prezentację.exe", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "GROK.md", "zainstaluj-skill.ps1", "zainstaluj-skill.cmd", "CZYTAJ - jak zrobić prezentację.txt") {
    $s = Join-Path $Src $f
    if (Test-Path -LiteralPath $s) { Copy-Item -LiteralPath $s -Destination (Join-Path $Root $f) -Force }
}
# szablon PPTX mógł być poprawiany ręcznie: wgrywamy go, gdy go nie ma ALBO gdy to niezmieniona stara wersja (skrót z listy)
Wgraj-Szablon $Src $Root @(@@STARE@@)
L ("gotowe, wersja " + (Get-Content -LiteralPath (Join-Path $Root "pliki programu\wersja.txt") -Raw).Trim())
Start-Process -FilePath (Join-Path $Root "Stwórz prezentację.exe")
"""


def skrypt_ps1():
    """Skrypt podmiany z wstawioną listą skrótów starych wydań szablonu."""
    return PS1.replace("@@STARE@@", ", ".join("'%s'" % h.upper() for h in STARE_SZABLONY))


def apply(src):
    """Uruchamia skrypt podmiany w tle. Po powrocie program ma się zamknąć."""
    ok, why = can_self_update()
    if not ok:
        raise RuntimeError(why)
    os.makedirs(paths.LOG_DIR, exist_ok=True)
    ps = os.path.join(UPD_DIR, "zastosuj.ps1")
    with open(ps, "w", encoding="utf-8-sig", newline="\r\n") as f:  # BOM: PowerShell 5.1 inaczej psuje polskie litery
        f.write(skrypt_ps1())
    subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", ps,
                      "-Src", src, "-Root", paths.ROOT, "-ProcId", str(os.getpid()),
                      "-Log", os.path.join(paths.LOG_DIR, "aktualizacja.log")],
                     creationflags=DETACHED, close_fds=True, cwd=UPD_DIR,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True
