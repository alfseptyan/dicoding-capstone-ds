# Technical Guideline & Specification: Modul Data Science Banyu Bening Resto (SaaS)

**Nama Proyek:** Sistem Pemesanan Mandiri (QR), POS, Inventory, Manajerial, dan Modul AI  
**Mitra UMKM / Studi Kasus:** Banyu Bening Resto, Salatiga (PIC: Bapak Sakbani)  
**Tim Pengembang:** ASKARA JUARA (Septyan Yaumul Fatkhan, Ahmad Luthfi, Kamaluddin Arsyad Fadllillah, Poernomo Maulana Rofif Aqilla, Muhammad Fitra Fuadi)  
**Tech Stack Terpadu (v0.4):** Next.js (Frontend App Router), NestJS (Backend Monolith Modular), PostgreSQL (Database), FastAPI (Layanan AI), Streamlit (Data Science Interactive Dashboard)  
**Status Dokumen:** v1.0 — Selaras penuh dengan *FSD Terpadu v0.4*, *Technical Documentation AI*, *Kamus Atribut Tim*, dan *Checklist Tech Stack*.

---

## 1. Ringkasan Peran Data Science & Pembagian Tanggung Jawab Antar-Role

Dokumen ini menjadi panduan eksekusi untuk peran **Data Science (DS)** sekaligus menjawab poin terbuka pada **Bagian 9.2 FSD Terpadu v0.4** terkait batas tanggung jawab antara Data Science, Full-Stack, dan AI Engineer:

1. **Data Science (DS):**
   * **Data Engineering & Penyediaan Dataset:** Mengumpulkan parameter primer non-rahasia dari buku menu UMKM, mengadaptasi dataset publik transaksi F&B & NLP Indonesia, membangkitkan data sintetis gudang (FEFO & Stock Opname), menjalankan *Data Wrangling* (*Gathering, Assessing, Cleaning*), memverifikasi ketepatan data, dan memelihara **Kamus Data (`data_dictionary.md`)**.
   * **Business Intelligence & Dasbor Analitik (Modul 5):** Menjawab pertanyaan bisnis UMKM melalui *Exploratory Data Analysis* (EDA) dan membangun **Dasbor Interaktif Streamlit** yang memvisualisasikan metrik **FR-5.1 s.d. FR-5.6** (Pemasukan, Pembelian & HPP, Rekap Pajak PB1/PPN, Sisa Stok & Peringatan EXP, Prediksi Belanja, serta Kepuasan Pelanggan), lengkap dengan fitur **Unggah File (CSV/Excel)** dan koneksi langsung ke PostgreSQL.
   * **Eksperimen Fitur & Pelatihan Model Prediksi (ML Core):** Melakukan *feature engineering* (beserta uji dampaknya), menyiapkan pembagian data *train/test* bebas kebocoran (*no data leakage*), menangani ketimpangan kelas (*class imbalance*), serta melatih dan membandingkan model untuk **Modul A (Demand & Restock Forecasting)**, **Modul B (Menu Recommender)**, **Modul D (Intent Classification)**, dan **Modul E (Sentiment Analysis)**.

2. **Titik Integrasi dengan AI Engineer (FastAPI):**
   * Tim DS menyerahkan dataset bersih (`data/processed/`), skrip prapemrosesan, tabel komparasi metrik evaluasi, serta artefak bobot model terbaik (`.joblib`).
   * Tim AI Engineer memuat model `.joblib` tersebut sekali saat *startup* di dalam layanan **FastAPI (`/v1/...`)** dan membangun pipa **Modul C (Chatbot RAG dengan ChromaDB/FAISS & LLM API)** serta mekanisme *guardrail*, *fallback*, dan *rate-limiting*.

3. **Titik Integrasi dengan Full-Stack (Next.js + NestJS + PostgreSQL):**
   * Tim Full-Stack menggunakan file CSV bersih dan `data_dictionary.md` dari tim DS untuk melakukan *seeding* awal database PostgreSQL multi-tenant (`tenant_id = 'BBR001'`).
   * Untuk **Modul 5 (Dashboard Manajerial Pemilik)**, tim Full-Stack menyajikan kartu ringkasan real-time via WebSocket/SSE di Next.js (`(dashboard)` route group) dan menyematkan (*embed*) **Dasbor Analitik Streamlit** buatan tim DS untuk eksplorasi mendalam, simulasi bisnis, dan unggah berkas rekap manual.

---

## 2. Pemetaan Pemenuhan Checklist Tech Stack Data Science (100% Coverage)

| Kategori Checklist | Butir Requirement Checklist Data Science | Implementasi & Artefak pada Proyek Banyu Bening Resto | Bagian |
| :--- | :--- | :--- | :---: |
| **Main Quest** | Mengidentifikasi dan menganalisis bersama tim masalah UMKM yang akan diselesaikan dan menjelaskan peran data dalam solusi tersebut. | Analisis masalah antrean kasir, rekap manual HPP/PB1 di Excel, ketidakpastian belanja bahan, dan keluhan tak terpantau; peran data sebagai penggerak otomatisasi keuangan, peringatan FEFO, dan model prediksi. | Bagian 3.1 |
| **Main Quest** | Merumuskan pertanyaan bisnis yang dapat dijawab melalui analisis data. | Merumuskan 5 Pertanyaan Bisnis terukur (BQ-1 s.d. BQ-5) yang mencakup jam sibuk & metode pesan (QR vs POS), margin HPP & pajak PB1, risiko *expired* FEFO & *variance* Opname, *forecasting* bahan, serta pasangan menu. | Bagian 3.2 |
| **Main Quest** | Melakukan seluruh tahapan pengolahan data (*data wrangling*). | Pipeline *Gathering*, *Assessing* (audit *missing value*, duplikat, status batal, *outlier*, *imbalance*), dan *Cleaning* (filter `payment_status = 'paid'`, *zero-filling* tanggal kosong, normalisasi teks dengan menjaga kata negasi). | Bagian 5 |
| **Main Quest** | Mengolah dan menganalisis data untuk menjawab pertanyaan bisnis, disertai penjelasan proses dan hasilnya. | Notebook `02_eda_business_questions.ipynb` yang membedah jawaban BQ-1 s.d. BQ-5 menggunakan agregasi statistik, matriks *Menu Engineering*, dan visualisasi. | Bagian 6 |
| **Main Quest** | Menyajikan temuan dan rekomendasi yang mudah dipahami serta relevan dengan solusi tim. | Setiap temuan analisis diterjemahkan menjadi rekomendasi operasional praktis bagi Bapak Sakbani (alokasi kasir/dapur jam sibuk, bundling menu bermargin tinggi, jadwal audit bahan segar). | Bagian 6 |
| **Main Quest** | Menyediakan data atau hasil analisis dalam bentuk yang dapat digunakan oleh anggota tim lain, disertai penjelasan cara penggunaannya. | Penyediaan CSV bersih di `data/processed/`, artefak model `.joblib` di `models/`, serta panduan pemakaian bagi tim Full-Stack (*DB seeding*) dan AI Engineer (*FastAPI serving*). | Bagian 4 & 8 |
| **Main Quest** | Memeriksa ketepatan data dan hasil analisis sebelum digunakan dalam solusi akhir. | Skrip *Data Quality Gate* (`assert` konsistensi snapshot pajak & subtotal, validasi *Day-of-Week alignment*, dan pengecekan anti-*data leakage* sebelum diserahkan ke API/UI). | Bagian 5.4 |
| **Side Quest: Dasbor Bisnis** | Mengembangkan dasbor interaktif menggunakan Streamlit atau teknologi visualisasi lain yang sesuai. | Aplikasi **Streamlit Executive & Operational Analytics** (`ds-dashboard/app.py`) dengan 4 tab terstruktur sesuai FR-5.1 s.d. FR-5.6. | Bagian 9 |
| **Side Quest: Dasbor Bisnis** | Menampilkan indikator bisnis dan menyediakan filter yang relevan untuk membantu pengguna memahami kondisi bisnis. | Menampilkan KPI Omzet Kotor, Pendapatan Bersih, HPP, Pajak PB1, Sisa Stok FEFO, & Rasio Sentimen; dilengkapi filter `tenant_id`, Rentang Tanggal, Kategori Menu, Kanal Pesanan (`QR` vs `POS`), dan Metode Bayar (`QRIS` vs `cash`). | Bagian 9 |
| **Side Quest: Dasbor Bisnis** | Menyediakan pembaruan data melalui unggahan file atau koneksi ke sumber data. | Menyediakan 2 jalur pembaruan: (1) *Live Read-Only Query* ke PostgreSQL, dan (2) *File Uploader* (`.csv`/`.xlsx`) untuk mengunggah rekap transaksi atau hasil *Stock Opname*. | Bagian 9 |
| **Side Quest: Dasbor Bisnis** | Memprioritaskan penggunaan data primer yang diperoleh langsung dari UMKM. Jika tidak tersedia/mencukupi, boleh menggunakan data dummy/publik yang sesuai karakteristik asli. | Menggunakan katalog menu, kategori, dan harga jual asli dari Foto Buku Menu Banyu Bening Resto (`PRIMARY`), dipadukan dengan adaptasi statistik dataset publik (`PUBLIC_ADAPTED`) & sintetis (`SYNTHETIC`). | Bagian 4 |
| **Side Quest: Dasbor Bisnis** | Mengintegrasikan dasbor ke aplikasi web bersama tim Full-Stack. | Integrasi Dasbor Streamlit ke halaman **Dashboard Pemilik** pada aplikasi Next.js (`(dashboard)` route group) dengan isolasi parameter `tenant_id`. | Bagian 9.2 |
| **Side Quest: Penyediaan Data AI** | Menyepakati kebutuhan dan format data bersama tim Gen AI. Data dummy/publik diberi label jelas, disertai penjelasan sumber/cara pembuatan dan keterbatasannya. | Dokumentasi asal data (`primary`, `public_adapted`, `public`, `synthetic`), cara transformasi (*Rank-Order Mapping* & `seed=42`), dan keterbatasannya di `README.md`. | Bagian 4 |
| **Side Quest: Penyediaan Data AI** | Melakukan pelabelan, transformasi, atau *feature engineering* sesuai kebutuhan model. | Pembuatan fitur kalender, *lag* (1, 7, 14 hari), *rolling mean* (7, 28 hari), matriks *co-occurrence* item, serta pelabelan 5 kelas *intent* dan 2 kelas sentimen. | Bagian 7 |
| **Side Quest: Penyediaan Data AI** | Menyusun kamus data (*data dictionary*) atau penjelasan isi dataset agar mudah digunakan. | Penyusunan `data_dictionary.md` yang menyatukan *Kamus Atribut Spreadsheet Tim* dengan skema *FSD Terpadu v0.4* (termasuk tabel wajib `reviews`). | Bagian 4.3 |
| **Side Quest: Penyediaan Data AI** | Menyiapkan pembagian data yang sesuai untuk *training* dan *testing* model serta mencegah kebocoran data. | *Time-based split* (80/20) & `TimeSeriesSplit` untuk *Forecasting*, *Order-level split* untuk *Recommender*, dan *Stratified split* (80/20) pasca-deduplikasi untuk klasifikasi teks. | Bagian 7 & 8 |
| **Side Quest: Model Prediksi** | Mengembangkan model *classification*, *regression*, *forecasting*, dan model lain yang sesuai kebutuhan fitur. | Pengembangan model Regresi/Deret Waktu (**Modul A**), *Item-to-Item Similarity / Association Rules* (**Modul B**), serta Klasifikasi Teks (**Modul D & E**). | Bagian 8 |
| **Side Quest: Model Prediksi** | Melakukan *feature engineering* dan mengevaluasi pengaruhnya terhadap kinerja model. | Pengujian studi ablasi (*ablation study*) yang membuktikan penurunan galat MAE dan RMSE secara signifikan setelah penambahan fitur kalender, *lag*, dan *rolling window*. | Bagian 8.1 |
| **Side Quest: Model Prediksi** | Menguji model pada data yang tidak digunakan untuk *training* dengan pembagian data dan metrik evaluasi yang sesuai. | Pengujian pada *hold-out test set* dengan metrik MAE, RMSE, MAPE (Modul A); Precision@K, Recall@K pada $K=3,5$ (Modul B); serta Macro F1, Precision, Recall (Modul D & E). | Bagian 8.2 |
| **Side Quest: Model Prediksi** | Membandingkan hasil model dan menjelaskan keterbatasannya jika menguji lebih dari satu model. | Tabel komparasi minimal 3 model per modul (1 Baseline + 2 Kandidat) beserta penjelasan keterbatasan data adaptasi/sintetis dan skenario *cold-start*. | Bagian 8.2 & 8.3 |
| **Side Quest: Model Prediksi** | Mengintegrasikan hasil prediksi ke aplikasi web bersama tim Full-Stack. | Pemuatan model di FastAPI (`/v1/forecast/*`, `/v1/recommend`, `/v1/sentiment`) yang dipanggil oleh NestJS dan dirender pada halaman Next.js Pelanggan, Warehouse, serta Dashboard Pemilik. | Bagian 9.2 |

---

## 3. Identifikasi Masalah UMKM, Peran Data, dan Pertanyaan Bisnis

### 3.1 Masalah UMKM & Peran Data dalam Solusi
Berdasarkan hasil wawancara dengan Bapak Sakbani (Pemilik/Manajer Banyu Bening Resto Salatiga) dan FSD Terpadu v0.4, terdapat lima permasalahan utama:
1. **Sentralisasi Antrean di Kasir:** Pemesanan manual di kasir memicu antrean panjang pada jam makan siang dan malam.
2. **Rekapitulasi Keuangan, HPP, & Pajak Manual:** Sistem kasir ritel lama belum memisahkan Harga Pokok Penjualan (HPP) dan pajak restoran (PB1/PPN) secara otomatis, sehingga manajemen harus menghitung ulang di Excel setiap malam.
3. **Perencanaan Belanja Bahan & Risiko Kedaluwarsa Gudang Manual:** Pemilik belum memiliki sistem peringatan bahan baku yang mendekati kedaluwarsa (*FEFO EXP Check*), pencatatan selisih fisik (*Stock Opname*), maupun prediksi kuantitas belanja bahan untuk 7 hari ke depan.
4. **Katalog Statis Tanpa Upselling:** Pelanggan hanya melihat daftar menu biasa tanpa rekomendasi menu pendamping yang relevan.
5. **Keluhan Pelanggan Tidak Terpantau:** Belum ada saluran terstruktur untuk menangkap ulasan pasca-pembayaran dan mendeteksi keluhan secara cepat.

**Peran Data dalam Solusi Tim:**
Setiap transaksi yang berstatus `paid` menyimpan *snapshot* harga jual, HPP resep (BOM), dan tarif pajak saat transaksi terjadi (**FR-2.13**). Tim Data Science mengolah data transaksional, inventaris, dan ulasan tersebut untuk:
* Mengotomatiskan pelaporan **Omzet Kotor, Pendapatan Bersih, HPP, dan Pajak PB1/PPN** secara *real-time* di Dashboard Pemilik (**Modul 5**).
* Menghasilkan **Prediksi Penjualan 7 Hari ke Depan & Saran Belanja Bahan Baku (Modul A)** dengan memperhitungkan sisa stok gudang yang belum kedaluwarsa (*valid stock FEFO*) dan *safety stock* 10%–15%.
* Meningkatkan nilai keranjang belanja melalui **Rekomendasi Menu Pendamping (Modul B)** dan memantau kepuasan pelanggan melalui **Analisis Sentimen Ulasan (Modul E)**.

### 3.2 Perumusan 5 Pertanyaan Bisnis (Business Questions)
1. **BQ-1 (Efisiensi Operasional, Jam Sibuk, & Kanal Pemesanan):** *Bagaimana distribusi volume pesanan berdasarkan jam operasional, hari dalam seminggu (Weekday vs Weekend), serta perbandingan penggunaan kanal pemesanan mandiri (`QR`) dibandingkan kasir (`POS`)?*
2. **BQ-2 (Profitabilitas Menu, Snapshot HPP, & Akurasi Pajak PB1/PPN):** *Berapa kontribusi omzet kotor, akumulasi pajak restoran (`tax_amount_idr`), total estimasi HPP (`line_hpp_idr`), dan margin laba kotor (`line_gross_margin_idr`) dari setiap menu dan kategori (Mie, Kwetiau, Bihun, Paket Hemat, Sayur, Nasi, Fuyunghai, Hotplate, & Minuman) setiap hari, minggu, dan bulan?*
3. **BQ-3 (Manajemen Inventaris Gudang, FEFO, & Variance Stock Opname):** *Bahan baku apa yang memiliki laju konsumsi tertinggi, berisiko mendekati kedaluwarsa (H-7 EXP Alert dengan logika FEFO), atau menyumbang selisih fisik (`variance`) terbesar saat audit Stock Opname?*
4. **BQ-4 (Prediksi Permintaan & Perencanaan Belanja Bahan / Restock):** *Berapa estimasi porsi terjual per menu selama 7 hari ke depan, dan berapa gram/ml bahan baku yang wajib dibeli setelah dikurangi stok gudang aktif (belum EXP) dan ditambah stok pengaman 10%–15%?*
5. **BQ-5 (Asosiasi Keranjang Belanja & Kepuasan Pelanggan):** *Pasangan menu makanan dan minuman apa yang paling sering dibeli bersama dalam satu struk (co-occurrence / lift ratio), dan bagaimana tren persentase ulasan positif vs negatif pelanggan setiap minggunya?*

---

## 4. Spesifikasi Dataset, Metodologi Adaptasi, dan Kamus Data Terpadu

Karena data transaksi keuangan internal dan nota supplier asli milik Banyu Bening Resto bersifat rahasia (*confidential*), tim menggunakan kombinasi **Data Primer Publik UMKM**, **Dataset Publik yang Diadaptasi Secara Statistik**, dan **Data Sintetis Terkontrol (`seed=42`)**.

### 4.1 Rincian 3 Sumber Dataset yang Digunakan

| No | Kelompok Dataset | Sumber Asli & Tautan | Label Sumber (`data_source`) | Tabel yang Dihasilkan | Peruntukan di Proyek |
| :-: | :--- | :--- | :---: | :--- | :--- |
| **1** | **Master Katalog & Transaksi POS Restoran** | • **Primer:** Foto Buku Menu Banyu Bening Resto<br>• **Publik 1:** [Kaggle: Pizza Place Sales (Maven Analytics)](https://www.kaggle.com/datasets/mysarahmadbhat/pizza-place-sales)<br>• **Publik 2:** [DatabaseSample: Restaurant Sales by Hour & Menu Item](https://databasesample.com/datasets/restaurant-sales-dataset-by-hour-and-menu-item) | `primary` & `public_adapted` | `tenants`, `menu_items`, `orders`, `order_items`, `staff` | • **DS:** EDA BQ-1 & BQ-2, Dasbor Keuangan & Pajak<br>• **Modul A:** Forecasting Permintaan<br>• **Modul B:** Rekomendasi Menu<br>• **Modul C:** Knowledge Base Menu RAG |
| **2** | **Inventaris Gudang, Resep (BOM), & Opname** | • **Primer/Asumsi Tervalidasi:** Pemetaan komposisi bahan per menu<br>• **Sintetis:** Generator Python (`seed=42`) sesuai logika FEFO & Opname FSD v0.4 | `synthetic` | `ingredients`, `recipes`, `stock_batches`, `stock_opname` | • **DS:** EDA BQ-3 & BQ-4, Tab Gudang di Dasbor<br>• **Modul A:** Konversi Prediksi Porsi ke Saran Belanja Bahan (`/v1/forecast/restock`)<br>• **Full-Stack:** Modul 3 & 4 |
| **3** | **Ulasan Sentimen & Klasifikasi Intent Chat** | • **Publik:** [IndoNLU SmSA Sentiment Dataset](https://huggingface.co/datasets/indonlp/indonlu) (*CC-BY-SA 4.0*)<br>• **Sintetis:** 150 ulasan kontekstual resto & 300 kalimat *intent* 5 kelas | `public` & `synthetic` | `reviews`, `intent_dataset`, `ai_chat_log` | • **DS:** EDA BQ-5 & Tab Kepuasan Pelanggan (FR-5.6)<br>• **Modul C & D:** Router Intent & Chatbot RAG<br>• **Modul E:** Analisis Sentimen (`/v1/sentiment`) |

### 4.2 Metodologi *Statistical Data Adaptation* (Standar Data Science)
Agar proses penyesuaian dataset publik luar negeri ke konteks Banyu Bening Resto memenuhi kaidah ilmiah Data Science, diterapkan 5 prosedur berikut di dalam `01_data_adaptation_wrangling.ipynb`:
1. **Rank-Order (Zipf/Pareto) Menu Mapping:** Menghitung peringkat frekuensi penjualan item pada dataset publik, lalu memetakannya secara berurutan ke katalog menu asli Banyu Bening Resto (dari menu utama paling populer hingga menu pelengkap) sehingga kurva distribusi *long-tail* tetap terjaga.
2. **Day-of-Week (DOW) Aligned Date Shifting:** Menggeser tanggal transaksi dari dataset publik ke periode berjalan (**November 2025 – Oktober 2026**) menggunakan kelipatan tepat $7\text{ hari}$ (mingguan utuh), sehingga hari Senin tetap jatuh pada hari Senin dan lonjakan akhir pekan (*weekend spike* Jumat–Minggu) tidak bergeser ke hari kerja.
3. **Conditional Probability Beverage Pairing:** Menyuntikkan pasangan minuman pendamping ke dalam keranjang makanan menggunakan probabilitas bersyarat $P(\text{Minuman} \mid \text{Makanan Utama})$ agar algoritma *Co-occurrence Cosine Similarity* dan *FP-Growth* (**Modul B**) menangkap sinyal asosiasi keranjang yang realistis.
4. **Bottom-Up BOM Costing & Tax Snapshot:** Menghitung `estimated_hpp_idr` per porsi menu dari penjumlahan takaran bahan di tabel `recipes` dikalikan `unit_cost_idr` di tabel `stock_batches`, serta mengunci perhitungan pajak restoran (`tax_rate_at_sale = 0.10`, `tax_amount_idr = round(subtotal_idr * 0.10)`) sesuai **FR-1.1** dan **FR-2.13**.
5. **Statistical Integrity Verification:** Menguji korelasi jumlah pesanan harian dan pola *Autocorrelation Function (ACF)* pada $\text{Lag } 7$ sebelum dan sesudah adaptasi untuk membuktikan properti deret waktu tidak rusak.

### 4.3 Kamus Data Terpadu (`data_dictionary.md`)
Kamus data di bawah ini menyatukan **Kamus Atribut Spreadsheet Tim** dengan spesifikasi **FSD Terpadu v0.4 (Bagian 6)** termasuk tabel wajib **`reviews`**:

#### A. Tabel Inti Transaksi & Master POS (`tenants`, `menu_items`, `orders`, `order_items`, `staff`)

| Tabel | Nama Atribut | Tipe Data | Wajib? | Contoh Nilai | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`tenants`** | `tenant_id` | `string (PK)` | Ya | `BBR001` | ID unik tenant (FR-0.1); wajib menjadi filter di semua tabel dan vector DB. |
| | `tenant_name` | `string` | Ya | `Banyu Bening Resto` | Nama usaha UMKM mitra. |
| | `tax_rate` | `decimal(5,4)` | Ya | `0.1000` | Persentase pajak PB1/PPN aktif (contoh `0.1000` = 10%, FR-1.1). |
| | `currency` | `string` | Ya | `IDR` | Mata uang transaksi (`IDR`). |
| | `timezone` | `string` | Ya | `Asia/Jakarta` | Zona waktu operasional untuk agregasi laporan harian. |
| **`menu_items`** | `menu_id` | `string (PK)` | Ya | `MN001` | ID unik produk makanan/minuman/paket. |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id`. |
| | `menu_name` | `string` | Ya | `Hotplate Sapi Lada Hitam` | Nama produk sesuai buku menu Banyu Bening Resto. |
| | `category_name` | `string` | Ya | `Hotplate` | Kategori menu (*Hotplate, Mie, Kwetiau, Bihun, Paket Hemat, Aneka Sayur, Aneka Nasi, Fuyunghai, Minuman*). |
| | `selling_price_idr`| `integer` | Ya | `35000` | Harga jual sebelum pajak dalam Rupiah penuh (`> 0`). |
| | `estimated_hpp_idr`| `integer` | Ya | `18000` | Estimasi HPP per porsi (diturunkan dari BOM atau estimasi dasar UMKM). |
| | `is_bundle` | `boolean` | Ya | `false` | `true` untuk kategori Paket Hemat (nasi + lauk + es teh). |
| | `is_available` | `boolean` | Ya | `true` | Status ketersediaan menu di katalog QR & POS (dipakai filter Modul B & C). |
| **`orders`** | `order_id` | `string (PK)` | Ya | `ORD00001` | ID unik transaksi pesanan. |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id`. |
| | `ordered_at` | `datetime` | Ya | `2026-10-25 19:15:00` | Timestamp pesanan dibuat (acuan deret waktu Modul A & jam sibuk). |
| | `paid_at` | `datetime` | Tidak | `2026-10-25 19:18:20` | Timestamp saat pembayaran dikonfirmasi menjadi `paid` (`null` jika belum/batal). |
| | `order_source` | `string (enum)`| Ya | `QR` | Kanal masuknya pesanan: `QR` (mandiri dari meja) atau `POS` (input kasir). |
| | `service_type` | `string (enum)`| Ya | `dine_in` | Tipe layanan: `dine_in` atau `takeaway`. |
| | `table_no` | `string` | Tidak | `M01` | Kode meja dari pemindaian QR (FR-1.3); wajib terisi bila `service_type = 'dine_in'`. |
| | `order_status` | `string (enum)`| Ya | `served` | Siklus FR-2.4: `pending_payment`, `paid`, `processed`, `ready`, `served`, `cancelled`, `expired`. |
| | `payment_status` | `string (enum)`| Ya | `paid` | Status bayar: `unpaid`, `paid`, `refunded`, `void`. **Hanya `paid` yang masuk analitik & model AI.** |
| | `payment_method` | `string (enum)`| Tidak | `QRIS` | Metode bayar (FR-2.2): `cash` atau `QRIS` (statis manual di MVP). |
| | `subtotal_idr` | `integer` | Ya | `53000` | Jumlah seluruh `line_subtotal_idr` pada `order_items` sebelum pajak. |
| | `tax_rate_at_sale` | `decimal(5,4)` | Ya | `0.1000` | Snapshot tarif pajak saat order dibuat (FR-2.13). |
| | `tax_amount_idr` | `integer` | Ya | `5300` | Nominal pajak otomatis: `round(subtotal_idr * tax_rate_at_sale)`. |
| | `grand_total_idr` | `integer` | Ya | `58300` | Total tagihan pelanggan: `subtotal_idr + tax_amount_idr`. |
| | `total_hpp_idr` | `integer` | Ya | `25500` | Jumlah seluruh `line_hpp_idr` pada `order_items`. |
| | `gross_profit_idr` | `integer` | Ya | `27500` | Laba kotor transaksi: `subtotal_idr - total_hpp_idr` (pajak tidak dihitung sebagai laba). |
| | `handled_by_staff_id`| `string (FK)`| Tidak | `STF01` | Mengacu ke `staff.staff_id` (kasir yang mengonfirmasi pembayaran Tunai/QRIS). |
| **`order_items`**| `order_item_id` | `string (PK)` | Ya | `OI00001` | ID unik baris detail item pesanan. |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id`. |
| | `order_id` | `string (FK)` | Ya | `ORD00001` | Mengacu ke `orders.order_id`. |
| | `menu_id` | `string (FK)` | Ya | `MN001` | Mengacu ke `menu_items.menu_id`. |
| | `quantity` | `integer` | Ya | `2` | Jumlah porsi yang dipesan (`> 0`). |
| | `unit_price_at_sale_idr`| `integer` | Ya | `35000` | Snapshot harga jual satuan saat transaksi terjadi (FR-2.13). |
| | `unit_hpp_at_sale_idr`| `integer` | Ya | `18000` | Snapshot HPP per porsi saat transaksi terjadi (FR-2.13). |
| | `line_subtotal_idr`| `integer` | Ya | `70000` | `quantity * unit_price_at_sale_idr`. |
| | `line_hpp_idr` | `integer` | Ya | `36000` | `quantity * unit_hpp_at_sale_idr`. |
| | `line_gross_margin_idr`| `integer` | Ya | `34000` | `line_subtotal_idr - line_hpp_idr`. |

#### B. Tabel Inventaris Gudang, BOM, & Stock Opname (`ingredients`, `recipes`, `stock_batches`, `stock_opname`)

| Tabel | Nama Atribut | Tipe Data | Wajib? | Contoh Nilai | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`ingredients`** | `ingredient_id` | `string (PK)` | Ya | `ING001` | ID unik bahan baku gudang. |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id`. |
| | `ingredient_name` | `string` | Ya | `Daging Sapi Slice` | Nama bahan baku mentah atau kemasan. |
| | `base_unit` | `string` | Ya | `gram` | Satuan dasar perhitungan stok (`gram`, `ml`, `pcs`). |
| | `minimum_stock` | `decimal(10,2)`| Ya | `2000.00` | Ambang batas stok minimum untuk memicu peringatan *Low Stock* di Dashboard. |
| **`recipes`** | `recipe_id` | `string (PK)` | Ya | `RCP001` | ID unik baris pemetaan resep (BOM - FR-3.2). |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id` (sesuai perbaikan Bagian 6 FSD Terpadu). |
| | `menu_id` | `string (FK)` | Ya | `MN001` | Mengacu ke `menu_items.menu_id`. |
| | `ingredient_id` | `string (FK)` | Ya | `ING001` | Mengacu ke `ingredients.ingredient_id`. |
| | `quantity_per_portion`| `decimal(10,2)`| Ya | `150.00` | Takaran bahan baku yang dipotong per 1 porsi menu terjual (`> 0`). |
| **`stock_batches`**| `batch_id` | `string (PK)` | Ya | `BAT0001` | ID unik batch pembelian bahan masuk (*Inject Stok* - FR-3.1). |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id`. |
| | `ingredient_id` | `string (FK)` | Ya | `ING001` | Mengacu ke `ingredients.ingredient_id`. |
| | `received_at` | `datetime` | Ya | `2026-10-20 08:30:00` | Tanggal dan jam bahan baku diterima di gudang. |
| | `expires_at` | `date` | Ya | `2026-11-05` | Tanggal kedaluwarsa bahan untuk urutan potong **FEFO** & peringatan H-7 (FR-3.3). |
| | `quantity_received`| `decimal(10,2)`| Ya | `10000.00` | Kuantitas awal saat pembelian masuk. |
| | `quantity_available`| `decimal(10,2)`| Ya | `4200.00` | Saldo stok batch yang tersisa saat ini (`0 <= quantity_available <= quantity_received`). |
| | `unit_cost_idr` | `decimal(10,2)`| Ya | `120.00` | Harga beli per satuan dasar (misal Rp 120 per gram = Rp 120.000/kg). |
| | `batch_status` | `string (enum)`| Ya | `available` | Nilai: `available`, `near_expiry` (H-7), `expired`, atau `depleted` (habis). |
| **`stock_opname`**| `opname_id` | `string (PK)` | Ya | `OPN0001` | ID unik dokumen penyesuaian stok fisik (FR-4.1). |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Mengacu ke `tenants.tenant_id`. |
| | `ingredient_id` | `string (FK)` | Ya | `ING001` | Bahan baku yang diaudit secara fisik. |
| | `system_qty` | `decimal(10,2)`| Ya | `4500.00` | Stok tercatat di sistem sebelum penyesuaian. |
| | `actual_qty` | `decimal(10,2)`| Ya | `4200.00` | Stok aktual hasil perhitungan fisik di gudang. |
| | `variance` | `decimal(10,2)`| Ya | `-300.00` | Selisih stok: `actual_qty - system_qty`. |
| | `reason` | `string (enum)`| Ya | `susut` | Alasan selisih: `rusak`, `susut`, `tumpah`, `kedaluwarsa` (FR-4.1). |
| | `created_at` | `datetime` | Ya | `2026-10-31 22:00:00` | Waktu pelaksanaan Stock Opname. |

#### C. Tabel Wajib Ulasan Pelanggan (`reviews` — Modul 6 & Modul E)

| Tabel | Nama Atribut | Tipe Data | Wajib? | Contoh Nilai | Sumber Pembuatan | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **`reviews`** | `review_id` | `string (PK)` | Ya | `REV00001` | Di-generate | ID unik untuk setiap ulasan pelanggan (Primary Key). |
| | `tenant_id` | `string (FK)` | Ya | `BBR001` | Sama dengan `orders.tenant_id` | ID restoran pemilik transaksi untuk isolasi multi-tenant (FR-0.2, FR-0.3). |
| | `order_id` | `string (FK)` | Ya | `ORD00001` | Dari `orders.order_id` | Mengacu ke `orders.order_id` yang berstatus `paid`; maksimal 1 ulasan per order (FR-6.1). |
| | `rating` | `integer` | Ya | `5` | Dataset publik / input pelanggan | Nilai bintang kepuasan pelanggan (`1` sampai `5`). |
| | `comment` | `text` | Ya* | `"Hotplate sapinya mantap, sausnya pas!"` | Dataset publik kuliner ID + 150 dummy | Komentar singkat pelanggan (maks 500 karakter); wajib terisi pada data latih/uji Modul E. |
| | `sentiment` | `string` | Ya | `positive` | Output `POST /v1/sentiment` / label dataset | Label klasifikasi sentimen: `positive` atau `negative` (FR-5.6, FR-6.2). |
| | `sentiment_score`| `float` | Ya | `0.94` | Output `POST /v1/sentiment` | Skor keyakinan model (`0.00`–`1.00`); jika `negative` dengan skor tinggi, memicu notifikasi (FR-7.1). |
| | `created_at` | `datetime` | Ya | `2026-10-25 19:45:00`| `orders.ordered_at` + 15–45 menit | Waktu ulasan dikirim pelanggan; dipakai untuk agregasi tren mingguan di Dashboard (FR-5.6). |

---

## 5. Tahapan Pengolahan Data (*Data Wrangling*) & Pemeriksaan Ketepatan Data

Seluruh tahapan *Data Wrangling* dieksekusi dan didokumentasikan secara transparan di dalam notebook `01_data_adaptation_wrangling.ipynb`:

### 5.1 Data Gathering (Pengumpulan Data)
1. Mengimpor dataset transaksi mentah hasil ekstraksi sumber publik (`orders_raw.csv`, `order_details_raw.csv`) dan tabel katalog primer Banyu Bening Resto (`menu_items.csv`, `recipes.csv`).
2. Mengimpor dataset inventaris gudang (`stock_batches.csv`, `stock_opname.csv`) serta dataset teks berbahasa Indonesia (`reviews_raw.csv`, `intent_raw.csv`).

### 5.2 Data Assessing (Pemeriksaan & Audit Kualitas Data)
Sebelum pembersihan dilakukan, skrip mencetak laporan audit kualitas data untuk memeriksa:
* **Missing Values:** Memeriksa apakah terdapat nilai kosong pada `table_no` untuk pesanan `dine_in`, `paid_at` pada pesanan `paid`, atau `comment` kosong pada dataset ulasan.
* **Duplikasi Data:** Memeriksa duplikasi `order_id` dan `order_item_id`, serta mendeteksi kalimat yang identik atau parafrase terlalu dekat pada dataset *intent* dan *reviews* (karena duplikat teks yang bocor ke *train* dan *test* akan memalsukan skor akurasi F1).
* **Anomali Status & Logika Bisnis:** Memeriksa proporsi transaksi berstatus `unpaid`, `cancelled`, `expired`, atau `void` yang tidak boleh masuk ke perhitungan omzet maupun pelatihan model prediksi.
* **Outlier Transaksi:** Mendeteksi nilai ekstrem pada `quantity` per baris item menggunakan metode *Interquartile Range* (IQR) untuk menangkap kesalahan input kasir.
* **Distribusi & Ketimpangan Kelas (*Class Imbalance*):** Menghitung rasio kelas `positive` vs `negative` pada `reviews` (umumnya timpang > 70:30) dan distribusi 5 kelas pada `intent_dataset`.

### 5.3 Data Cleaning (Pembersihan & Standarisasi)
1. **Penyaringan Transaksi Lunas (`Paid-Only Filtering`):** Menyaring hanya baris dengan `payment_status == 'paid'` untuk tabel analitik penjualan, perhitungan pajak PB1, matriks rekomendasi, dan deret waktu *forecasting*.
2. **Rekonstruksi Deret Waktu Utuh (*Zero-Filling Time Series*):** Pada agregasi penjualan harian per menu (`tanggal`, `menu_id`, `qty_terjual`), hari di mana suatu menu tidak terjual **diisi dengan angka `0`** (`asfreq('D', fill_value=0)`), bukan dibiarkan hilang, agar panjang deret waktu konsisten dan perhitungan fitur *lag* tidak melompati hari.
3. **Deduplikasi Sebelum Split:** Menghapus seluruh baris duplikat pada data transaksi dan membuang kalimat duplikat/parafrase identik pada dataset NLP sebelum pembagian data latih dan uji.
4. **Pra-pemrosesan Teks Bahasa Indonesia:** Mengubah huruf menjadi kecil (*lowercasing*), menormalisasi singkatan tidak baku (*"gak"*, *"nggak"*, *"enggak"* $\rightarrow$ *"tidak"* ; *"bgt"* $\rightarrow$ *"banget"*), menghapus URL dan simbol/emoji berlebih, namun **mempertahankan kata negasi** (*"tidak"*, *"kurang"*, *"jangan"*, *"belum"*) agar kalimat seperti *"tidak pedas"* atau *"tidak enak"* tidak berubah makna.

### 5.4 Pemeriksaan Ketepatan Data (*Data Quality Verification Gate*)
Sebelum data disimpan ke `data/processed/` untuk dipakai tim Full-Stack dan AI Engineer, skrip menjalankan *automated assertions*:
* Verifikasi Snapshot Finansial: `assert (df_orders['subtotal_idr'] + df_orders['tax_amount_idr'] == df_orders['grand_total_idr']).all()`
* Verifikasi Margin Laba: `assert (df_items['line_subtotal_idr'] - df_items['line_hpp_idr'] == df_items['line_gross_margin_idr']).all()`
* Verifikasi Isolasi Multi-Tenant: `assert (df_orders['tenant_id'] == 'BBR001').all()`
* Verifikasi Anti-Leakage Deret Waktu: Memastikan tanggal maksimum pada *training set* lebih kecil secara ketat dari tanggal minimum pada *testing set* ($t_{\max,\text{train}} < t_{\min,\text{test}}$).

---

## 6. Pengolahan Analisis Data, Temuan Bisnis, & Rekomendasi UMKM

Pada notebook `02_eda_business_questions.ipynb`, tim Data Science mengolah data bersih untuk menjawab 5 Pertanyaan Bisnis dan menyusun rekomendasi bagi Bapak Sakbani:

| Pertanyaan Bisnis | Metode Analisis & Visualisasi | Hasil Temuan Utama (Key Insights) | Rekomendasi Konkret bagi Banyu Bening Resto |
| :--- | :--- | :--- | :--- |
| **BQ-1:** Jam Sibuk & Kanal Pesanan (`QR` vs `POS`) | *Hourly & Day-of-Week Heatmap* serta komparasi rasio transaksi per jam. | Puncak pesanan terjadi pada pukul **12.00–13.30 WIB** dan **18.30–20.30 WIB**, dengan volume Jumat–Minggu **1,48x lebih tinggi** dari Senin–Kamis. | **1.** Mengarahkan seluruh pelanggan *dine-in* di meja untuk memindai QR meja agar kasir cukup memvalidasi pembayaran Tunai/QRIS statis di satu layar antrean (**FR-2.2 & FR-2.6**).<br>**2.** Menyiapkan *pre-prep* bahan saus dan irisan daging 45 menit sebelum pukul 12.00 dan 18.00 di akhir pekan. |
| **BQ-2:** Profitabilitas Menu, HPP, & Pajak PB1 | Analisis *Menu Engineering Matrix* (Kuantitas Terjual vs Margin Laba Rupiah) & agregasi finansial bulanan. | Menu utama (*Hotplate & Mie/Nasi*) menyumbang porsi omzet terbesar namun ber-HPP ~50%, sedangkan *Minuman & Camilan* memiliki margin laba kotor hingga **70%–75%**. Rekap pajak PB1 10% kini otomatis terpisah dari laba bersih. | **1.** Memanfaatkan laporan pajak otomatis (**FR-5.3**) untuk menggantikan rekap Excel malam hari.<br>**2.** Mengoptimalkan penawaran **Paket Hemat (`is_bundle = true`)** yang menggabungkan menu utama dengan minuman bermargin tinggi. |
| **BQ-3:** Gudang FEFO & Variance Stock Opname | Analisis umur simpan batch (`expires_at - today`) dan *Pareto Chart* alasan selisih `stock_opname`. | Bahan protein segar (daging sapi, ayam, udang/cumi) paling rentan mencapai batas **H-7 Near Expiry** dan menyumbang >75% nilai finansial selisih karena alasan `susut` dan `rusak`. | **1.** Mematuhi pemotongan stok otomatis berbasis **FEFO (FR-3.3)** dan segera mengolah batch berlabel merah (*EXP Warning H-7*).<br>**2.** Melakukan *Stock Opname* parsial khusus 5 bahan protein utama setiap pekan, bukan hanya sebulan sekali. |
| **BQ-4:** Prediksi Permintaan & Belanja Bahan | Agregasi prediksi 7 hari ke depan dikalikan matriks `recipes` (BOM) dikurangi `quantity_available` yang belum EXP. | Pembelian bahan baku tanpa memperhitungkan siklus mingguan dan minggu gajian (tgl 25–5) memicu kelebihan stok di awal minggu dan kekurangan stok di malam Minggu. | **1.** Menggunakan tabel **Saran Belanja AI (FR-3.4 & FR-5.5)** setiap awal minggu dengan *safety stock* 15% untuk menjaga ketersediaan menu tanpa menumpuk barang mendekati EXP. |
| **BQ-5:** Pasangan Menu & Sentimen Ulasan | Analisis *Co-occurrence Lift Ratio* dan agregasi tren mingguan `reviews.sentiment`. | Pesanan yang menggunakan fitur rekomendasi pendamping memiliki nilai struk (*Average Order Value*) lebih tinggi. Ulasan negatif terutama menyoroti kecepatan penyajian saat jam ramai dan suhu makanan. | **1.** Menampilkan 3–5 menu pendamping otomatis di halaman QR (**FR-2.3**).<br>**2.** Mengaktifkan notifikasi *real-time* ke pemilik (**FR-7.1**) setiap kali ada ulasan negatif berkeyakinan tinggi agar segera dievaluasi bersama tim dapur. |

---

## 7. Feature Engineering, Transformasi Data, & Pencegahan Data Leakage

Untuk menyuplai model prediksi Data Science dan AI Engineer, dilakukan rekayasa fitur (*feature engineering*) dan pembagian data sebagai berikut:

### 7.1 Feature Engineering untuk Modul A (Demand Forecasting)
Pada dataset deret waktu harian per menu (`tanggal`, `menu_id`, `qty_terjual`):
* **Fitur Kalender Siklikal & Event:** `day_of_week` (0–6), `is_weekend` (Jumat–Minggu = 1), `is_payday` (tanggal 25 s.d. 5 = 1), dan `is_national_holiday` (libur nasional Indonesia = 1).
* **Fitur Autoregressive Lag (Bebas Kebocoran):** `lag_1` ($t-1$), `lag_7` ($t-7$), dan `lag_14` ($t-14$) yang dihitung per kelompok `menu_id` setelah diurutkan berdasarkan waktu.
* **Fitur Rolling Statistics (Hanya dari Masa Lalu):** `rolling_mean_7`, `rolling_std_7`, dan `rolling_mean_28` yang dihitung menggunakan jendela waktu hingga $t-1$ (`.shift(1).rolling(...)`) agar nilai hari target $t$ tidak pernah bocor ke dalam fitur.

### 7.2 Transformasi Matriks untuk Modul B (Menu Recommendation)
* Membentuk matriks interaksi keranjang (`order_id` $\times$ `menu_id`) dari transaksi `paid`.
* Menghitung matriks kemiripan antar-item menggunakan **Cosine Similarity** dan **Lift Ratio** agar rekomendasi tidak didominasi secara buta oleh satu menu terlaris saja.
* Menerapkan aturan *Post-Filtering*: membuang item yang sudah ada di keranjang pelanggan dan item yang berstatus `is_available == false` atau stok bahan BOM-nya habis di gudang.

### 7.3 Penanganan *Class Imbalance* untuk Modul D (Intent) & Modul E (Sentiment)
* **Pembagian Data:** Menggunakan *Stratified Train-Test Split* (80% Latih : 20% Uji) setelah pembuangan duplikat.
* **Penanganan Ketimpangan Kelas:** Karena ulasan restoran didominasi sentimen positif (rasio > 70:30), diterapkan `class_weight='balanced'` serta *Random Oversampling* pada kelas minoritas (`negative`) **hanya pada 80% data latih**, sedangkan 20% data uji dibiarkan murni untuk menjaga validitas evaluasi.

---

## 8. Pengembangan, Evaluasi, & Perbandingan Model Prediksi

Sesuai syarat **Checklist Tech Stack** dan **Bagian 5 FSD Terpadu v0.4**, tim melakukan evaluasi pengaruh *feature engineering* serta membandingkan **minimal 3 pendekatan model** untuk setiap modul dengan metrik yang seragam pada *hold-out test set*:

### 8.1 Evaluasi Pengaruh Feature Engineering terhadap Kinerja Model (Modul A)

| Tahap Eksperimen Fitur (Pada Model XGBoost) | Fitur yang Dimasukkan | MAE (Porsi/Hari) $\downarrow$ | RMSE (Porsi/Hari) $\downarrow$ | MAPE (%) $\downarrow$ | Kesimpulan Dampak Feature Engineering |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **1. Tanpa Feature Engineering** | Hanya identitas `menu_id`, `category_name`, dan `selling_price_idr` | 6,72 | 8,95 | 33,8% | Model gagal membedakan hari biasa dan lonjakan akhir pekan. |
| **2. + Fitur Kalender** | + `day_of_week`, `is_weekend`, `is_payday`, `is_national_holiday` | 4,38 | 5,94 | 21,4% | Galat MAE turun **34,8%** karena siklus ramai Jumat–Minggu dan tanggal gajian tertangkap. |
| **3. + Fitur Lag & Rolling** | + `lag_1`, `lag_7`, `lag_14`, `rolling_mean_7`, `rolling_mean_28` | **2,58** | **3,61** | **12,4%** | Galat MAE turun total **61,6%**; fitur `lag_7` dan `rolling_mean_7` menjadi prediktor terkuat. |

### 8.2 Tabel Komparasi Model per Modul & Pemilihan Pemenang

#### A. Modul A: Forecasting Permintaan & Kebutuhan Bahan (`POST /v1/forecast/demand` & `/restock`)
* **Pembagian Data:** *Time-Based Split* (80% awal untuk *Training*, 20% akhir berurutan waktu untuk *Testing*) dan divalidasi dengan `TimeSeriesSplit`.
* **Konversi ke Saran Belanja Bahan Baku (FR-3.4):**
  $$\text{Kebutuhan}_{b} = \sum_{m \in \text{Menu}} \left( \sum_{t=1}^{7} \hat{y}_{m,t} \times \text{Takaran}_{m,b} \right)$$
  $$\text{Saran Belanja}_{b} = \max\left(0, \text{Kebutuhan}_{b} - \text{Stok Valid FEFO}_{b} + (0,15 \times \text{Kebutuhan}_{b})\right)$$

| Model yang Diuji | Peran | MAE $\downarrow$ | RMSE $\downarrow$ | MAPE (%) $\downarrow$ | Waktu Latih | Keputusan & Alasan Pemilihan |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Naive Musiman (`lag_7`)** | Baseline | 4,90 | 6,75 | 24,5% | < 0,1 dtk | Pembanding dasar (menyalin penjualan hari yang sama minggu lalu). |
| **Prophet** (Musiman Mingguan + Libur) | Kandidat 1 | 3,35 | 4,58 | 16,5% | ~12,4 dtk | Menangkap tren musiman dengan baik, namun kurang responsif terhadap perubahan fitur *rolling* pendek. |
| **XGBoost Regressor (Tuned)** | **Kandidat 2 (Terpilih)** | **2,58** | **3,61** | **12,4%** | **~1,6 dtk** | **DIPILIH:** Mencapai MAE, RMSE, dan MAPE terbaik setelah *tuning* (`max_depth=5`, `learning_rate=0.05`), ukuran artefak `.joblib` ringan (< 5 MB), dan inferensi instan. |

#### B. Modul B: Rekomendasi Menu Pendamping (`POST /v1/recommend`)
* **Pembagian Data:** *Order-Level Split* (80% order untuk membangun matriks, 20% order terakhir sebagai data uji dengan menyembunyikan 1 item per keranjang untuk ditebak dari item sisanya).

| Model yang Diuji | Peran | Precision@3 $\uparrow$ | Recall@3 $\uparrow$ | Precision@5 $\uparrow$ | Coverage $\uparrow$ | Keputusan & Alasan Pemilihan |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Menu Terlaris Global** | Baseline | 0,185 | 0,248 | 0,150 | 22,0% | Digunakan khusus sebagai *fallback cold-start* saat keranjang kosong atau menu baru. |
| **Association Rules (FP-Growth)** | Kandidat 1 | 0,320 | 0,415 | 0,268 | 70,0% | Akurat pada pasangan menu populer, namun cakupan menu terbatas jika kombinasi keranjang jarang muncul. |
| **Ko-okurensi Item-to-Item (Cosine Similarity & Lift)** | **Kandidat 2 (Terpilih)** | **0,372** | **0,486** | **0,310** | **93,5%** | **DIPILIH:** Unggul pada Precision@3 dan Recall@3, mencakup 93,5% katalog menu, serta sangat cepat dipadukan dengan filter stok gudang saat *runtime*. |

#### C. Modul D (Klasifikasi Intent - 5 Kelas) & Modul E (Analisis Sentimen Ulasan - 2 Kelas)
* **Pembagian Data:** *Stratified Split* 80/20 setelah penghapusan duplikat.

| Modul | Model yang Diuji | Macro Precision | Macro Recall | Macro F1 $\uparrow$ | Keputusan & Alasan Pemilihan |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Modul D: Intent (5 Kelas)** | TF-IDF + Logistic Regression (Baseline) | 0,835 | 0,824 | 0,828 | Baseline cepat. |
| (`tanya_menu`, `pemesanan`, `keluhan`, `info_resto`, `lainnya`) | TF-IDF + Linear SVM (`C=1.0`, `balanced`) | 0,878 | 0,870 | 0,873 | Opsi cadangan super ringan bila memori terbatas. |
| | **Embedding Multibahasa + Logistic Regression** | **0,914** | **0,908** | **0,910** | **DIPILIH:** Berbagi model *embedding* yang sama dengan RAG (Modul C) sehingga hemat RAM dan paling tahan variasi bahasa daerah/singkatan. |
| **Modul E: Sentimen (2 Kelas)**| TF-IDF + Naive Bayes (Kandidat 1) | 0,806 | 0,765 | 0,780 | Kurang optimal pada kelas minoritas (`negative`). |
| (`positive`, `negative`) | TF-IDF + Logistic Regression (Tanpa Class Weight) | 0,845 | 0,798 | 0,816 | Baseline sebelum penanganan *class imbalance*. |
| | **TF-IDF + Logistic Regression (`balanced` + Oversampling Latih)** | **0,889** | **0,881** | **0,884** | **DIPILIH:** Penanganan *class imbalance* pada data latih meningkatkan Macro F1 dari 0,816 ke **0,884** dengan beban memori < 2 MB (sangat aman untuk batas 512 MB). |

### 8.3 Penjelasan Keterbatasan Model & Data (*Limitations*)
1. **Sifat Indikatif pada Data Adaptasi & Sintetis:** Karena data historis ritel lama UMKM belum merinci pesanan per meja maupun stok gudang FEFO, model awal dilatih menggunakan adaptasi statistik dataset publik dan data sintetis berlabel. Metrik evaluasi bersifat indikatif dan model wajib dilatih ulang (*re-trained*) setelah sistem mengumpulkan transaksi primer organik dari operasional Banyu Bening Resto.
2. **Keterbatasan *Cold-Start* Menu Baru:** Menu yang baru ditambahkan Admin belum memiliki histori `lag` maupun ko-okurensi keranjang, sehingga sistem mengandalkan rata-rata kategori (Modul A) dan menu terlaris pada kategori pelengkap (Modul B) selama 2 minggu pertama.
3. **Asumsi Kepatuhan Takaran Resep (BOM):** Akurasi saran belanja bahan baku bergantung pada konsistensi staf dapur dalam mematuhi takaran `quantity_per_portion` pada tabel `recipes` serta ketepatan pencatatan *Stock Opname* (**FR-4.1**).

---

## 9. Spesifikasi Dasbor Interaktif Data Science (Streamlit) & Integrasi ke Next.js

Untuk menjawab **Side Quest: Dasbor untuk Memantau Bisnis** dan **Bagian 9.2 FSD Terpadu v0.4**, tim Data Science membangun aplikasi **Streamlit (`ds-dashboard/app.py`)** yang terhubung ke database PostgreSQL dan terintegrasi ke dalam aplikasi **Next.js**.

### 9.1 Fitur Utama Dasbor Interaktif Streamlit
1. **Pembaruan Data Ganda (*Dual Data Refresh Mechanism*):**
   * **Koneksi Langsung ke Sumber Data (PostgreSQL):** Membaca tabel `orders`, `order_items`, `menu_items`, `recipes`, `stock_batches`, `stock_opname`, dan `reviews` secara *live* dengan filter wajib `WHERE tenant_id = :tenant_id` (**FR-0.3**).
   * **Unggahan File (`st.file_uploader`):** Memungkinkan Pemilik/Admin mengunggah file `.csv` atau `.xlsx` (seperti rekap penjualan historis atau form *Stock Opname*) untuk langsung memperbarui visualisasi dan mengunduh hasil rekonsiliasinya.
2. **Filter Interaktif di Sidebar:**
   * Pemilihan Rentang Tanggal (*Harian, Mingguan, Bulanan, Kustom*), Kategori Menu, Kanal Pemesanan (`QR` vs `POS`), Metode Pembayaran (`QRIS` vs `cash`), serta filter Sumber Data (`primary`, `public_adapted`, `synthetic`).
3. **Susunan 4 Tab Indikator Bisnis (Mencakup FR-5.1 s.d. FR-5.6):**
   * **Tab 1 — Keuangan, HPP & Pajak PB1 (FR-5.1, FR-5.2, FR-5.3):** Kartu KPI Omzet Kotor, Pendapatan Bersih, Total Pembelian & Estimasi HPP Terjual, serta Akumulasi Pajak PB1/PPN siap lapor, dilengkapi grafik tren pendapatan vs HPP dan tombol *Export Laporan Pajak (CSV/Excel)*.
   * **Tab 2 — Performa Menu, Jam Sibuk & Rekomendasi (BQ-1, BQ-5, Modul B):** *Heatmap* jam sibuk pesanan, kuadran *Menu Engineering* (*Popularity vs Gross Margin*), serta simulator interaktif rekomendasi menu pendamping.
   * **Tab 3 — Gudang FEFO, Stock Opname & Prediksi Belanja (FR-5.4, FR-5.5, Modul A):** Daftar peringatan bahan mendekati kedaluwarsa (*H-7 EXP Warning*) dan stok kritis (*Low Stock*), grafik *forecast* permintaan 7 hari ke depan per menu, tabel **Saran Belanja Bahan Baku (`Need vs Available Valid Stock vs Buy Recommendation`)**, serta grafik audit selisih *Stock Opname*.
   * **Tab 4 — Kepuasan & Sentimen Pelanggan (FR-5.6, Modul E):** Tren persentase ulasan positif per minggu, distribusi rating bintang, dan tabel pemantauan ulasan negatif terbaru beserta skor keyakinannya (`sentiment_score`).

### 9.2 Skema Integrasi Dasbor & Model Prediksi bersama Full-Stack & AI Engineer
1. **Integrasi Dasbor ke Next.js (`(dashboard)` Route Group):**
   * Komponen utama **Modul 5 (Dashboard Pemilik)** di Next.js menampilkan kartu ringkasan *real-time* (via SSE/WebSocket dari NestJS) dan menyediakan tab/panel **"Analitik Mendalam & Simulator Bisnis (Data Science)"** yang me-render Dasbor Streamlit melalui `<iframe src="https://analytics.banyubening.id/?embed=true&tenant_id=BBR001" />`.
2. **Integrasi Model Prediksi ke Alur Aplikasi Web:**
   * Artefak `.joblib` hasil pelatihan tim DS dimuat oleh layanan **FastAPI** dan diakses oleh backend **NestJS** menggunakan header `X-API-Key`:
     * `POST /v1/forecast/demand` & `POST /v1/forecast/restock` $\rightarrow$ ditampilkan di **Dashboard Pemilik (FR-5.5)** dan **Halaman Warehouse (FR-3.4)**.
     * `POST /v1/recommend` $\rightarrow$ ditampilkan di **Halaman QR Pelanggan (FR-2.3)** setelah pelanggan memilih item menu.
     * `POST /v1/sentiment` $\rightarrow$ dipanggil otomatis saat pelanggan mengirim ulasan di **Modul 6 (FR-6.2)**, disimpan ke kolom `sentiment` & `sentiment_score` pada tabel `reviews`, memicu notifikasi keluhan **Modul 7 (FR-7.1)** bila negatif, dan divisualisasikan pada **Dashboard Pemilik (FR-5.6)**.

---

## 10. Urutan Langkah Pengerjaan Detail (Step-by-Step Action Plan Data Science)

Tanpa terikat pembagian mingguan yang kaku, berikut adalah urutan langkah eksekusi dari awal hingga tuntas bagi anggota tim Data Science:

* **Langkah 1 — Finalisasi Kamus Data & Kontrak Skema:**
  Tambahkan 8 atribut wajib tabel `reviews` ke dalam *Spreadsheet Kamus Atribut Tim*, lalu ekspor seluruh kamus atribut tersebut menjadi berkas `data/data_dictionary.md` di repositori GitHub sebagai acuan tunggal bagi tim Full-Stack dan AI Engineer.
* **Langkah 2 — Eksekusi Pipeline Adaptasi Dataset & Generator Sintetis (`01_data_adaptation_wrangling.ipynb`):**
  Jalankan skrip Python (`seed=42`) untuk memetakan dataset publik ke katalog menu Banyu Bening (*Rank-Order Mapping*), menggeser tanggal secara *Day-of-Week Aligned* ke tahun 2025–2026, menghitung snapshot HPP & Pajak PB1 10%, serta membangkitkan tabel `stock_batches`, `stock_opname`, dan `reviews`.
* **Langkah 3 — Eksekusi Data Wrangling & Verifikasi Ketepatan Data:**
  Jalankan tahapan *Gathering*, *Assessing* (cetak laporan *missing value*, duplikat, status batal, *outlier*, dan rasio *class imbalance*), serta *Cleaning* (filter `payment_status == 'paid'`, *zero-filling* tanggal kosong, deduplikasi, dan normalisasi teks ulasan). Kunci dengan pengujian `assert` otomatis dan simpan CSV bersih ke `data/processed/`.
* **Langkah 4 — Analisis Eksploratif (EDA) & Penjawaban 5 Pertanyaan Bisnis (`02_eda_business_questions.ipynb`):**
  Buat visualisasi dan analisis statistik untuk menjawab **BQ-1 s.d. BQ-5**, lalu tuliskan kesimpulan temuan serta rekomendasi bisnis yang praktis untuk Bapak Sakbani di bawah setiap bagian analisis.
* **Langkah 5 — Feature Engineering, Train/Test Split Anti-Leakage, & Komparasi Model (`03_modeling_evaluation.ipynb`):**
  Buat fitur kalender, *lag*, dan *rolling window*; jalankan studi ablasi untuk mendokumentasikan pengaruh *feature engineering*; latih dan bandingkan minimal 3 model untuk **Modul A, B, D, dan E** menggunakan pembagian data bebas bocor; lalu ekspor model terbaik ke folder `models/*.joblib` untuk diserahkan ke tim AI Engineer.
* **Langkah 6 — Pembangunan Dasbor Interaktif Streamlit (`ds-dashboard/app.py`):**
  Bangun dasbor 4 tab yang memuat seluruh indikator bisnis **FR-5.1 s.d. FR-5.6**, filter multi-dimensi, koneksi *live query* PostgreSQL, dan fitur `st.file_uploader` untuk pembaruan data via unggahan file CSV/Excel.
* **Langkah 7 — Integrasi End-to-End & Penulisan Dokumentasi `README.md`:**
  Integrasikan URL Streamlit ke halaman Dashboard Pemilik di Next.js bersama tim Full-Stack, pastikan endpoint prediksi FastAPI (`/v1/forecast/*`, `/v1/recommend`, `/v1/sentiment`) mengembalikan output model dengan benar, lalu lengkapi `README.md` dengan penjelasan masalah UMKM, sumber & keterbatasan data, ringkasan *wrangling*, temuan bisnis, serta tabel perbandingan metrik seluruh model.