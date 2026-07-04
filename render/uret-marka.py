#!/usr/bin/env python3
"""AKZERN — MARKA postu (5 doğrulanmış kesim kompozisyonu + slogan/logo, fiyatsız).
bg = assets/kapak-hero.png (kompoze cover). Girdi: job.json (slogan/baslik)."""
import json, subprocess, urllib.parse, os, http.server, socketserver, threading, functools, sys, shutil
CHROME = os.environ.get("CHROME_BIN") or shutil.which("chromium") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = os.path.dirname(os.path.abspath(__file__)); PORT = 8791
TPL = "AKZERN Marka DINAMIK.html"

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

def main(job_json, outdir):
    server(); os.makedirs(outdir, exist_ok=True)
    job = json.load(open(job_json, encoding="utf-8"))
    f = {"bg":"assets/kapak-hero.png",
         "baslik":job.get("baslik","Yapının|Sağlam İsmi"),
         "slogan":job.get("slogan","Zarafet · Güven · Kalite"),
         "kicker":job.get("kicker","AKZERN YAPI"),
         "handle":job.get("handle","")}
    url = f"http://localhost:{PORT}/{urllib.parse.quote(TPL)}?" + urllib.parse.urlencode(f)
    render(f"{outdir}/marka.png", url)
    print("✓ marka postu")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
