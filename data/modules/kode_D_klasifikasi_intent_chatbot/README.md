# Dataset Kode D — Klasifikasi Intent (Router Chatbot 5 Kelas)
- **Modul:** Klasifikasi intent pesan pelanggan
- **Jenis:** Klasifikasi Teks Bahasa Indonesia (5 Kelas: `pemesanan`, `tanya_menu`, `info_resto`, `keluhan`, `lainnya`)
- **Dipakai di:** Router Chatbot AI di Halaman QR
- **Prioritas:** Nilai Tambah

## Daftar File di Folder Ini
1. `intent_dataset_clean.csv`: **546 kalimat unik bersih** setelah normalisasi singkatan tidak baku (`gak/ga/nggak -> tidak` dengan tetap mempertahankan kata negasi) dan penghapusan 448 baris duplikat dari `intent_raw.csv`.
2. `intent_train.csv` (436 kalimat — 80%) & `intent_test.csv` (110 kalimat — 20%): Pembagian data menggunakan *Stratified Train/Test Split* pasca-deduplikasi (`overlap = 0`, bebas kebocoran data).
3. `intent_raw.csv`: 994 kalimat mentah sebelum proses *Data Cleaning & Deduplication*.
4. `evaluasi_intent_4_metode.csv`: Tabel perbandingan metrik `5-Fold CV Macro-F1`, `Test Accuracy`, `Macro Precision`, `Macro Recall`, dan `Macro-F1` pada 4 metode klasifikasi teks.
