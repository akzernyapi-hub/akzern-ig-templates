#!/usr/bin/env python3
"""Şeffaf ürün PNG'lerinin boş kenarlarını kırpar (content bbox).
Böylece şablonda bottom-align ile ürün podyuma tam oturur. Kullanım: python3 trim.py a.png b.png ..."""
from PIL import Image
import sys
for path in sys.argv[1:]:
    im = Image.open(path).convert("RGBA")
    bbox = im.split()[3].getbbox()  # alfa kanalının doluluk sınırı
    if bbox:
        im.crop(bbox).save(path)
        print(f"✓ trim {path} -> {im.crop(bbox).size}")
    else:
        print(f"! bbox yok: {path}")
