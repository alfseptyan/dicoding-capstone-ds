# Dataset Kode A — Forecasting Permintaan & Kebutuhan Bahan Baku
- **Modul:** Forecasting permintaan dan kebutuhan bahan
- **Jenis:** Forecasting / Regresi Deret Waktu
- **Dipakai di:** Dashboard Pemilik (Owner) & Halaman Warehouse / Restock
- **Prioritas:** Wajib

## Daftar File di Folder Ini
1. `daily_ingredient_usage_timeseries.csv`: Deret waktu pemakaian harian bahan baku (`date`, `ingredient_id`, `usage_qty`, `base_unit`, `shelf_life_days`).
2. `daily_menu_demand_timeseries.csv`: Deret waktu jumlah porsi terjual per menu per hari (`date`, `menu_id`, `portions_sold`).
3. `ingredients_clean.csv`: Master 106 bahan baku gudang beserta `minimum_stock`, `shelf_life_days`, dan `reference_unit_cost_idr`.
4. `recipes_bom_clean.csv`: 1.481 baris komponen resep (*Bill of Materials* / BOM) yang menghubungkan menu ke takaran bahan baku.
5. `orders_clean.csv` & `order_items_clean.csv`: Data histori transaksi `paid` (2.017 struk, Mei–Oktober 2026).
6. `forecast_7_hari.csv`: Output hasil prediksi pemakaian harian 97 bahan aktif untuk 7 hari ke depan (`Random Forest` vs `Pooled DOW`).
7. `saran_stok.csv`: Output rekomendasi pembelian bahan (*restock*) dengan kuantil *safety stock* tingkat layanan 95%.
8. `ringkasan_rata_rata_lipatan.csv` & `evaluasi_semua_lipatan.csv`: Hasil komparasi metrik WAPE Mingguan, nMAE, dan Scaled RMSE pada 2 lipatan waktu (*chronological split*).
