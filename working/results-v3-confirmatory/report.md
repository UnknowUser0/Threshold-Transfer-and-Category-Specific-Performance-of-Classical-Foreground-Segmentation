# Laporan Eksperimen B v3 — CONFIRMATORY (CDnet 2014)

**STATUS:** CONFIRMATORY, previously unseen categories. Jangan menyebut hasil development sebagai confirmatory.  
**Data:** 27 sekuens, kategori PTZ, cameraJitter, intermittentObjectMotion, lowFramerate, thermal, turbulence; 0 sekuens tune, 27 sekuens test (seed 42, lihat `splits.csv`).  
**Resolusi kerja:** 320 px (lebar). **Pipeline B1-B4:** blur 5x5, ambang tetap, morfologi open(3)+close(7), kontur >= 0.10% luas frame.  
**Lingkungan:** Intel64 Family 6 Model 191 Stepping 2, GenuineIntel, OpenCV 5.1.0, Python 3.15.2.  
**Parameter terpilih (tune):** `{"frame_diff": {"fixed_thr": 5}, "mog2": {"var_threshold": 25}, "knn": {"dist2_threshold": 600.0}, "farneback": {"flow_thr": 1.0}}`.

**Definisi metrik.** Piksel (utama): label GT 255 = positif; 0 dan 50 (hard shadow) = negatif; 85 (luar ROI) dan 170 (unknown) diabaikan; prediksi di luar ROI dinolkan; metrik dihitung per sekuens lalu dirata-rata per kategori dan antar-kategori. Frame: positif = ada >= 1 box; MCC. Box GT diturunkan dari mask label 255 (closing 5x5, kontur >= 0.10% luas); TP box = pencocokan satu-ke-satu dengan IoU >= 0.5. 'IoU (TP)' = rerata IoU pasangan TP.

### Hasil utama pada 27 sekuens uji (rerata antar-kategori; metrik piksel CDnet; CI95 bootstrap bertingkat)

| Algoritma | P | R | F [CI95] | PWC | MCC frame | F1 box@0.5 | IoU (TP) | FPS (median) |
|---|---|---|---|---|---|---|---|---|
| B1 Frame Difference (tuned) | 0.350 | 0.627 | 0.230 [0.172, 0.287] | 15.13 | 0.199 [0.137, 0.266] | 0.097 | 0.629 | 2546 |
| B2 MOG2 (tuned) | 0.672 | 0.453 | 0.471 [0.405, 0.545] | 3.50 | 0.373 [0.297, 0.450] | 0.272 | 0.720 | 598 |
| B3 KNN (tuned) | 0.666 | 0.496 | 0.483 [0.404, 0.562] | 3.79 | 0.387 [0.310, 0.470] | 0.281 | 0.732 | 403 |
| B4 Farneback (tuned) | 0.231 | 0.555 | 0.203 [0.151, 0.253] | 17.55 | 0.182 [0.113, 0.253] | 0.061 | 0.624 | 86 |
| Selalu foreground (trivial) | 0.038 | 1.000 | 0.070 [0.049, 0.095] | 96.19 | 0 | - | - | - |

### Konfigurasi default vs tuned (F piksel, rerata antar-kategori)

| Algoritma | Parameter | Default | Tuned | F piksel default (test) | F piksel tuned (test) | F piksel default (semua seq) |
|---|---|---|---|---|---|---|
| B1 Frame Difference | fixed_thr | 25 | 5 | 0.228 | 0.230 | 0.228 |
| B2 MOG2 | var_threshold | 16 | 25 | 0.459 | 0.471 | 0.459 |
| B3 KNN | dist2_threshold | 400 | 600 | 0.489 | 0.483 | 0.489 |
| B4 Farneback | flow_thr | 1 | 1 | 0.203 | 0.203 | 0.203 |

### F piksel per kategori CDnet (algoritma tuned, sekuens uji)

| Kategori | n | B1 Frame Difference | B2 MOG2 | B3 KNN | B4 Farneback | Selalu FG |
|---|---|---|---|---|---|---|
| PTZ | 4 | 0.316 | 0.215 | 0.203 | 0.204 | 0.019 |
| cameraJitter | 4 | 0.154 | 0.667 | 0.709 | 0.128 | 0.081 |
| intermittentObjectMotion | 6 | 0.259 | 0.317 | 0.372 | 0.171 | 0.123 |
| lowFramerate | 4 | 0.279 | 0.486 | 0.474 | 0.220 | 0.062 |
| thermal | 5 | 0.339 | 0.517 | 0.573 | 0.394 | 0.125 |
| turbulence | 4 | 0.032 | 0.626 | 0.569 | 0.098 | 0.011 |

### Perbandingan algoritma sekunder dua sisi (F piksel; sign-flip eksak kategori, Holm m=2). Uji terarah H1-H2 lihat tabel hipotesis.

| Perbandingan | n sekuens | n kategori | efek [CI95] | menang | p kategori | p Holm | p Wilcoxon seq eksploratori |
|---|---|---|---|---|---|---|---|
| B2t - B1t | 27 | 6 | 0.241 [0.196, 0.285] | 24/27 | 0.094 | 0.188 | <0.001 |
| B3t - B1t | 27 | 6 | 0.253 [0.200, 0.303] | 25/27 | 0.062 | 0.188 | <0.001 |
| B4t - B1t | 27 | 6 | -0.027 [-0.052, -0.005] | 9/27 | 0.406 | 0.406 | 0.077 |

### Uji sekunder: 6 pasangan algoritma (sign-flip kategori; Holm per metrik)

| Metrik | Perbandingan | n sekuens | n kategori | efek [CI95] | menang | p kategori | p Holm | p Wilcoxon seq eksploratori |
|---|---|---|---|---|---|---|---|---|
| F piksel | B2t - B1t | 27 | 6 | 0.241 [0.196, 0.284] | 24/27 | 0.094 | 0.312 | <0.001 |
| F piksel | B3t - B1t | 27 | 6 | 0.253 [0.199, 0.303] | 25/27 | 0.062 | 0.312 | <0.001 |
| F piksel | B4t - B1t | 27 | 6 | -0.027 [-0.052, -0.003] | 9/27 | 0.406 | 0.812 | 0.077 |
| F piksel | B3t - B2t | 27 | 6 | 0.012 [-0.017, 0.036] | 16/27 | 0.625 | 0.812 | 0.162 |
| F piksel | B4t - B2t | 27 | 6 | -0.269 [-0.314, -0.224] | 3/27 | 0.031 | 0.188 | <0.001 |
| F piksel | B4t - B3t | 27 | 6 | -0.281 [-0.332, -0.228] | 2/27 | 0.062 | 0.312 | <0.001 |
| MCC frame | B2t - B1t | 19 | 6 | 0.094 [0.056, 0.131] | 13/19 | 0.562 | 1.000 | 0.087 |
| MCC frame | B3t - B1t | 19 | 6 | 0.115 [0.076, 0.158] | 13/19 | 0.406 | 1.000 | 0.029 |
| MCC frame | B4t - B1t | 21 | 6 | -0.017 [-0.053, 0.011] | 4/21 | 0.844 | 1.000 | 0.004 |
| MCC frame | B3t - B2t | 23 | 6 | 0.013 [-0.012, 0.039] | 13/23 | 0.688 | 1.000 | 0.427 |
| MCC frame | B4t - B2t | 19 | 6 | -0.097 [-0.141, -0.052] | 5/19 | 0.531 | 1.000 | 0.011 |
| MCC frame | B4t - B3t | 19 | 6 | -0.119 [-0.170, -0.068] | 5/19 | 0.406 | 1.000 | 0.012 |
| F1 box@0.5 | B2t - B1t | 27 | 6 | 0.175 [0.120, 0.225] | 23/27 | 0.062 | 0.250 | <0.001 |
| F1 box@0.5 | B3t - B1t | 27 | 6 | 0.185 [0.126, 0.241] | 24/27 | 0.062 | 0.250 | <0.001 |
| F1 box@0.5 | B4t - B1t | 27 | 6 | -0.035 [-0.054, -0.018] | 6/27 | 0.031 | 0.188 | <0.001 |
| F1 box@0.5 | B3t - B2t | 27 | 6 | 0.009 [-0.017, 0.034] | 15/27 | 0.750 | 0.750 | 0.279 |
| F1 box@0.5 | B4t - B2t | 27 | 6 | -0.210 [-0.261, -0.153] | 3/27 | 0.062 | 0.250 | <0.001 |
| F1 box@0.5 | B4t - B3t | 27 | 6 | -0.220 [-0.275, -0.162] | 3/27 | 0.031 | 0.188 | <0.001 |

Friedman sekunder EKSPLORATORI per-sekuens (F piksel): chi2=44.467, p=<0.001, n=27; tidak digunakan sebagai uji utama

### Ablasi faktorial frame_diff (b=blur, m=morfologi; tuned; sekuens uji)

| Sel | P | R | F [CI95] |
|---|---|---|---|
| b0-fixed-m0 | 0.177 | 0.580 | 0.162 [0.122, 0.206] |
| b0-fixed-m1 | 0.314 | 0.655 | 0.223 [0.168, 0.280] |
| b0-otsu-m0 | 0.358 | 0.298 | 0.168 [0.119, 0.216] |
| b0-otsu-m1 | 0.430 | 0.305 | 0.210 [0.163, 0.256] |
| b1-fixed-m0 | 0.323 | 0.525 | 0.200 [0.148, 0.251] |
| b1-fixed-m1 | 0.350 | 0.627 | 0.230 [0.173, 0.290] |
| b1-otsu-m0 | 0.404 | 0.288 | 0.185 [0.136, 0.233] |
| b1-otsu-m1 | 0.427 | 0.347 | 0.218 [0.165, 0.270] |

### Efek faktorial frame_diff (kontras on-off, sign-flip kategori, Holm per metrik)

| Metrik | Efek | n sekuens | n kategori | efek [CI95] | menang | p kategori | p Holm | p Wilcoxon seq eksploratori |
|---|---|---|---|---|---|---|---|---|
| px_f | blur | 27 | 6 | 0.017 [0.002, 0.035] | 20/27 | 0.250 | 1.000 | 0.058 |
| px_f | otsu | 27 | 6 | -0.009 [-0.033, 0.015] | 14/27 | 0.844 | 1.000 | 0.485 |
| px_f | morph | 27 | 6 | 0.041 [0.029, 0.056] | 25/27 | 0.031 | 0.219 | <0.001 |
| px_f | blur x otsu | 27 | 6 | -0.005 [-0.015, 0.005] | 12/27 | 0.469 | 1.000 | 0.628 |
| px_f | blur x morph | 27 | 6 | -0.010 [-0.016, -0.003] | 8/27 | 0.031 | 0.219 | 0.026 |
| px_f | otsu x morph | 27 | 6 | -0.004 [-0.014, 0.005] | 13/27 | 0.656 | 1.000 | 0.427 |
| px_f | blur x otsu x morph | 27 | 6 | 0.006 [-0.000, 0.012] | 13/27 | 0.250 | 1.000 | 0.290 |
| px_precision | blur | 27 | 6 | 0.056 [0.033, 0.082] | 23/27 | 0.031 | 0.219 | <0.001 |
| px_precision | otsu | 27 | 6 | 0.114 [0.084, 0.144] | 27/27 | 0.031 | 0.219 | <0.001 |
| px_precision | morph | 27 | 6 | 0.064 [0.053, 0.077] | 26/27 | 0.031 | 0.219 | <0.001 |
| px_precision | blur x otsu | 27 | 6 | -0.035 [-0.046, -0.024] | 5/27 | 0.062 | 0.219 | <0.001 |
| px_precision | blur x morph | 27 | 6 | -0.040 [-0.048, -0.032] | 1/27 | 0.031 | 0.219 | <0.001 |
| px_precision | otsu x morph | 27 | 6 | -0.017 [-0.028, -0.007] | 14/27 | 0.469 | 0.750 | 0.162 |
| px_precision | blur x otsu x morph | 27 | 6 | 0.015 [0.001, 0.028] | 13/27 | 0.375 | 0.750 | 0.269 |
| px_recall | blur | 27 | 6 | -0.013 [-0.028, 0.001] | 13/27 | 0.531 | 0.531 | 0.485 |
| px_recall | otsu | 27 | 6 | -0.287 [-0.318, -0.258] | 0/27 | 0.031 | 0.219 | <0.001 |
| px_recall | morph | 27 | 6 | 0.061 [0.047, 0.075] | 22/27 | 0.062 | 0.250 | <0.001 |
| px_recall | blur x otsu | 27 | 6 | 0.029 [0.020, 0.039] | 24/27 | 0.062 | 0.250 | <0.001 |
| px_recall | blur x morph | 27 | 6 | 0.020 [0.015, 0.024] | 27/27 | 0.031 | 0.219 | <0.001 |
| px_recall | otsu x morph | 27 | 6 | -0.028 [-0.035, -0.021] | 5/27 | 0.031 | 0.219 | <0.001 |
| px_recall | blur x otsu x morph | 27 | 6 | 0.006 [0.002, 0.010] | 16/27 | 0.188 | 0.375 | 0.111 |
| px_fpr | blur | 27 | 6 | -0.028 [-0.037, -0.020] | 1/27 | 0.031 | 0.219 | <0.001 |
| px_fpr | otsu | 27 | 6 | -0.121 [-0.148, -0.095] | 0/27 | 0.031 | 0.219 | <0.001 |
| px_fpr | morph | 27 | 6 | -0.012 [-0.019, -0.006] | 5/27 | 0.125 | 0.250 | 0.002 |
| px_fpr | blur x otsu | 27 | 6 | 0.027 [0.021, 0.032] | 27/27 | 0.031 | 0.219 | <0.001 |
| px_fpr | blur x morph | 27 | 6 | 0.020 [0.016, 0.024] | 27/27 | 0.031 | 0.219 | <0.001 |
| px_fpr | otsu x morph | 27 | 6 | 0.002 [-0.004, 0.008] | 20/27 | 0.750 | 0.750 | 0.141 |
| px_fpr | blur x otsu x morph | 27 | 6 | -0.009 [-0.013, -0.007] | 2/27 | 0.062 | 0.219 | <0.001 |

### Ablasi faktorial mog2 (b=blur, m=morfologi; tuned; sekuens uji)

| Sel | P | R | F [CI95] |
|---|---|---|---|
| b0-fixed-m0 | 0.584 | 0.460 | 0.419 [0.343, 0.500] |
| b0-fixed-m1 | 0.691 | 0.455 | 0.476 [0.403, 0.550] |
| b1-fixed-m0 | 0.619 | 0.438 | 0.433 [0.361, 0.508] |
| b1-fixed-m1 | 0.672 | 0.453 | 0.471 [0.403, 0.545] |

### Efek faktorial mog2 (kontras on-off, sign-flip kategori, Holm per metrik)

| Metrik | Efek | n sekuens | n kategori | efek [CI95] | menang | p kategori | p Holm | p Wilcoxon seq eksploratori |
|---|---|---|---|---|---|---|---|---|
| px_f | blur | 27 | 6 | 0.005 [-0.009, 0.020] | 11/27 | 0.781 | 0.812 | 0.841 |
| px_f | morph | 27 | 6 | 0.048 [0.033, 0.063] | 21/27 | 0.094 | 0.281 | <0.001 |
| px_f | blur x morph | 27 | 6 | -0.009 [-0.018, -0.002] | 12/27 | 0.406 | 0.812 | 0.148 |
| px_precision | blur | 27 | 6 | 0.008 [-0.011, 0.025] | 12/27 | 0.656 | 0.656 | 0.934 |
| px_precision | morph | 27 | 6 | 0.080 [0.055, 0.108] | 26/27 | 0.031 | 0.094 | <0.001 |
| px_precision | blur x morph | 27 | 6 | -0.027 [-0.039, -0.015] | 3/27 | 0.031 | 0.094 | <0.001 |
| px_recall | blur | 27 | 6 | -0.012 [-0.021, -0.002] | 6/27 | 0.125 | 0.250 | 0.011 |
| px_recall | morph | 27 | 6 | 0.004 [-0.006, 0.014] | 17/27 | 0.500 | 0.500 | 0.162 |
| px_recall | blur x morph | 27 | 6 | 0.010 [0.006, 0.014] | 25/27 | 0.031 | 0.094 | <0.001 |
| px_fpr | blur | 27 | 6 | -0.000 [-0.002, 0.001] | 12/27 | 0.812 | 0.812 | 0.336 |
| px_fpr | morph | 27 | 6 | -0.004 [-0.005, -0.002] | 1/27 | 0.031 | 0.094 | <0.001 |
| px_fpr | blur x morph | 27 | 6 | 0.002 [0.001, 0.002] | 25/27 | 0.031 | 0.094 | <0.001 |

### Sensitivitas lantai Otsu (frame difference, blur + Otsu + morfologi)

| Lantai Otsu | P | R | F [CI95] |
|---|---|---|---|
| 0 | 0.128 | 0.454 | 0.161 [0.115, 0.207] |
| 5 | 0.408 | 0.387 | 0.209 [0.154, 0.263] |
| 10 | 0.427 | 0.347 | 0.218 [0.165, 0.271] |
| 15 | 0.452 | 0.305 | 0.232 [0.181, 0.285] |
| 20 | 0.482 | 0.268 | 0.229 [0.184, 0.276] |

### Hipotesis confirmatory (uji satu sisi terarah eksak per kategori; Holm per keluarga)

| Hipotesis | Keluarga | Metrik | n kategori | Efek [CI95] | p satu sisi kategori | p dua sisi (deskriptif) | p Holm | Keputusan statistik |
|---|---|---|---|---|---|---|---|---|
| H1: MOG2 > Frame Difference (F piksel) | algoritma | F piksel | 6 | 0.241 [0.196, 0.285] | 0.047 | 0.094 | 0.062 | tidak signifikan |
| H2: KNN > Frame Difference (F piksel) | algoritma | F piksel | 6 | 0.253 [0.201, 0.304] | 0.031 | 0.062 | 0.062 | tidak signifikan |
| H3: Blur menurunkan FPR Frame Difference | preprocessing | FPR piksel | 6 | -0.028 [-0.036, -0.020] | 0.016 | 0.031 | 0.031 | arah didukung |
| H4: Morphology meningkatkan F1 Frame Difference | preprocessing | F piksel | 6 | 0.041 [0.029, 0.057] | 0.016 | 0.031 | 0.031 | arah didukung |

### Sensitivitas terhadap konstruksi box GT (tuned, sekuens uji): peringkat stabil bila urutan & tau tetap

| Varian GT | B1 F1 box | B2 F1 box | B3 F1 box | B4 F1 box | Urutan | tau vs primer |
|---|---|---|---|---|---|---|
| primer | 0.097 | 0.272 | 0.281 | 0.061 | B3 > B2 > B1 > B4 | 1.00 |
| tanpa_close | 0.096 | 0.269 | 0.280 | 0.061 | B3 > B2 > B1 > B4 | 1.00 |
| close9 | 0.100 | 0.263 | 0.272 | 0.063 | B3 > B2 > B1 > B4 | 1.00 |
| area_kecil | 0.096 | 0.263 | 0.275 | 0.061 | B3 > B2 > B1 > B4 | 1.00 |
| area_besar | 0.098 | 0.269 | 0.280 | 0.063 | B3 > B2 > B1 > B4 | 1.00 |

### Processing FPS per algoritma secara terisolasi: serial, 1 thread OpenCV, 300 frame pertama dari 1 sekuens/kategori, median dari 5 pengulangan

| Eksperimen | fps_median | fps_min | fps_max |
|---|---|---|---|
| B1 Frame Difference (default) | 1976.4 | 1605.1 | 3545.0 |
| B2 MOG2 (default) | 556.9 | 380.9 | 566.5 |
| B3 KNN (default) | 362.6 | 350.9 | 363.6 |
| B4 Farneback (default) | 85.3 | 84.6 | 85.8 |
| B1 Frame Difference (tuned) | 2545.9 | 2380.5 | 2691.0 |
| B2 MOG2 (tuned) | 598.2 | 591.4 | 612.7 |
| B3 KNN (tuned) | 403.2 | 396.9 | 415.0 |
| B4 Farneback (tuned) | 85.8 | 79.1 | 88.7 |

## Keterbatasan (cantumkan di paper)

- Box GT diturunkan dari mask piksel, bukan anotasi manusia; lihat sensitivitas GT.
- Metrik piksel dihitung pada resolusi kerja (bukan resolusi asli) bila `resize_width` diisi; tidak setara persis dengan papan peringkat resmi CDnet.
- Rerata aritmetika per sekuens -> kategori -> keseluruhan mengikuti konvensi CDnet; rerata F per sekuens tidak sama dengan F dari rerata Precision/Recall.
- Hanya lima kategori (kamera diam); PTZ, cameraJitter, turbulence, dll. tidak dinilai.
- Satu parameter sensitivitas per algoritma yang dituning; parameter lain default.
- Uji sign-flip menggunakan rerata per kategori sebagai unit inferensial; CI bootstrap bersyarat kategori tetap.
- Data development/test v2 telah ditinjau dan bersifat eksploratori, bukan holdout buta yang baru.
- Enam kategori confirmatory merupakan distribusi kondisi berbeda (domain shift), bukan sampel IID dari 5 kategori awal.
- Komparasi threshold 320px tidak langsung setara dengan benchmark leaderboard resolusi asli.
- FPS spesifik perangkat/versi OpenCV; diukur serial pada subset frame.
