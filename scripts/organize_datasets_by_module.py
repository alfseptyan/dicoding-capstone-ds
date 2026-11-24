#!/usr/bin/env python3
"""
Organize Datasets into Dedicated Module Folders (Kode A s.d. Kode E)
====================================================================
Membuat struktur folder terpisah per modul di dalam `data/modules/` (dan `datasets_by_module/`)
agar tim Developer (Full-Stack & Gen AI Engineer) dapat langsung mengambil file sesuai kode modulnya:

- `kode_A_forecasting_permintaan_dan_kebutuhan_bahan/` (Dashboard Pemilik, Warehouse - Wajib)
- `kode_B_rekomendasi_menu_item_to_item/` (Halaman QR - Wajib)
- `kode_C_chatbot_menu_rag/` (Halaman QR, Kanal Chat - Wajib)
- `kode_D_klasifikasi_intent_chatbot/` (Router Chatbot - Nilai Tambah)
- `kode_E_analisis_sentimen_ulasan/` (Dashboard Pemilik - Nilai Tambah)
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
MODULES_DIR = BASE_DIR / "data" / "modules"
BACKEND_MASTER_JSON = (
    BASE_DIR.parent
    / "dicoding-capstone-backend"
    / "src"
    / "database"
    / "factories"
    / "data"
    / "master-data.json"
)

DIR_A = MODULES_DIR / "kode_A_forecasting_permintaan_dan_kebutuhan_bahan"
DIR_B = MODULES_DIR / "kode_B_rekomendasi_menu_item_to_item"
DIR_C = MODULES_DIR / "kode_C_chatbot_menu_rag"
DIR_D = MODULES_DIR / "kode_D_klasifikasi_intent_chatbot"
DIR_E = MODULES_DIR / "kode_E_analisis_sentimen_ulasan"

for d in (DIR_A, DIR_B, DIR_C, DIR_D, DIR_E):
    d.mkdir(parents=True, exist_ok=True)


def organize_kode_a() -> None:
    print("[KODE A] Menyiapkan folder dataset Forecasting Permintaan & Kebutuhan Bahan...")
    orders = pd.read_csv(PROC_DIR / "orders_clean.csv")
    order_items = pd.read_csv(PROC_DIR / "order_items_clean.csv")
    recipes = pd.read_csv(PROC_DIR / "recipes_bom_clean.csv")
    ingredients = pd.read_csv(PROC_DIR / "ingredients_clean.csv")

    # 1. Buat matriks pemakaian bahan harian (daily_ingredient_usage_matrix.csv)
    orders["ordered_at"] = pd.to_datetime(orders["ordered_at"])
    paid = orders.loc[orders["payment_status"] == "paid", ["order_id", "ordered_at"]].copy()
    paid["date"] = paid["ordered_at"].dt.strftime("%Y-%m-%d")
    lines = order_items.merge(paid[["order_id", "date"]], on="order_id")
    usage = lines.merge(recipes, on="menu_id")
    usage["usage_qty"] = usage["quantity"] * usage["quantity_per_portion"]

    daily_long = (
        usage.groupby(["date", "ingredient_id"], as_index=False)["usage_qty"]
        .sum()
        .merge(
            ingredients[
                [
                    "ingredient_id",
                    "ingredient_name",
                    "category",
                    "base_unit",
                    "minimum_stock",
                    "shelf_life_days",
                    "reference_unit_cost_idr",
                ]
            ],
            on="ingredient_id",
            how="left",
        )
        .sort_values(["date", "ingredient_id"])
    )
    daily_long.to_csv(DIR_A / "daily_ingredient_usage_timeseries.csv", index=False)

    # 2. Buat daily menu demand timeseries (permintaan porsi per menu per hari)
    menu_daily = (
        lines.groupby(["date", "menu_id", "menu_name", "category_name"], as_index=False)[
            "quantity"
        ]
        .sum()
        .rename(columns={"quantity": "portions_sold"})
        .sort_values(["date", "menu_id"])
    )
    menu_daily.to_csv(DIR_A / "daily_menu_demand_timeseries.csv", index=False)

    # 3. Salin file pendukung utama Kode A
    for fname in ("ingredients_clean.csv", "recipes_bom_clean.csv", "orders_clean.csv", "order_items_clean.csv"):
        shutil.copy2(PROC_DIR / fname, DIR_A / fname)
    for fname in ("forecast_7_hari.csv", "saran_stok.csv", "ringkasan_rata_rata_lipatan.csv", "evaluasi_semua_lipatan.csv"):
        if (MODELS_DIR / fname).exists():
            shutil.copy2(MODELS_DIR / fname, DIR_A / fname)

    readme_a = """# Dataset Kode A — Forecasting Permintaan & Kebutuhan Bahan Baku
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
"""
    (DIR_A / "README.md").write_text(readme_a, encoding="utf-8")


def organize_kode_b() -> None:
    print("[KODE B] Menyiapkan folder dataset Rekomendasi Menu (Recommender Item-to-Item)...")
    for fname in (
        "menu_top_recommendations.csv",
        "menu_cooccurrence_pairs.csv",
        "recommender_baskets_train.csv",
        "recommender_baskets_test.csv",
        "menu_items_clean.csv",
        "order_items_clean.csv",
    ):
        shutil.copy2(PROC_DIR / fname, DIR_B / fname)

    if (MODELS_DIR / "evaluasi_recommender_3_metode.csv").exists():
        shutil.copy2(
            MODELS_DIR / "evaluasi_recommender_3_metode.csv",
            DIR_B / "evaluasi_recommender_3_metode.csv",
        )

    readme_b = """# Dataset Kode B — Rekomendasi Menu (Recommender Item-to-Item)
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
"""
    (DIR_B / "README.md").write_text(readme_b, encoding="utf-8")


def organize_kode_c() -> None:
    print("[KODE C] Menyiapkan folder dataset Chatbot Menu (RAG & Knowledge Base)...")
    with open(BACKEND_MASTER_JSON, "r", encoding="utf-8") as f:
        master = json.load(f)

    shutil.copy2(PROC_DIR / "menu_items_clean.csv", DIR_C / "menu_items_clean.csv")
    shutil.copy2(
        PROC_DIR / "menu_top_recommendations.csv",
        DIR_C / "menu_top_recommendations.csv",
    )

    # Ekspor option_groups & option_choices dari master-data.json jika ada
    opt_groups = master.get("option_groups", [])
    opt_choices = master.get("option_choices", [])
    if opt_groups:
        pd.DataFrame(opt_groups).to_csv(DIR_C / "menu_option_groups.csv", index=False)
    if opt_choices:
        pd.DataFrame(opt_choices).to_csv(DIR_C / "menu_option_choices.csv", index=False)

    # Bangun dokumen Knowledge Base RAG (chatbot_rag_knowledge_chunks.csv & .jsonl)
    # Menggabungkan katalog menu, alergen bahan dari BOM, opsi wajib/opsional, dan info operasional restoran
    menus = pd.read_csv(PROC_DIR / "menu_items_clean.csv")
    recipes = pd.read_csv(PROC_DIR / "recipes_bom_clean.csv")
    ingredients = pd.read_csv(PROC_DIR / "ingredients_clean.csv")

    ing_map = ingredients.set_index("ingredient_id")[
        ["ingredient_name", "allergen_tags"]
    ].to_dict("index")
    menu_ings: dict[str, list[str]] = {}
    menu_allergens: dict[str, set[str]] = {}
    for _, r in recipes.iterrows():
        m_id = r["menu_id"]
        i_id = r["ingredient_id"]
        info = ing_map.get(i_id)
        if info:
            menu_ings.setdefault(m_id, []).append(info["ingredient_name"])
            tags = str(info.get("allergen_tags") or "").strip()
            if tags and tags != "nan":
                for t in tags.split(";"):
                    if t.strip():
                        menu_allergens.setdefault(m_id, set()).add(t.strip())

    rag_chunks = []
    # Chunk info operasional restoran
    resto_chunks = [
        (
            "RAG_INFO_001",
            "info_operasional",
            "Jam Buka & Operasional Banyu Bening Resto Salatiga",
            "Banyu Bening Resto Salatiga buka setiap hari: Senin–Jumat pukul 10:00–22:00 WIB, Sabtu–Minggu pukul 09:00–23:00 WIB. Melayani makan di tempat (dine-in) lewat scan QR meja dan bungkus (takeaway).",
        ),
        (
            "RAG_INFO_002",
            "info_fasilitas_wifi",
            "Fasilitas, Wi-Fi, Halal, dan Metode Pembayaran",
            "Fasilitas Banyu Bening Resto: Area makan indoor & outdoor, Parkir luas, Mushola (Prayer Room), dan Toilet bersih. Seluruh menu berstatus Halal. Wi-Fi tamu: SSID 'BanyuBening-Guest' (sandi dapat ditanyakan ke kasir). Pembayaran menerima Tunai (Cash) dan QRIS.",
        ),
        (
            "RAG_INFO_003",
            "info_reservasi",
            "Kebijakan Reservasi & Rombongan Keluarga",
            "Reservasi diterima untuk keluarga atau rombongan lebih dari 10 orang melalui WhatsApp resto (nomor kontak dapat ditanyakan ke kasir). Tersedia Paket Personal dan Paket Ber 5 untuk makan bersama.",
        ),
    ]
    for cid, ctype, title, content in resto_chunks:
        rag_chunks.append(
            {
                "chunk_id": cid,
                "tenant_id": "BBR001",
                "chunk_type": ctype,
                "reference_id": "TENANT_BBR001",
                "title": title,
                "content_text": content,
                "data_origin": "primary_validated",
            }
        )

    for _, m in menus.iterrows():
        m_id = m["menu_id"]
        ings_list = menu_ings.get(m_id, [])
        allergens_list = sorted(list(menu_allergens.get(m_id, set())))
        allergen_str = (
            f"Peringatan alergen: {', '.join(allergens_list)}."
            if allergens_list
            else "Tidak tercatat alergen khusus."
        )
        ing_str = (
            f"Komposisi bahan utama: {', '.join(ings_list[:8])}."
            if ings_list
            else ""
        )
        status_str = "Tersedia" if m["is_available"] else "Sedang Habis"
        content = (
            f"Menu {m['menu_name']} (ID: {m_id}, Kategori: {m['category_name']}). "
            f"Harga: Rp {int(m['selling_price_idr']):,} per {m['selling_unit']}. "
            f"Status: {status_str}. {ing_str} {allergen_str}"
        ).replace(",", ".")
        rag_chunks.append(
            {
                "chunk_id": f"RAG_MENU_{m_id}",
                "tenant_id": "BBR001",
                "chunk_type": "katalog_menu",
                "reference_id": m_id,
                "title": f"{m['menu_name']} ({m['category_name']})",
                "content_text": content,
                "data_origin": "primary",
            }
        )

    df_rag = pd.DataFrame(rag_chunks)
    df_rag.to_csv(DIR_C / "chatbot_rag_knowledge_chunks.csv", index=False)

    with open(DIR_C / "chatbot_context_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "tenant": master.get("tenant", {}),
                "categories_count": len(master.get("categories", [])),
                "menu_items_count": len(master.get("menu_items", [])),
                "option_groups_count": len(opt_groups),
                "option_choices_count": len(opt_choices),
                "rag_chunks_count": len(rag_chunks),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    readme_c = """# Dataset Kode C — Chatbot Menu (Gen AI / RAG Knowledge Base)
- **Modul:** Chatbot menu (RAG & Tool-Calling Context)
- **Jenis:** Generative AI (LLM + Knowledge Base Katalog, Opsi Menu, Komposisi Alergen, & Info Restoran)
- **Dipakai di:** Halaman QR Pelanggan (Widget Kanal Chat Pemesanan)
- **Prioritas:** Wajib

## Daftar File di Folder Ini
1. `chatbot_rag_knowledge_chunks.csv`: **202 dokumen teks terstruktur (RAG Chunks)** yang menggabungkan info operasional restoran, fasilitas, harga menu, komposisi bahan dari BOM, dan tag peringatan alergen untuk setiap menu.
2. `menu_items_clean.csv`: Katalog lengkap 199 menu Banyu Bening Resto.
3. `menu_option_groups.csv` (307 grup opsi) & `menu_option_choices.csv` (809 pilihan opsi): Struktur opsi wajib dan opsional (level pedas, penyajian dingin/hangat, takaran gula, topping) beserta `price_delta`.
4. `menu_top_recommendations.csv`: Kandidat rekomendasi menu terlaris dan pendamping (`rekomendasi_menu` & `rekomendasi_tambahan`).
5. `chatbot_context_snapshot.json`: Ringkasan metadata konteks tenant `BBR001`.
"""
    (DIR_C / "README.md").write_text(readme_c, encoding="utf-8")


def organize_kode_d() -> None:
    print("[KODE D] Menyiapkan folder dataset Klasifikasi Intent (Router Chatbot)...")
    shutil.copy2(RAW_DIR / "intent_raw.csv", DIR_D / "intent_raw.csv")
    for fname in ("intent_dataset_clean.csv", "intent_train.csv", "intent_test.csv"):
        shutil.copy2(PROC_DIR / fname, DIR_D / fname)
    if (MODELS_DIR / "evaluasi_intent_4_metode.csv").exists():
        shutil.copy2(
            MODELS_DIR / "evaluasi_intent_4_metode.csv",
            DIR_D / "evaluasi_intent_4_metode.csv",
        )

    readme_d = """# Dataset Kode D — Klasifikasi Intent (Router Chatbot 5 Kelas)
- **Modul:** Klasifikasi intent pesan pelanggan
- **Jenis:** Klasifikasi Teks Bahasa Indonesia (5 Kelas: `pemesanan`, `tanya_menu`, `info_resto`, `keluhan`, `lainnya`)
- **Dipakai di:** Router Chatbot AI di Halaman QR
- **Prioritas:** Nilai Tambah

## Daftar File di Folder Ini
1. `intent_dataset_clean.csv`: **546 kalimat unik bersih** setelah normalisasi singkatan tidak baku (`gak/ga/nggak -> tidak` dengan tetap mempertahankan kata negasi) dan penghapusan 448 baris duplikat dari `intent_raw.csv`.
2. `intent_train.csv` (436 kalimat — 80%) & `intent_test.csv` (110 kalimat — 20%): Pembagian data menggunakan *Stratified Train/Test Split* pasca-deduplikasi (`overlap = 0`, bebas kebocoran data).
3. `intent_raw.csv`: 994 kalimat mentah sebelum proses *Data Cleaning & Deduplication*.
4. `evaluasi_intent_4_metode.csv`: Tabel perbandingan metrik `5-Fold CV Macro-F1`, `Test Accuracy`, `Macro Precision`, `Macro Recall`, dan `Macro-F1` pada 4 metode klasifikasi teks.
"""
    (DIR_D / "README.md").write_text(readme_d, encoding="utf-8")


def organize_kode_e() -> None:
    print("[KODE E] Menyiapkan folder dataset Analisis Sentimen Ulasan Pelanggan...")
    shutil.copy2(RAW_DIR / "reviews_v2.xlsx", DIR_E / "reviews_v2_raw.xlsx")
    shutil.copy2(PROC_DIR / "reviews_clean.csv", DIR_E / "reviews_clean.csv")
    shutil.copy2(PROC_DIR / "reviews_v2_prediksi.csv", DIR_E / "reviews_v2_prediksi.csv")

    if (MODELS_DIR / "evaluasi_sentimen_7_metode.csv").exists():
        shutil.copy2(
            MODELS_DIR / "evaluasi_sentimen_7_metode.csv",
            DIR_E / "evaluasi_sentimen_7_metode.csv",
        )

    # Ekstrak juga 100 komentar uji tulisan tangan independen (normal vs sulit/negasi) dari notebook 04 ke CSV tersendiri
    nb_path = BASE_DIR / "notebooks" / "04_sentiment_evaluation_banyu_bening.ipynb"
    if nb_path.exists():
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.loads(f.read())
        ns: dict = {}
        exec("".join(nb["cells"][5]["source"]), ns)
        T = ns.get("T", [])
        if T:
            df_test_100 = pd.DataFrame(
                [
                    {
                        "test_id": f"TST{i:03d}",
                        "tenant_id": "BBR001",
                        "comment": txt,
                        "sentiment_label": lab,
                        "difficulty_group": "hard_negation_contrast" if grp == "h" else "normal",
                        "data_origin": "handwritten_independent_test",
                    }
                    for i, (txt, lab, grp) in enumerate(T, start=1)
                ]
            )
            df_test_100.to_csv(
                DIR_E / "reviews_independent_handwritten_test_100.csv", index=False
            )

    readme_e = """# Dataset Kode E — Analisis Sentimen Ulasan Pelanggan
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
"""
    (DIR_E / "README.md").write_text(readme_e, encoding="utf-8")


if __name__ == "__main__":
    organize_kode_a()
    organize_kode_b()
    organize_kode_c()
    organize_kode_d()
    organize_kode_e()
    print("\n" + "=" * 78)
    print("SELURUH DATASET KODE A s.d. KODE E BERHASIL DIORGANISASIKAN KE data/modules/!")
    print("=" * 78)
