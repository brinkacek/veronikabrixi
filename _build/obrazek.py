#!/usr/bin/env python3
"""Připraví obrázky k článku blogu ve všech potřebných velikostech.

Použití (z kořene repozitáře):
    python3 _build/obrazek.py <slug-clanku> <cesta-k-puvodnimu-obrazku>

Vytvoří:
    img/blog/<slug>.jpg         – velký obrázek v článku (šířka max. 1600 px)
    img/blog/<slug>-sm.jpg      – náhled na kartě článku (900 × 600)
    img/og/blog-<slug>.jpg      – obrázek pro sdílení na sítích (1200 × 630)
Vyžaduje Pillow:  pip install pillow
"""
import os
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save(im, path, q=82):
    im.convert("RGB").save(path, "JPEG", quality=q, optimize=True, progressive=True)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    slug, src = sys.argv[1], sys.argv[2]
    im = ImageOps.exif_transpose(Image.open(src))
    big = im.copy()
    if big.width > 1600:
        big = big.resize((1600, round(big.height * 1600 / big.width)), Image.LANCZOS)
    save(big, os.path.join(ROOT, "img", "blog", f"{slug}.jpg"))
    save(ImageOps.fit(im, (900, 600)), os.path.join(ROOT, "img", "blog", f"{slug}-sm.jpg"))
    save(ImageOps.fit(im, (1200, 630)), os.path.join(ROOT, "img", "og", f"blog-{slug}.jpg"), q=85)
    print("Hotovo:", slug)


if __name__ == "__main__":
    main()
