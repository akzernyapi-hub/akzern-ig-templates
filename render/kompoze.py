#!/usr/bin/env python3
"""AKZERN — şeffaf TEK-KOL kesimlerinden kapak + iç hero'ları kompoze eder.
AYNI kesim hem kapakta (5'i podyum sırasında) hem iç sayfada kullanılır
=> kapaktaki ürün ile iç sayfadaki ürün BİREBİR AYNI (sapma yok)."""
import sys, json, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")

def plate_cx(im):
    """kesimin alt %7'sindeki opak piksellerin x-merkezi = plaka merkezi (hizalama)"""
    a = im.split()[3]; px = a.load(); w, h = im.size; xs = []
    for y in range(int(h*0.93), h):
        for x in range(w):
            if px[x, y] > 40: xs.append(x)
    return (min(xs)+max(xs))//2 if xs else w//2

# kapak podyum zemini (kapak-podyum.png = row-b) üzerindeki 5 sabit slot: (cx, taban_y, yükseklik)
COVER_SLOTS = [(135,802,320),(330,838,315),(540,778,345),(730,835,315),(925,802,320)]

def cover(slugs, out):
    bg = Image.open(f"{A}/kapak-podyum.png").convert("RGBA").resize((1080,1350))
    sh = Image.new("RGBA", bg.size, (0,0,0,0)); sd = ImageDraw.Draw(sh)
    for (cx,by,h) in COVER_SLOTS:
        sd.ellipse([cx-52,by-11,cx+52,by+11], fill=(40,32,24,110))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    order = sorted(range(len(slugs)), key=lambda i: COVER_SLOTS[i][1])  # arka->ön
    for i in order:
        cx,by,h = COVER_SLOTS[i]
        im = Image.open(f"{A}/cut/{slugs[i]}.png").convert("RGBA")
        w = int(im.width*h/im.height); im = im.resize((w,h)); pcx = plate_cx(im)
        bg.alpha_composite(im, (cx-pcx, by-h+8))
    bg.convert("RGB").save(out)

def inner(slug, out):
    bg = Image.open(f"{A}/pod-bg.png").convert("RGBA").resize((1080,1350))
    cx, by = 540, 892
    im = Image.open(f"{A}/cut/{slug}.png").convert("RGBA")
    h = 500; w = int(im.width*h/im.height); im = im.resize((w,h)); pcx = plate_cx(im)
    ts = Image.new("RGBA", bg.size, (0,0,0,0))
    ImageDraw.Draw(ts).ellipse([cx-72,by-13,cx+72,by+13], fill=(40,32,24,110))
    bg.alpha_composite(ts.filter(ImageFilter.GaussianBlur(8)))
    bg.alpha_composite(im, (cx-pcx, by-h+8))
    bg.convert("RGB").save(out)

if __name__ == "__main__":
    slugs = json.loads(sys.argv[1])            # ["kristal","lotus-siyah","noyan","lama","anka"]
    cover(slugs, f"{A}/kapak-hero.png")
    os.makedirs(f"{A}/ic", exist_ok=True)
    for s in slugs:
        inner(s, f"{A}/ic/{s}.png")
    print("kompoze ok:", slugs)
