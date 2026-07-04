#!/usr/bin/env python3
"""
AKZERN Instagram — tek-ürün post render aracı (routine'in render adımı).
Şablonu (sabit düzen) ürün verisiyle doldurup 1080x1350 PNG üretir.
Konumlar şablonda sabit → her post birebir aynı yerde (feed nizami).

Kullanım:
  python3 render-post.py urun.json cikti.png
  # veya stdin: cat urun.json | python3 render-post.py - cikti.png

urun.json örnek:
{
  "sablon": "AKZERN Ic Sayfa DINAMIK.html",
  "bg": "assets/pod-bg.png",
  "urun": "assets/kat/istanbul-lotus.png",   # şeffaf ürün (Magnific remove-bg çıktısı / Shopify CDN)
  "kategori": "Kapı Kolu · ODA",
  "ad": "İstanbul Lotus|Aynalı Kapı Kolu",    # | = satır sonu
  "olcu": "Nikel Saten",
  "indirim": "%25", "eskifiyat": "₺999", "fiyat": "749", "kurus": ",90",
  "sira": "2 / 6 ›",
  "cip1": "1 Takım", "cip2": "Vidalar Dahil"  # mobilya kulbunda: cip1=ölçü, cip2=""
}
"""
import sys, json, subprocess, urllib.parse, os, http.server, socketserver, threading, functools

import shutil
CHROME = os.environ.get("CHROME_BIN") or shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8791

FIELDS = ["bg","urun","kategori","ad","olcu","indirim","eskifiyat","fiyat","kurus","sira","cip1","cip2"]

def ensure_server():
    try:
        import urllib.request
        urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=1)
    except Exception:
        Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
        httpd = socketserver.TCPServer(("", PORT), Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

def render(data, out):
    sablon = data.get("sablon", "AKZERN Ic Sayfa DINAMIK.html")
    qs = {k: data[k] for k in FIELDS if k in data}
    url = f"http://localhost:{PORT}/{urllib.parse.quote(sablon)}?{urllib.parse.urlencode(qs)}"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=2", "--window-size=1080,1350",
                    f"--screenshot={out}", url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"✓ {out}")

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    data = json.load(sys.stdin) if src == "-" else json.load(open(src, encoding="utf-8"))
    ensure_server()
    render(data, out)
