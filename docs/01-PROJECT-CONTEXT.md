# 01 — Konteks Proyek

## 1. Identitas dan sumber konteks

| Atribut | Isi | Status |
| --- | --- | --- |
| Nama produk | Manufacturing Knowledge Hub (AI Platform) | BRIEF |
| Bidang | Pengetahuan rekayasa dan operasional pabrik petrokimia | BRIEF |
| Studi kasus | PT Chandra Asri Pacific Tbk — SDK LLDPE Expansion Project | BRIEF |
| Bentuk aplikasi | Platform web AI enterprise terintegrasi | BRIEF |
| Tahap pekerjaan saat ini | Dokumentasi supervisi, discovery, dan perencanaan implementasi | Permintaan pengguna |
| Target rilis pertama | Hackathon/demo, PoC, pilot internal, atau produksi belum ditentukan | TERBUKA, D-01 |
| Pengesah keputusan produk | Pengguna bersama pihak proyek yang nantinya ditunjuk | TERBUKA, D-28 |

Sumber yang digunakan:

- **S-01 — Brief pengguna:** rangkuman produk, matriks RBAC, struktur monorepo, contoh kontrak JSON, dan empat tahap pembangunan. Pesan yang berulang diperlakukan sebagai satu baseline yang sama.
- **S-02 — Inventaris workspace, 18 September 2026:** daftar direktori dan nama file di `supporting_data/`. Rincian pada [inventaris data](02-DATA-INVENTORY.md).

Isi PDF, gambar, workbook, dan slide deck belum diperiksa dalam penyusunan konteks awal ini. Nilai proses, setpoint, relasi interlock, isi 31 kolom, dan isi 211 record tidak disimpulkan dari nama file.

## 2. Ringkasan produk

Manufacturing Knowledge Hub mengonsolidasikan dokumen teknis yang tersebar menjadi satu basis pengetahuan yang dapat ditelusuri melalui percakapan. Operator dan engineer mengajukan pertanyaan mengenai equipment, prosedur, suku cadang, instrumentasi, interlock, maupun kejadian maintenance. Sistem mengambil sumber yang boleh diakses pengguna, menyusun respons AI berbasis bukti, menampilkan bentuk UI yang sesuai, dan menghubungkan jawaban dengan dokumen asalnya.

Tiga fondasi produk dalam brief:

1. **Tata kelola akses:** tiga peran utama dan pembatasan pengetahuan berdasarkan divisi.
2. **Pencarian berbasis konteks rekayasa:** hybrid dan graph-augmented RAG yang menghubungkan equipment, instrument, interlock, dokumen, serta data maintenance.
3. **Antarmuka percakapan industri:** pengalaman bergaya Gemini, warna industrial yang ditentukan, sitasi yang dapat dibuka, dan empat jenis rich UI component.

Label enterprise menjelaskan aspirasi produk. Kebutuhan operasional terukur, jumlah pengguna, target ketersediaan, dan lingkungan penerapan tetap perlu diputuskan.

## 3. Kumpulan pengetahuan target

| Sumber | Pemanfaatan yang dijelaskan dalam brief | Detail yang belum diketahui |
| --- | --- | --- |
| SOP/OPL | Menjawab pertanyaan prosedur dan menampilkan checklist kerja | Struktur langkah, versi resmi, cara menentukan divisi, serta persistensi checklist |
| Equipment datasheet | Menjawab spesifikasi equipment atau loop | Schema tabel, satuan, kualitas ekstraksi, serta field wajib |
| GA drawing | Membaca susunan equipment dan BOM/suku cadang | Apakah setiap drawing memuat BOM dan apakah tabel dapat diekstrak secara andal |
| P&ID | Relasi equipment/instrument dan konteks proses | Cara membaca PNG, konektivitas, bukti relasi, dan tingkat interpretasi yang diharapkan |
| Interlock/Cause & Effect | Menjelaskan hubungan kondisi pemicu dan efek | Voting, delay, reset, setpoint, dan struktur node/edge yang benar-benar tersedia |
| Plot plan | Konteks lokasi/spasial equipment | Sekadar viewer/lokasi relatif atau perhitungan koordinat/jarak |
| Maintenance history | Riwayat kerusakan, ringkasan kejadian, dan kalkulasi melalui SQL | Header aktual, tipe data, unit, definisi metrik, dan aturan akses per record |
| Safety matrix, SIL, RCA | Kebutuhan HSE & Reliability dalam matriks divisi | Apakah merupakan file tersendiri, bagian dokumen lain, atau field maintenance |

**211 record maintenance dan model 31 kolom: BRIEF, belum diverifikasi dari workbook.**

## 4. Kebutuhan fungsional

Seluruh fitur berikut merupakan target yang disebutkan dalam brief. Keikutsertaan pada rilis pertama masih perlu disepakati melalui D-01.

| ID | Kebutuhan | Bentuk hasil yang diharapkan |
| --- | --- | --- |
| F-01 | Registrasi mandiri dan approval | Pengguna dapat mendaftar, melihat status pending, lalu memperoleh akses setelah disetujui dan dialokasikan divisi |
| F-02 | Autentikasi dan RBAC | Identitas, status akun, peran, dan divisi menentukan akses di backend |
| F-03 | Repository pengetahuan | Katalog, pencarian/filter dokumen, serta membuka sumber yang diizinkan |
| F-04 | Ingestion dan import | PDF/sumber teknis diindeks; workbook maintenance disimpan secara relasional |
| F-05 | Hybrid retrieval | Pencarian semantik dan lexical/exact-match digabungkan melalui rancangan yang disepakati |
| F-06 | Graph-augmented retrieval | Relasi `Equipment_Tag`, `Related_Interlock`, dan `Instrument_Tag` digunakan untuk memperkaya konteks |
| F-07 | Jawaban AI terstruktur | Backend menghasilkan respons JSON tervalidasi yang dapat dirender frontend |
| F-08 | Empat rich component | ProcedureChecklist, InterlockLogicCard, SparePartBOMTable, dan RootCauseCard |
| F-09 | Sitasi dan Inspector | Pengguna mengeklik citation chip untuk melihat sumber, halaman/gambar, dan kutipan |
| F-10 | Analitik maintenance | Pertanyaan numerik diarahkan ke sumber relasional melalui service SQL |
| F-11 | Chat dan riwayat | Session/message history, sidebar pencarian riwayat, serta perilaku streaming yang akan ditentukan |
| F-12 | Input multimodal | Input teks, attachment gambar, dan perekaman suara |
| F-13 | Administrasi pengguna | Approval queue dan alokasi divisi |
| F-14 | Administrasi dokumen | Upload dokumen baru, katalog lintas divisi, dan monitor pipeline ingestion |
| F-15 | Super Admin | Akses seluruh data, analitik token, audit query, dan konfigurasi API gateway |

## 5. Peran dan matriks akses awal

### 5.1 Peran

| Peran | Kewenangan eksplisit dalam brief | Hal yang perlu diputuskan |
| --- | --- | --- |
| Super Admin | Akses mutlak seluruh data, analitik token, audit log query, konfigurasi API gateway | Bootstrap akun pertama, pengelolaan Admin, detail pengaturan gateway, serta operasi yang tersedia di UI |
| Admin | Menyetujui pendaftaran, mengalokasikan divisi, mengunggah dokumen, melihat katalog seluruh divisi | Apakah akses lintas divisi hanya metadata katalog atau juga isi, chat lintas divisi, download, audit, perubahan role, dan penghapusan |
| User | Operator/Maintenance Engineer; registrasi mandiri, pending, disetujui, lalu mengakses dokumen sesuai divisi | Satu/banyak divisi, perubahan divisi, batas fitur, serta akses data maintenance |

### 5.2 Divisi

| Divisi | Cakupan pengetahuan menurut brief |
| --- | --- |
| Mechanical | Datasheet, GA drawing/BOM, OPL mekanikal, riwayat kerusakan mekanikal |
| Electrical & Instrumentation | Interlock/C&E, P&ID, datasheet loop, OPL kalibrasi DVC6200 dan sensor getaran |
| Process / Operations | P&ID, plot plan, interlock trip, OPL operasi seperti inerting N2, priming, dan draining boot vessel |
| HSE & Reliability | Safety matrix, rating SIL, penanganan H2/N2, riwayat breakdown dan RCA |

Matriks di atas merupakan cakupan konseptual. Matriks tersebut belum menetapkan ACL untuk setiap file, chunk, row maintenance, atau relasi graph. Satu tipe dokumen dapat relevan untuk lebih dari satu divisi; nama file tidak cukup untuk menentukan hak akses final.

### 5.3 Titik penerapan akses yang perlu dirancang

**USULAN turunan F-02, menunggu rincian D-06:** konteks akses yang sama digunakan saat membaca katalog, mengambil chunk dense/lexical, menelusuri graph, membaca maintenance, mengakses attachment/riwayat, serta membuka file melalui sitasi. Cakupan cache dan perubahan akses juga perlu mengikuti kebijakan yang dipilih.

Filter pada frontend saja tidak memenuhi kebutuhan RBAC berbasis backend dalam brief. Filter Qdrant saja juga belum mencakup jalur SQL, graph, file viewer, dan history.

## 6. Alur produk target

### 6.1 Pendaftaran dan akses

1. Calon pengguna mengisi registrasi.
2. Sistem membuat akun berstatus `pending`.
3. Pengguna melihat halaman status pending.
4. Admin meninjau pendaftaran, menyetujui, dan mengalokasikan divisi.
5. Pengguna yang telah disetujui mengakses pengetahuan sesuai kewenangannya.

Detail penolakan, penonaktifan, reset password, verifikasi email, notifikasi, dan pencabutan session belum disebutkan.

### 6.2 Upload dan ingestion

1. Admin mengunggah sumber baru atau pipeline membaca dataset awal.
2. Sumber memperoleh identitas, klasifikasi, equipment/tag terkait, dan aturan akses.
3. Dokumen diekstrak sesuai format; workbook diimpor sesuai schema yang diverifikasi.
4. Hasil yang diperlukan untuk dense, lexical, dan graph disiapkan.
5. Dokumen menjadi tersedia untuk retrieval sesuai definisi status ingestion yang dipilih.
6. Admin melihat keberhasilan atau kegagalan proses.

Langkah 2–5 merinci kebutuhan agar upload dan retrieval saling terhubung; teknologi, status job, dan aturan publikasinya **TERBUKA**.

### 6.3 Pertanyaan hingga jawaban bersitasi

1. Pengguna mengirim teks atau input multimodal yang telah diproses sesuai fitur aktif.
2. Backend memperoleh identitas, status, role, dan divisi pengguna.
3. Router memilih sumber dokumen, graph, SQL, atau gabungannya sesuai rancangan retrieval.
4. Retrieval hanya menyediakan bukti yang sesuai akses.
5. Gateway LLM menyusun respons sesuai schema yang disepakati.
6. Backend memvalidasi struktur dan rujukan respons.
7. Frontend merender narasi dan komponen yang sesuai.
8. Klik sitasi membuka sumber melalui Inspector dengan otorisasi yang tetap berlaku.

Langkah validasi dan verifikasi rujukan merupakan **USULAN penerapan** kebutuhan respons terstruktur dan sitasi; detailnya ada pada D-15, D-17, dan D-18.

### 6.4 Analitik maintenance

Pertanyaan yang membutuhkan hitungan menggunakan data relasional melalui `sql_service.py`. Kolom, formula, interval waktu, timezone, penanganan data kosong, satuan, bentuk jawaban, dan referensi ke row asal belum diputuskan. Contoh KPI seperti MTBF/MTTR bukan otomatis kebutuhan yang telah disepakati.

## 7. Pengalaman antarmuka

### 7.1 Desain yang disebutkan

- Referensi pengalaman percakapan: Google Gemini.
- Warna utama/SlimRail: **Industrial Deep Blue `#1E56A0`**.
- Kanvas terang: **`#F4F7FA`**.
- Tanpa karakter emotikon.
- SlimRail paling kiri, Sidebar collapsible untuk riwayat dan pencarian, area percakapan utama, Inspector geser di kanan.
- Input teks, attachment gambar, dan tombol voice recorder.
- Citation chips yang mengarah ke dokumen asli.
- Layout responsif.

Font, logo, icon set, bahasa UI/jawaban, breakpoint, prioritas perangkat, dark mode, library komponen, dan detail aksesibilitas belum ditentukan. Tidak ada screenshot/Figma tambahan yang disertakan pada brief ini.

### 7.2 Peta halaman dari brief

| Halaman | Fungsi |
| --- | --- |
| `/login` | Login |
| `/register` | Pendaftaran |
| `/pending` | Status menunggu approval |
| `/chat` | Workspace percakapan |
| `/knowledge` | Repository viewer dokumen |
| `/admin/users` | Approval dan alokasi pengguna |
| `/admin/docs` | Upload serta monitor ingestion |

Halaman khusus analytics, audit, dan gateway Super Admin belum memiliki path/rancangan pada struktur awal.

## 8. Struktur monorepo baseline

**BRIEF — struktur target, belum dibuat.** Lokasi root aplikasi terhadap workspace `Caliber2026` perlu diputuskan melalui D-02.

```text
manufacturing-knowledge-hub/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   └── security.py
│       ├── models/
│       │   ├── user.py
│       │   ├── chat.py
│       │   └── maintenance.py
│       ├── schemas/
│       │   ├── auth.py
│       │   ├── chat.py
│       │   └── components.py
│       ├── api/
│       │   ├── auth.py
│       │   ├── admin.py
│       │   ├── chat.py
│       │   └── knowledge.py
│       └── services/
│           ├── llm_gateway.py
│           ├── vector_service.py
│           └── sql_service.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       ├── app/
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   ├── register/page.tsx
│       │   │   └── pending/page.tsx
│       │   ├── chat/page.tsx
│       │   ├── knowledge/page.tsx
│       │   └── admin/
│       │       ├── users/page.tsx
│       │       └── docs/page.tsx
│       ├── components/
│       │   ├── layout/
│       │   │   ├── SlimRail.tsx
│       │   │   └── Sidebar.tsx
│       │   ├── chat/
│       │   │   ├── ChatInput.tsx
│       │   │   ├── MessageItem.tsx
│       │   │   └── Inspector.tsx
│       │   └── rich-components/
│       │       ├── ProcedureChecklist.tsx
│       │       ├── InterlockLogicCard.tsx
│       │       ├── SparePartBOMTable.tsx
│       │       └── RootCauseCard.tsx
│       └── lib/
│           ├── api.ts
│           └── audio.ts
└── scripts/
    ├── requirements.txt
    ├── ingest_docs.py
    ├── seed_maintenance.py
    └── data/
```

Komponen yang belum diwakili dengan jelas oleh tree awal antara lain penyimpanan dokumen/revisi, graph service, lexical index, status ingestion, migration, pengujian, serta tampilan Super Admin. Penambahan modul perlu mengikuti keputusan arsitektur, bukan diasumsikan sudah ada.

## 9. Empat tahap dari brief

| Tahap asli | Isi baseline | Penjabaran pada backlog |
| --- | --- | --- |
| 1 | Compose PostgreSQL, Qdrant, backend, frontend; environment konfigurasi | Fase 1 |
| 2 | Seed Excel; ekstraksi PDF; embedding; simpan ke Qdrant | Fase 2, ditambah keputusan sumber PNG dan graph/hybrid |
| 3 | Auth, approval, RBAC-filtered retrieval, gateway structured output | Fase 3–5 |
| 4 | Layout Next.js, multimodal input, renderer komponen, Inspector | Fase 6–7 |

Fase 0 pada backlog adalah discovery untuk menutup informasi yang hilang. Fase 8 adalah verifikasi dan penyerahan hasil sesuai target rilis yang dipilih.

## 10. Definisi keberhasilan yang perlu disepakati

**USULAN kategori evaluasi, tanpa angka target:**

| Dimensi | Bukti yang dapat digunakan | Keputusan |
| --- | --- | --- |
| Cakupan data | Manifest sumber, hasil import, laporan ekstraksi dan indexing | D-07 sampai D-12 |
| Ketepatan retrieval | Query uji dengan sumber relevan yang telah ditandai | D-13, D-14, D-26 |
| Grounding jawaban | Kesesuaian klaim, kutipan, tag, angka, satuan, dan dokumen | D-15, D-18, D-26 |
| Akses | Hasil pengujian per role/divisi untuk dokumen, SQL, graph, sitasi, dan history | D-06, D-26 |
| Performa | Latency jawaban/awal stream, concurrency, waktu ingestion | D-04, D-19, D-26 |
| Biaya | Pemakaian embedding, generation, OCR/vision, dan suara | D-04, D-16, D-24 |
| Usability | Penyelesaian alur operator, Admin, dan Super Admin di perangkat target | D-23, D-24, D-26 |

Tidak ada tenggat, estimasi biaya, kapasitas, formula KPI, maupun persentase akurasi yang telah disepakati pada brief.

## 11. Peran supervisor AI

**USULAN cara kerja, D-28:**

- Menjaga konteks lintas sesi melalui dokumen yang memiliki sumber dan status jelas.
- Mengubah jawaban pengguna menjadi keputusan tercatat, lengkap dengan alasan dan dampak.
- Menurunkan keputusan menjadi task, dependensi, kontrak, dan kriteria penerimaan.
- Menandai penghambat spesifik; bagian yang sudah jelas dapat dilanjutkan sesuai scope kerja berikutnya.
- Memeriksa hasil kerja terhadap bukti, bukan menganggap checklist selesai berdasarkan niat.
- Meminta klarifikasi ketika detail produk/data belum diketahui dan memisahkan saran teknis dari keputusan final.

Daftar keputusan ada di [dokumen arsitektur](03-ARCHITECTURE-AND-DECISIONS.md); seluruh pertanyaan discovery saat ini ada di [dokumen pertanyaan](06-OPEN-QUESTIONS.md).
