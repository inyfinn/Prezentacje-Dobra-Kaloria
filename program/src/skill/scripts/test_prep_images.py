"""cutout_dark działa bez scipy (program nie ma jej w paczce; do 1.2.2 grafiki na czarnym tle były pomijane)."""
import builtins
import os

import numpy as np
from PIL import Image

import prep_images


def test_cutout_dark_bez_scipy(tmp_path, monkeypatch):
    real_import = builtins.__import__

    def bez_scipy(name, *a, **k):
        if name == "scipy" or name.startswith("scipy."):
            raise ImportError("No module named 'scipy'")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", bez_scipy)
    a = np.zeros((200, 200, 3), np.uint8)
    a[50:150, 60:140] = (200, 120, 40)        # produkt
    a[90:110, 90:110] = (10, 10, 10)          # ciemne miejsce W ŚRODKU produktu ma zostać
    src, dst = tmp_path / "src.png", tmp_path / "dst.png"
    Image.fromarray(a).save(src)
    prep_images.cutout_dark(str(src), str(dst), max_side=1000)
    out = Image.open(dst)
    alpha = np.asarray(out.split()[-1])
    assert out.size[0] < 200 and out.size[1] < 200, "tło przycięte"
    assert alpha[alpha.shape[0] // 2, alpha.shape[1] // 2] > 200, "ciemny środek produktu nieprzezroczysty"
    assert alpha[0, 0] < 128 or out.size[0] <= 84, "róg = tło"
