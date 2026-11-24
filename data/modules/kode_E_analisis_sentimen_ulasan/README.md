# Dataset Kode E — Analisis Sentimen Ulasan Pelanggan
- **Modul:** Analisis sentimen ulasan pasca-pembayaran
- **Jenis:** Klasifikasi Teks Bahasa Indonesia (`positive` vs `negative`, dengan penanganan fenomena negasi & kalimat kontras)
- **Dipakai di:** Dashboard Pemilik (Owner)
- **Prioritas:** Nilai Tambah

## Daftar File di Folder Ini
1. `reviews_clean.csv`: Dataset **2.000 ulasan pelanggan** (`review_id`, `order_id`, `rating`, `comment`, `sentiment_label`).
2. `reviews_independent_handwritten_test_100.csv`: **100 komentar uji tulisan tangan independen** (80 kalimat normal + 20 kalimat sulit bernegasi/kontras seperti *"Nggak mengecewakan sama sekali"* atau *"Enak sih, tapi nunggunya lama banget"*) yang tidak pernah muncul di data latih.
3. `reviews_v2_prediksi.csv`: Hasil prediksi *Out-of-Fold* (5-Fold StratifiedKFold) beserta skor keyakinan (`sentiment_model` & `score_model`) dari model pemenang **M6 Hibrida (Leksikon-Negasi + TF-IDF Negasi + Logistic Regression)**.
4. `evaluasi_sentimen_7_metode.csv`: Tabel perbandingan 7 metode sentimen (`M1` s.d. `M6`) pada Skema Latih A & B (`Macro-F1`, `95% CI`, `F1 Kalimat Sulit`, `Brier Score`, `ECE`).
5. `reviews_v2_raw.xlsx`: File Excel mentah ulasan pelanggan.
