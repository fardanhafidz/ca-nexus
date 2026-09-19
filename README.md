# Manufacturing Knowledge Hub

Dokumentasi supervisi dan perencanaan platform AI untuk pengetahuan operasional pabrik petrokimia, dengan studi kasus **PT Chandra Asri Pacific Tbk — SDK LLDPE Expansion Project**, sebagaimana disebutkan dalam brief pengguna.

**Status: discovery dan perencanaan.** Tanggal penyusunan awal: **18 September 2026**. Dokumen ini merekam kebutuhan, rancangan awal, pekerjaan implementasi, serta keputusan yang masih perlu dibahas. Fitur yang tercantum merupakan target produk, bukan klaim bahwa aplikasinya sudah tersedia.

## Ringkasan

Platform menyatukan OPL/SOP, datasheet, GA drawing, P&ID, interlock/Cause & Effect, plot plan, dan maintenance history. Pengguna bertanya melalui antarmuka percakapan, memperoleh jawaban berbasis sumber, melihat komponen teknis interaktif, dan membuka dokumen rujukan melalui sitasi. Akses pengetahuan mengikuti peran serta divisi pengguna.

Baseline teknologi dalam brief adalah Next.js 14, Tailwind CSS, FastAPI, PostgreSQL, Qdrant, OpenAI/OpenRouter, serta Docker Compose. **Hybrid search dan graph-augmented RAG adalah kebutuhan yang disebutkan, tetapi rancangan implementasinya belum lengkap.**

## Peta dokumen

| Dokumen | Isi |
| --- | --- |
| [01 — Konteks proyek](docs/01-PROJECT-CONTEXT.md) | Tujuan, fitur, peran, alur pengguna, tampilan, struktur monorepo dari brief, dan batas informasi yang diketahui. |
| [02 — Inventaris data](docs/02-DATA-INVENTORY.md) | Data yang benar-benar ditemukan di workspace, cakupan pemeriksaan, serta gap terhadap rencana ingestion. |
| [03 — Arsitektur, stack, dan keputusan](docs/03-ARCHITECTURE-AND-DECISIONS.md) | Setiap teknologi yang disebutkan, komponen yang belum ditentukan, trade-off, dan register keputusan D-01 sampai D-28. |
| [04 — Kontrak respons AI](docs/04-AI-RESPONSE-CONTRACT.md) | Kontrak JSON asli, kekurangan schema, kebutuhan payload, sitasi, dan hubungan dengan streaming. |
| [05 — Backlog terperinci](docs/05-DETAILED-BACKLOG.md) | Task bertahap dengan subtugas, dependensi, keputusan terkait, hasil kerja, serta kriteria penerimaan. |
| [06 — Pertanyaan keputusan](docs/06-OPEN-QUESTIONS.md) | Seluruh pertanyaan discovery yang teridentifikasi saat ini, dikelompokkan berdasarkan keputusan dan prioritas. |

## Cara membaca status informasi

| Label | Arti |
| --- | --- |
| **BRIEF** | Disebutkan secara eksplisit oleh pengguna. Menjadi baseline kebutuhan/rancangan awal, bukan bukti implementasi atau hasil pengujian. |
| **TERVERIFIKASI-WORKSPACE** | Diamati melalui pemeriksaan workspace. Cakupan buktinya disebutkan; keberadaan file tidak membuktikan isi atau akurasi teknisnya. |
| **TERBUKA** | Belum dijelaskan, belum dipilih, atau memerlukan penyelesaian ketidaksesuaian dalam brief. |
| **USULAN** | Saran supervisor untuk dibahas. Belum menjadi keputusan pengguna. |
| **DISEPAKATI** | Keputusan lanjutan yang sudah dikonfirmasi pengguna dan dicatat bersama alasan serta dampaknya. Belum ada keputusan lanjutan berstatus ini pada versi awal. |

## Temuan awal yang memengaruhi rencana

- Workspace awal berisi folder `supporting_data/`; belum ditemukan kode aplikasi maupun dokumentasi proyek di dalamnya saat pemeriksaan awal.
- Ditemukan **8 set equipment**, berisi **88 PDF dan 8 PNG**, ditambah **1 workbook XLSX dan 1 slide deck PPTX**. Perhitungan berdasarkan daftar file, bukan pemeriksaan isi.
- P&ID tersedia sebagai **PNG**. Pipeline yang hanya membaca PDF belum mencakup semua sumber yang tersedia.
- **211 record dan 31 kolom maintenance** adalah angka dari brief; isi workbook belum diperiksa untuk memverifikasinya.
- `scripts/data/` dan `/data/...` merupakan path rancangan/contoh pada brief. Lokasi data aktual saat ini ada di `supporting_data/Case 1_ Manufacturing Knowledge Hub/`.
- Penyimpanan graph, pencarian lexical, OCR/vision, transkripsi suara, payload komponen terperinci, serta protokol streaming belum ditetapkan.

## Cara melanjutkan diskusi

1. Jawab kelompok **pertanyaan pembuka** pada [daftar pertanyaan](docs/06-OPEN-QUESTIONS.md#pertanyaan-pembuka).
2. Catat jawaban sebagai keputusan pada register D-xx; sertakan bagian yang masih terbuka.
3. Tentukan fitur rilis pertama sebelum menetapkan jadwal atau memulai task yang bergantung pada keputusan tersebut.
4. Gunakan ID task pada backlog untuk melacak implementasi dan bukti verifikasi.

Jawaban boleh berupa pilihan, penjelasan bebas, atau permintaan rekomendasi beserta trade-off. Jawaban yang belum diberikan tetap dicatat sebagai **TERBUKA**.
