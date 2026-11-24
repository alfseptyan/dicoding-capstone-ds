# Dataset Kode C — Chatbot Menu (Gen AI / RAG Knowledge Base)
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
