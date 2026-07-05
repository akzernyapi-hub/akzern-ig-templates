#!/usr/bin/env python3
"""AKZERN — GERÇEK (arka planı silinmiş) ürün kesimlerinden kapak + iç hero.
AI çizmez => form BİREBİR gerçek, asla sapmaz. Kesim ortalanır (her ürün şekli için sağlam)."""
import sys, json, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
# kapak podyum sıra zemini slotları: (merkez_x, taban_y, yükseklik)
COVER_SLOTS = [(135,805,300),(330,840,290),(540,782,320),(730,840,290),(925,805,300)]

def fit(im, h):
    bb = im.split()[3].getbbox()
    if bb: im = im.crop(bb)
    w = int(im.width*h/im.height); return im.resize((w, h)), w

def cover(slugs, out):
    bg = Image.open(f"{A}/kapak-podyum.png").convert("RGBA").resize((1080,1350))
    sh = Image.new("RGBA", bg.size, (0,0,0,0)); sd = ImageDraw.Draw(sh)
    for (cx,by,h) in COVER_SLOTS: sd.ellipse([cx-56,by-12,cx+56,by+12], fill=(40,32,24,105))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    for i in sorted(range(len(slugs)), key=lambda i: COVER_SLOTS[i][1]):
        cx,by,h = COVER_SLOTS[i]
        im,w = fit(Image.open(f"{A}/cut/{slugs[i]}.png").convert("RGBA"), h)
        bg.alpha_composite(im, (cx-w//2, by-h+10))
    bg.convert("RGB").save(out)

def inner(slug, out):
    bg = Image.open(f"{A}/pod-bg.png").convert("RGBA").resize((1080,1350))
    cx, by = 540, 910
    im,w = fit(Image.open(f"{A}/cut/{slug}.png").convert("RGBA"), 450)
    ts = Image.new("RGBA", bg.size, (0,0,0,0))
    ImageDraw.Draw(ts).ellipse([cx-150,by-22,cx+150,by+22], fill=(40,32,24,115))
    bg.alpha_composite(ts.filter(ImageFilter.GaussianBlur(12)))
    bg.alpha_composite(im, (cx-w//2, by-450+18))
    bg.convert("RGB").save(out)


def lifestyle(slug, out):
    bg = Image.open(f"{A}/lifestyle-sahne.png").convert("RGBA").resize((1080,1350))
    cx, by = 560, 952
    im, w = fit(Image.open(f"{A}/cut/{slug}.png").convert("RGBA"), 300)
    ts = Image.new("RGBA", bg.size, (0,0,0,0))
    ImageDraw.Draw(ts).ellipse([cx-85,by-13,cx+85,by+13], fill=(25,18,10,150))
    bg.alpha_composite(ts.filter(ImageFilter.GaussianBlur(11)))
    bg.alpha_composite(im, (cx-w//2, by-300+6))
    bg.convert("RGB").save(out)

if __name__ == "__main__":
    slugs = json.loads(sys.argv[1])
    tip = sys.argv[2] if len(sys.argv) > 2 else "carousel"
    if tip == "lifestyle":
        os.makedirs(f"{A}/lc", exist_ok=True)
        for sl in slugs: lifestyle(sl, f"{A}/lc/{sl}.png")
        print("kompoze lifestyle ok:", slugs)
    else:
        cover(slugs, f"{A}/kapak-hero.png")
        os.makedirs(f"{A}/ic", exist_ok=True)
        for sl in slugs: inner(sl, f"{A}/ic/{sl}.png")
        print("kompoze ok:", slugs)
