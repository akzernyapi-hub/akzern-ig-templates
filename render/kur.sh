#!/usr/bin/env bash
set -e
python3 -m pip install --quiet Pillow >/dev/null 2>&1 || true
if ! command -v chromium >/dev/null && ! command -v chromium-browser >/dev/null && ! command -v google-chrome >/dev/null; then
  python3 -m pip install --quiet playwright >/dev/null 2>&1 && python3 -m playwright install --with-deps chromium || \
  (sudo apt-get update -y && sudo apt-get install -y chromium) || true
fi
# playwright chromium yolunu CHROME_BIN'e koy
PW=$(python3 - <<'PY'
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p: print(p.chromium.executable_path)
except Exception: print("")
PY
)
[ -n "$PW" ] && echo "export CHROME_BIN=$PW"
echo "kurulum tamam"
