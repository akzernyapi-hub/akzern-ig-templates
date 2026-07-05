#!/usr/bin/env python3
"""AKZERN — KİLİTLİ şablon zeminlerine (assets/sablon/*) onaylı-form ürünleri
İRİ + grounded yerleştirir. Şablonlar sabit; ürün AI ile üretilir, buraya oturur."""
import sys, json, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets"); SB = os.path.join(A, "sablon")

def prep(path, w):
    im = Image.open(path).convert("RGBA"); bb = im.split()[3].getbbox()
    if bb: im = im.crop(bb)
    knob = (im.width/im.height) > 0.85
    return im.resize((w, int(w/(im.width/im.height)))), knob

def place(bg, im, cx, ty, knob, sink=18):
    W,H = bg.size
    if not knob: im = im.rotate(-5, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(sh).ellipse([cx-im.width//3, ty-12, cx+im.width//3, ty+16], fill=(25,18,10,150))
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    bg.alpha_composite(im, (cx-im.width//2, ty-im.height+sink))

# TEK PODYUM (ic, kampanya): (cx, ust_y, urun_genislik)
SINGLE = (560, 1150, 270)
# 5'Lİ KÜME (kapak-kollar, kapak-kulp, marka) sabit slotlar: (cx, ust_y, genislik, sink)
COVER_SLOTS = [(300,845,185,14),(700,940,175,14),(150,995,165,14),(830,1010,175,14),(470,1085,178,14)]

def inner(slug, out, bgname="ic.png"):
    bg = Image.open(f"{SB}/{bgname}").convert("RGBA").resize((1080,1350))
    cx,ty,w = SINGLE
    im,knob = prep(f"{A}/cut/{slug}.png", w)
    place(bg, im, cx, ty, knob, sink=22)
    bg.convert("RGB").save(out)

def cover(slugs, out, bgname="kapak-kollar.png"):
    bg = Image.open(f"{SB}/{bgname}").convert("RGBA").resize((1080,1350))
    for i in sorted(range(len(slugs)), key=lambda i: COVER_SLOTS[i][1]):
        cx,ty,w,sink = COVER_SLOTS[i]
        im,knob = prep(f"{A}/cut/{slugs[i]}.png", w)
        place(bg, im, cx, ty, knob, sink=sink)
    bg.convert("RGB").save(out)

if __name__ == "__main__":
    slugs = json.loads(sys.argv[1])
    tip = sys.argv[2] if len(sys.argv) > 2 else "carousel"
    if tip == "lifestyle":
        pass  # lifestyle AI-sahne (Action sahne_url indirir), kompoze kullanmaz
    else:
        cover(slugs, f"{A}/kapak-hero.png")
        os.makedirs(f"{A}/ic", exist_ok=True)
        for sl in slugs: inner(sl, f"{A}/ic/{sl}.png")
        print("kompoze ok (kilitli sablon):", slugs)
