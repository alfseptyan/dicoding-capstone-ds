# Kamus Data Terpadu (*Data Dictionary*) — Banyu Bening Resto (`BBR001`)

Dokumen ini mendefinisikan struktur skema, tipe data, satuan, label sumber data (`data_origin`), serta aturan validasi bisnis untuk seluruh dataset yang disiapkan oleh tim **Data Science** bagi tim **Full-Stack (NestJS + React/Vite + PostgreSQL)** dan tim **AI Engineer (FastAPI)**.

---

## 1. Label Asal & Karakteristik Data (`data_origin`)

Sesuai syarat rubrik **Penyediaan Data untuk Model AI**, setiap tabel dan baris data diberi label asal (`data_origin`) yang eksplisit:

| Kode Label | Penjelasan Sumber & Cara Pembuatan | Keterbatasan Penggunaan (*Limitations*) |
| :--- | :--- | :--- |
| **`primary`** | Diperoleh langsung dari katalog produk dan harga resmi situs/buku menu **UMKM Banyu Bening Resto, Salatiga** (`https://restobanyubening.com/`). | Harga menu kurasi ikan segar yang di situs tertulis `/ ons` telah dinormalisasi ke satuan `porsi` utuh agar seragam di POS & keranjang QR. |
| **`primary_validated`** | Komposisi bahan baku (`ingredients`), takaran resep (`recipes` / BOM), dan estimasi HPP per porsi yang diturunkan secara *bottom-up* dari menu asli Banyu Bening Resto. | Takaran gram/ml per porsi merupakan standar resep dapur; akurasi pemotongan stok nyata bergantung pada kepatuhan takaran juru masak dan audit *Stock Opname* rutin. |
| **`synthetic_seed_20261112`** | Data transaksi historis (`orders`, `order_items`), batch stok FEFO (`stock_batches`), dan penyesuaian fisik (`stock_opname`) yang dibangkitkan secara deterministik (`seed=20261112` & `seed=42`) mengikuti distribusi jam sibuk restoran keluarga dan pola akhir pekan (*weekend spike*). | Karena nota keuangan internal UMKM bersifat rahasia (*confidential*), urutan peringkat model ML pada data ini bersifat indikatif dan model wajib dilatih ulang (*re-trained*) setelah aplikasi mengumpulkan data transaksi organik selama 1–3 bulan. |
| **`synthetic_contextual_v2`** | Dataset 2.000 ulasan pelanggan berbahasa Indonesia (`reviews_clean.csv`) beserta 100 komentar uji tulisan tangan independen (*independent hand-written test set*) yang mencakup kalimat normal serta kalimat sulit (negasi & kontras). | Dibangun untuk menguji ketahanan model klasifikasi sentimen terhadap fenomena negasi (*"nggak mengecewakan"*, *"tidak lambat"*) dan kalimat kontras (*"tempatnya bagus, tapi makanannya hambar"*). |

---

## 2. Tabel Master Katalog & Resep BOM

### 2.1 `menu_items_clean.csv` (199 Baris — 26 Kategori)

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Aturan Transformasi / Validasi |
| :--- | :--- | :--- | :--- |
| `tenant_id` | `string` | `BBR001` | Identifier tenant UMKM Banyu Bening Resto (UUID di Postgres: `4d1f5d21-6d61-4b7c-9c3e-4f4a2a5db001`). |
| `menu_id` | `string (PK)` | `M0003` | Kode unik item menu (`M0001` s.d. `M0199`). |
| `category_id` | `string (FK)` | `CAT002` | Kode unik kategori menu (`CAT001` s.d. `CAT026`). |
| `category_name` | `string` | `Alacarte` | Nama kategori menu (*Alacarte, Bihun, Gurame, Hotplate, Juice, Kwetiau, Lele, Mie, Minuman Standar, Nasi Goreng, Nila, Paket Ber 5, Paket Personal, Sambal, Sapo Tahu, Sayuran, Snack, Soda, Soto*, dll.). |
| `menu_name` | `string` | `Ayam Bakar Tok` | Nama produk bersih (akhiran `/ ons` pada 29 menu ikan telah dibersihkan). |
| `selling_price_idr` | `integer` | `23000` | Harga jual per porsi dalam Rupiah penuh sebelum pajak (`>= 0`). Untuk menu yang awalnya `/ ons`, harga telah dikalikan faktor porsi standar (Gurame $\times 5$, Nila $\times 4$, Lele $\times 3$). |
| `estimated_hpp_idr` | `integer` | `8280` | Estimasi Harga Pokok Penjualan (HPP) per porsi dari penjumlahan biaya komponen resep BOM. |
| `gross_margin_idr` | `integer` | `14720` | Margin laba kotor per porsi dalam Rupiah (`selling_price_idr - estimated_hpp_idr`). |
| `gross_margin_pct` | `float` | `64.0` | Persentase margin laba kotor (`(gross_margin_idr / selling_price_idr) * 100`). |
| `selling_unit` | `string` | `porsi` | Satuan jual terstandarisasi (`porsi`). |
| `was_per_ons` | `boolean` | `False` | Penanda apakah menu tersebut berasal dari harga `/ ons` pada data mentah. |
| `portion_factor` | `integer` | `1` | Faktor pengali konversi dari `/ ons` ke `porsi` (`1` untuk porsi biasa, `5` untuk Gurame 500g, `4` untuk Nila 400g, `3` untuk Lele 300g). |
| `is_bundle` | `boolean` | `False` | `True` untuk menu paket (Paket Personal / Paket Ber 5). |
| `is_available` | `boolean` | `True` | Status aktif/tersedia di katalog pemesanan QR dan Chatbot AI. |
| `data_origin` | `string` | `primary` | Label sumber data (`primary`). |

### 2.2 `ingredients_clean.csv` (106 Baris Bahan Baku)

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :--- |
| `tenant_id` | `string` | `BBR001` | Identifier tenant. |
| `ingredient_id` | `string (PK)` | `ING001` | Kode unik bahan baku (`ING001` s.d. `ING106`). |
| `ingredient_name` | `string` | `Daging Ayam Potong` | Nama bahan baku gudang. |
| `category` | `string` | `Protein` | Kelompok bahan baku (*Protein, Sayur, Bumbu, Bahan Kering, Minuman, Kemasan*, dll.). |
| `base_unit` | `string (enum)`| `gram` | Satuan dasar takaran stok: `gram`, `milliliter`, atau `piece`. |
| `minimum_stock` | `integer` | `2000` | Batas ambang stok kritis (*Low Stock Threshold*) untuk memicu peringatan di Dashboard Owner. |
| `shelf_life_days` | `integer` | `3` | Estimasi masa simpan bahan (hari) sejak diterima; digunakan sebagai fitur `log_shelf_life` pada model Forecasting dan perhitungan risiko *expired* FEFO. |
| `reference_unit_cost_idr` | `integer` | `45` | Harga beli acuan per 1 satuan dasar (`base_unit`) dalam Rupiah. |
| `allergen_tags` | `string` | `ikan;seafood` | Daftar pemicu alergi dipisahkan titik koma (`;`). |
| `data_origin` | `string` | `primary_validated` | Label sumber data. |

### 2.3 `recipes_bom_clean.csv` (1.481 Baris Komponen Resep / Bill of Materials)

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :--- |
| `tenant_id` | `string` | `BBR001` | Identifier tenant. |
| `recipe_id` | `string (PK)` | `R0001` | Kode unik baris komponen resep (`R0001` s.d. `R1481`). |
| `menu_id` | `string (FK)` | `M0003` | Mengacu ke `menu_items_clean.menu_id`. |
| `ingredient_id` | `string (FK)` | `ING001` | Mengacu ke `ingredients_clean.ingredient_id`. |
| `quantity_per_portion` | `integer` | `150` | Kuantitas bahan baku yang dibutuhkan untuk membuat 1 porsi menu (`> 0`, sudah dikalikan `portion_factor` untuk menu ikan). |
| `unit` | `string` | `gram` | Satuan takaran (wajib identik dengan `ingredients_clean.base_unit`). |
| `scaled_for_portion` | `boolean` | `False` | `True` jika kuantitas resep telah disesuaikan dari satuan `/ ons` ke 1 ekor/porsi penuh. |
| `verification_status` | `string` | `terverifikasi` | Status verifikasi takaran BOM. |
| `data_origin` | `string` | `primary_validated` | Label sumber data. |

---

## 3. Tabel Transaksi Penjualan & Ulasan Pelanggan

### 3.1 `orders_clean.csv` (2.017 Transaksi Lunas / `paid` dari 2.285 Total Order)

> **Catatan Data Cleaning:** Sebanyak **268 baris** pada data mentah yang berstatus `placed` (`pending`) atau `cancelled` telah dibuang dari dataset analitik & pelatihan model agar tidak mencemari perhitungan omzet maupun peramalan permintaan (*demand forecasting*).

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :--- |
| `tenant_id` | `string` | `BBR001` | Identifier tenant. |
| `order_id` | `string (PK)` | `ORD000001` | Kode unik pesanan. |
| `ordered_at` | `datetime` | `2026-05-01 11:38:00` | Timestamp pesanan dibuat (`YYYY-MM-DD HH:MM:SS`, rentang `2026-05-01` s.d. `2026-10-31`). |
| `paid_at` | `datetime` | `2026-05-01 11:42:00` | Timestamp pembayaran lunas. |
| `order_source` | `string (enum)`| `QR` | Kanal masuknya pesanan: `QR` (mandiri dari meja) atau `POS` (input kasir). |
| `service_type` | `string (enum)`| `dine_in` | Tipe layanan: `dine_in` (makan di tempat) atau `takeaway` (bungkus). |
| `table_no` | `string` | `13` | Nomor meja (`1`–`18` untuk `dine_in`, atau `TA01` untuk `takeaway`). |
| `order_status` | `string` | `served` | Status pesanan selesai disajikan. |
| `payment_status` | `string` | `paid` | Hanya transaksi berstatus `paid` yang lolos ke tabel bersih (`assert payment_status == 'paid'`). |
| `payment_method` | `string (enum)`| `QRIS` | Metode pembayaran: `QRIS` atau `cash` (nilai `card` pada data mentah telah dinormalisasi ke `QRIS` sesuai kontrak pembayaran MVP). |
| `subtotal_idr` | `integer` | `125000` | Total nilai pesanan sebelum pajak dalam Rupiah. |
| `tax_rate_at_sale` | `float` | `0.11` | Snapshot tarif pajak restoran saat transaksi terjadi (`0.11` = 11% / 1.100 bps). |
| `tax_amount_idr` | `integer` | `13750` | Nominal pajak terkumpul: `round(subtotal_idr * tax_rate_at_sale)`. |
| `grand_total_idr` | `integer` | `138750` | Total yang dibayarkan pelanggan: `subtotal_idr + tax_amount_idr`. |
| `total_hpp_idr` | `integer` | `45000` | Snapshot HPP aktual pesanan. |
| `gross_profit_idr` | `integer` | `80000` | Estimasi laba kotor pesanan: `subtotal_idr - total_hpp_idr`. |
| `data_origin` | `string` | `synthetic_seed_20261112` | Label sumber data. |

### 3.2 `reviews_clean.csv` (2.000 Ulasan Pelanggan Berbahasa Indonesia)

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Aturan Validasi |
| :--- | :--- | :--- | :--- |
| `review_id` | `string (PK)` | `REV00001` | Identifier unik ulasan pelanggan. |
| `tenant_id` | `string` | `BBR001` | Identifier tenant. |
| `order_id` | `string (FK)` | `ORD000001` | Mengacu ke transaksi `orders_clean.order_id`. |
| `rating` | `integer` | `5` | Skor bintang kepuasan pelanggan (`1` s.d. `5`). |
| `comment` | `string` | `"Makan siang di sini hari Minggu. Ayam bakarnya empuk..."` | Teks ulasan pelanggan berbahasa Indonesia (mencakup variasi bahasa formal, santai, singkatan, negasi, dan kalimat kontras). |
| `sentiment_label` | `string (enum)`| `positive` | Label kelas sentimen: `positive` (rating 4–5), `negative` (rating 1–2), atau `neutral` (rating 3). |
| `data_origin` | `string` | `synthetic_contextual_v2` | Label sumber data. |
