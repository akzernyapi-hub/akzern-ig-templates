# AKZERN YAPI — Instagram Otomasyon Sistemi

Premium Türk kapı kolu/hırdavat markası. Shopify kataloğundan (~1000+ ürün) **otonom, bulut-tabanlı Instagram içerik fabrikası**. Her post: gerçek ürün → AI ile premium sahne → HTML yazı → Notion onayı → otomatik Instagram yayını.

> Bu dosya sistemin tam dökümüdür. Yeni oturumda bunu + hafızayı (`instagram-premium-sablon.md`) oku, kaldığın yerden devam et.

---

## 1) MİMARİ / AKIŞ
```
Routine (bulut CCR, zamanlı) → Shopify MCP (ürün + fiyat + görsel)
  → render/job.json yaz + git push
  → GitHub Action "render-carousel" (açık internet, FAL_KEY):
       uret.py → nbpro.py (fal NB Pro: KİLİTLİ şablona GERÇEK ürünü grounded oturtur)
               → Chrome headless + HTML şablon (dinamik yazı)
               → arsiv/<klasor>/*.png commit + Drive (rclone)
  → Routine FORM-QA (Read ile gerçekle karşılaştır; çift/bozuk/renk → max 3 tur yeniden)
  → Notion "İçerik Takvimi" kartı: 🟠 Onay Bekliyor
KULLANICI Notion'da → 🔵 Onaylandı
  → Yayıncı routine (saatlik) → publish-instagram Action (graph.instagram.com) → Instagram
  → Notion → 🟢 Yayınlandı
```
**Neden GitHub Action:** fal.ai + Chrome bulut sandbox'ta engelli; Action açık internet + chromium sağlar. Routine sandbox'ı fal'a erişemez, Action erişir.

---

## 2) REPO — github.com/akzernyapi-hub/akzern-ig-templates
- `render/nbpro.py` — fal NB Pro sarmalayıcı (single/cluster/lifestyle/packshot/rembg) + **KİLİTLİ PROMPTLAR**
- `render/uret.py` — job.json → nbpro sahne + HTML yazı render orkestratörü (tip: tekil/carousel/lifestyle/marka)
- `render/config.json` — 9 kategori (tip + duruş + koleksiyon + kapak başlığı)
- `render/LIFESTYLE_SAHNELER.json` — lifestyle montaj + ortam rotasyonu + SIKI form kuralı
- `render/OTURTMA_PROMPT.md` — kilitli cover/oturtma/swap promptları
- `render/assets/sablon/*.png` — **5 KİLİTLİ boş şablon**: kapak-kollar, kapak-kulp, ic, marka, kampanya (AI ÜRETMEZ)
- `render/assets/cut/*.png` — onaylı kesimler (anka, kristal, lotus-oda/wc/n/s, noyan, avanti)
- `render/AKZERN *.html` — dinamik yazı şablonları: "Ic Sayfa KALITE" (tekil/slayt), "Kapak - Kapi Kollari" (cover), "Lifestyle DINAMIK", "Marka DINAMIK", "Kampanya DINAMIK", "Kapak - Mobilya Kulplari"
- `.github/workflows/render-carousel.yml` — Pillow+playwright kurar, uret.py çalıştırır, commit + Drive
- `.github/workflows/publish-instagram.yml` — graph.instagram.com yayın (tek + carousel)
- `arsiv/<klasor>/` — üretilen postlar (raw.githubusercontent ile Notion/IG erişir)

---

## 3) ★ KİLİTLİ PROMPTLAR (nbpro.py — DEĞİŞTİRME)

**SINGLE_TMPL** (tekil/slayt; `{tip}`+`{durus}` kategori-duyarlı):
> "Take the empty cream podium scene from the FIRST image and keep it 100% identical (podium, background, lighting, orange ring). Take the **{tip}** from the SECOND image and place ONE single piece **{durus}**, LARGE and prominent, filling the center, with a natural soft contact shadow. The product MUST be 100% IDENTICAL to the second image — exact shape, profile, parts, screws/posts, holes/slot AND EXACT COLOR/FINISH. CRITICAL COLOR RULE: matte black stays PURE MATTE BLACK (never blue/navy/grey/teal); nickel/satin/chrome keeps that exact metal tone. Do NOT shift or recolor. Do NOT redesign, do NOT make a pair. Photorealistic, keep the upper area empty for a headline."

**DURUS** (duruşlar):
- `dik` = "standing perfectly UPRIGHT and VERTICAL on top of the podium, its base firmly PLANTED and GROUNDED on the podium surface (never floating)"
- `slas` = "oriented DIAGONALLY like a forward slash '/', tilted to the RIGHT about 35 degrees, HOVERING and floating a little ABOVE the podium (elegant levitating product shot, not lying flat, not resting), with a soft shadow cast on the podium below" — kulp/ray için

**CLUSTER_P** (cover = KİLİTLİ boş cluster şablonu + 5 ürün; `image_urls=[sablon, urun1..5]`):
> "The FIRST image is a fixed studio scene with empty cream and terracotta cylindrical podiums — keep it 100% UNCHANGED. Place the {tip}s from the other images onto the podiums, ONE distinct handle per podium (every one DIFFERENT — do NOT duplicate/repeat/twice). Each stands UPRIGHT+GROUNDED (kulpta '/' eğimli havada). Make each VERY LARGE, THICK, SUBSTANTIAL — bold/tall (NOT thin/small). Arrange richly but none cut off. Each 100% IDENTICAL form to its reference; matte black not blue; nickel exact; no pairs. Keep upper third empty for headline."

**SWAP** (üretilen cover'da bir ürünü değiştir, gerisini koru; `image_urls=[cover, dogru_urun]`):
> "The FIRST image is a finished scene. Replace ONLY the [KONUM ör. FAR LEFT / duplicate Arrendi / straight black bar] handle with the handle in the SECOND image, on the SAME podium, same size + '/' pose + shadow, 100% identical form+color to the reference. Keep EVERYTHING ELSE 100% IDENTICAL — other handles, podiums, positions, lighting, shadows, background. Photorealistic, seamless."

**LIFESTYLE** (ürünü ortama monteli; `image_urls=[urun]` + prompt = montaj + ortam + kural):
> kural (SIKI): "CRITICAL FORM FIDELITY — reproduce the handle EXACTLY (lever/backplate/screws/slot/finish; matte black stays pure black, never blue). Install correctly and technically as the sharp hero. Keep the upper third calmer for a headline. Photorealistic professional interior photoshoot, ultra sharp product, softly blurred background. No text/logo/watermark. 4:5 vertical."
> Ortam rotasyonu — kapı kolu: hol(ceviz)/salon(meşe)/yatak(gri-yeşil)/çalışma(dumanlı meşe); kulp: mutfak/banyo/gardırop/salon.

**PACKSHOT_P** — düz beyaz zeminde tek dik ürün (rembg öncesi; artık cover için kullanılmıyor).

---

## 4) KATEGORİ-DUYARLI SİSTEM (config.json — 9 kategori)
Her ürün job.json'da `tip` + `durus` taşır; nbpro prompta işler.

| key | tip (İngilizce) | duruş | koleksiyon(lar) |
|---|---|---|---|
| kapi-kollari | door handle on a long rectangular backplate | dik | aynali-kapi-kollari, kapi-kollari, kapi-kolu |
| kulplar-uzun | furniture cabinet drawer bar pull | slas (/) | genel-kulplar |
| kulplar-dugme | furniture cabinet knob | dik | dugme-kulplar |
| kilitler | door lock / cylinder lock body | dik | kapi/daire/celik/gomme-kilitleri, asma-kilitler, emniyet-kilitleri |
| dolap-ayaklari | furniture leg / adjustable foot | dik | dolap-ayaklari |
| menteseler | door hinge | dik | kapi-menteseleri |
| askiliklar | wall-mounted coat/towel hook | dik | askiliklar, banyo-askisi |
| kapi-cekmeler | door pull / gate pull bar | dik | kapi-cekmeler |
| cekmece-raylari | drawer slide / runner rail | slas | cekmece-raylari |

**Durum:** kapı kolları + uzun kulplar **tam kalibre & yayınlandı**; diğerleri rotasyonda ama ilk çalıştırmada şablon/duruş kontrolü gerekir.

---

## 5) ROUTINE'LER (bulut CCR; /schedule → RemoteTrigger; env `env_012epA4PLxUQMN779PMdkJ1p`; model claude-sonnet-4-6)

| Routine | ID | Cron (UTC) | Ne yapar |
|---|---|---|---|
| Günlük İçerik | `trig_01HKd9qB5Vhy49Q3M7Tn8hVA` | `0 17 * * 0,2,4` (Paz/Sal/Per 20:00) | 2 tekil kapı kolu + form-QA → 🟠 Onay Bekliyor |
| Haftalık Carousel | `trig_01JcSEbjdiHaksZyCv26WF9B` | `0 6 * * 1` (Pzt 09:00) | kategori rotasyon (durum.kategori_index), cover+5 slayt |
| Lifestyle | `trig_01TaNvCkRCRg1x2UewJ1jjki` | `0 17 * * 2` (Sal 20:00) | kategori+ortam rotasyon, monteli sahne |
| Yayıncı | `trig_01Xh2HFXxaQAvthsBnkhuUqH` | `0 * * * *` (saatlik) | 🔵 Onaylandı → IG + SEO caption → 🟢 Yayınlandı |
| Token yenile | `trig_01Dhkmtr2vWx3pkZp8pH588m` | `0 3 1 * *` (aylık) | IG uzun-token refresh |
| Aşama-2 (KAPALI) | `trig_01Xoq28G2RS8tgfjxbxXwr1Z` | — | gereksiz, disabled |

Tetikleme: `RemoteTrigger {action:"run", trigger_id:"..."}`. MCP: Shopify + Notion.

---

## 6) SECRETS (GitHub repo)
`FAL_KEY` · `IG_TOKEN` · `IG_USER_ID` · `IG_APP_SECRET` · `RCLONE_CONF` (Drive drive.file, sınırlı kapsam).

---

## 7) INSTAGRAM (Instagram API with Instagram Login)
- Hesap: **@akzernyapi** (BUSINESS) · IG user id **27642596102095132**
- Meta app "AKZERN I OTOMASYON": FB App ID `1355413343198702`, Instagram App ID `2101305397085956`
- API: **graph.instagram.com** (graph.facebook.com DEĞİL). Token `IGAA...` ile başlar (uzun-ömürlü, `instagram_business_content_publish` var)
- Yayın: tek = `media`(image_url)+`media_publish`; carousel = her çocuk `media_type=IMAGE`+`is_carousel_item=true` → `CAROUSEL` container → `media_publish`
- **UYARILAR:**
  - IG API **post silmeyi desteklemez** → mükerrer olursa elle sil.
  - Meta app "Development" modunda → Meta ara sıra **e-posta/telefon DOĞRULAMA** ister; tamamlanana kadar tüm API `"API access blocked"` (kod 200) verir. Developer panelinde "Required actions" tamamla.
  - Token kurulumu: app → use case "Manage messaging & content on Instagram" → "Add all required permissions" + "Add account". Hata "Yetersiz geliştirici görevi" = IG hesabı **App roles → Instagram Testers**'a eklenip IG'den davet kabul edilmeli. IG şifresi FB-bağlı hesapta ayrı belirlenmeli.

---

## 8) NOTION AKIŞI
- İçerik Takvimi data source: `collection://0283145f-5b90-40b6-b533-c182849c1ac2`
- "Onay Durumu" (SADECE 4): **🟠 Onay Bekliyor · 🔵 Onaylandı · 🟢 Yayınlandı · 🔴 Reddedildi**
- Görseller `raw.githubusercontent.com/.../arsiv/.../0N.png` ile gömülür
- **Notion görseli önbelleğe alır** → aynı isimle güncelleme görünmez; **yeni dosya adı (cache-bust: -v1/-v2)** + kart URL'sini güncelle
- Yayıncı, başarılı yayından sonra kartı **🟢 Yayınlandı** yapmalı (yoksa saat başı mükerrer)
- Görseller kartın **İÇİNDE** (liste görünümünde görünmez, karta tıkla)

---

## 9) ARAÇLAR / MCP / MODELLER
- **fal.ai** (REST, Action'da): `fal-ai/nano-banana-pro/edit` (kilitli şablon + ürün oturtma, çoklu görsel), `fal-ai/birefnet/v2` (arka plan silme). Bakiye biterse `"User is locked. Exhausted balance"` → **fal.ai/dashboard/billing**.
- **rembg** (yerel; `pip install rembg onnxruntime`, u2net) — fal yokken bg silme + mavi→nötr renk düzeltme (numpy: mavi-baskın pikselleri lümine çek).
- **Magnific MCP** (imagen-nano-banana-2) — denendi ama bu oturum/routine'den **403 Akamai engelli**; fal kullanılıyor.
- **MCP connectors:** Shopify (ürün/fiyat), Notion (onay takvimi), Google Drive/Canva/runware.ai (bağlı, az kullanılan).
- **Skiller:** `/schedule` (routine kur/güncelle — RemoteTrigger), memory (hafıza).
- **Render:** Chrome headless `--screenshot`, 1080×1350, `--force-device-scale-factor=2`. HTML şablon URL param'ları: `hero, baslik(|→<br>), kategori, ad(|→<br>), olcu, fiyat, kurus, eskifiyat, indirim, cip1, cip2, fine(|→<br>), kk`.

---

## 10) KAZANILAN KURALLAR / DERSLER
1. **Form sadakati:** gerçek ürün + NB Pro kilitli şablona oturtur + **kullanıcı-yargıç döngüsü** (form yanlışsa yeniden). Kesip-yapıştır/lineup/rembg-composite **BIRAKILDI** (havada/küçük/bozuk kalıyordu).
2. **Renk kilidi:** NB Pro siyahı/kromu maviye çeviriyor → prompta katı renk kuralı + gerekirse yerel mavi-nötrleme.
3. **Kilitli şablon:** 6 şablon sabit, AI üretmez; sadece ürün AI ile oturur.
4. **Cover:** fal NB Pro 5-ürün-tek-sahne (CLUSTER_P). 5'i-bir-arada bazen çift/bozuk → **SWAP** ile tek ürün düzelt (gerisini koru). "Farklı ürünler seç" (aynısını tekrar koymasın).
5. **Dinamik fiyat:** Shopify'dan güncel; indirim yoksa `?eskifiyat=&indirim=` boş geç (default %25/₺999 rozeti çıkmasın).
6. **Slayt yazısı:** "Vidalı" yerine ürün mm ölçüsü; çift-renk ürünlerde iki renk yaz (ör. Nardin = Mat Siyah–Mat Saten). Cover sağ-alt (`fine`) = malzeme + ölçüler.
7. **Duruş:** kapı kolu/kilit/menteşe **dik**; kulp/ray **"/" eğimli havada + gölge**. Rozetli kollar yatay.
8. **Mükerrer yayın:** Yayıncı'yı elle Action + routine aynı anda tetikleme → **sadece routine `run`**.
9. **Görselleri hep `ONIZLEME/` klasörüne kaydet** — kullanıcı benim Read çıktımı göremez, o klasörden bakar.

---

## 11) YAYINLANAN POSTLAR
1. Anka Aynalı Kapı Kolu tekil — ₺749,99
2. Kapı Kolları kategori carousel (6 slayt)
3. Anka Lifestyle (WC, ceviz kapıda monteli)
4. Uzun Kulplar carousel (Nardin çift-renk / Asya / Kordon / Derya / Garmin altın, ölçülü)

---

## 12) SIRADAKİ / KALAN
- **Düğme Kulplar** (kulplar-dugme): yuvarlak knob'lar, dik duruş, ayrı carousel — **başlanacak** (kaldığımız yer).
- Diğer kategoriler (kilitler, menteşe, ayak, askılık, çekme, ray): config'de tanımlı, ilk çalıştırmada şablon/duruş/renk kontrolü.
- Lifestyle sahneleri: kapı kolu + kulp var; diğer kategoriler LIFESTYLE_SAHNELER.json'a eklenecek.
- İnox Yakut formu (ertelendi — fal formu bozuyor, sonra bakılacak).
- Kampanya / Marka post tipleri (uret.py destekliyor, test edilmedi).

---

## 13) YENİ OTURUMDA NASIL DEVAM EDİLİR
1. Bu dosyayı + hafızayı (`instagram-premium-sablon.md`) oku.
2. `git clone https://github.com/akzernyapi-hub/akzern-ig-templates`.
3. Yeni içerik: routine zamanını bekle **veya** `RemoteTrigger run <id>` ile hemen tetikle → Notion'a düşer → onayla → Yayıncı atar.
4. Yeni kategori/ürün: config.json'a `tip`+`durus`, gerekirse yeni kilitli şablon; **birkaç aday üret → kullanıcıya ONIZLEME'de göster → onayla → routine'e işle** (form/renk/duruşta kullanıcı yargıç).
5. fal bakiyesi + IG token + Meta doğrulama canlı mı kontrol et (bkz. §7, §9).
