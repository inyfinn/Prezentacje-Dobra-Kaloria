# -*- coding: utf-8 -*-
"""Generuje instrukcje dla AI (CLAUDE.md, AGENTS.md, PROMPT BEZ PROGRAMU.md, GEMINI.md, GROK.md) z jednej treści.

    python generuj.py

Wspólna treść: tresc.md. Kod Drogi B: dk_szablon.py. Katalog slajdów: WORK\\skill-prezentacje\\assets\\katalog-szablonu.json.
Wynik: instrukcje (md) w WORK, paczka dla AI (zip) na wierzchu folderu programu (od 1.3).
Różnice między agentami (kim jest, gdzie skill) są w AGENCI niżej. Program odsyła do „AGENTS.md sekcja 3b” -
nie zmieniaj numeru tej sekcji.
"""
import json
import os
import re
import shutil

TU = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(TU)         # WORK: tu leżą instrukcje dla AI, skill-prezentacje, pliki programu
ROOT = os.path.dirname(WORK)       # folder programu „— SZABLON AI - skrypt” (wierzch: tu ląduje paczka zip)

M365 = ("\nNa końcu raportu przypomnij użytkownikowi: „Masz Claude na komputerze? Otwórz plik w PowerPoincie i użyj "
        "wtyczki Claude (Claude for Microsoft 365) - wklej to samo polecenie, poprawi slajdy od razu w pliku.”\n")


def krok0(katalog, nazwa, cel_opcja):
    ps = katalog.replace("%USERPROFILE%", "$env:USERPROFILE")
    instal = ('uruchom `& "<folder programu>\\WORK\\zainstaluj-skill.cmd"%s` (albo skopiuj folder `<folder programu>\\WORK\\skill-prezentacje\\` '
              'w to miejsce). Skrypt niczego nie kasuje — istniejącą wersję przenosi do `…\\skills\\_poprzednie\\`.'
              % (' -Cel "%s"' % ps if cel_opcja else ""))
    return ("Sprawdź, czy masz skill: `%s\\SKILL.md` (%s; PowerShell: `Test-Path \"%s\\SKILL.md\"`).\n\n"
            "- **Nie ma albo brakuje w nim `references\\dopracowanie.md`:** %s Sprawdź jeszcze raz.\n"
            "- **Potem** wczytaj skill `/prezentacje` (`SKILL.md` sekcje 0 i 1b, `references\\dopracowanie.md`, "
            "`references\\lekcje.md`). Skill zainstalowany w trakcie rozmowy może nie być widoczny — czytaj wtedy te pliki "
            "prosto z katalogu (bez restartu).\n"
            "- **Brak mechanizmu skilli albo dostępu do profilu** (czat, piaskownica): nic nie instaluj — czytaj "
            "`<folder programu>\\WORK\\skill-prezentacje\\SKILL.md` i `references\\` prosto z folderu programu."
            % (katalog, nazwa, katalog.replace("%USERPROFILE%", "$env:USERPROFILE"), instal))


AGENCI = {
    "CLAUDE.md": dict(
        agent="Claude (Claude Code, Claude Desktop, Cowork, claude.ai)",
        kim="Jesteś Claude — pracujesz w Claude Code, Claude Desktop (Cowork), w rozmowie na claude.ai albo we wtyczce PowerPointa.",
        krok0=krok0("%USERPROFILE%\\.claude\\skills\\prezentacje", "Claude Code", False), m365=True),
    "AGENTS.md": dict(
        agent="AI (ChatGPT / Codex, Claude, Gemini, Cursor, Antigravity…)",
        kim="Jesteś asystentem AI (ChatGPT, Codex, Claude, Gemini, Cursor, Antigravity…).",
        krok0=krok0("<katalog skilli Twojego agenta>\\prezentacje", "Claude Code: `%USERPROFILE%\\.claude\\skills`, Codex: "
                    "`%USERPROFILE%\\.codex\\skills`, Gemini: `%USERPROFILE%\\.gemini\\skills`, Cursor: "
                    "`%USERPROFILE%\\.cursor\\skills`", True), m365=True),
    "PROMPT BEZ PROGRAMU.md": dict(
        agent="AI",
        kim="",
        krok0=krok0("<katalog skilli Twojego agenta>\\prezentacje", "Claude Code: `%USERPROFILE%\\.claude\\skills`, Codex: "
                    "`%USERPROFILE%\\.codex\\skills`, Gemini: `%USERPROFILE%\\.gemini\\skills`, Cursor: "
                    "`%USERPROFILE%\\.cursor\\skills`", True), m365=True),
    "GEMINI.md": dict(
        agent="Gemini (Gemini CLI, Antigravity, czat Gemini)",
        kim="Jesteś Gemini — pracujesz w Gemini CLI, w Antigravity albo w czacie.",
        krok0=krok0("%USERPROFILE%\\.gemini\\skills\\prezentacje", "Gemini CLI", True), m365=False),
    "GROK.md": dict(
        agent="Grok (Grok w Cursorze, czat Groka)",
        kim="Jesteś Grok — pracujesz w Cursorze albo w czacie Groka.",
        krok0=krok0("%USERPROFILE%\\.cursor\\skills\\prezentacje", "Cursor", True), m365=False),
}



def wariant(tekst, paczka):
    """<!--A-->…<!--/A--> zostaje tylko w plikach programu, <!--P-->…<!--/P--> tylko w prompcie z paczki."""
    usun, zostaw = ("A", "P") if paczka else ("P", "A")
    tekst = re.sub(r"<!--%s-->.*?<!--/%s-->" % (usun, usun), "", tekst, flags=re.S)
    return tekst.replace("<!--%s-->" % zostaw, "").replace("<!--/%s-->" % zostaw, "")


def katalog():
    with open(os.path.join(WORK, "skill-prezentacje", "assets", "katalog-szablonu.json"), encoding="utf8") as f:
        d = json.load(f)
    rows = ["| Nr | Slajd | Kiedy | Mieści |", "|---|---|---|---|"]
    for s in d["slajdy"]:
        if s["nr"] <= 2:
            continue
        rows.append("| %d | %s | %s | %s |" % (s["nr"], s["nazwa"], s["uzyj_gdy"].replace("|", "/"), s["miesci"].replace("|", "/")))
    return "\n".join(rows)


def main():
    tresc = open(os.path.join(TU, "tresc.md"), encoding="utf8").read()
    kod = open(os.path.join(TU, "dk_szablon.py"), encoding="utf8").read().rstrip()
    compile(kod, "dk_szablon.py", "exec")  # kod w instrukcji musi się kompilować
    kat = katalog()
    for plik, a in AGENCI.items():
        out = (wariant(tresc, plik == "PROMPT BEZ PROGRAMU.md").replace("{{AGENT}}", a["agent"]).replace("{{KIM}} ", a["kim"] + " " if a["kim"] else "").replace("{{KROK0}}", a["krok0"])
               .replace("{{M365}}", M365 if a["m365"] else "").replace("{{KOD}}", kod).replace("{{KATALOG}}", kat))
        reszta = re.findall(r"\{\{[A-Z0-9]+\}\}", out)
        assert not reszta, reszta
        assert "### 3b. " in out or plik == "PROMPT BEZ PROGRAMU.md"  # program odsyła do „AGENTS.md sekcja 3b”
        if plik == "PROMPT BEZ PROGRAMU.md":  # prompt z paczki mówi tylko o tym, co jest w paczce
            zle = [s for s in ("folder programu", "stworz-cli", "pliki programu", "skill-prezentacje", "render.ps1",
                               "verify.ps1", "G:\\", "M:\\", "D:\\Marketing", "Droga A") if s in out]
            assert not zle, zle
        with open(os.path.join(WORK, plik), "w", encoding="utf8", newline="\n") as f:
            f.write(out)
        print("%s: %d linii" % (plik, out.count("\n")))
    for inst in ("zainstaluj-skill.ps1", "zainstaluj-skill.cmd"):   # instalator skilla leży w WORK obok skill-prezentacje (kopia z tego folderu)
        shutil.copyfile(os.path.join(TU, inst), os.path.join(WORK, inst))
    paczka()


PACZKA = "DK - paczka prezentacji dla AI.zip"

POMIN_KAT = {".cache", ".pytest_cache", "examples", "__pycache__"}
# Lekka wersja skilla w paczce (czaty przyjmują pliki do 30 MB): bez ikon i paczek demo (32 MB) - w Drodze B
# ikony i paczki są w szablonie. Znacznik LEKKA chroni pełną instalację przed nadpisaniem (instalatory go sprawdzają).
POMIN_LEKKA = {"prezentacje": {"assets/icons", "assets/demo"}}
LEKKA = "PACZKA-LEKKA.txt"
LEKKA_TRESC = ("Lekka wersja skilla z paczki „DK - paczka prezentacji dla AI.zip” (21.10.2026): bez assets/icons i assets/demo,\n"
               "żeby zip zmieścił się w limicie 30 MB czatów. Wystarcza do pracy bez programu (Droga B) - ikony i paczki\n"
               "są w szablonie. Pełna wersja: folder programu „— SZABLON AI - skrypt\\WORK\\skill-prezentacje”.\n"
               "Instalator nie nadpisuje pełnej wersji lekką.\n")
LIMIT_MB = 28  # limit czatu 30 MB, z zapasem
NOTA_LEKKA = """

> **Wersja z paczki (bez programu, bez dysków firmy, także Linux / Mac / chmura).** Zacznij od sekcji **1c** i
> `references/bez-programu.md`, a całą pracę prowadź według `PROMPT BEZ PROGRAMU.md` z paczki (Droga B).
> Ścieżki `D:\\`, `M:\\`, `G:\\`, program „Stwórz prezentację” (`stworz-cli.exe`), `szybka.py`, `qa_all.ps1`, `verify.ps1`,
> `render.ps1` i `ikony` z `assets/icons` dotyczą komputera firmowego z Windows i programem — tu ich nie używasz.
> `ui-ux-pro-max` jest w paczce obok (`skille/ui-ux-pro-max`); `uidesigner` — tylko jeśli go masz.
"""


def _skill(zrodlo, nazwa):
    """Wpisy skilla do zipa jako skille/<nazwa>/: lista (nazwa w zipie, ścieżka albo bajty).
    Bez cache, przykładów, *.pyc i ciężkich zasobów lekkiej wersji."""
    assert os.path.isfile(os.path.join(zrodlo, "SKILL.md")), zrodlo
    pomin = POMIN_LEKKA.get(nazwa, set())
    wpisy = []
    if pomin:
        wpisy.append(("skille/%s/%s" % (nazwa, LEKKA), LEKKA_TRESC.encode("utf-8")))
    for dp, dn, fn in os.walk(zrodlo):
        rel = os.path.relpath(dp, zrodlo).replace("\\", "/")
        if pomin and rel == "." and "SKILL.md" in fn:  # lekka wersja: SKILL.md z notą na start (Droga B, bez Windows)
            fn = [f for f in fn if f != "SKILL.md"]
            t = open(os.path.join(dp, "SKILL.md"), encoding="utf8").read()
            k = t.index("\n---", 3) + 4  # koniec frontmattera
            wpisy.append(("skille/%s/SKILL.md" % nazwa, (t[:k] + NOTA_LEKKA + t[k:]).encode("utf-8")))
        dn[:] = sorted(d for d in dn if d not in POMIN_KAT and (d if rel == "." else rel + "/" + d) not in pomin)
        for f in sorted(fn):
            if not f.endswith(".pyc"):
                pelna = os.path.join(dp, f)
                wpisy.append(("skille/%s/%s" % (nazwa, os.path.relpath(pelna, zrodlo).replace("\\", "/")), pelna))
    return wpisy


def paczka():
    """Zip do wysłania osobie bez dysków firmy: README, instrukcja, szablon, czcionki, kod Drogi B, instalatory, skille.
    Kolejność w zipie = kolejność ważności: agent, który widzi tylko początek listy, i tak zobaczy README i oba skille."""
    import zipfile

    sk = os.path.join(os.path.expanduser("~"), ".claude", "skills")  # źródło prawdy skilli (build.ps1 kopiuje stąd)
    fonty = os.path.join(sk, "prezentacje", "assets", "fonts")
    pliki = [(os.path.join(WORK, "PROMPT BEZ PROGRAMU.md"), "PROMPT BEZ PROGRAMU.md"),
             (os.path.join(WORK, "pliki programu", "DK - szablon prezentacji - pełen.pptx"), "DK - szablon prezentacji - pełen.pptx"),
             (os.path.join(TU, "dk_szablon.py"), "dk_szablon.py"),
             (os.path.join(TU, "zainstaluj-skill.ps1"), "zainstaluj-skill.ps1"),
             (os.path.join(TU, "zainstaluj-skill.cmd"), "zainstaluj-skill.cmd"),
             (os.path.join(TU, "zainstaluj-skille.sh"), "zainstaluj-skille.sh")]
    pliki += [(os.path.join(fonty, f), "fonty/" + f) for f in ("Mindset.otf", "MindsetSlim.otf", "Lato-Regular.ttf", "Lato-Bold.ttf")]
    brak = [p for p, _ in pliki if not os.path.isfile(p)]
    assert not brak, brak
    uiux = _skill(os.path.join(sk, "ui-ux-pro-max"), "ui-ux-pro-max")
    prez = _skill(os.path.join(sk, "prezentacje"), "prezentacje")
    # SKILL.md obu skilli tuż po plikach głównych - widać je nawet w uciętej liście
    glowne = [w for w in uiux + prez if w[0].endswith("/SKILL.md") and w[0].count("/") == 2]
    reszta = [w for w in uiux + prez if w not in glowne]
    razem = 1 + len(pliki) + len(uiux) + len(prez)
    readme = (open(os.path.join(TU, "README-paczki.md"), encoding="utf8").read()
              .replace("{{N_RAZEM}}", str(razem)).replace("{{N_UIUX}}", str(len(uiux))).replace("{{N_PREZ}}", str(len(prez))))
    assert "{{" not in readme
    cel = os.path.join(ROOT, PACZKA)
    with zipfile.ZipFile(cel, "w", zipfile.ZIP_DEFLATED) as z:  # polskie nazwy: zipfile sam ustawia flagę UTF-8
        z.writestr("README.md", readme.encode("utf-8"))  # pierwszy plik, który czyta agent i człowiek
        for p, w in pliki:
            z.write(p, w)
        for w, zr in glowne + reszta:
            if isinstance(zr, bytes):
                z.writestr(w, zr)
            else:
                z.write(zr, w)
    with zipfile.ZipFile(cel) as z:
        assert len(z.namelist()) == razem, (len(z.namelist()), razem)
    mb = os.path.getsize(cel) / 2 ** 20
    print("%s: %d plików (ui-ux-pro-max %d, prezentacje %d), %.1f MB" % (PACZKA, razem, len(uiux), len(prez), mb))
    assert mb < LIMIT_MB, "paczka %.1f MB - czaty przyjmują najwyżej 30 MB" % mb


if __name__ == "__main__":
    main()
