# CDnet2014 — MASTER FINAL RESEARCH PACKAGE

**Satu paket konsolidasi, bukan rangkaian V5/V6/V7.** Semua kode dan hasil lama yang disuplai telah dipertahankan, sementara analisis lanjut dan naskah ditempatkan dalam satu struktur.

## 1. Status riil (22 November 2026)

| Komponen | Status | Bukti |
|---|---|---|
| Development (26 sekuens, 5 kategori) | Telah dijalankan | working/results-v3-development |
| Evaluasi lanjutan terpisah (27 sekuens, 6 kategori) | Telah dijalankan | working/results-v3-confirmatory |
| Analisis eksploratori V4 | Telah dijalankan | working/results-v4-posthoc |
| Audit integritas SHA-256 sumber V4 | Lulus | FINAL_AUDIT.json |
| Unit & integration tests | 21/21 lulus (lingkungan penyusunan) | tests/ |
| Tabel gabungan 11 kategori dengan label fase | Telah dibuat | paper/EVIDENCE_MASTER.md |
| Manuskrip jurnal bahasa Inggris | Tersusun dari hasil riil | paper/MANUSCRIPT_MASTER.md dan .docx |
| Analisis temporal post-hoc (3 sekuens, 6.653 frame berlabel) | Telah dijalankan; eksploratori | working/final-temporal |
| Evaluasi resolusi 320/640/native pada 3 sekuens | Telah dijalankan; eksploratori | working/final-resolution |
| Evaluasi model modern | Adapter tersedia; **belum ada mask/prediksi model** | final_studies/external_masks.py |
| Bukti independen waktu penetapan hipotesis | Belum tersedia | wajib disiapkan jika menulis 'preregistered' |
| Jurnal tujuan SINTA 2 dan author template | IJCCS dipilih; template resmi disertakan | paper/IJCCS_Journal_Template.doc, SUBMISSION_GATE.md |

IJCCS guidance: English manuscript, bilingual abstracts (each <=200 words), 10–12 pages on Letter, 3 cm margins, single spacing, Times New Roman 11 (title 18), one column, IEEE references with URLs, at least 10 references and 80% primary sources. The main experiments remain frozen; three-sequence follow-ups are explicitly exploratory. Acceptance cannot be guaranteed.

## 2. File penting

- `RUN_FINAL_WORKFLOW.ipynb`: satu notebook untuk PyCharm, memuat audit, ringkasan, dan opsi menjalankan analisis tambahan.
- `run_final.py`: satu command-line interface yang memanggil semua studi; tidak ada penomoran versi baru.
- `paper/MANUSCRIPT_MASTER.docx`: draf Word dengan spesifikasi IJCCS; periksa pagination di Microsoft Word.
- `paper/IJCCS_Journal_Template.doc`: template resmi IJCCS dari situs jurnal.
- `paper/MANUSCRIPT_MASTER.md`: sumber naskah yang dapat diedit, lengkap dengan tabel dan referensi terverifikasi.
- `paper/REFERENCES.bib`: sitasi untuk Zotero/Mendeley/BibTeX.
- `paper/EVIDENCE_MASTER.md`: gabungan 11 kategori dengan fase yang dipisahkan.
- `paper/FIG_ALL_11_CATEGORIES_PHASED.png`: heatmap 11 kategori dengan penjelasan perbedaan fase.
- `FINAL_AUDIT.json`: hasil audit yang benar-benar dieksekusi.
- `SUBMISSION_GATE.md`: daftar bukti dan keputusan akhir sebelum kirim.
- `working/results-v3-*` dan `working/results-v4-posthoc`: seluruh data dan keluaran lama. **Jangan overwrite.**

## 3. Cara mulai di PyCharm (notebook)

1. Ekstrak **SELURUH** folder `CDnet_Research_Final/` dalam ZIP ke folder lokal.
2. Buka folder proyek itu sebagai Project di PyCharm (bukan `.ipynb` saja).
3. Pilih kernel Python yang memiliki numpy, pandas, cv2, matplotlib, scipy, tabulate dan notebook support.
4. Buka `RUN_FINAL_WORKFLOW.ipynb`, lalu **Run All**. Cell analisis berat dinonaktifkan (`False`) agar hasil lama tidak terhapus dan tidak terjadi run besar secara tidak sengaja.
5. Periksa output audit dan grafik. Bila ingin memproses video asli, isi `DATASET_DIR` dan aktifkan studi yang dibutuhkan.

Tersedia juga dari terminal di root folder proyek:

```powershell
python run_final.py audit
python run_final.py compile
python run_final.py tests
```

Membuka `RUN_FINAL_WORKFLOW.ipynb` tidak memerlukan pengaturan `CDNET_MODE`. Variabel itu hanya dipakai runner V3 lama untuk fase eksperimen asli dan **tidak perlu dijalankan ulang untuk manuskrip ini**.

## 4. Environment yang disarankan

Untuk **instalasi baru**, gunakan Python 3.11 dan virtual environment terpisah. File `requirements.txt` memuat dependensi yang dipin untuk alur itu, termasuk `tabulate==0.9.0` (perbaikan error `DataFrame.to_markdown()`).

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_final.py tests
```

Hasil asli user dicatat menggunakan Python 3.15.2 dan OpenCV 5.1.0. Environment Python 3.11 **bukan** environment asli; pengulangan hasil adalah replikasi baru yang harus disimpan di lokasi berbeda. Jangan campur `opencv-python` dengan `opencv-python-headless`.

## 5. Analisis temporal per frame (post-hoc, eksploratori)

Jalankan dari root proyek, setelah `DATASET_DIR` benar:

```powershell
python run_final.py temporal --dataset "D:\Datasets\CDnet2014"
```

Default menganalisis tiga sekuens prioritas: `PTZ/intermittentPan`, `turbulence/turbulence0`, dan `cameraJitter/badminton`. Data video harus mengikuti folder CDnet: `<dataset>/<category>/<sequence>/input`, `groundtruth`, `temporalROI.txt`, `ROI.bmp` jika tersedia. Keluaran: `working/final-temporal/` berisi CSV per frame, ringkasan sequence-level, grafik dan overlay. Frame yang dipilih untuk ilustrasi bersifat *post-hoc*.

Untuk menyertakan lebih banyak sekuens, gunakan `--sequences` dengan ID `kategori/sekuens`. Semua frame awal sebelum temporal ROI tetap diproses untuk warm-up model.

## 6. Sensitivitas resolusi (post-hoc, eksploratori)

```powershell
python run_final.py resolution --dataset "D:\Datasets\CDnet2014" --widths 320 640 native
```

Nilai 640 dipotong ke lebar native jika sumber lebih kecil. Threshold yang dibekukan saat 320 px **tidak diskalakan**, sehingga hasil ini adalah uji ketahanan parameter, bukan re-tuning. Output aktual tersimpan di working/final-resolution. Pilot kecil ini tidak mendukung klaim konfirmatori mengenai resolusi.

## 7. Pembanding metode modern (opsional)

Tidak ada model deep learning yang pura-pura diimplementasikan. Jika tersedia mask segmentasi dari implementasi resmi model lain, susun:

```
D:\ModelPredictions\nama_model\PTZ\intermittentPan\fg000001.png
D:\ModelPredictions\nama_model\PTZ\intermittentPan\fg000002.png
...
```

Lalu evaluasi **semua 27 sekuens** pada frame ground truth yang sama:

```powershell
python run_final.py external --dataset "D:\Datasets\CDnet2014" --predictions "D:\ModelPredictions" --model nama_model
```

Default menolak mask yang ukurannya bukan ukuran kerja 320px dan menolak missing predictions. Jika benar-benar perlu resize, `--allow-resize` harus dibenarkan di metode. Anda tetap harus memeriksa apakah model tersebut dilatih pada video yang sama, sehingga perbandingan dapat dibuat secara adil. Keluaran baru adalah eksploratori karena data ujinya sudah dilihat.

## 8. Penggunaan untuk IJCCS

Gunakan `paper/MANUSCRIPT_MASTER.docx` sebagai dokumen kerja dan periksa hasil render akhir di Microsoft Word agar tepat 10–12 halaman. Isi penulis, afiliasi, email, ORCID, etika, konflik, kontribusi, dan funding berdasarkan fakta. Lihat `SUBMISSION_GATE.md` sebelum mengirimkan. Jurnal dan template sudah dipilih; metadata penulis belum tersedia.

## 9. Integritas dan interpretasi

- Tidak ada simulasi yang dipakai sebagai evidence nyata.
- Data V3 dan V4 asli dipertahankan untuk audit.
- Statistik H1–H4 berasal dari fase V3 yang sudah dibekukan.
- Grafik V4 dan calon analisis per frame/resolusi disebut post-hoc.
- Dataset raw digunakan lokal untuk audit dan pilot lanjutan dan tidak disalin ke arsip distribusi.
