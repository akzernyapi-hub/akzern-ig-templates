#!/usr/bin/env python3
"""AKZERN — Nano Banana Pro ile KİLİTLİ şablona GERÇEK ürünü grounded yerleştirir.
Şablon sabit kalır, ürün gerçeğinden birebir; AI sadece sahneye oturtur.
FAL_KEY env gerekir. fal-ai/nano-banana-pro/edit (çoklu görsel)."""
import os, io, base64, json, urllib.request, sys
from PIL import Image

KEY = os.environ["FAL_KEY"]
HERE = os.path.dirname(os.path.abspath(__file__)); SB = os.path.join(HERE, "assets", "sablon")

def _uri(path):
    im = Image.open(path).convert("RGB")
    b = io.BytesIO(); im.save(b, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()

def _fetch_uri(src):
    """Local path or http(s) URL → base64 data URI (JPEG). Downloads remote images so fal.run never needs to fetch CDN URLs directly."""
    if not src.startswith("http://") and not src.startswith("https://"):
        return _uri(src)
    import time, tempfile
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (compatible; AkzernBot/1.0)"})
            data = urllib.request.urlopen(req, timeout=60).read()
            ct = "image/png" if src.lower().split("?")[0].endswith(".png") else "image/jpeg"
            im = Image.open(io.BytesIO(data)).convert("RGB")
            b = io.BytesIO(); im.save(b, "JPEG", quality=92)
            return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
        except Exception as e:
            last = e; time.sleep(3 * (attempt + 1))
    raise last

def _call(image_urls, prompt, out, ar="4:5"):
    import time
    body = json.dumps({"prompt": prompt, "image_urls": image_urls, "aspect_ratio": ar, "num_images": 1}).encode()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request("https://fal.run/fal-ai/nano-banana-pro/edit", data=body,
                headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=240))
            u = r["images"][0]["url"]
            for d in range(3):
                try:
                    urllib.request.urlretrieve(u, out); return
                except Exception as e:
                    last = e; time.sleep(3)
            raise last
        except Exception as e:
            last = e; time.sleep(5 * (attempt + 1))
    raise last

# KATEGORİ-DUYARLI tekil prompt: {tip}=ürün tipi tarifi, {durus}=podyumdaki duruş. config.json'dan gelir.
SINGLE_TMPL = ("Take the empty cream podium scene from the FIRST image and keep it 100% identical (podium, background, lighting, orange ring). "
  "Take the {tip} from the SECOND image and place ONE single piece {durus}, LARGE and prominent, filling the center, with a natural soft contact shadow. "
  "The product MUST be 100% IDENTICAL to the second image — exact shape, profile, parts, screws/posts, holes/slot AND EXACT COLOR/FINISH. "
  "CRITICAL COLOR RULE: preserve the exact original finish and color from the source photo — matte black stays PURE MATTE BLACK (never blue/navy/grey/teal); nickel/satin/chrome keeps that exact metal tone. Do NOT shift or recolor. "
  "Do NOT redesign, do NOT make a pair. Photorealistic, keep the upper area empty for a headline.")

# Varsayılan duruşlar (kategori duruş vermezse)
DURUS = {
  "dik": "standing perfectly UPRIGHT and VERTICAL on top of the podium, its base firmly PLANTED and GROUNDED on the podium surface (never floating)",
  "slas": "oriented DIAGONALLY like a forward slash '/', tilted to the RIGHT about 35 degrees, HOVERING and floating a little ABOVE the podium (elegant levitating product shot, not lying flat, not resting), with a soft shadow cast on the podium below",
}

# ★ KİLİTLİ KAZANAN COVER PROMPTU (2026-07-07 kullanıcı onayı) — DEĞİŞTİRME
# fal NB Pro edit: image_urls=[KİLİTLİ boş cluster şablonu, ürün1..5] + bu prompt.
CLUSTER_P = ("The FIRST image is a fixed studio scene with empty cream and terracotta cylindrical podiums — keep it 100% UNCHANGED "
  "(same podiums, same positions, same background). Place the door handles from the other images onto the podiums, ONE distinct handle per podium "
  "(every handle is a DIFFERENT product — do NOT duplicate or repeat any handle, do NOT put the same handle twice). "
  "Each handle stands perfectly UPRIGHT and VERTICAL on the flat TOP SURFACE of its podium, its bottom base firmly PLANTED and GROUNDED resting on the podium top "
  "with a soft contact shadow — never floating, never hovering above. Make each handle VERY LARGE, THICK and SUBSTANTIAL — bold, prominent, tall, occupying most of its "
  "podium's height and clearly the hero (NOT thin, NOT small, NOT weak). Arrange them richly across the cluster but with enough separation that none is cut off by the border. "
  "Each handle 100% IDENTICAL in form to its reference image — exact rectangular backplate, lever shape, screw holes, keyhole/WC slot and finish; "
  "matte black stays PURE MATTE BLACK (never blue/navy); nickel/satin stays that exact metal tone; do NOT redesign, distort, merge or make pairs. "
  "Photorealistic premium studio product photography. Keep the upper third of the image emptier for a headline.")

def single(product_url, out, template="ic.png", tip="door handle", durus="dik"):
    d = DURUS.get(durus, durus)  # anahtar ('dik'/'slas') ya da doğrudan metin
    prompt = SINGLE_TMPL.format(tip=tip, durus=d)
    _call([_uri(f"{SB}/{template}"), _fetch_uri(product_url)], prompt, out)

def cluster(product_urls, out, template="kapak-kollar.png", tip="door handle", durus="dik"):
    # kulp gibi ürünler için tip + duruş prompta işlenir
    poz = ("standing perfectly UPRIGHT and VERTICAL on the flat TOP SURFACE of each podium, base firmly grounded, never floating"
           if durus == "dik" else
           "resting elegantly on each podium, oriented DIAGONALLY like a forward slash '/', tilted to the right and slightly raised, as a premium display")
    p = CLUSTER_P.replace("door handles", tip + "s").replace("door handle", tip).replace(
        "standing perfectly UPRIGHT and VERTICAL on the flat TOP SURFACE of each podium, its bottom base firmly PLANTED and GROUNDED resting on the podium top "
        "with a soft contact shadow — never floating, never hovering above.", poz + ". ")
    _call([_uri(f"{SB}/{template}")] + [_fetch_uri(u) for u in product_urls], p, out)

def lifestyle(product_url, scene_prompt, out):
    _call([_fetch_uri(product_url)], scene_prompt, out)

PACKSHOT_P = ("Product photo: place the EXACT door handle from the image standing perfectly UPRIGHT and VERTICAL, centered on a plain pure white seamless studio background, large and sharp, soft shadow. ONE single handle only, no pair. "
  "Keep it 100% identical including EXACT finish — matte black stays PURE MATTE BLACK (never blue/navy), nickel stays nickel. Photorealistic e-commerce packshot.")

def packshot(product_url, out):
    _call([product_url], PACKSHOT_P, out, ar="3:4")

def rembg(path, out):
    import time
    b = json.dumps({"image_url": _uri(path)}).encode()
    for a in range(3):
        try:
            req = urllib.request.Request("https://fal.run/fal-ai/birefnet/v2", data=b,
                headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"})
            r = json.load(urllib.request.urlopen(req, timeout=120)); urllib.request.urlretrieve(r["image"]["url"], out); return
        except Exception as e:
            last = e; time.sleep(4)
    raise last

if __name__ == "__main__":
    # CLI: nbpro.py single <product_url> <out> [template]  |  cluster <out> <template> <url1..>  |  lifestyle <url> <out> <prompt>
    mode = sys.argv[1]
    if mode == "single":
        single(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "ic.png")
    elif mode == "cluster":
        cluster(sys.argv[4:], sys.argv[2], sys.argv[3])
    elif mode == "lifestyle":
        lifestyle(sys.argv[2], sys.argv[4], sys.argv[3])
    print("nbpro ok:", mode, "->", sys.argv[3] if mode=="cluster" else sys.argv[3] if mode!="cluster" else "")
