# Dataset Kode B — Rekomendasi Menu (Recommender Item-to-Item)
- **Modul:** Rekomendasi menu pendamping
- **Jenis:** Recommender Item-to-Item (Co-occurrence Cosine Similarity + Lift Ratio + Cross-Category)
- **Dipakai di:** Halaman QR Pelanggan (Kartu rekomendasi pendamping & upselling keranjang)
- **Prioritas:** Wajib

## Daftar File di Folder Ini
1. `menu_top_recommendations.csv`: **File siap pakai API/UI** berisi Top-5 rekomendasi menu pendamping terbaik untuk setiap menu aktif (`menu_id`, `rank`, `recommended_menu_id`, `recommended_menu_name`, `cosine_similarity`, `lift`).
2. `menu_cooccurrence_pairs.csv`: Matriks lengkap 4.168 pasangan item-to-item (`co_occurrence_count`, `support`, `confidence`, `lift`, `cosine_similarity`, `hybrid_score`).
3. `recommender_baskets_train.csv` (1.613 struk, 80% awal) & `recommender_baskets_test.csv` (404 struk, 20% akhir): Pembagian keranjang belanja secara kronologis (*Order-Level Chronological Split* bebas bocor).
4. `menu_items_clean.csv` & `order_items_clean.csv`: Katalog 199 menu dan baris detail item pesanan.
5. `evaluasi_recommender_3_metode.csv`: Tabel perbandingan `Precision@3`, `Recall@3`, `HitRate@3`, `Precision@5`, `Recall@5`, dan `Catalog Coverage %` antara *Global Best-Sellers*, *FP-Growth Association Rules*, dan *Item-to-Item Hybrid*.
