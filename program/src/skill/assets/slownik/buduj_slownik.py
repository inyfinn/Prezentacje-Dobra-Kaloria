# -*- coding: utf-8 -*-
"""Buduje pliki slownika dla lint_tekst.py (uruchamiane RAZ przez autora; program ich nie potrzebuje).

    python buduj_slownik.py <katalog z pl_PL.aff, pl_PL.dic, pl_full.txt, en_50k.txt> <katalog wyjsciowy>

Zrodla (patrz LICENCJA.txt):
  pl_PL.aff + pl_PL.dic  - slownik ortograficzny sjp.pl w wersji LibreOffice (Apache 2.0 / GPL / LGPL / MPL / CC BY-SA)
  pl_full.txt, en_50k.txt - listy frekwencyjne z napisow OpenSubtitles 2018 (hermitdave/FrequencyWords, CC BY-SA 4.0)
Wynik:
  czeste.xz  - tekst UTF-8, trzy sekcje rozdzielone pusta linia: najczestsze formy slownikowe (od najczestszej);
               slowa spoza slownika czeste w napisach (obce, potoczne); najczestsze slowa angielskie, ktorych nie ma
               w polskim slowniku (lint nie bierze ich za literowki)
  forms.bloom - filtr Blooma ze WSZYSTKIMI formami slownika (po rozwinieciu przyrostkow); bledy filtra (ok. 9 %) dzialaja
               tylko w strone "slowo uznane za poprawne" = pominiecie, nie falszywy alarm
"""
import hashlib
import lzma
import os
import re
import sys

TOP_SLOWNIK = 150000      # ile najczestszych form slownikowych trzymamy dokladnie
TOP_ANGIELSKIE = 30000
MIN_OBCE = 20             # slowa spoza slownika: minimum wystapien w napisach
BLOOM_BITS = 16_000_000
BLOOM_K = 4
LITERY = re.compile(r"^[a-ząćęłńóśźż]+$")


def rozwin(aff_path, dic_path):
    aff = open(aff_path, encoding="iso-8859-2").read().splitlines()
    sfx, pfx = {}, {}
    i = 0
    while i < len(aff):
        p = aff[i].split()
        if p and p[0] in ("SFX", "PFX") and len(p) == 4 and p[2] in "YN":
            n, rules = int(p[3]), []
            for l in aff[i + 1:i + 1 + n]:
                q = l.split()
                strip = "" if q[2] == "0" else q[2]
                add = "" if q[3] == "0" else q[3]
                cond = q[4] if len(q) > 4 else "."
                rx = re.compile(("^.*" + cond + "$") if p[0] == "SFX" else ("^" + cond + ".*$"))
                rules.append((strip, add, rx))
            (sfx if p[0] == "SFX" else pfx)[p[1]] = (p[2] == "Y", rules)
            i += n
        i += 1
    out = set()
    for l in open(dic_path, encoding="iso-8859-2").read().splitlines()[1:]:
        w, _, fl = l.partition("/")
        w = w.lower()
        out.add(w)
        formy = []
        for f in fl:
            if f in sfx:
                for strip, add, rx in sfx[f][1]:
                    if rx.match(w) and w.endswith(strip):
                        formy.append(w[:len(w) - len(strip)] + add)
        out.update(formy)
        for f in fl:
            if f in pfx:
                for strip, add, rx in pfx[f][1]:
                    if rx.match(w):
                        out.add(add + w[len(strip):])
                        if pfx[f][0]:
                            out.update(add + x[len(strip):] for x in formy)
    return out


def hasze(w, m):
    d = hashlib.blake2b(w.encode("utf-8"), digest_size=16).digest()
    return int.from_bytes(d[:8], "little") % m, (int.from_bytes(d[8:], "little") | 1) % m or 1


def main(src, dst):
    formy = rozwin(os.path.join(src, "pl_PL.aff"), os.path.join(src, "pl_PL.dic"))
    # przedrostek "nie-" lint sprawdza w locie: formy z nie- nie wchodza do filtra
    formy = {w for w in formy if LITERY.match(w) and not (w.startswith("nie") and w[3:] in formy)}
    freq = []
    for l in open(os.path.join(src, "pl_full.txt"), encoding="utf-8"):
        w, _, c = l.rpartition(" ")
        freq.append((w, int(c)))
    freq.sort(key=lambda x: -x[1])
    slownik = [w for w, c in freq if w in formy and c >= 3][:TOP_SLOWNIK]
    obce = [w for w, c in freq if c >= MIN_OBCE and w not in formy and LITERY.match(w) and len(w) >= 2]
    pl = set(slownik) | set(obce)
    ang = []
    for l in open(os.path.join(src, "en_50k.txt"), encoding="utf-8"):
        w = l.split(" ")[0]
        if LITERY.match(w) and len(w) >= 3 and w not in formy and w not in pl:
            ang.append(w)
    ang = ang[:TOP_ANGIELSKIE]
    with lzma.open(os.path.join(dst, "czeste.xz"), "wt", encoding="utf-8", preset=9 | lzma.PRESET_EXTREME) as f:
        f.write("\n".join(slownik) + "\n\n" + "\n".join(obce) + "\n\n" + "\n".join(ang) + "\n")
    bits = bytearray(BLOOM_BITS // 8 + 1)
    for w in formy:
        h1, h2 = hasze(w, BLOOM_BITS)
        for i in range(BLOOM_K):
            b = (h1 + i * h2) % BLOOM_BITS
            bits[b >> 3] |= 1 << (b & 7)
    with open(os.path.join(dst, "forms.bloom"), "wb") as f:
        f.write(BLOOM_BITS.to_bytes(4, "little") + bytes([BLOOM_K]) + bytes(bits))
    print("formy", len(formy), "slownik", len(slownik), "obce", len(obce), "angielskie", len(ang))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
