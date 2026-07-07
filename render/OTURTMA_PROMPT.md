# AKZERN — KİLİTLİ PROMPTLAR (değiştirme)

Cover/cluster üretimi: ÜRÜN promptu + OTURTMA promptu birleştirilip AI'a (Nano Banana 2 / NB Pro) verilir.
Kesip-yapıştır YOK — ürünleri AI podyumlara oturtur (tek-ürün metodu kanıtlandı).

## 1) OTURTMA PROMPTU (podyum zeminlerine grounded) — KİLİTLİ
```
Place each door handle so it STANDS UPRIGHT and VERTICAL directly on the flat TOP SURFACE of its OWN cylindrical podium. The bottom/base of every handle must be firmly PLANTED and GROUNDED on the podium's top surface, resting on it with a soft realistic contact shadow — never floating, never hovering in the air, never above the podium. EXACTLY ONE handle per podium, evenly distributed across all podiums, with clear spacing so NO handle overlaps, touches or covers another, and NONE is cut off by the image border. Each handle is LARGE and prominent, occupying most of its podium's height. Keep every podium, its position and the whole background scene 100% unchanged and intact.
```

## 2) ÜRÜN PROMPTU (form+renk sadakati) — KİLİTLİ
```
Each handle must be 100% IDENTICAL to its reference product image — exact rectangular backplate, exact lever shape, screw holes, keyhole/WC slot and finish. Matte black stays PURE MATTE BLACK (never blue/navy/teal); nickel/satin stays that exact metal tone. Do NOT redesign, do NOT merge handles, do NOT create pairs. Photorealistic premium studio product photography, ultra detailed, sharp.
```

## 3) BİRLEŞİK (cover üretimi için) = OTURTMA + ÜRÜN
İlk görsel = KİLİTLİ boş cluster şablonu (assets/sablon/kapak-kollar.png). Sonraki görseller = gerçek ürünler (sırayla). Model: imagen-nano-banana-2 (Magnific) veya fal nano-banana-pro. aspectRatio 4:5. Üst bölge başlık için boş kalsın.

---
## ★ KİLİTLİ KAZANAN YÖNTEM (2026-07-07 kullanıcı onayladı — DEĞİŞTİRME)
Cover = `nbpro.cluster(product_urls, out, "kapak-kollar.png")` → fal NB Pro edit: image_urls=[KİLİTLİ boş cluster şablonu, ürün1..5] + `nbpro.CLUSTER_P`.
Sonuç: 5 farklı ürün podyumlara İRİ + grounded + ayrı ayrı oturur (şablon bozulmaz). uret.py carousel/marka bunu kullanır.

### Tek kolu düzeltme (swap) — biri yanlış/çift çıkarsa
image_urls=[üretilen_cover, doğru_ürün_referansı] + prompt:
```
The FIRST image is a finished scene with door handles on podiums. Replace ONLY the [KONUM, ör: FAR LEFT / leftmost] handle with the handle in the SECOND image, on the SAME podium, same large size, upright and grounded, 100% identical in form to the second image. Keep EVERYTHING ELSE 100% IDENTICAL — other handles, podiums, positions, lighting, shadows, background unchanged. Photorealistic, seamless.
```
