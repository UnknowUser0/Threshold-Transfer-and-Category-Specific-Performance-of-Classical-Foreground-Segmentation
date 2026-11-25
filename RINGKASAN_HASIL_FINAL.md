# Ringkasan hasil CDnet2014 untuk naskah target IJCCS

**Status:** audit teknis lulus dan manuskrip berformat IJCCS telah dibuat. Dataset CDnet2014 tersedia lokal untuk dua pilot post-hoc. Metadata penulis dan verifikasi layout akhir masih diperlukan sebelum submit.

## Hasil riil yang dapat dilaporkan

Sebanyak **26 sekuens dari lima kategori** digunakan dalam development (10 tuning + 16 test development yang hasilnya telah diperiksa). Sebanyak **27 sekuens dari enam kategori berbeda** kemudian diuji dengan parameter terpilih yang dibekukan. Jadi keseluruhan 53 sekuens mencakup 11 kategori, tetapi **bukan 53 sekuens test independen**.

### Rata-rata F1 piksel per kategori — 27 sekuens tahap evaluasi

| Metode | F1 | Interval bootstrap 95% | FPS processing-only |
|---|---:|---|---:|
| Frame Difference | 0,230 | 0,172–0,287 | 2546 |
| MOG2 | 0,471 | 0,405–0,545 | 598 |
| KNN | 0,483 | 0,404–0,562 | 403 |
| Farneback | 0,203 | 0,151–0,253 | 86 |

KNN menang dalam rerata deskriptif, tetapi hasil pengujian hipotesis H1 dan H2 **tidak signifikan** sesudah Holm (p = 0,062). MOG2 menang pada kategori turbulence F1 0,626; Frame Difference justru menang kategori PTZ F1 0,316. Threshold KNN default menghasilkan F1 0,489 sedangkan threshold tune 0,483 di kategori baru.

### Empat hipotesis terdokumentasi

| Kontras | p Holm | Makna |
|---|---:|---|
| H1 MOG2 > Frame Difference | 0,062 | Tidak signifikan |
| H2 KNN > Frame Difference | 0,062 | Tidak signifikan |
| H3 Gaussian Blur mengurangi FPR | 0,031 | Didukung dalam uji satu sisi yang didokumentasikan |
| H4 Morfologi meningkatkan F1 | 0,031 | Didukung dalam uji satu sisi yang didokumentasikan |

**Peringatan:** H3/H4 hanya boleh disebut *konfirmatori yang dipreregistrasi* jika tersedia bukti objektif waktu penetapan arah hipotesis **sebelum** hasil kategori baru diperiksa. Jika bukti itu tidak ada, ungkap secara transparan dan pertimbangkan label analisis eksploratori. Tidak boleh menutupi hasil dua sisi yang lebih konservatif.

## Kontribusi penelitian yang dapat dipertahankan

- Pemisahan eksplisit fase tuning dan evaluasi pada kategori berbeda.
- Laporan ketidakstabilan ranking berdasarkan kategori dan transfer threshold yang tidak selalu menguntungkan.
- Definisi ground truth dan ROI yang didokumentasikan dan konsisten secara komputasional.
- Uji pasangan dengan unit kategori dan koreksi banyak hipotesis.
- Analisis *post-hoc* yang menonjolkan kegagalan PTZ/intermittentPan, tanpa mengarang sebab mekanismenya.
- Analisis temporal tiga sekuens pada 6.653 frame anotasi; bersifat eksploratori dan frame bukan unit inferensi independen.
- Sensitivitas resolusi 320/640/native pada tiga sekuens; post-hoc, dengan parameter numerik 320 piksel dibekukan.

Tidak ada penemuan algoritma baru. Manuskrip ini paling tepat diposisikan sebagai studi empiris terkait *evaluation protocol*, *algorithm selection* dan *threshold robustness*. Kelayakannya untuk jurnal SINTA 2 bergantung pada scope dan mutu argumen novelty, bukan hanya angka F1.

## Yang sudah benar-benar diselesaikan di paket ini

- Gabungan kode runner dan notebook V3/V4 yang tetap bisa diaudit.
- Satu `run_final.py` untuk semua audit dan analisis tambahan.
- Analisis temporal dan resolusi pada data lokal; evaluasi mask eksternal tetap berupa adapter tanpa prediksi model modern.
- Tabel gabungan sebelas kategori dengan label development vs evaluation.
- Manuskrip Word dan Markdown, abstrak bilingual, 12 referensi bernomor, panduan dan template resmi IJCCS.
- 21 pengujian otomatis lulus; tujuh hash sumber lama cocok.
- Error dependensi `tabulate` sudah ditangani pada requirements lingkungan baru.

## Hal yang belum boleh diklaim selesai

- Replikasi pihak ketiga dari video dan anotasi mentah; berkas dataset sengaja tidak dimasukkan ke ZIP.
- Performa model deep learning pembanding, karena tidak ada checkpoint/prediksi yang diberikan.
- Bukti timestamp independen untuk preregistrasi.
- Metadata penulis, surat pernyataan, dan inspeksi visual Word untuk memastikan batas 10–12 halaman IJCCS.
- Penerimaan jurnal.

**Gunakan `START_HERE.md` untuk menjalankan, `paper/MANUSCRIPT_MASTER.docx` untuk menulis, dan `SUBMISSION_GATE.md` sebelum submit.**
