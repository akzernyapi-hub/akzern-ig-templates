#!/usr/bin/env python3
"""AKZERN — TEK-ÜRÜN (standalone) Instagram postları (KALITE şablonu, sabit konum).
Her ürün kendi <slug>.png dosyası olur. Girdi: products.json (hero=assets/ic/<slug>.png)."""
import json, subprocess, urllib.parse, os, http.server, socketserver, threading, functools, sys, shutil
CHROME = os.environ.get("CHROME_BIN") or shutil.which("chromium") or shutil.which("chromium-browser") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 8791
TPL = "AKZERN Ic Sayfa KALITE.html"

def server():
    try:
        import urllib.request; urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=1)
    except Exception:
        H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
        threading.Thread(target=socketserver.TCPServer(("", PORT), H).serve_forever, daemon=True).start()

def tr_fiyat(p):
    s = f"{float(p):.2f}"; i, d = s.split("."); return f"{int(i):,}".replace(",", "."), "," + d

def render(out, url):
    subprocess.run([CHROME,"--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars",
        "--force-device-scale-factor=2","--window-size=1080,1350",f"--screenshot={out}",url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main(products_json, outdir):
    server(); os.makedirs(outdir, exist_ok=True)
    prods = json.load(open(products_json, encoding="utf-8"))
    base = f"http://localhost:{PORT}/{urllib.parse.quote(TPL)}"
    for pr in prods:
        fiyat, kurus = tr_fiyat(pr["price"])
        f = {"hero":pr["hero"],"kategori":pr.get("kategori","AKZERN YAPI"),"ad":pr["ad"],
             "olcu":pr["finish"],"fiyat":fiyat,"kurus":kurus,"sira":pr.get("sira",""),
             "cip1":pr.get("cip1","1 Adet"),"cip2":pr.get("cip2","Stokta")}
        ca = pr.get("compareAtPrice")
        if ca and float(ca) > float(pr["price"]):
            ei, ek = tr_fiyat(ca); f["eskifiyat"] = "₺"+ei+ek
            f["indirim"] = "%"+str(round((1-float(pr["price"])/float(ca))*100))
        else:
            f["eskifiyat"] = ""; f["indirim"] = ""
        url = base + "?" + urllib.parse.urlencode(f)
        render(f"{outdir}/{pr['slug']}.png", url)
        print(f"✓ {pr['slug']}  —  {pr['ad'].replace('|',' ')}  ₺{fiyat}{kurus}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
