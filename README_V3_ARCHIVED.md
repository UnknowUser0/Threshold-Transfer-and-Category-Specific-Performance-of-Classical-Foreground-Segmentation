# CDnet2014 — Experiment B v3 / Paket penelitian menuju naskah jurnal

Paket ini **merevisi kode HTML/notebook versi 2**, bukan membuat hasil eksperimen CDnet asli yang belum tersedia. Ada dua jalur: `development` (eksploratori, 5 kategori yang sudah dianalisis) dan `confirmatory` (6 kategori lain yang belum pernah digunakan). Semua klaim publikasi harus didasarkan pada output dataset nyata, bukan file tes sintetis.

## Struktur proyek

| Berkas/folder | Fungsi |
|---|---|
| `experiment_b_cdnet2014_paper_v3.ipynb` | Notebook editabel; kode sama dengan skrip Python |
| `experiment_b_cdnet2014_paper_v3.py` | Runner tanpa Jupyter; disarankan untuk run final |
| `paper_protocol.py` | Pencegahan leakage, label/ROI GT yang valid, exact sign-flip |
| `PROTOCOL.md` | Pra-spesifikasi hipotesis, data independen, evaluasi & keterbatasan |
| `protocol/frozen_v2_params.json` | Threshold hasil tuning v2, harus tetap beku |
| `protocol/seen_v2.json` | 26 sekuens v2 yang dilarang untuk konfirmasi |
| `protocol/preregistration.json` | ID versi kode, hash sumber/parameter, hipotesis |
| `references/` | Cuplikan file hasil v2 untuk provenance — **bukan hasil v3** |
| `tests/` | Unit tests dan generator data sintetis untuk smoke test saja |
| `paper_audit.py` | Pemeriksa kelengkapan output run terhadap protokol |
| `PAPER_OUTLINE.md` | Struktur naskah, tabel & gerbang kualitas untuk submit |

## Persiapan lingkungan

**Rekomendasi Python 3.11.** Jalankan perintah berikut dalam direktori paket ini:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q tests/test_protocol.py
```

Jangan jalankan dari direktori lain tanpa memastikan `protocol/` tersedia pada current working directory. Tutup proses Python lain yang memakai CUDA/CPU berat saat mengukur FPS (kode ini CPU). Untuk hasil pembandingan hardware, catat versi OpenCV dan konfigurasi environment yang sama.

## Struktur dataset CDnet2014

Download dan ekstrak dataset **resmi** ke folder milik Anda, contohnya `/data/CDnet2014`. Harus ada struktur per kategori dan video seperti:

```text
/data/CDnet2014/
  baseline/
    highway/
      input/in000001.jpg
      groundtruth/gt000001.png
      temporalROI.txt
      ROI.bmp
  cameraJitter/
    ...
  intermittentObjectMotion/
    ...
  lowFramerate/
    ...
  PTZ/
    ...
  thermal/
    ...
  turbulence/
    ...
```

Folder sekuens dicari secara rekursif. Tidak ada data video CDnet yang disertakan dalam ZIP kode ini. Jika ROI.bmp tidak tersedia, evaluasi menggunakan area yang tercantum dalam GT 85/170; cek secara manual kesetaraan dengan kebijakan benchmark resmi sebelum membuat klaim.

## 1. Jalankan versi pengembangan (eksploratori)

**Linux/macOS:**

```bash
CDNET_DATA_DIR=/data/CDnet2014 CDNET_MODE=development python experiment_b_cdnet2014_paper_v3.py
```

**Windows PowerShell:**

```powershell
$env:CDNET_DATA_DIR = 'D:\Datasets\CDnet2014'
$env:CDNET_MODE = 'development'
python .\experiment_b_cdnet2014_paper_v3.py
```

Output: `working/results-v3-development/`. Jalur ini melakukan tuning baru pada 10 sekuens kategori lama dan menilai sisanya. **Jangan sebut hasil baru/konfirmatori** karena data test v2 sudah dianalisis sebelumnya dan bisa memiliki perubahan akibat perbaikan ROI atau versi OpenCV.

## 2. Jalankan konfirmasi *out-of-category* (HANYA setelah protocol freeze)

Periksa dulu `PROTOCOL.md` dan pastikan **enam kategori konfirmatori benar-benar belum dipakai dalam keputusan desain riset**. Jalankan sekali dengan parameter v2 yang dibekukan:

**Linux/macOS:**

```bash
CDNET_DATA_DIR=/data/CDnet2014 CDNET_MODE=confirmatory python experiment_b_cdnet2014_paper_v3.py
```

**Windows PowerShell:**

```powershell
$env:CDNET_DATA_DIR = 'D:\Datasets\CDnet2014'
$env:CDNET_MODE = 'confirmatory'
python .\experiment_b_cdnet2014_paper_v3.py
```

Output: `working/results-v3-confirmatory/`. Mode ini otomatis menolak duplikasi dari 26 sekuens v2, subset, kekurangan kategori (<4 sekuens per kategori), training baru, dan resolusi tidak kompatibel. Untuk run final simpan `pip freeze > working/results-v3-confirmatory/pip_freeze.txt` setelah proses selesai.

Audit output:

```bash
python paper_audit.py working/results-v3-confirmatory
```

`paper_audit.py` memeriksa kebocoran, syarat metadata dan berkas pendukung. **Audit lolos bukan berarti naskah diterima atau metode memiliki novelty memadai.**

## Output yang dihasilkan

`table_main.*`, `table_by_category.*`, `table_hypotheses.*`, `stats_primary.*`, `stats_secondary.*`, `stats_ablation_*.{csv,tex}`, `fig_main.{png,pdf}`, `fig_by_category`, `fig_ablation`, `table_fps`, `tuning_results.csv` (hanya development), `run_info.json`, `splits.csv`, `all_per_seq.csv`, `report.md`.

- Pada `development`, hasil tabel akan **berbeda** dari v2 pada beberapa bagian karena ada perbaikan ROI dan pengujian kategori; jangan menyalin angka v2 sebagai angka v3.
- Pada `confirmatory`, parameter diambil dari `protocol/frozen_v2_params.json`; tidak ada pencarian threshold.
- Kecepatan adalah *processing FPS* saja. Waktu pembacaan file JPEG, resizing, penulisan output, dll **bukan** bagian dari angka tersebut.
- Jangan mengekstrapolasi hasil pada lebar kerja 320 piksel sebagai skor resmi seluruh CDnet2014 pada resolusi asli.

## Pengujian perangkat lunak (BUKAN hasil paper)

```bash
python -m pytest -q tests/test_protocol.py
# Optional smoke test pada data buatan; jangan dikutip sebagai hasil riset.
python tests/make_synthetic_cdnet.py ./tmp_synthetic --mode confirmatory
```

Untuk menjalankan smoke test sintetis, arahkan `CDNET_DATA_DIR` ke `./tmp_synthetic`, set `CDNET_MODE=confirmatory` serta `CDNET_BOOTSTRAPS=100`, `CDNET_N_JOBS=1`, `CDNET_BENCH_REPEATS=1`; hasilnya tidak untuk publikasi.

## Lanjutan sebelum submission

1. Jalankan versi pengembangan pada data **nyata** untuk memverifikasi kebersihan data, label, ROI dan konsistensi output setelah perubahan kode. Pastikan pembagian dan hasil tidak diam-diam berbeda dari asumsi v2.
2. Konfirmasikan novelty lewat *related work* 2022–2026, khususnya benchmark komparatif dan ablation pada classical foreground segmentation.
3. Kunci versi, lakukan evaluasi enam kategori baru dengan parameter beku; simpan seluruh output termasuk hasil nol atau negatif.
4. Replikasi dengan environment berbeda atau eksperimen resolusi asli sebagai **analisis sensitivitas sekunder**, dilabeli berbeda dan tidak dicampur ke hasil utama.
5. Tulis IMRaD sesuai `PAPER_OUTLINE.md`; periksa aturan jurnal dan lakukan tinjauan ulang bersama pembimbing, termasuk ketepatan uji statistik dan etika.

Referensi data: Wang et al., 2014 — https://openaccess.thecvf.com/content_cvpr_workshops_2014/W12/html/Wang_CDnet_2014_An_2014_CVPR_paper.html
