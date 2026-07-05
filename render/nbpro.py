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

def _call(image_urls, prompt, out, ar="4:5"):
    body = json.dumps({"prompt": prompt, "image_urls": image_urls, "aspect_ratio": ar, "num_images": 1}).encode()
    req = urllib.request.Request("https://fal.run/fal-ai/nano-banana-pro/edit", data=body,
        headers={"Authorization": f"Key {KEY}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=240))
    urllib.request.urlretrieve(r["images"][0]["url"], out)

SINGLE_P = ("Take the empty cream podium scene from the FIRST image and keep it 100% identical (podium, background, lighting, orange ring). "
  "Take the product from the SECOND image and place ONE single item standing UPRIGHT on top of the podium, LARGE and prominent, filling the center, "
  "firmly grounded on the podium surface with a natural soft contact shadow. The product MUST be 100% IDENTICAL to the second image — "
  "exact shape, lever, backplate, screws, slot, holes and finish; do NOT redesign, do NOT make a pair. Photorealistic, keep the upper area empty for a headline.")

CLUSTER_P = ("Take the empty cream/terracotta clustered podium scene from the FIRST image and keep it 100% identical. "
  "Place EACH of the following product images (one per remaining image) standing UPRIGHT and grounded on top of one of the podiums, LARGE and prominent, "
  "arranged across the cluster, each firmly grounded with natural contact shadows. Each product MUST be 100% IDENTICAL to its source image — "
  "exact shape, lever, plate, screws, finish; do NOT redesign, one item per podium. Photorealistic, keep the upper area empty for a headline.")

def single(product_url, out, template="ic.png"):
    _call([_uri(f"{SB}/{template}"), product_url], SINGLE_P, out)

def cluster(product_urls, out, template="kapak-kollar.png"):
    _call([_uri(f"{SB}/{template}")] + list(product_urls), CLUSTER_P, out)

def lifestyle(product_url, scene_prompt, out):
    _call([product_url], scene_prompt, out)

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
