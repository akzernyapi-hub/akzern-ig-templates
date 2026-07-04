#!/usr/bin/env python3
"""AKZERN — LIFESTYLE post render (ürün lüks iç mekânda, gerçek form).
bg = assets/lc/<slug>.png (kompoze lifestyle çıktısı). Girdi: products.json."""
import json, subprocess, urllib.parse, os, http.server, socketserver, threading, functools, sys, shutil
CHROME = os.environ.get("CHROME_BIN") or shutil.which("chromium") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__)); PORT = 8791
TPL = "AKZERN Lifestyle DINAMIK.html"

def server():
    try:
        import urllib.request; urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=1)
    except Exception:
        H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
        threading.Thread(target=socketserver.TCPServer(("", PORT), H).serve_forever, daemon=True).start()

def render(out, url):
    subprocess.run([CHROME,"--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars",
        "--force-device-scale-factor=2","--window-size=1080,1350",f"--screenshot={out}",url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def main(products_json, outdir):
    server(); os.makedirs(outdir, exist_ok=True)
    prods = json.load(open(products_json, encoding="utf-8"))
    base = f"http://localhost:{PORT}/{urllib.parse.quote(TPL)}"
    for pr in prods:
        f = {"bg":f"assets/lc/{pr['slug']}.png",
             "kicker":pr.get("kategori","AKZERN YAPI"),
             "baslik":pr.get("baslik","Detaylarda|Zarafet"),
             "kategori":pr.get("kategori",""),
             "ad":pr["ad"], "alt":pr.get("finish",""), "tag":pr.get("tag","Yeni")}
        url = base + "?" + urllib.parse.urlencode(f)
        render(f"{outdir}/{pr['slug']}.png", url)
        print(f"✓ lifestyle {pr['slug']}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
