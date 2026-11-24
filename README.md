# Modul Data Science — Banyu Bening Resto (`dicoding-capstone-ds`)

Repositori ini merupakan artefak lengkap **Data Science (DS)** untuk proyek Capstone **Tumbass SaaS Operasional Restoran (Studi Kasus Mitra UMKM: Banyu Bening Resto, Salatiga)**. Repositori ini mendokumentasikan seluruh tahapan dari identifikasi masalah UMKM, perumusan pertanyaan bisnis, *data wrangling*, analisis eksploratif (EDA), *feature engineering*, pencegahan *data leakage*, hingga evaluasi komparasi multi-model (*Forecasting* & *Sentiment Classification*) dan integrasinya dengan tim **Full-Stack** serta **Gen AI Engineer**.

---

## Daftar Isi & Pemetaan Pemenuhan 100% Rubrik Data Science

| Kategori Rubrik | Butir Kriteria Penilaian Data Science | Lokasi Bukti & Artefak di Repositori Ini | Status |
| :--- | :--- | :--- | :---: |
| **1. Analisis Masalah & Data Wrangling (Main Quest)** | Mengidentifikasi dan menganalisis bersama tim masalah UMKM yang akan diselesaikan dan menjelaskan peran data dalam solusi tersebut. | Bagian 1 di `README.md` ini & `docs/TECHNICAL_GUIDELINE_DS.md` | **TERPENUHI** |
| | Merumuskan pertanyaan bisnis yang dapat dijawab melalui analisis data. | Bagian 2 di `README.md` ini (5 Pertanyaan Bisnis: **BQ-1 s.d. BQ-5**) | **TERPENUHI** |
| | Melakukan seluruh tahapan pengolahan data (*data wrangling*: *Gathering, Assessing, Cleaning*). | Bagian 3 di `README.md` ini & skrip otomatis `scripts/run_ds_pipeline.py` | **TERPENUHI** |
| | Mengolah dan menganalisis data untuk menjawab pertanyaan bisnis, disertai penjelasan proses dan hasilnya. | Bagian 4 di `README.md` ini, `notebooks/03_ingredient_demand_forecasting_restock.ipynb`, & `data/processed/ds_evaluation_summary.json` | **TERPENUHI** |
| | Menyajikan temuan dan rekomendasi yang mudah dipahami serta relevan dengan solusi tim. | Bagian 4 di `README.md` ini (Tabel Temuan & Rekomendasi Operasional UMKM) | **TERPENUHI** |
| | Menyediakan data atau hasil analisis dalam bentuk yang dapat digunakan oleh anggota tim lain, disertai penjelasan cara penggunaannya. | Folder `data/processed/*.csv` + sinkronisasi ke `dicoding-capstone-backend/src/database/factories/data/master-data.json` | **TERPENUHI** |
| | Memeriksa ketepatan data dan hasil analisis sebelum digunakan dalam solusi akhir. | *Automated Data Quality Verification Gate* (`assert`) di `scripts/run_ds_pipeline.py` | **TERPENUHI** |
| **2. Dasbor untuk Memantau Bisnis** | Mengembangkan dasbor interaktif menggunakan Streamlit atau teknologi visualisasi lain yang sesuai. | Terintegrasi *native* dengan **React 19 + Recharts** di `dicoding-capstone-frontend/src/features/owner-dashboard/` | **TERPENUHI** |
| | Menampilkan indikator bisnis dan menyediakan filter yang relevan untuk membantu pengguna memahami kondisi bisnis. | KPI Omzet, Pajak, Laba Kotor, Margin %, AOV, HPP vs Laba, Shift, Stok Kritis, Kedaluwarsa FEFO, & Asisten AI + Filter Periode & Mode Grafik | **TERPENUHI** |
| | Menyediakan pembaruan data melalui unggahan file atau koneksi ke sumber data. | Live Query PostgreSQL (`GET /api/v1/reports/overview`) + fitur **Impor CSV & Unduh CSV** di `business-insights-banner.tsx` | **TERPENUHI** |
| | Memprioritaskan penggunaan data primer yang diperoleh langsung dari UMKM (atau data dummy/publik yang sesuai karakteristik asli). | 199 Menu, 26 Kategori, 106 Bahan Baku, & 1.481 Resep BOM asli Banyu Bening Resto + Transaksi Sintetis Berlabel | **TERPENUHI** |
| | Mengintegrasikan dasbor ke aplikasi web bersama tim Full-Stack. | Halaman `/dashboard`, `/dashboard/finance`, `/dashboard/shifts`, & `/assistant` pada web app Tumbass | **TERPENUHI** |
| **3. Penyediaan Data untuk Model AI** | Menyepakati kebutuhan dan format data bersama tim Gen AI. Data dummy/publik diberi label jelas (`data_origin`), disertai penjelasan sumber/cara pembuatan dan keterbatasannya. | `docs/DATA_DICTIONARY.md` (Bagian 1) & kolom `data_origin` pada seluruh file di `data/processed/` | **TERPENUHI** |
| | Melakukan pelabelan, transformasi, atau *feature engineering* sesuai kebutuhan model. | 34 fitur deret waktu (`lag_7..28`, `roll_mean_7..28`, `dow_factor`, `log_shelf_life`) & penandaan negasi (`negtag` + leksikon) di `notebooks/` | **TERPENUHI** |
| | Menyusun kamus data (*data dictionary*) atau penjelasan isi dataset agar mudah digunakan. | Dokumen lengkap [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | **TERPENUHI** |
| | Menyiapkan pembagian data yang sesuai untuk *training* dan *testing* model serta mencegah kebocoran data (*anti-data-leakage*). | *Chronological Two-Fold Time-Series Split* (tanpa pengacakan) pada Forecasting & *Independent Hand-Written Test Set* + *Out-of-Fold CV* pada Sentimen | **TERPENUHI** |
| **4. Model Prediksi untuk Fitur Aplikasi** | Mengembangkan model *classification*, *regression*, *forecasting*, dan model lain yang sesuai kebutuhan fitur. | • **Forecasting & Regresi Pemakaian Bahan (8 Model ML + 5 Baseline)** di `notebooks/03_ingredient_demand_forecasting_restock.ipynb`<br>• **Klasifikasi Sentimen Ulasan (7 Metode)** di `notebooks/04_sentiment_evaluation_banyu_bening.ipynb` | **TERPENUHI** |
| | Melakukan *feature engineering* dan mengevaluasi pengaruhnya terhadap kinerja model. | Evaluasi fitur *Lag*, *Rolling*, *Global Demand Factor*, serta *Negation Tagging* (`n_`) pada kalimat sulit/kontras | **TERPENUHI** |
| | Menguji model pada data yang tidak digunakan untuk *training* dengan pembagian data dan metrik evaluasi yang sesuai. | WAPE Mingguan, nMAE, Scaled RMSE, Bias %, & Service-Level Coverage (Forecasting); Macro F1, 95% Bootstrap CI, F1 Kalimat Sulit, Brier Score, & ECE (Sentimen) | **TERPENUHI** |
| | Membandingkan hasil model dan menjelaskan keterbatasannya jika menguji lebih dari satu model. | Bagian 6 & 7 di `README.md` ini beserta analisis keterbatasan data sintetis & bahan *intermittent* | **TERPENUHI** |

---

## 1. Identifikasi Masalah UMKM & Peran Data dalam Solusi

Berdasarkan observasi katalog dan proses operasional mitra UMKM **Banyu Bening Resto (Salatiga)** bersama tim Full-Stack dan Gen AI, teridentifikasi 4 permasalahan utama:
1. **Ketidakpastian Belanja Bahan Baku & Risiko *Waste* (Kedaluwarsa):** Restoran mengelola **199 menu** yang bergantung pada **106 bahan baku** (banyak di antaranya adalah protein segar seperti ikan gurame, nila, lele, ayam, daging sapi, dan sayuran dengan umur simpan singkat 2–5 hari). Tanpa peramalan permintaan (*forecasting*) berbasis resep (*Bill of Materials* / BOM), gudang sering mengalami kelebihan stok yang berakhir kedaluwarsa atau kehabisan bahan utama saat puncak akhir pekan.
2. **Rekapitulasi Keuangan, HPP, dan Pajak Restoran Manual:** Perhitungan HPP per porsi menu dan pemisahan pajak restoran dari omzet harian sebelumnya harus direkap manual. Selain itu, terdapat **29 menu olahan ikan** yang pada daftar menu dicantumkan dengan harga `/ ons`, sehingga menyulitkan standardisasi harga porsi dan pemotongan stok otomatis.
3. **Antrean Pemesanan & Kurangnya Panduan Menu Interaktif:** Pada jam makan siang dan malam akhir pekan, pelanggan membutuhkan asisten pemesanan mandiri berbasis QR yang mampu menjawab info restoran dan merekomendasikan menu terlaris yang stok bahannya masih tersedia.
4. **Evaluasi Kepuasan Pelanggan yang Belum Terukur:** Ulasan pelanggan berbahasa Indonesia sering kali mengandung kata negasi (*"nggak mengecewakan"*, *"tidak lambat"*) atau kalimat kontras (*"ayamnya enak, tapi nunggunya lama banget"*), sehingga membutuhkan model klasifikasi sentimen yang tahan terhadap pembalikan makna.

---

## 2. Perumusan 5 Pertanyaan Bisnis (*Business Questions*)

1. **BQ-1 (Pola Permintaan, Jam Sibuk, & Kanal Pemesanan):** *Bagaimana pola distribusi transaksi lunas (`paid`) berdasarkan jam operasional, hari kerja vs akhir pekan (Jumat–Minggu), serta proporsi pemesanan mandiri via `QR` dibandingkan `POS` kasir?*
2. **BQ-2 (Struktur Profitabilitas Menu, HPP BOM, & Metode Pembayaran):** *Menu dan kategori apa yang memberikan kontribusi omzet serta margin laba kotor (`gross_margin_idr`) tertinggi setelah normalisasi satuan `/ ons` ke `porsi`, dan bagaimana perbandingan adopsi pembayaran `QRIS` vs `Tunai`?*
3. **BQ-3 (Karakteristik Pemakaian 106 Bahan Baku & Risiko Kedaluwarsa FEFO):** *Bagaimana pengelompokan 106 bahan baku berdasarkan frekuensi pemakaian hariannya (`rutin`, `jarang`, `sangat_jarang`, `tanpa_riwayat`), dan bahan apa yang paling rentan mengalami stok kritis atau kedaluwarsa dalam 7 hari?*
4. **BQ-4 (Peramalan Kebutuhan Bahan 7 Hari ke Depan & Saran Stok / *Restock*):** *Seberapa akurat model Machine Learning meramalkan kebutuhan mingguan tiap bahan baku dibandingkan metode baseline statistik, dan berapa kuantitas saran belanja bahan untuk mencapai target tingkat layanan (service level coverage) 95%?*
5. **BQ-5 (Analisis Sentimen Ulasan Pelanggan & Penanganan Kalimat Negasi/Kontras):** *Metode klasifikasi teks mana di antara 7 kandidat model yang memiliki performa Macro-F1 dan kalibrasi probabilitas (Brier Score & ECE) terbaik, khususnya pada kalimat ulasan berbahasa Indonesia yang mengandung negasi dan kontras?*

---

## 3. Tahapan Pengolahan Data (*Data Wrangling*) & Pemeriksaan Kualitas Data

Seluruh proses *Data Wrangling* dijalankan secara terotomasi melalui [`scripts/run_ds_pipeline.py`](scripts/run_ds_pipeline.py):

### 3.1 *Data Gathering & Assessing* (Temuan Audit Data Mentah)
Dari hasil pemeriksaan terhadap file mentah (`menu_items_raw.csv`, `orders_raw.csv`, `orders_dengan_timestamp.xlsx`, `bahan_resep_banyu_bening.xlsx`, dan `reviews_v2.xlsx`), ditemukan 5 isu kualitas data yang wajib dibersihkan:
1. **Ketidakkonsistenan Satuan Jual `/ ons` (29 Menu):** Terdapat 29 menu ikan (Gurame, Nila, Lele) dengan `selling_unit = "ons (verifikasi)"` dan harga per ons (mis. Gurame Bakar Madu Rp 10.500/ons), sedangkan sistem POS & keranjang QR membutuhkan harga per 1 porsi sajian utuh.
2. **Kolom `estimated_hpp_idr` Kosong pada CSV Menu Mentah (199 Baris):** Seluruh baris di `menu_items_raw.csv` belum memiliki nilai HPP, sehingga harus dihitung secara *bottom-up* dari tabel `recipes` $\times$ `ingredients` (`hpp_estimasi`).
3. **Transaksi Belum Lunas / Batal pada Data Order (268 dari 2.285 Order):** Dari 2.285 total baris order, terdapat **268 transaksi** berstatus `placed` (`pending`) atau `cancelled`. Sesuai kontrak FSD, transaksi non-`paid` tidak boleh masuk ke laporan omzet maupun matriks pemakaian bahan.
4. **Timestamp Kosong pada `orders_raw.csv` & Metode Bayar `card`:** File `orders_raw.csv` awal tidak memiliki nilai `ordered_at` dan masih memuat metode bayar `card`, sehingga digantikan oleh `orders_dengan_timestamp.xlsx` (rentang penuh `2026-05-01` s.d. `2026-10-31`) dan dinormalisasi ke dua metode pembayaran sah MVP (`QRIS` dan `cash`).
5. **Deret Waktu Pemakaian Bahan Berpola *Intermittent / Sparse*:** Sebanyak **60 dari 106 bahan baku** memiliki $>50\%$ hari tanpa pemakaian (nilai 0), sehingga hari tanpa transaksi wajib dilakukan *zero-filling* (`reindex` kalender harian penuh 184 hari dengan `fill_value=0.0`) agar perhitungan `lag` tidak melompati tanggal.

### 3.2 *Data Cleaning* & *Quality Verification Gate*
Setelah pembersihan, skrip menjalankan *automated assertions* (`assert`):
* **Normalisasi Porsi Ikan:** Gurame dikalikan faktor $\times 5\text{ ons}$ (500g), Nila $\times 4\text{ ons}$ (400g), dan Lele $\times 3\text{ ons}$ (300g) baik pada harga jual maupun kuantitas bahan di BOM (`recipes_bom_clean.csv`).
* **Verifikasi Konsistensi Finansial:** `subtotal_idr + tax_amount_idr == grand_total_idr` dan `subtotal_idr - total_hpp_idr == gross_profit_idr` lulus 100% pada **2.017 order `paid`**.
* **Verifikasi Anti-Leakage:** Tanggal transaksi terakhir pada *Training Set* lebih kecil dari tanggal pertama pada *Test Set*.

---

## 4. Jawaban Pertanyaan Bisnis, Temuan Utama, & Rekomendasi UMKM

| Pertanyaan Bisnis | Temuan Analisis Data (Key Findings) | Rekomendasi Operasional untuk Banyu Bening Resto |
| :--- | :--- | :--- |
| **BQ-1 & BQ-2:** Pola Transaksi, Kanal, & Profitabilitas Menu | • Rata-rata terdapat **11,0 order `paid` per hari** (total 2.017 order `paid` dan 5.000 baris item selama 184 hari).<br>• Kanal pemesanan didominasi **QR Mandiri (~79%)** dibanding POS Kasir (~21%), dengan pembayaran digital **QRIS (~61%)** mengungguli Tunai (~39%).<br>• Rata-rata margin laba kotor katalog mencapai **~64%** (HPP rata-rata ~36%). | **1.** Mempertahankan QR Ordering + AI Chatbot di seluruh 18 meja makan untuk memangkas antrean kasir pada puncak akhir pekan.<br>**2.** Memanfaatkan fitur *rekomendasi tambahan (upselling)* pada Chatbot AI untuk menawarkan minuman/snack bermargin tinggi sebelum pelanggan checkout. |
| **BQ-3:** Segmentasi 106 Bahan Baku Gudang | Dari 106 bahan baku pada matriks 184 hari:<br>• **40 bahan `rutin`** (hari nol $\le 40\%$)<br>• **47 bahan `jarang`** (hari nol $40\%–90\%$)<br>• **10 bahan `sangat_jarang`** (hari nol $>90\%$)<br>• **9 bahan `tanpa_riwayat`** (kemasan/item belum pernah terpakai). | **1.** Terapkan peramalan ML mingguan untuk **87 bahan `rutin` & `jarang`**.<br>**2.** Untuk **19 bahan `sangat_jarang` & `tanpa_riwayat`**, jangan gunakan model regresi harian; gunakan kebijakan *Reorder Point* berbasis ambang `minimum_stock` dan pantau peringatan **Kedaluwarsa H-7 (FEFO)** di Dashboard Owner. |
| **BQ-4:** Akurasi Forecasting & Saran Belanja Bahan | Prediksi harian per bahan memiliki variasi tinggi, namun ketika diagregasikan ke **kebutuhan mingguan (7 hari)**, galat WAPE turun drastis menjadi **26,6%** (Random Forest) dengan cakupan tingkat layanan (*out-of-sample service coverage*) mencapai **96,1%** (melampaui target 95%). | Gunakan angka **Forecast 7 Hari + Kuantil Safety Stock** setiap awal pekan untuk menyusun daftar belanja PO (*Purchase Order*), di mana estimasi belanja penuh untuk 106 bahan adalah sekitar **Rp 2.256.235 / minggu** (dikurangi saldo stok valid FEFO di gudang). |
| **BQ-5:** Evaluasi Sentimen Ulasan Pelanggan | Model sederhana berbasis kata tanpa negasi (M1/M2) mengalami penurunan akurasi tajam pada kalimat negasi (*"tidak mengecewakan"*) dan kalimat kontras. Model hibrida **M6 (Leksikon Negasi + TF-IDF Penanda Negasi + Logistic Regression)** memberikan F1 tertinggi dan skor kalibrasi terbaik. | Gunakan pipeline **M6** untuk memfilter ulasan pelanggan secara otomatis: ulasan yang terdeteksi `negative` dengan skor keyakinan tinggi langsung diprioritaskan untuk evaluasi kualitas rasa dan kecepatan penyajian dapur. |

---

## 5. Feature Engineering & Pencegahan Kebocoran Data (*Anti-Data-Leakage*)

### 5.1 Protokol Forecasting Pemakaian Bahan (`03_ingredient_demand_forecasting_restock.ipynb`)
* **Mencegah Kebocoran Horizon 7 Hari:** Karena tujuan bisnis adalah meramal pemakaian **7 hari sekaligus** ke depan, seluruh fitur *lag* dan *rolling* hanya boleh membaca data yang berumur **minimal 7 hari (`y.shift(7)`)**:
  * **Autoregressive Lags (Normalized by Ingredient Scale):** `lag_7`, `lag_14`, `lag_21`, `lag_28`.
  * **Rolling Statistics:** `roll_mean_7`, `roll_mean_14`, `roll_mean_28`, `roll_nz_28` (proporsi hari aktif dalam 28 hari terakhir), dan `exp_mean` (*expanding mean* hingga $t-7$).
  * **Global Market Demand Signals:** `dow_factor` (rasio keramaian hari dalam seminggu terhadap rata-rata keseluruhan), `g_lag_7`, `g_roll_28`, `pooled_dow`, dan `roll28_dow`.
  * **Kalender & Karakteristik Bahan:** `dow` (One-Hot), `is_fri_sun` (akhir pekan), `day_of_month`, `is_month_end` (tanggal gajian $\ge 25$), `log_scale`, `log_shelf_life`, serta One-Hot kategori & satuan bahan (**total 34 fitur**).
* **Pembagian Data Bersarang Berbasis Waktu (*Nested Two-Fold Chronological Split*):**
  * **Lipatan A (`A_sep`):** Tuning pada Agustus 2026 $\rightarrow$ Evaluasi pada **September 2026**.
  * **Lipatan B (`B_okt`):** Data Latih `2026-06-04` s.d. `2026-09-30` (11.543 baris) $\rightarrow$ Data Uji `2026-10-01` s.d. `2026-10-31` (3.007 baris). Tidak ada pengacakan baris (*zero shuffling*).

### 5.2 Protokol Klasifikasi Sentimen (`04_sentiment_evaluation_banyu_bening.ipynb`)
* **Feature Engineering Negasi Bahasa Indonesia (`negtag`):** Kata setelah pemicu negasi (`nggak`, `tidak`, `bukan`, `gak`, `ga`, `tak`) dalam jendela 3 token diberi prefiks `n_` (mis. `"tidak enak"` $\rightarrow$ `"NEG n_enak"`), dipadukan dengan fitur skor leksikon bernegasi (`lexfeat`) dan TF-IDF N-gram `(1,2)`.
* **Pembagian Data Bebas Bocor:**
  1. **Ujian Utama pada 100 Komentar Tulisan Tangan Independen (`T`):** Ditulis manual di luar template generator (terdiri atas 80 kalimat normal dan 20 kalimat sulit bernegasi/kontras) sehingga tidak pernah muncul di korpus latih.
  2. **Prediksi *Out-of-Fold* (5-Fold StratifiedKFold) pada 2.000 Review (`reviews_v2.xlsx`):** Setiap ulasan diprediksi oleh model yang dilatih pada 4 lipatan lainnya.

---

## 6. Hasil Komparasi Model & Pemilihan Model Terbaik

### 6.1 Komparasi Model Forecasting Pemakaian Bahan (Colab: `1O-5imMbm7PjD5dQv-HYX0rWPMyBi3cbZ`)
Dievaluasi pada **8 Model Machine Learning** (`Ridge`, `Lasso`, `Random Forest`, `Extra Trees`, `LightGBM L2`, `LightGBM Tweedie`, `XGBoost`, `CatBoost`) dan **5 Baseline Statistik** (`seasonal_naive`, `dow_mean_4w`, `rolling_mean_28d`, `pooled_dow`, `roll28_dow`):

| Peringkat / Kelompok | Nama Model | Konfigurasi Terbaik | Val nMAE (`A_sep`) | WAPE Mingguan (Rata-rata 2 Lipatan) $\downarrow$ | Bias Mingguan (%) | Status Keputusan |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **1 (ML Winner)** | **Random Forest Regressor** | `max_depth=6, min_samples_leaf=20` | 1,0636 | **0,266 (26,6%)** | **+0,3%** | **Terpilih untuk Model ML (`model_forecast.joblib`)** |
| **2 (Baseline Terbaik)** | **Pooled Day-of-Week (`pooled_dow`)** | `exp_mean * dow_factor` | — | **0,268 (26,8%)** | -2,6% | **Baseline Pembanding Utama (Sangat Kompetitif)** |
| **3** | **LightGBM Tweedie Regressor** | `Tweedie variance power` (Cocok data *zero-inflated*) | **0,9170** | ~0,271 | -1,4% | Terbaik pada nMAE harian bahan *sparse* |
| **4** | **Extra Trees Regressor** | Tuned Grid | 1,0335 | ~0,274 | +0,8% | Kandidat Ensemble Pohon |
| **5** | **LightGBM L2 / XGBoost / CatBoost** | Tuned Grid | 1,0279 | ~0,278 | +1,2% | Kandidat Gradient Boosting |
| **6** | **Lasso / Ridge Regression** | Regularized Linear | 1,0469 / 1,0859 | ~0,285 | +2,1% | Kandidat Linear |

* **Validasi Aturan Saran Stok (*Out-of-Sample Backtest*):** Menggunakan kuantil residu dari Lipatan A (September) untuk menetapkan *Safety Stock* pada Lipatan B (Oktober) menghasilkan **Cakupan Layanan Aktual 96,1%** (target 95,0%).

### 6.2 Komparasi 7 Metode Klasifikasi Sentimen (Colab: `1RhBkU_zi4LnmMyFvKq1zBBC-y0Kh_bO_`)
Diuji pada **2 Skema Pelatihan** (*Skema A: Korpus Sintetis 4.000 kalimat* vs *Skema B: Sintetis + Review Berlabel Rating*) terhadap **100 Komentar Uji Tulisan Tangan (Normal & Sulit/Negasi)**:

| Kode | Metode / Arsitektur Model | Karakteristik Fitur Utama | Performa pada Kalimat Normal | Ketahanan pada Kalimat Sulit (Negasi & Kontras) | Keputusan |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **M1** | Leksikon Aturan Kata (Tanpa Negasi) | Hitung kata positif/negatif murni | Baik | **Gagal** pada kalimat *"tidak mengecewakan"* / *"nggak lambat"* | Baseline Dasar |
| **M1b** | Leksikon + Pembalik Negasi | Membalik polaritas kata setelah `tidak/nggak/bukan` | Baik | Meningkat pada negasi tunggal, lemah pada kalimat kontras panjang | Baseline Leksikon |
| **M2** | TF-IDF Kata `(1,2)` + Multinomial Naive Bayes | Frekuensi kata & bigram (`alpha=0.3`) | Tinggi | Rentan salah klasifikasi bila kata sifat positif dinegasikan | Kandidat Probabilistik |
| **M3** | TF-IDF Kata + Karakter `(2,5)` + Logistic Regression | Tahan salah ketik/slang (`class_weight='balanced'`) | Sangat Tinggi | Cukup baik lewat bigram, namun jendela negasi >1 kata masih lolos | Kandidat Linear Kuat |
| **M4** | TF-IDF Kata + Karakter + Calibrated LinearSVM | Margin maksimum + kalibrasi Sigmoid 5-Fold | Sangat Tinggi | Setara M3 dengan kalibrasi probabilitas baik | Kandidat SVM |
| **M5** | TF-IDF Penanda Negasi (`negtag`) + Logistic Regression | Transformasi 3 kata setelah negasi menjadi token `n_<kata>` | Sangat Tinggi | **Sangat Tangguh** membedakan `enak` vs `n_enak` | Kandidat Fitur Negasi |
| **M6** | **Hibrida: Leksikon-Negasi + TF-IDF(`negtag`) + Logistic Regression** | Gabungan `FunctionTransformer(negcol)` + `lexfeat` + `LogisticRegression(C=4, balanced)` | **Terbaik** | **Terbaik (Macro-F1 Tertinggi & Brier/ECE Terendah)** | **Model Final Terpilih** |

---

## 7. Penjelasan Keterbatasan Model & Data (*Limitations*)

1. **Keterbatasan Data Sintetis & Horizon 6 Bulan:** Karena data transaksi (`2026-05-01` s.d. `2026-10-31`, 2.017 order `paid`) dan ulasan (`reviews_v2.xlsx`, 2.000 review) merupakan data sintetis terkontrol, keunggulan tipis `Random Forest` atas baseline `pooled_dow` (+0,001 WAPE) belum membuktikan superioritas di operasional nyata. Model baseline `pooled_dow` sangat direkomendasikan sebagai *fallback* produksi yang ringan dan mudah dirawat.
2. **Bahan Baku Sangat Jarang & Tanpa Riwayat:** Sebanyak 19 bahan baku (10 `sangat_jarang` + 9 `tanpa_riwayat` seperti kemasan takeaway) tidak dapat diramal dengan akurat menggunakan regresi deret waktu dan harus dikelola menggunakan ambang `minimum_stock` statis.
3. **Asumsi Tingkat Layanan & Kepatuhan BOM:** Perhitungan saran stok mengasumsikan takaran resep BOM dipatuhi 100% oleh dapur tanpa pencatatan *waste* historis; penyimpangan fisik wajib dikoreksi berkala melalui fitur **Stock Opname** di aplikasi Tumbass.

---

## 8. Cara Menjalankan Pipeline Data Science

```powershell
cd "c:\Kerjaan Septyan\STUDI INDEPENDEN\Output\dicoding-capstone-ds"
py -3.12 scripts/run_ds_pipeline.py
```

Perintah di atas akan:
1. Mengaudit seluruh dataset mentah di `data/raw/`.
2. Menghasilkan dataset bersih siap pakai di `data/processed/` (`menu_items_clean.csv`, `ingredients_clean.csv`, `recipes_bom_clean.csv`, `orders_clean.csv`, `reviews_clean.csv`).
3. Menjalankan *Data Quality Verification Gate* (`assert` konsistensi finansial & *anti-leakage chronological split*).
4. Menyimpan laporan evaluasi JSON di `data/processed/ds_evaluation_summary.json`.
