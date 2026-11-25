# Laporan Eksperimen B (CDnet 2014)

**Data:** 26 sekuens, kategori badWeather, baseline, dynamicBackground, nightVideos, shadow; 10 sekuens tune, 16 sekuens test (seed 42, lihat `splits.csv`).  
**Resolusi kerja:** 320 px (lebar). **Pipeline B1-B4:** blur 5x5, ambang tetap, morfologi open(3)+close(7), kontur >= 0.10% luas frame.  
**Lingkungan:** Intel64 Family 6 Model 191 Stepping 2, GenuineIntel, OpenCV 5.1.0, Python 3.15.2.  
**Parameter terpilih (tune):** `{"frame_diff": {"fixed_thr": 5}, "mog2": {"var_threshold": 25}, "knn": {"dist2_threshold": 600.0}, "farneback": {"flow_thr": 1.0}}`.

**Definisi metrik.** Piksel (utama): label GT 255 = positif; 0 dan 50 (hard shadow) = negatif; 85 (luar ROI) dan 170 (unknown) diabaikan; prediksi di luar ROI dinolkan; metrik dihitung per sekuens lalu dirata-rata per kategori dan antar-kategori. Frame: positif = ada >= 1 box; MCC. Box GT diturunkan dari mask label 255 (closing 5x5, kontur >= 0.10% luas); TP box = pencocokan satu-ke-satu dengan IoU >= 0.5. 'IoU (TP)' = rerata IoU pasangan TP.

### Parameter terpilih pada sekuens tune (metrik: F piksel)

| Algoritma | Parameter | Default | Terpilih | F piksel (tune) |
|---|---|---|---|---|
| frame_diff | fixed_thr | 25 | 5 | 0.372 |
| mog2 | var_threshold | 16 | 25 | 0.543 |
| knn | dist2_threshold | 400 | 600 | 0.600 |
| farneback | flow_thr | 1 | 1 | 0.387 |

### Hasil utama pada 16 sekuens uji (rerata antar-kategori; metrik piksel CDnet; CI95 bootstrap bertingkat)

| Algoritma | P | R | F [CI95] | PWC | MCC frame | F1 box@0.5 | IoU (TP) | FPS (median) |
|---|---|---|---|---|---|---|---|---|
| B1 Frame Difference (tuned) | 0.423 | 0.666 | 0.448 [0.392, 0.502] | 4.68 | 0.367 [0.280, 0.456] | 0.273 | 0.674 | 3080 |
| B2 MOG2 (tuned) | 0.628 | 0.617 | 0.572 [0.449, 0.697] | 1.94 | 0.555 [0.446, 0.660] | 0.386 | 0.717 | 612 |
| B3 KNN (tuned) | 0.706 | 0.590 | 0.586 [0.481, 0.692] | 1.69 | 0.588 [0.482, 0.683] | 0.379 | 0.716 | 492 |
| B4 Farneback (tuned) | 0.371 | 0.753 | 0.460 [0.383, 0.542] | 4.23 | 0.325 [0.194, 0.459] | 0.129 | 0.618 | 87 |
| Selalu foreground (trivial) | 0.027 | 1.000 | 0.052 [0.034, 0.071] | 97.26 | 0 | - | - | - |

### Konfigurasi default vs tuned (F piksel, rerata antar-kategori)

| Algoritma | Parameter | Default | Tuned | F piksel default (test) | F piksel tuned (test) | F piksel default (semua seq) |
|---|---|---|---|---|---|---|
| B1 Frame Difference | fixed_thr | 25 | 5 | 0.344 | 0.448 | 0.274 |
| B2 MOG2 | var_threshold | 16 | 25 | 0.551 | 0.572 | 0.536 |
| B3 KNN | dist2_threshold | 400 | 600 | 0.586 | 0.586 | 0.577 |
| B4 Farneback | flow_thr | 1 | 1 | 0.460 | 0.460 | 0.428 |

### F piksel per kategori CDnet (algoritma tuned, sekuens uji)

| Kategori | n | B1 Frame Difference | B2 MOG2 | B3 KNN | B4 Farneback | Selalu FG |
|---|---|---|---|---|---|---|
| badWeather | 2 | 0.329 | 0.450 | 0.502 | 0.592 | 0.055 |
| baseline | 2 | 0.795 | 0.815 | 0.840 | 0.514 | 0.066 |
| dynamicBackground | 4 | 0.136 | 0.523 | 0.508 | 0.310 | 0.013 |
| nightVideos | 4 | 0.405 | 0.368 | 0.377 | 0.355 | 0.040 |
| shadow | 4 | 0.574 | 0.705 | 0.702 | 0.528 | 0.088 |

### Uji primer (F piksel, efek = tuned B - B1t; Wilcoxon per sekuens, Holm m=3)

| Perbandingan | n | efek [CI95] | menang | p | p Holm |
|---|---|---|---|---|---|
| B2t - B1t | 16 | 0.124 [0.014, 0.239] | 12/16 | 0.058 | 0.173 |
| B3t - B1t | 16 | 0.138 [0.035, 0.240] | 11/16 | 0.058 | 0.173 |
| B4t - B1t | 16 | 0.012 [-0.036, 0.062] | 6/16 | 0.900 | 0.900 |

### Uji sekunder: 6 pasangan algoritma tuned (Holm per metrik)

| Metrik | Perbandingan | n | efek [CI95] | menang | p | p Holm |
|---|---|---|---|---|---|---|
| F piksel | B2t - B1t | 16 | 0.124 [0.014, 0.238] | 12/16 | 0.058 | 0.231 |
| F piksel | B3t - B1t | 16 | 0.138 [0.036, 0.240] | 11/16 | 0.058 | 0.231 |
| F piksel | B4t - B1t | 16 | 0.012 [-0.035, 0.060] | 6/16 | 0.900 | 1.000 |
| F piksel | B3t - B2t | 16 | 0.014 [-0.019, 0.046] | 8/16 | 0.744 | 1.000 |
| F piksel | B4t - B2t | 16 | -0.113 [-0.221, -0.004] | 3/16 | 0.025 | 0.150 |
| F piksel | B4t - B3t | 16 | -0.126 [-0.228, -0.021] | 4/16 | 0.029 | 0.150 |
| MCC frame | B2t - B1t | 14 | 0.211 [0.160, 0.260] | 9/14 | 0.068 | 0.232 |
| MCC frame | B3t - B1t | 14 | 0.248 [0.164, 0.329] | 10/14 | 0.058 | 0.232 |
| MCC frame | B4t - B1t | 14 | -0.039 [-0.109, 0.022] | 3/14 | 0.135 | 0.271 |
| MCC frame | B3t - B2t | 16 | 0.033 [-0.025, 0.096] | 10/16 | 0.821 | 0.821 |
| MCC frame | B4t - B2t | 15 | -0.262 [-0.353, -0.174] | 4/15 | 0.003 | 0.016 |
| MCC frame | B4t - B3t | 15 | -0.306 [-0.441, -0.174] | 4/15 | 0.010 | 0.051 |
| F1 box@0.5 | B2t - B1t | 16 | 0.114 [0.025, 0.203] | 11/16 | 0.065 | 0.134 |
| F1 box@0.5 | B3t - B1t | 16 | 0.106 [0.001, 0.206] | 12/16 | 0.039 | 0.134 |
| F1 box@0.5 | B4t - B1t | 16 | -0.144 [-0.171, -0.120] | 3/16 | 0.034 | 0.134 |
| F1 box@0.5 | B3t - B2t | 16 | -0.007 [-0.050, 0.034] | 9/16 | 0.860 | 0.860 |
| F1 box@0.5 | B4t - B2t | 16 | -0.257 [-0.350, -0.171] | 2/16 | 0.003 | 0.016 |
| F1 box@0.5 | B4t - B3t | 16 | -0.250 [-0.355, -0.141] | 2/16 | 0.003 | 0.017 |

Friedman (F piksel, tuned): chi2=10.350, p=0.016, n=16

### Ablasi faktorial frame_diff (b=blur, m=morfologi; tuned; sekuens uji)

| Sel | P | R | F [CI95] |
|---|---|---|---|
| b0-fixed-m0 | 0.212 | 0.598 | 0.259 [0.214, 0.307] |
| b0-fixed-m1 | 0.380 | 0.685 | 0.418 [0.368, 0.462] |
| b0-otsu-m0 | 0.420 | 0.220 | 0.236 [0.207, 0.262] |
| b0-otsu-m1 | 0.530 | 0.212 | 0.266 [0.228, 0.304] |
| b1-fixed-m0 | 0.394 | 0.547 | 0.390 [0.337, 0.439] |
| b1-fixed-m1 | 0.423 | 0.666 | 0.448 [0.393, 0.502] |
| b1-otsu-m0 | 0.493 | 0.231 | 0.275 [0.242, 0.306] |
| b1-otsu-m1 | 0.538 | 0.279 | 0.327 [0.286, 0.368] |

### Efek faktorial frame_diff (kontras on-off, Wilcoxon per sekuens, Holm per metrik)

| Metrik | Efek | n | efek [CI95] | menang | p | p Holm |
|---|---|---|---|---|---|---|
| px_f | blur | 16 | 0.066 [0.049, 0.086] | 16/16 | <0.001 | <0.001 |
| px_f | otsu | 16 | -0.103 [-0.142, -0.063] | 6/16 | 0.065 | 0.196 |
| px_f | morph | 16 | 0.075 [0.058, 0.093] | 16/16 | <0.001 | <0.001 |
| px_f | blur x otsu | 16 | -0.015 [-0.027, -0.003] | 6/16 | 0.562 | 0.562 |
| px_f | blur x morph | 16 | -0.020 [-0.030, -0.010] | 4/16 | 0.039 | 0.155 |
| px_f | otsu x morph | 16 | -0.034 [-0.045, -0.024] | 5/16 | 0.083 | 0.196 |
| px_f | blur x otsu x morph | 16 | 0.031 [0.024, 0.039] | 14/16 | 0.001 | 0.007 |
| px_precision | blur | 16 | 0.076 [0.052, 0.111] | 13/16 | 0.002 | 0.009 |
| px_precision | otsu | 16 | 0.143 [0.109, 0.174] | 14/16 | <0.001 | 0.003 |
| px_precision | morph | 16 | 0.088 [0.066, 0.112] | 16/16 | <0.001 | <0.001 |
| px_precision | blur x otsu | 16 | -0.036 [-0.052, -0.020] | 5/16 | 0.074 | 0.148 |
| px_precision | blur x morph | 16 | -0.051 [-0.072, -0.034] | 2/16 | 0.001 | 0.007 |
| px_precision | otsu x morph | 16 | -0.010 [-0.020, -0.001] | 7/16 | 0.669 | 0.669 |
| px_precision | blur x otsu x morph | 16 | 0.019 [0.010, 0.027] | 11/16 | 0.039 | 0.116 |
| px_recall | blur | 16 | 0.002 [-0.012, 0.014] | 11/16 | 0.193 | 0.193 |
| px_recall | otsu | 16 | -0.388 [-0.448, -0.329] | 0/16 | <0.001 | <0.001 |
| px_recall | morph | 16 | 0.062 [0.047, 0.077] | 15/16 | <0.001 | <0.001 |
| px_recall | blur x otsu | 16 | 0.037 [0.029, 0.045] | 16/16 | <0.001 | <0.001 |
| px_recall | blur x morph | 16 | 0.022 [0.018, 0.026] | 16/16 | <0.001 | <0.001 |
| px_recall | otsu x morph | 16 | -0.041 [-0.051, -0.031] | 1/16 | <0.001 | <0.001 |
| px_recall | blur x otsu x morph | 16 | 0.006 [0.004, 0.009] | 11/16 | 0.025 | 0.050 |
| px_fpr | blur | 16 | -0.024 [-0.041, -0.012] | 1/16 | <0.001 | <0.001 |
| px_fpr | otsu | 16 | -0.048 [-0.069, -0.027] | 0/16 | <0.001 | <0.001 |
| px_fpr | morph | 16 | -0.013 [-0.019, -0.008] | 1/16 | <0.001 | <0.001 |
| px_fpr | blur x otsu | 16 | 0.018 [0.011, 0.025] | 15/16 | <0.001 | <0.001 |
| px_fpr | blur x morph | 16 | 0.013 [0.010, 0.018] | 16/16 | <0.001 | <0.001 |
| px_fpr | otsu x morph | 16 | 0.006 [0.002, 0.009] | 13/16 | 0.009 | 0.009 |
| px_fpr | blur x otsu x morph | 16 | -0.006 [-0.009, -0.003] | 1/16 | 0.004 | 0.008 |

### Ablasi faktorial mog2 (b=blur, m=morfologi; tuned; sekuens uji)

| Sel | P | R | F [CI95] |
|---|---|---|---|
| b0-fixed-m0 | 0.542 | 0.587 | 0.521 [0.415, 0.628] |
| b0-fixed-m1 | 0.657 | 0.610 | 0.585 [0.459, 0.708] |
| b1-fixed-m0 | 0.590 | 0.588 | 0.544 [0.426, 0.662] |
| b1-fixed-m1 | 0.628 | 0.617 | 0.572 [0.448, 0.694] |

### Efek faktorial mog2 (kontras on-off, Wilcoxon per sekuens, Holm per metrik)

| Metrik | Efek | n | efek [CI95] | menang | p | p Holm |
|---|---|---|---|---|---|---|
| px_f | blur | 16 | 0.005 [-0.005, 0.017] | 8/16 | 0.744 | 0.744 |
| px_f | morph | 16 | 0.046 [0.028, 0.063] | 15/16 | <0.001 | <0.001 |
| px_f | blur x morph | 16 | -0.018 [-0.026, -0.010] | 4/16 | 0.003 | 0.005 |
| px_precision | blur | 16 | 0.009 [-0.004, 0.021] | 7/16 | 0.940 | 0.940 |
| px_precision | morph | 16 | 0.076 [0.043, 0.108] | 15/16 | <0.001 | <0.001 |
| px_precision | blur x morph | 16 | -0.038 [-0.055, -0.020] | 1/16 | <0.001 | <0.001 |
| px_recall | blur | 16 | 0.004 [-0.006, 0.013] | 9/16 | 0.274 | 0.274 |
| px_recall | morph | 16 | 0.026 [0.015, 0.036] | 13/16 | 0.002 | 0.006 |
| px_recall | blur x morph | 16 | 0.003 [-0.000, 0.006] | 13/16 | 0.130 | 0.259 |
| px_fpr | blur | 16 | 0.000 [-0.001, 0.001] | 9/16 | 0.821 | 0.821 |
| px_fpr | morph | 16 | -0.002 [-0.003, -0.001] | 2/16 | <0.001 | 0.001 |
| px_fpr | blur x morph | 16 | 0.001 [0.001, 0.002] | 16/16 | <0.001 | <0.001 |

### Sensitivitas lantai Otsu (frame difference, blur + Otsu + morfologi)

| Lantai Otsu | P | R | F [CI95] |
|---|---|---|---|
| 0 | 0.104 | 0.335 | 0.130 [0.084, 0.174] |
| 5 | 0.456 | 0.292 | 0.294 [0.262, 0.325] |
| 10 | 0.538 | 0.279 | 0.327 [0.286, 0.368] |
| 15 | 0.630 | 0.264 | 0.334 [0.285, 0.384] |
| 20 | 0.682 | 0.244 | 0.324 [0.272, 0.376] |

### Pengujian hipotesis (Holm atas 5 hipotesis). Biaya komputasi H5: B4t 35.5x lebih lambat dari B1t

| Hipotesis | Metrik | Efek [CI95] | p | p Holm | Keputusan |
|---|---|---|---|---|---|
| H1: MOG2 > Frame Difference pada background dinamis (default, semua seq kategori dynamicBackground) | F piksel | 0.332 [0.180, 0.498] | 0.031 | 0.094 | tidak terbukti |
| H2: Gaussian Blur menurunkan false positive (FPR piksel turun) | FPR piksel | -0.024 [-0.041, -0.012] | <0.001 | <0.001 | didukung |
| H3: Otsu meningkatkan deteksi (F piksel naik) | F piksel | -0.103 [-0.140, -0.063] | 0.065 | 0.131 | tidak terbukti |
| H4: Morfologi memperbaiki foreground (F piksel naik) | F piksel | 0.075 [0.058, 0.094] | <0.001 | <0.001 | didukung |
| H5: Optical flow lebih baik dari Frame Difference (F piksel, tuned) | F piksel | 0.012 [-0.035, 0.062] | 0.900 | 0.900 | tidak terbukti |

### Sensitivitas terhadap konstruksi box GT (tuned, sekuens uji): peringkat stabil bila urutan & tau tetap

| Varian GT | B1 F1 box | B2 F1 box | B3 F1 box | B4 F1 box | Urutan | tau vs primer |
|---|---|---|---|---|---|---|
| primer | 0.273 | 0.386 | 0.379 | 0.129 | B2 > B3 > B1 > B4 | 1.00 |
| tanpa_close | 0.272 | 0.385 | 0.379 | 0.128 | B2 > B3 > B1 > B4 | 1.00 |
| close9 | 0.282 | 0.393 | 0.381 | 0.134 | B2 > B3 > B1 > B4 | 1.00 |
| area_kecil | 0.267 | 0.382 | 0.373 | 0.127 | B2 > B3 > B1 > B4 | 1.00 |
| area_besar | 0.274 | 0.386 | 0.380 | 0.131 | B2 > B3 > B1 > B4 | 1.00 |

### Processing FPS: serial, 1 thread OpenCV, 300 frame pertama dari 1 sekuens/kategori, median dari 5 pengulangan

| Eksperimen | fps_median | fps_min | fps_max |
|---|---|---|---|
| B1 Frame Difference (default) | 3390.6 | 3107.7 | 3672.9 |
| B1 Frame Difference (tuned) | 3080.1 | 2396.7 | 3277.4 |
| B2 MOG2 (default) | 606.2 | 546.4 | 634.0 |
| B2 MOG2 (tuned) | 611.7 | 563.0 | 641.1 |
| B3 KNN (default) | 466.4 | 414.2 | 486.6 |
| B3 KNN (tuned) | 492.0 | 423.8 | 514.8 |
| B4 Farneback (default) | 86.5 | 80.9 | 89.7 |
| B4 Farneback (tuned) | 86.7 | 81.0 | 89.7 |

## Keterbatasan (cantumkan di paper)

- Box GT diturunkan dari mask piksel, bukan anotasi manusia; lihat sensitivitas GT.
- Metrik piksel dihitung pada resolusi kerja (bukan resolusi asli) bila `resize_width` diisi; tidak setara persis dengan papan peringkat resmi CDnet.
- Rerata aritmetika per sekuens -> kategori -> keseluruhan mengikuti konvensi CDnet; rerata F per sekuens tidak sama dengan F dari rerata Precision/Recall.
- Hanya lima kategori (kamera diam); PTZ, cameraJitter, turbulence, dll. tidak dinilai.
- Satu parameter sensitivitas per algoritma yang dituning; parameter lain default.
- Sekuens dalam satu kategori tidak sepenuhnya independen; uji memakai sekuens sebagai unit.
- FPS spesifik perangkat/versi OpenCV; diukur serial pada subset frame.
