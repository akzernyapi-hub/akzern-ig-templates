# AKZERN — Haftalık Kategori Carousel · ROUTINE FORMÜLÜ (v1, standart)

> Bu, routine'in **her hafta 1 kategori** için birebir izleyeceği dinamik reçetedir.
> Çıktı: `carousel-canli/` → **01 kapak + 02–06 iç sayfa + _TAM-CAROUSEL.png** (kontakt).
> Girdi: `config.ornek.json`'daki haftanın kategorisi. Ürün, fiyat, indirim, görsel **canlı** gelir; tasarım/konum **sabittir** (feed nizami).

## ⭐ MODEL KURALI (tüm Magnific üretimleri için — ÖNCELİKLİ)
1. **Önce `imagen-nano-banana-2-flash` (Nano Banana 2)** ile üret — hızlı ve ucuz. (Hero, kapak, sahne… hepsi.)
2. Çıktıyı **gözle kontrol et** (form referansa uyuyor mu, kol/plaka bozulmuş mu?).
3. **Form bozulduysa** aynı üretimi **`imagen-nano-banana-2` (Nano Banana Pro)** ile yeniden yap — en iyi form/renk sadakati.
> Yani NB2 varsayılan, NB Pro sadece "kurtarma". Maliyet düşer, kalite garanti kalır.

---

## ADIM 1 — Ürünleri çek (Shopify MCP)

`graphql_query` ile kategoriden **5 ürün** (config'deki `shopify_sorgu`):

```graphql
query {
  products(first: 5, query: "<KATEGORI.shopify_sorgu>") {
    edges { node {
      title
      featuredImage { url }
      variants(first: 1) { edges { node { price compareAtPrice } } }
    } }
  }
}
```

Her ürün için sakla: `title`, `image_url`, `price`, `compareAtPrice`.

---

## ADIM 2 — Her ürün için "podyumda oturan" hero üret (Magnific MCP)

Her ürün görselini işle:
1. `creations_upload_image` (image_url) → identifier   *(hotlink sorunu olursa request_upload+PUT)*
2. `images_generate` **mode=`imagen-nano-banana-2-flash`** (NB2 — varsayılan; form bozulursa `imagen-nano-banana-2` NB Pro ile retry), `references=[{type:image, identifier}]`, `aspectRatio="4:5"`, `count=1`, prompt:

```
Professional e-commerce product photo. ONE single <ÜRÜN TİPİ> — <kısa form tarifi: uzun dik plaka + kol + anahtar deliği>, <RENK/FINISH> finish — standing UPRIGHT and CENTERED on a cream cylindrical podium. Bright airy warm cream-to-beige (mink) studio background. Generous empty beige space at TOP and BOTTOM for text. Subtle burnt-orange rim on the podium base. Soft studio lighting, gentle contact shadow and reflection. STRICT: preserve the EXACT shape, proportions, curvature, plate length and finish from the reference — do NOT warp, bend, stretch or restyle. No text, no watermark, no logo. Photorealistic, 4:5.
```

3. `creations_wait` → hero URL → indir: `assets/hero/<slug>.png`

> ⚠️ **FORM KONTROLÜ (Lama dersi):** İnce/kavisli kollarda NB Pro formu bozabilir. Hero'yu **gözle doğrula**; form referanstan saparsa prompt'a `preserve exact geometry, keep the lever curve identical, do not thin or bend` ekleyip **1 kez retry** et.

---

## ADIM 3 — Kapak kompozisyonunu üret (Magnific MCP)

5 ürünün identifier'ıyla tek kompozisyon:
`images_generate` mode=`imagen-nano-banana-2-flash` (NB2 varsayılan; form bozulursa `imagen-nano-banana-2` NB Pro ile retry), `references=[5 ürün]`, `aspectRatio="4:5"`, `count=2`, prompt:

```
Professional e-commerce catalog hero. FIVE different <ÜRÜN TİPİ> — one from EACH reference — each STANDING UPRIGHT, arranged on geometric cylindrical podiums of varying heights. Podiums in warm cream, beige and taupe (mink) tones with ONE burnt-orange accent podium. Bright warm cream-to-beige studio background. Keep TOP 40% empty for a headline; cluster products in the lower portion. Soft lighting, contact shadows, warm orange rim accent. STRICT FIDELITY: reproduce each handle's exact form and finish; do NOT bend, merge or invent — exactly five, upright. No text/watermark/logo. Photorealistic 4:5.
```

En iyi çıktıyı seç → `assets/kapak-hero.png`. Kapağı render et:
```bash
chrome --headless=new --window-size=1080,1350 --force-device-scale-factor=2 \
  --screenshot=kapak-kapikollari.png "http://localhost:8791/AKZERN%20Kapak%20-%20Kapi%20Kollari.html"
```
*(Kapak başlığı/kicker/rozet paramla da değiştirilebilir; bkz. kapak şablonu.)*

---

## ADIM 4 — `products.json` oluştur

Shopify başlığını **temizle** → `ad` (| = satır sonu) + `finish`. Marka öneklerini ("İstanbul Door Handles", "Sofuoğlu", "Güzel Metal") ve "ODA/WC/YALE" ekini at; model + "Kapı Kolu" bırak. Finish'i başlıktan çıkar (Nikel Saten / Mat Siyah / Antrasit / Krom / Altın …).

```json
[
  {"ad":"Kristal Aynalı|Kapı Kolu","finish":"Nikel Saten","price":"819.99","compareAtPrice":null,"hero":"assets/hero/kristal.png"},
  {"ad":"Lama Aynalı|Kapı Kolu","finish":"Mat Siyah","price":"219.99","compareAtPrice":"269.99","hero":"assets/hero/lama.png"}
]
```

---

## ADIM 5 — Render (deterministik script)

```bash
python3 uret-carousel.py products.json carousel-canli "kapak-kapikollari.png"
```

Script yapar: fiyat TR biçim (₺, binlik nokta, kuruş virgül) · indirim % otomatik (compareAtPrice'tan) · indirim yoksa blok gizlenir · her slaytı **sabit konumda** render · kontakt sayfası. Kategori-özel çipler `products.json`'a `cip1/cip2` ile eklenebilir (kapı kolu → "1 Takım/Vidalar Dahil"; kulp → ölçü).

---

## ADIM 6 — Yayın hattı (opsiyonel)

6 slaytı **Notion İçerik Takvimi**'ne carousel olarak "🟠 Onay Bekliyor" ekle → onay → **Metricool** ile yayınla.

---

## ÖZET AKIŞ

```
config kategori → Shopify(5 ürün) → Magnific(5 hero + 1 kapak, form KORU) →
products.json → uret-carousel.py → carousel-canli/ (6 slayt) → Notion → yayın
```

**Maliyet:** kategori başına ~6 Magnific üretimi. Haftalık 1 kategori.
**Değişmez:** tasarım, konum, font, palet, logo → feed hep nizami.
**Değişir:** ürün görselleri + ad + fiyat + indirim.

*Not: Bu formül tek-ürün iç sayfa + kategori kapağı içindir. Lifestyle/Marka/Kampanya şablonları ayrı formüllerle (bkz. OTOMASYON.md) beslenir.*

---

## ⭐⭐ GÖRSEL KÖPRÜSÜ (BULUT ZORUNLU — cdnpk.net & cdn.shopify.com sandbox'ta ENGELLİ)
Bulut sandbox pikaso.cdnpk.net'e erişemez. Magnific görselini render'a sokmanın TEK çalışan yolu **GitHub Actions köprüsü**:

1. Tüm Magnific üretimleri bittikten sonra (5 hero + 1 kapak pikaso URL'leri elde) `render/heroes-manifest.json` yaz:
   `{"images":[{"url":"<pikaso_url>","path":"render/assets/hero/<slug>.png"}, ... , {"url":"<kapak_pikaso>","path":"render/assets/kapak-hero-src.png"}]}`
2. `git add render/heroes-manifest.json && git commit -m "run heroes" && git push` → bu `fetch-heroes` Action'ını tetikler (runner açık internetle pikaso'yu indirir + repoya commit'ler).
3. Action bitene kadar bekle: `for i in $(seq 1 12); do sleep 15; git pull -q; [ -f render/assets/hero/<son-slug>.png ] && break; done` (ya da `gh run list --workflow fetch-heroes` ile success bekle). ~30-90 sn.
4. Artık hero PNG'leri repoda/yerelde → `uret-carousel.py` bunları localhost'tan servis edip render eder. Kapak için kapak-hero-src.png'yi assets/kapak-hero.png'ye kopyala.

NOT: sandbox `raw.githubusercontent.com` (200) ve `git push/pull` (api.github.com) erişebilir; `pikaso.cdnpk.net`, `cdn.shopify.com`, `github.io`, `drive.google.com` (curl) ENGELLİ. Drive/Notion sadece MCP ile çalışır (curl değil).

---

## ⭐ KAPAK MODEL KURALI (form bozulmasını önle)
Kapak 5 ürünü tek karede birleştirdiği için form bozma riski YÜKSEK (kristal kol buruşmuştu).
Bu yüzden **kapak kompozisyonu HER ZAMAN `imagen-nano-banana-2` (NB Pro)** ile üretilir — en iyi form sadakati.
Tek-ürün hero'lar `imagen-nano-banana-2-flash` (NB2) kalabilir (tek ürün, bozulma az). Prompt'ta "do NOT crumple/bend/twist any handle" vurgusu ekle.
