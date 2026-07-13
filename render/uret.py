#!/usr/bin/env python3
"""AKZERN — job.json -> Nano Banana Pro (kilitli sablon + gercek urun) -> HTML yazi -> post.
tip: tekil | carousel | lifestyle | marka. FAL_KEY + CHROME_BIN env."""
import json, os, subprocess, urllib.parse, http.server, socketserver, threading, functools, shutil, sys
import nbpro
from PIL import Image, ImageDraw, ImageFilter

def lineup_cover(product_urls, out):
    """5 mükemmel tek-çekim packshot (fal.ai) -> bg-remove -> premium sıralı dizilim.
    NB Pro 5'i-bir-arada kümesi form bozuyordu; bu yöntem her ürünü tek üretip diziyor."""
    W, H = 1080, 1350
    bg = Image.new("RGB", (W, H)); t = (247, 242, 233); bcol = (226, 214, 197)
    for y in range(H):
        k = y / H; ImageDraw.Draw(bg).line([(0, y), (W, y)], fill=tuple(int(t[i]*(1-k)+bcol[i]*k) for i in range(3)))
    bg = bg.convert("RGBA")
    cuts = []
    for i, u in enumerate(product_urls[:5]):
        nbpro.packshot(u, f"/tmp/pk{i}.png"); nbpro.rembg(f"/tmp/pk{i}.png", f"/tmp/pkc{i}.png")
        im = Image.open(f"/tmp/pkc{i}.png").convert("RGBA"); bb = im.split()[3].getbbox()
        cuts.append(im.crop(bb) if bb else im)
    n = len(cuts); base_y = 1130
    xs = [int(W*(j+0.5)/n) for j in range(n)]; hs = [560, 660, 600, 650, 560][:n]
    for x, im, h in zip(xs, cuts, hs):
        w = int(im.width*h/im.height); im = im.resize((w, h))
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([x-w//3, base_y-8, x+w//3, base_y+18], fill=(30, 22, 14, 120))
        bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
        bg.alpha_composite(im, (x-w//2, base_y-h+6))
    bg.convert("RGB").save(out)

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
        # ★ KİLİTLİ COVER: fal NB Pro kilitli boş cluster şablonuna 5 ürünü CLUSTER_P (tip+duruş) ile oturtur
        t0 = prods[0].get("tip", "door handle"); d0 = prods[0].get("durus", "dik")
        sb = job.get("kapak_sablon", "kapak-kollar.png")
        kk_tpl = job.get("kapak_tpl", "AKZERN Kapak - Kapi Kollari.html")
        nbpro.cluster([p["gercek_url"] for p in prods], f"{A}/kapak-hero.png", sb, t0, d0); cover_crop(f"{A}/kapak-hero.png")
        shot(kk_tpl,
             {"hero": "assets/kapak-hero.png", "baslik": job.get("kapak_baslik", "Zarafeti|Kapınıza Taşıyın"),
              "kk": "AKZERN YAPI · "+job.get("kategori", "")}, f"{out}/01.png")
        for i, p in enumerate(prods, start=2):
            h = f"{A}/hero-{p['slug']}.png"; nbpro.single(p["gercek_url"], h, "ic.png", p.get("tip","door handle"), p.get("durus","dik")); cover_crop(h)
            f = urun_params(p, f"{i} / {len(prods)+1} ›"); f["hero"] = f"assets/hero-{p['slug']}.png"
            shot(KAL, f, f"{out}/{i:02d}.png")
    elif tip == "lifestyle":
        for p in prods:
            h = f"{A}/hero-{p['slug']}.png"; nbpro.lifestyle(p["gercek_url"], p.get("lifestyle_prompt", ""), h); cover_crop(h)
            shot("AKZERN Lifestyle DINAMIK.html",
                 {"bg": f"assets/hero-{p['slug']}.png", "kicker": p.get("kategori", ""), "baslik": p.get("baslik", "Detaylarda|Zarafet"),
                  "kategori": p.get("kategori", ""), "ad": p["ad"], "alt": p.get("finish", ""), "tag": "Yeni"}, f"{out}/{p['slug']}.png")
    elif tip == "marka":
        t0 = prods[0].get("tip", "door handle"); d0 = prods[0].get("durus", "dik")
        nbpro.cluster([p["gercek_url"] for p in prods], f"{A}/kapak-hero.png", "marka.png", t0, d0); cover_crop(f"{A}/kapak-hero.png")
        shot("AKZERN Marka DINAMIK.html", {"bg": "assets/kapak-hero.png", "baslik": job.get("baslik", "Yapının|Sağlam İsmi"),
              "slogan": job.get("slogan", "Zarafet · Güven · Kalite"), "kicker": "AKZERN YAPI"}, f"{out}/marka.png")
    else:  # tekil
        tpl = "kampanya.png" if job.get("kampanya") else "ic.png"
        for p in prods:
            h = f"{A}/hero-{p['slug']}.png"; nbpro.single(p["gercek_url"], h, tpl, p.get("tip","door handle"), p.get("durus","dik")); cover_crop(h)
            f = urun_params(p); f["hero"] = f"assets/hero-{p['slug']}.png"
            shot(KAL, f, f"{out}/{p['slug']}.png")
    print("uret ok:", tip, klasor)

if __name__ == "__main__":
    main()
