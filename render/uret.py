#!/usr/bin/env python3
"""AKZERN — job.json -> Nano Banana Pro (kilitli sablon + gercek urun) -> HTML yazi -> post.
tip: tekil | carousel | lifestyle | marka. FAL_KEY + CHROME_BIN env."""
import json, os, subprocess, urllib.parse, http.server, socketserver, threading, functools, shutil, sys
import nbpro
from PIL import Image

CHROME = os.environ.get("CHROME_BIN") or shutil.which("chromium") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__)); PORT = 8791; A = os.path.join(HERE, "assets")

def server():
    try:
        import urllib.request; urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=1)
    except Exception:
        H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
        threading.Thread(target=socketserver.TCPServer(("", PORT), H).serve_forever, daemon=True).start()

def cover_crop(path):
    im = Image.open(path).convert("RGB"); tw, th = 1080, 1350
    r = max(tw/im.width, th/im.height); nw, nh = int(im.width*r), int(im.height*r); im = im.resize((nw, nh))
    x = (nw-tw)//2; y = (nh-th)//2; im.crop((x, y, x+tw, y+th)).save(path)

def tr(p):
    s = f"{float(p):.2f}"; i, d = s.split("."); return f"{int(i):,}".replace(",", "."), "," + d

def shot(tpl, params, out):
    url = f"http://localhost:{PORT}/{urllib.parse.quote(tpl)}?" + urllib.parse.urlencode(params)
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", "--window-size=1080,1350", f"--screenshot={out}", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def urun_params(p, sira=""):
    f = {"kategori": p.get("kategori", "AKZERN YAPI"), "ad": p["ad"], "olcu": p.get("finish", ""),
         "sira": sira, "cip1": p.get("cip1", "1 Takım"), "cip2": p.get("cip2", "Vidalar Dahil")}
    fiyat, kurus = tr(p.get("price", "0")); f["fiyat"] = fiyat; f["kurus"] = kurus
    ca = p.get("compareAtPrice")
    if ca and float(ca) > float(p["price"]):
        ei, ek = tr(ca); f["eskifiyat"] = "₺"+ei+ek; f["indirim"] = "%"+str(round((1-float(p["price"])/float(ca))*100))
    else: f["eskifiyat"] = ""; f["indirim"] = ""
    return f

def main():
    server()
    job = json.load(open("job.json")); tip = job.get("tip", "tekil"); klasor = job["klasor"]
    out = os.path.join(HERE, "..", "arsiv", klasor); os.makedirs(out, exist_ok=True)
    prods = job["products"]
    KAL = "AKZERN Ic Sayfa KALITE.html"

    if tip == "carousel":
        nbpro.cluster([p["gercek_url"] for p in prods], f"{A}/kapak-hero.png", "kapak-kollar.png"); cover_crop(f"{A}/kapak-hero.png")
        shot("AKZERN Kapak - Kapi Kollari.html",
             {"hero": "assets/kapak-hero.png", "baslik": job.get("kapak_baslik", "Zarafeti|Kapınıza Taşıyın"),
              "kk": "AKZERN YAPI · "+job.get("kategori", "")}, f"{out}/01.png")
        for i, p in enumerate(prods, start=2):
            h = f"{A}/hero-{p['slug']}.png"; nbpro.single(p["gercek_url"], h, "ic.png"); cover_crop(h)
            f = urun_params(p, f"{i} / {len(prods)+1} ›"); f["hero"] = f"assets/hero-{p['slug']}.png"
            shot(KAL, f, f"{out}/{i:02d}.png")
    elif tip == "lifestyle":
        for p in prods:
            h = f"{A}/hero-{p['slug']}.png"; nbpro.lifestyle(p["gercek_url"], p.get("lifestyle_prompt", ""), h); cover_crop(h)
            shot("AKZERN Lifestyle DINAMIK.html",
                 {"bg": f"assets/hero-{p['slug']}.png", "kicker": p.get("kategori", ""), "baslik": p.get("baslik", "Detaylarda|Zarafet"),
                  "kategori": p.get("kategori", ""), "ad": p["ad"], "alt": p.get("finish", ""), "tag": "Yeni"}, f"{out}/{p['slug']}.png")
    elif tip == "marka":
        nbpro.cluster([p["gercek_url"] for p in prods], f"{A}/kapak-hero.png", "marka.png"); cover_crop(f"{A}/kapak-hero.png")
        shot("AKZERN Marka DINAMIK.html", {"bg": "assets/kapak-hero.png", "baslik": job.get("baslik", "Yapının|Sağlam İsmi"),
              "slogan": job.get("slogan", "Zarafet · Güven · Kalite"), "kicker": "AKZERN YAPI"}, f"{out}/marka.png")
    else:  # tekil
        tpl = "kampanya.png" if job.get("kampanya") else "ic.png"
        for p in prods:
            h = f"{A}/hero-{p['slug']}.png"; nbpro.single(p["gercek_url"], h, tpl); cover_crop(h)
            f = urun_params(p); f["hero"] = f"assets/hero-{p['slug']}.png"
            shot(KAL, f, f"{out}/{p['slug']}.png")
    print("uret ok:", tip, klasor)

if __name__ == "__main__":
    main()
