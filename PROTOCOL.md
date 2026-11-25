# Protokol penelitian v3 — dikunci sebelum evaluasi kategori baru

**Judul kerja:** *Threshold Generalization and Preprocessing Interactions in Classical Foreground Segmentation: A Controlled Evaluation on CDnet2014.*

**Jenis studi:** evaluasi empiris dan pengujian transfer lintas-kategori untuk metode klasik yang sudah ada. **Tidak mengklaim algoritma baru atau hasil state-of-the-art.**

**Provenance:** Notebook HTML versi 2 dan `results-2.zip` sudah pernah dijalankan dan hasilnya dianalisis. Ke-26 sekuens (10 tuning dan 16 test pada lima kategori) **bukan lagi data konfirmatori baru**. Semua nama sekuens sebelumnya dicatat di `protocol/seen_v2.json`. Hasil v2 hanya layak sebagai *exploratory development findings*.

## Rancangan utama

1. **Development (sudah pernah dianalisis):** baseline, dynamicBackground, nightVideos, badWeather, shadow. Hasil dapat direproduksi untuk pengecekan bug dan ilustrasi, bukan bukti pengujian independen baru.
2. **Konfirmatori prospektif:** enam kategori berbeda yang belum digunakan di v2: `cameraJitter`, `intermittentObjectMotion`, `lowFramerate`, `PTZ`, `thermal`, `turbulence`. Semua video di enam kategori diikutkan. Tidak boleh melakukan seleksi sekuens atau pembatasan jumlah frame.
3. **Parameter dibekukan:** Frame Difference `fixed_thr=5`; MOG2 `var_threshold=25`; KNN `dist2_threshold=600`; Farneback `flow_thr=1.0`. Parameter lainnya mengikuti kode dan `run_info_v2.json`. **Seluruh metode memakai lebar kerja 320 piksel**, karena threshold v2 dipilih pada resolusi tersebut. GT di-resize dengan *nearest neighbour*.
4. **Tidak ada tuning** atau perubahan preprocessing setelah data kategori baru dibuka. Bila ada bug, perbaikan wajib dicatat, keluaran lama dibatalkan dan status independensi dinilai ulang.
5. Evaluasi bukan angka yang sebanding langsung dengan CDnet leaderboard resmi jika tidak mengikuti seluruh resolusi/protokol resminya. Kategori konfirmatori merupakan *out-of-category distribution shift*, bukan sampel iid dari kategori awal.

## Definisi evaluasi

- **Primary endpoint:** pixel-level F1. Prediksi biner; GT 255 = foreground, 0 dan 50 = negative/background, 85 dan 170 = excluded; ROI.bmp wajib diterapkan pada metrik GT dan mask prediksi; temporalROI.txt membatasi frame dinilai; hitungan TP/FP/FN/TN diakumulasi untuk per-sekuens.
- **Agregasi:** per-sekuens metric, lalu *macro* average di dalam kategori, lalu *macro* across categories. Semua kategori berbobot sama; *macro F1* tidak sama dengan F1 dari rerata P dan R.
- **Unit inferensi:** kategori (6 unit). Besaran efek merupakan rerata efek pasangan algoritma/ablasi per kategori. P-value dari exact *sign-flip* test atas enam efek kategori; bukan ribuan frame yang diperlakukan sebagai observasi independen.
- **Confidence intervals:** *stratified within-category bootstrap*, 5000 resamples. CI ini bersyarat atas kategori yang dievaluasi; **bukan** interval generalisasi untuk semua kategori tak teramati. Gunakan CI beserta ukuran efek, jangan hanya p-value.
- **Secondary:** Precision, Recall, PWC, frame-MCC, box-F1@IoU=0.5. Bounding box GT diekstrak dari mask segmentasi dan bukan anotasi kotak independen; laporkan sensitivitas konstruksi GT. Benchmark FPS adalah *processing-only* (tidak termasuk JPEG decoding/resizing/GT I/O), 1 proses / 1 OpenCV thread / 1 detektor per run, warmup dibuang.

## Hipotesis konfirmatori — directional

**Keluarga algoritma:**

- **H1:** rerata efek `F1(MOG2) − F1(FrameDifference)` di enam kategori baru **positif**.
- **H2:** rerata efek `F1(KNN) − F1(FrameDifference)` di enam kategori baru **positif**.

**Keluarga preprocessing (faktorial Frame Difference):**

- **H3:** efek utama Gaussian Blur pada `pixel-FPR` adalah **negatif**.
- **H4:** efek utama operasi morfologi pada `pixel-F1` adalah **positif**.

Keempat arah di atas didasarkan pada studi pengembangan, bukan hasil data kategori konfirmatori. P-value konfirmatori satu sisi dengan alternatif seperti di atas, dikoreksi **Holm di setiap keluarga berisi dua pengujian**. Perubahan arah hipotesis setelah melihat data tidak diperbolehkan. Pelaporan menyertakan nilai p dua sisi deskriptif serta semua ukuran efek (termasuk yang berlawanan arah). Penggunaan uji satu sisi harus dijelaskan dan dapat dipertahankan secara ilmiah.

**Analisis eksploratori:** Farneback-vs-metode lain, seluruh pasangan algoritma, Friedman per-sekuens, semua faktor/tingkat interaksi, threshold Otsu, per kategori, dan box GT sensitivity. Nilai p tabel-tabel ini tidak boleh dicampur atau diberi narasi sebagai konfirmasi empat hipotesis utama. Hindari memilih hanya perbandingan yang signifikan.

## Ketentuan transparansi

- Catat sumber unduhan CDnet2014, versi, lisensi, tanggal akses, nama dan jumlah sekuens, serta hash kode/perintah.
- Simpan `run_info.json`, `splits.csv`, `all_per_seq.csv`, semua keluaran, commit Git, `pip freeze`, informasi CPU/RAM/OS/OpenCV dan seed.
- Jangan mengklaim peringkat state-of-the-art atau perbaikan metode baru hanya dari perubahan pilihan parameter.
- Bila kategori konfirmatori ternyata pernah dipakai sebelumnya untuk memilih hipotesis/parameter, sebut eksploratori dan rancang pengujian independen lain.
- Jangan memperbarui hipotesis ketika hanya ada enam kategori untuk memperoleh signifikansi. Bila hasil tidak signifikan, laporkan apa adanya.
- Untuk target SINTA 2, pilih jurnal yang sejalan dengan *computer vision / image processing*, verifikasi akreditasi, lalu ikuti template dan kebijakan data/etika/referensinya. **Akreditasi SINTA 2 melekat pada jurnal, bukan sertifikat kesiapan naskah ini.**

## Kelemahan yang harus didiskusikan

Pemilihan kategori konfirmatori berbeda dari lima kategori awal dan menimbulkan *domain shift*; kelompok kategori hanya enam, sehingga daya uji terbatas; shadow label 50 diperlakukan sebagai background sesuai definisi yang dipilih (beda kebijakan metrik akan mengubah angka); metrik box bersifat turunan; 320 px bukan resolusi asli; hanya metode klasik dibandingkan; tidak ada pembandingan terbaru terhadap arsitektur deep learning; dan hasil CV2/kecepatan bergantung versi/perangkat.

**Dasar dataset:** Wang et al. (2014), *CDnet 2014: An Expanded Change Detection Benchmark Dataset*, CVPR Workshops — https://openaccess.thecvf.com/content_cvpr_workshops_2014/W12/html/Wang_CDnet_2014_An_2014_CVPR_paper.html . Portal dataset: https://jacarini.dinf.usherbrooke.ca/dataset2014/ .
