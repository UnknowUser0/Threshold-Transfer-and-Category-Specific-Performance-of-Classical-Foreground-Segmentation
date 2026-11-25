# Verifikasi teknis paket v3

**Status:** pemeriksaan struktur, sintaks dan integrasi pada data sintetis berhasil. **Tidak ada eksperimen baru pada CDnet2014 yang dijalankan dalam penyusunan paket ini**, karena paket masukan hanya berisi laporan hasil dan notebook HTML, bukan file video/ground truth lengkap.

## Pekerjaan yang sudah dilakukan

- Kode Python dari seluruh sel notebook HTML v2 direkonstruksi menjadi `.ipynb` editabel dan `.py` yang dapat dijalankan.
- Logika evaluasi ground truth diperiksa: label 255/0/50/85/170, ROI yang membatasi prediksi dan ground truth, GT validasi sekali per frame, kategori dan fase diekspor.
- Eksekusi confirmatory menolak pengulangan 26 sekuens versi 2, data tidak lengkap menurut syarat kategori minimum, parameter tidak dibekukan, resolusi yang tidak cocok dan tuning.
- Statistik utama memakai kategori sebagai unit (`category_signflip_p`), analisis directional satu sisi dipisah keluarga uji dengan Holm dan p dua sisi tetap tampil.
- Benchmark FPS diperbaiki agar setiap eksperimen diukur sendiri, bukan bersamaan dengan tujuh detektor lain.
- Semua hasil diberi metadata disclosure development vs confirmatory.
- `paper_audit.py` memeriksa keberadaan output dan memberi error jika input jelas berupa data tes sintetis.

## Pengujian aktual paket

1. `python -m pytest -q tests/test_protocol.py`: **10 passed**.
2. **Development synthetic smoke**: sukses sampai `report.md`, CSV, TEX, PDF, PNG dan `run_info.json`.
3. **Confirmatory synthetic smoke**: sukses pada 24 sekuens sintetis (4 per kategori di enam kategori), menghasilkan seluruh berkas utama.
4. **Audit synthetic smoke**: secara sengaja **gagal**, karena file sintetis bukan data untuk paper dan jumlah bootstrap/repetisi benchmark diturunkan untuk mempercepat pemeriksaan fungsi.
5. Kode `.py` lulus `py_compile`; notebook `.ipynb` lulus validasi `nbformat`.

**Catatan:** Ini baru uji software. Angka penelitian dalam `references/` berasal dari versi 2 dan tidak boleh dicampur dengan output versi 3. Dataset CDnet asli, validasi metodologis oleh pembimbing, audit statistik dan novelty jurnal masih diperlukan.
