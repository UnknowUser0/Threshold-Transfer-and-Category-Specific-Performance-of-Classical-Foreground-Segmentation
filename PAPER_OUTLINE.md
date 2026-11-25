# Rencana penyusunan paper — bukan naskah berisi hasil baru

## Pilihan judul

**Threshold Generalization and Preprocessing Interactions in Classical Foreground Segmentation: A Controlled Evaluation on CDnet2014**

Bila hasil tak mendukung klaim besar, gunakan judul yang lebih netral: **An Empirical Assessment of Threshold Transferability and Preprocessing Effects Across CDnet2014 Categories**.

## Struktur IMRaD yang dapat diuji

### Abstract (150–250 kata sesuai jurnal)
- Latar: tantangan generalisasi metode foreground segmentation klasik terhadap kondisi berbeda.
- Gap: evaluasi threshold yang dipilih pada domain lama dan ditransfer tanpa tuning ke domain baru, beserta interaksi preprocessing.
- Metode: 4 algoritma, development 26 sequences/5 categories; confirmatory 6 kategori lain, 320px fixed, uji berbasis kategori.
- Hasil: isi setelah run asli; laporkan efek, F1 dan interval kepercayaan tanpa mengganti output kosong dengan angka v2.
- Kesimpulan: dibatasi konteks yang benar-benar didukung data.

### 1. Introduction
Motivasi low-resource foreground segmentation, alasan empat algoritma, pertanyaan generalisasi, kontribusi **empiris**, bukan arsitektur model baru. Bahas pembatasan transfer threshold 320 px dan domain shift.

### 2. Related Work
CDnet2014 benchmark original; FD/MOG2/KNN/Farneback classical baselines; dampak blur/morfologi/threshold; pemodelan background yang lebih modern; gap studi yang relevan untuk publikasi tahun submit. Buat matriks research gap (metode × kondisi × validasi independen × preprocessing × speed). **Wajib riset literatur terbaru dan kutip dari artikel primer.**

### 3. Method
- Dataset provenance, distribusi 11 kategori, 5 development + 6 out-of-category holdout.
- Penanganan GT/ROI (255,0,50,85,170), penghitungan per sekuens, agregasi antar kategori.
- Tuning *development-only*, threshold beku, pipeline dan parameter lengkap.
- Hipotesis arah H1–H4, factorial design, unit inferensi kategori, exact sign-flip satu sisi, Holm dalam keluarga, CI bersyarat kategori tetap.
- Benchmark FPS tanpa I/O JPEG, satu detektor sekali ukur, environment lengkap.

### 4. Results
**Tabel A — Development v2 sebagai eksplorasi:** 4 algoritma, parameter & F1; transparan bahwa sudah dianalisis sebelumnya.
**Tabel B — Hasil kategori confirmatory baru:** Precision, Recall, F1, PWC, mean & CI, kategori terpisah.
**Tabel C — Efek konfirmatori H1–H4:** effect size, sign, p one-sided, adjusted Holm, p two-sided deskriptif dan kategori n=6.
**Tabel D — Preprocessing factorial:** seluruh 2×2×2 cell FD dan efek per faktor beserta interaksi; MOG2 2×2.
**Tabel E — Efisiensi:** per-algoritma FPS; full reproducibility config.
**Gambar A — F1 per kategori** dengan peta efek relatif, **Gambar B — Tradeoff speed vs F1**, **Gambar C — Visualisasi prediksi dan GT**.

### 5. Discussion
Analisis berapa jauh peringkat di lima kategori awal berubah ketika diterapkan pada enam kategori baru, alasan kausal yang plausibel (JANGAN sebut terbukti tanpa rancangan kausal), dampak preprocessing, risiko nilai p signifikan palsu, keterbatasan 320px dan baseline klasik. Posisikan terhadap literatur terkini.

### 6. Conclusion
Jawab pertanyaan penelitian sesuai bukti yang tersedia; rekomendasi praktis dibatasi pada frame 320px dan CPU/OpenCV yang dipakai.

## Gerbang kualitas sebelum submit

| Gerbang | Persyaratan | Saat paket dibuat |
|---|---|---|
| A | Kode versi baru lengkap & dapat dieksekusi dengan fixture sintetis | Tercapai, lihat laporan verifikasi |
| B | 26 sekuens lama diblok pada run confirmatory | Tercapai lewat guard + unit test |
| C | Hasil CDnet 6 kategori baru diproduksi dengan threshold beku | **Belum**, dataset tidak tersedia di paket |
| D | Statistik utama dibahas, dibenarkan dan disetujui pembimbing | Belum |
| E | Related work dan research gap aktual serta novelty substansial | Belum |
| F | Data, reproducibility dan figures dari run asli terverifikasi | Belum |
| G | Pilih jurnal SINTA 2 yang tepat dan ikuti author guidelines | Belum |
| H | Pengecekan plagiarisme, atribusi, template, etika, pernyataan kontribusi | Belum |

**Catatan keputusan:** Tercapainya A dan B tidak berarti C–H otomatis terpenuhi. Jangan submit sebelum gerbang C–H selesai.
