#!/usr/bin/env python3
"""AKZERN — GERÇEK (arka planı silinmiş) ürün kesimlerinden kapak + iç hero.
AI çizmez => form BİREBİR gerçek, asla sapmaz. Kesim ortalanır (her ürün şekli için sağlam)."""
import sys, json, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
# kapak podyum sıra zemini slotları: (merkez_x, taban_y, yükseklik)
COVER_SLOTS = [(135,805,300),(330,840,290),(540,782,320),(730,840,290),(925,805,300)]

def fit(im, h):
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

if __name__ == "__main__":
    slugs = json.loads(sys.argv[1])
    cover(slugs, f"{A}/kapak-hero.png")
    os.makedirs(f"{A}/ic", exist_ok=True)
    for s in slugs: inner(s, f"{A}/ic/{s}.png")
    print("kompoze ok (gerçek kesim, ortalı):", slugs)
