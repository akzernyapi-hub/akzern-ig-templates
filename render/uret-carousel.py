#!/usr/bin/env python3
"""AKZERN — bir kategori carousel'ini CANLI Shopify verisinden üretir.
Girdi: products.json (Shopify'dan çekilen gerçek ürünler + şeffaf kesim yolu).
Çıktı: kapak (kopya) + N tek-ürün iç sayfa PNG.
Not: Shopify çekme ve Magnific removebg adımlarını Claude ajanı MCP ile yapar;
bu script fiyat biçimleme + render (sabit konum) adımını üstlenir."""
import json, subprocess, urllib.parse, os, http.server, socketserver, threading, functools, sys

import shutil
CHROME = os.environ.get("CHROME_BIN") or shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8791
TPL = "AKZERN Ic Sayfa KALITE.html"   # ürün podyumda oturan (Magnific hero) kaliteli yol

def server():
    try:
        import urllib.request; urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=1)
    except Exception:
        H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
        threading.Thread(target=socketserver.TCPServer(("", PORT), H).serve_forever, daemon=True).start()

def tr_fiyat(p):
    """'837.99' -> ('837', ',99') ; '1234.5' -> ('1.234', ',50')"""
    s = f"{float(p):.2f}"; intp, dec = s.split(".")
    return f"{int(intp):,}".replace(",", "."), "," + dec

def render(out, url):
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars","--no-sandbox",
        "--force-device-scale-factor=2","--window-size=1080,1350",f"--screenshot={out}",url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main(products_json, outdir, kapak):
    server(); os.makedirs(outdir, exist_ok=True)
    prods = json.load(open(products_json, encoding="utf-8"))
    subprocess.run(["cp", kapak, f"{outdir}/01.png"])
    base = f"http://localhost:{PORT}/{urllib.parse.quote(TPL)}"
    for i, pr in enumerate(prods, start=2):
        fiyat, kurus = tr_fiyat(pr["price"])
        f = {"hero":pr["hero"],"kategori":pr.get("kategori","Kapı Kolu · ODA"),
             "ad":pr["ad"],"olcu":pr["finish"],"fiyat":fiyat,"kurus":kurus,
             "sira":f"{i} / {len(prods)+1} ›","cip1":pr.get("cip1","1 Takım"),"cip2":pr.get("cip2","Vidalar Dahil")}
        ca = pr.get("compareAtPrice")
        if ca and float(ca) > float(pr["price"]):
            ei, ek = tr_fiyat(ca)
            f["eskifiyat"] = "₺"+ei+ek
            f["indirim"] = "%"+str(round((1-float(pr["price"])/float(ca))*100))
        else:
            f["eskifiyat"] = ""; f["indirim"] = ""   # indirim yoksa blok gizlenir
        url = base + "?" + urllib.parse.urlencode(f)
        render(f"{outdir}/{i:02d}.png", url)
        print(f"✓ {outdir}/{i:02d}.png  —  {pr['ad'].replace('|',' ')}  ₺{fiyat}{kurus}")
    # kontakt sayfası (tam carousel önizleme)
    n = len(prods) + 1
    cells = "".join(f'<div class=s><img src="{outdir}/{i:02d}.png"><b>{i}</b></div>' for i in range(1, n+1))
    open(os.path.join(HERE, "_montaj.html"), "w", encoding="utf-8").write(
        '<!doctype html><meta charset=utf-8><style>body{margin:0;background:#e8e2d6;display:flex;gap:14px;padding:18px}'
        '.s{position:relative}.s img{width:330px;display:block;border-radius:9px;box-shadow:0 8px 22px rgba(0,0,0,.18)}'
        '.s b{position:absolute;top:7px;left:7px;background:#2b2b2b;color:#fff;font-size:12px;font-weight:700;padding:3px 8px;border-radius:6px}'
        '</style>' + cells)
    subprocess.run([CHROME,"--headless=new","--disable-gpu","--hide-scrollbars","--no-sandbox","--force-device-scale-factor=2",
        f"--window-size={360*n+40},510", f"--screenshot={outdir}/_TAM-CAROUSEL.png",
        f"http://localhost:{PORT}/_montaj.html"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✓ {outdir}/_TAM-CAROUSEL.png (kontakt önizleme)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
