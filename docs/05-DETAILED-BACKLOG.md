# 05 — Backlog Implementasi Terperinci

## 1. Aturan penggunaan

Backlog ini adalah **USULAN penjabaran pekerjaan** berdasarkan kebutuhan pada brief dan gap yang ditemukan. Seluruh paket kerja di bawah **belum dinyatakan selesai**. Kode aplikasi, import, indexing, maupun pengujian belum dijalankan pada tahap dokumentasi awal.

- Scope rilis setiap task, penanggung jawab, estimasi, serta tanggal pelaksanaan **belum ditentukan**; isi setelah D-01 dan D-28 dijawab.
- Kotak `[ ]` adalah pekerjaan yang perlu dilakukan, bukan klaim fitur sudah tersedia.
- Referensi D-xx mengarah ke [register keputusan](03-ARCHITECTURE-AND-DECISIONS.md). Pertanyaan rinci ada di [daftar pertanyaan](06-OPEN-QUESTIONS.md).
- Task yang tergantung keputusan belum jelas harus mencatat penghambat spesifik. Discovery dan bagian yang inputnya sudah jelas dapat dilanjutkan sesuai scope kerja.
- Fitur yang ditunda harus dicatat pada keputusan scope; istilah hybrid, graph, multimodal, atau enterprise tidak digunakan sebagai klaim implementasi jika belum diverifikasi.
- Nomor fase mengelompokkan area kerja. **Dependensi menentukan urutan eksekusi**, termasuk dependensi lintas fase seperti bootstrap akun T1.6 dan invalidasi seluruh indeks T2.10.
- Setiap task selesai dengan hasil kerja dan bukti sesuai kriteria penerimaannya. Angka engineering, formula KPI, jumlah record, atau ambang performa tidak diisi secara spekulatif.

### Field pelacakan untuk setiap task

```text
ID task:
Scope rilis:
Status: DIRENCANAKAN / TERHALANG / DIKERJAKAN / DIVERIFIKASI / DITUNDA
Penanggung jawab:
Keputusan yang sudah tersedia:
Penghambat yang masih terbuka:
Estimasi dan dasar estimasi:
File/artefak berubah:
Bukti verifikasi:
Catatan tindak lanjut:
```

## 2. Checkpoint pembangunan

| Checkpoint | Hasil yang harus dapat dibuktikan | Dependensi utama |
| --- | --- | --- |
| M0 — Scope dan sumber | Rilis pertama, sumber otoritatif, use case, serta keputusan fondasi jelas | Fase 0; D-01, D-02, D-04, D-06, D-07 |
| M1 — Fondasi aplikasi | Service/config/schema dasar dapat dijalankan sesuai versi dan topologi terpilih | Fase 1; D-03, D-05, D-25 |
| M2 — Data siap digunakan | Import dapat direkonsiliasi; sumber terpilih memiliki ekstraksi, metadata, dan indeks yang diperlukan | Fase 2; D-08 sampai D-14 |
| M3 — Akses end-to-end | Role/divisi/status bekerja pada seluruh jalur data yang sudah aktif | Fase 3; D-06 |
| M4 — Jawaban bersumber | Retrieval, SQL/graph sesuai scope, kontrak komponen, dan sitasi terverifikasi | Fase 4; D-10, D-13 sampai D-18 |
| M5 — Chat dan multimodal | Session, transport, serta input terpilih bekerja melalui API | Fase 5; D-19 sampai D-22 |
| M6 — Pengalaman pengguna/admin | Layout, rich UI, Inspector, knowledge, approval, dan dashboard terpilih dapat digunakan | Fase 6–7; D-23, D-24 |
| M7 — Evaluasi dan delivery | Hasil evaluasi, build/deployment, dokumentasi operasional, dan UAT sesuai acceptance | Fase 8; D-26, D-27 |

M2 tidak menyiratkan bahwa seluruh graph/lexical service sudah selesai jika task terkait pada Fase 4 belum dijalankan. Status kesiapan per indeks harus terlihat secara terpisah sesuai D-08.

## Fase 0 — Discovery dan perencanaan

### T0.1 — Tetapkan scope rilis dan prioritas penggunaan

- **Prasyarat:** brief dan dokumentasi konteks awal.
- **Keputusan:** D-01, D-28.
- **Pekerjaan:**
  - [ ] Jawab tahap produk, audiens, tenggat, hasil penyerahan, tim, dan kapasitas kerja.
  - [ ] Tandai setiap F-01 sampai F-15 sebagai masuk rilis pertama atau dijadwalkan kemudian.
  - [ ] Urutkan use case prioritas berdasarkan nilai bagi pengguna/demo.
  - [ ] Tetapkan pemilik keputusan produk, teknis, dan validasi sumber.
- **Hasil:** scope rilis, urutan prioritas, dan catatan keputusan yang ditautkan ke backlog.
- **Diterima jika:** fitur wajib dan fitur tertunda jelas; tidak ada jadwal/kapasitas yang hanya diasumsikan dari nama folder hackathon atau label enterprise.

### T0.2 — Audit sumber asli dan isi dataset secara representatif

- **Prasyarat:** akses dataset lokal; inventaris nama file pada dokumen 02.
- **Keputusan:** D-07; hasil audit menjadi masukan D-09 dan D-11.
- **Pekerjaan:**
  - [ ] Baca slide deck penjelasan dan catat requirement tambahan atau perbedaan terhadap brief.
  - [ ] Profilkan workbook: sheet, header, jumlah row/kolom aktual, tipe, unit, formula, kosong, dan duplikasi.
  - [ ] Periksa sampel OPL, datasheet, drawing/BOM, C&E, plot plan, dan PNG P&ID di set yang representatif.
  - [ ] Catat kebutuhan teks/OCR/vision/layout dan contoh masalah ekstraksi dengan locator sumber.
  - [ ] Pisahkan hasil terverifikasi, interpretasi yang perlu konfirmasi, dan format yang belum dapat dibaca.
- **Hasil:** laporan audit isi dan gap, tanpa membuat data pengganti.
- **Diterima jika:** angka 211/31 dibuktikan atau selisihnya dijelaskan; setiap kesimpulan teknis memiliki sumber; isi PPTX tidak lagi dianggap telah tercakup hanya dari filename.

### T0.3 — Susun query acuan dan rancangan acceptance

- **Prasyarat:** T0.1 dan hasil relevan T0.2.
- **Keputusan:** D-26, D-06, D-10, D-15.
- **Pekerjaan:**
  - [ ] Pilih query representatif tiap fitur/divisi/equipment yang masuk scope.
  - [ ] Hubungkan query ke sumber/halaman/record yang seharusnya digunakan.
  - [ ] Sertakan kasus exact tag, lintas sumber, angka maintenance, akses tidak sesuai, bukti kurang, dan sumber bertentangan bila tersedia.
  - [ ] Minta validator yang ditunjuk menilai jawaban acuan dan formula terkait.
  - [ ] Tentukan metrik dan ambang acceptance tanpa membuat persentase keberhasilan sebelum evaluasi.
- **Hasil:** golden query set awal beserta rubric, role/divisi penguji, dan sumber bukti.
- **Diterima jika:** expected answer dapat dilacak ke sumber, bukan jawaban LLM yang diasumsikan benar.

### T0.4 — Lengkapi desain fondasi dan kontrak untuk slice pertama

- **Prasyarat:** T0.1, informasi sumber yang relevan dari T0.2, jawaban fondasi pengguna.
- **Keputusan:** D-02 sampai D-06, D-17 sampai D-19, D-25 sesuai slice.
- **Pekerjaan:**
  - [ ] Catat pilihan root repo, stack/version, deployment, role/ACL, dan session.
  - [ ] Selesaikan schema dan endpoint yang diperlukan untuk slice pertama; pertahankan daftar detail yang masih terbuka.
  - [ ] Tetapkan alur akses file dan cara kontrak menangani sumber non-PDF.
  - [ ] Perbarui diagram, tree modul, decision log, dan dependensi task setelah pilihan diterima.
- **Hasil:** baseline implementasi untuk slice pertama dan daftar penghambat fitur berikutnya.
- **Diterima jika:** implementer dapat bekerja tanpa memilih sendiri keputusan produk yang belum diberikan; bagian kontrak yang belum final tetap ditandai.

## Fase 1 — Monorepo, konfigurasi, dan infrastruktur

### T1.1 — Bentuk struktur monorepo dan koneksi ke dataset

- **Prasyarat:** keputusan lokasi repo/data pada T0.4.
- **Keputusan:** D-02, D-25.
- **Pekerjaan:**
  - [ ] Buat direktori backend, frontend, scripts, dan dokumentasi pada root yang dipilih.
  - [ ] Terapkan tree baseline beserta modul tambahan yang memang dibutuhkan keputusan arsitektur.
  - [ ] Hubungkan source root dataset melalui konfigurasi/mount sesuai keputusan.
  - [ ] Dokumentasikan penanganan path yang mengandung spasi, `&`, underscore, serta variasi nama folder OPL.
  - [ ] Tentukan file yang masuk version control dan file lokal/runtime sesuai workflow tim.
- **Hasil:** scaffold konsisten dan referensi data yang valid.
- **Diterima jika:** sumber ditemukan pada lingkungan target tanpa hard-code path absolut mesin pengembang atau menganggap path contoh sitasi sebagai file aktual.

### T1.2 — Tetapkan dependency dan runtime yang dapat direproduksi

- **Prasyarat:** T1.1; keputusan stack.
- **Keputusan:** D-03, D-25.
- **Pekerjaan:**
  - [ ] Pin runtime Python/Node, library backend/pipeline, Next.js/React, dan Tailwind sesuai pilihan.
  - [ ] Pilih driver PostgreSQL, engine XLSX, JWT/hash, serta SDK provider yang diperlukan.
  - [ ] Buat dependency manifest dan lockfile sesuai package manager terpilih.
  - [ ] Pin image/digest service sesuai kebijakan versi, termasuk penyelesaian tag Qdrant `latest`.
  - [ ] Jalankan pemeriksaan kompatibilitas instalasi/import/build dasar.
- **Hasil:** manifest dependency dan catatan kompatibilitas.
- **Diterima jika:** setup bersih memakai versi yang terdokumentasi; versi/model tidak diklaim didukung hanya karena ada dalam brief.

### T1.3 — Implementasikan konfigurasi environment

- **Prasyarat:** T1.1, T1.2.
- **Keputusan:** D-04, D-05, D-08, D-12, D-16, D-25.
- **Pekerjaan:**
  - [ ] Buat `backend/app/core/config.py` dan `.env.example` dengan placeholder yang jelas.
  - [ ] Definisikan database, Qdrant, source/storage root, origin, model, dan session config sesuai fitur aktif.
  - [ ] Bedakan URL service internal Compose dengan URL yang dapat diakses browser/host.
  - [ ] Validasi config wajib berdasarkan provider/fitur yang dipilih; dokumentasikan pesan jika nilai belum tersedia.
  - [ ] Pastikan API key dan kredensial backend tidak menjadi environment publik frontend.
- **Hasil:** konfigurasi tervalidasi dan contoh setup.
- **Diterima jika:** konfigurasi salah menghasilkan pesan yang dapat ditindaklanjuti, sedangkan `.env.example` tidak berisi rahasia nyata atau nilai produksi rekaan.

### T1.4 — Jalankan topologi Compose terpilih

- **Prasyarat:** T1.2, T1.3.
- **Keputusan:** D-03, D-04, D-25.
- **Pekerjaan:**
  - [ ] Buat Dockerfile backend/frontend dan Compose PostgreSQL/Qdrant/service lain yang telah dipilih.
  - [ ] Atur jaringan, port, volume persisten, source mount, dan perbedaan mode development/deployment.
  - [ ] Tambahkan health/readiness yang mencerminkan kesiapan service dan dependensi yang relevan.
  - [ ] Uji startup, koneksi antar-service, restart, dan persistensi data uji.
  - [ ] Dokumentasikan kebutuhan runtime host serta command setup yang benar-benar diuji.
- **Hasil:** infrastruktur aplikasi dapat dijalankan.
- **Diterima jika:** seluruh service terpilih dapat berkomunikasi dan data persisten tetap tersedia setelah restart sesuai konfigurasi; startup tidak bergantung pada urutan tebakan.

### T1.5 — Buat schema dasar dan migration

- **Prasyarat:** T1.4; keputusan model dasar pada T0.4.
- **Keputusan:** D-05, D-06, D-08, D-20, D-25.
- **Pekerjaan:**
  - [ ] Modelkan user, role/division membership, dan lifecycle akun sesuai cardinality yang dipilih.
  - [ ] Modelkan identitas dokumen/revision/ACL serta chat/session yang diperlukan slice aktif.
  - [ ] Tetapkan constraint, identitas stabil, timestamp/timezone, foreign key, dan index berdasarkan akses nyata.
  - [ ] Buat migration dan mekanisme upgrade pada database kosong.
  - [ ] Jadwalkan migration maintenance setelah T2.2; jangan membuat 31 kolom berdasarkan tebakan.
- **Hasil:** schema dasar berversi dan koneksi ORM.
- **Diterima jika:** migration membentuk schema konsisten dengan keputusan dan constraint menolak state tidak valid yang telah didefinisikan.

### T1.6 — Bootstrap Super Admin dan data identitas awal

- **Prasyarat:** T1.5 dan hashing/auth primitive pada T3.1.
- **Keputusan:** D-05, D-06.
- **Pekerjaan:**
  - [ ] Implementasikan bootstrap akun awal dengan mekanisme credential yang disepakati.
  - [ ] Seed divisi/role sesuai keputusan daftar tetap atau configurable.
  - [ ] Gunakan hashing dan model yang sama dengan jalur auth aplikasi.
  - [ ] Buat proses idempotent serta dokumentasikan penggunaan dan hasilnya.
- **Hasil:** akses administrasi awal tersedia melalui mekanisme terdokumentasi.
- **Diterima jika:** bootstrap ulang tidak menggandakan akun/role atau mengganti credential tanpa aturan yang disepakati.

## Fase 2 — Data preparation, import, dan ingestion

### T2.1 — Bangun manifest seluruh sumber dalam scope

- **Prasyarat:** T0.2, T1.1.
- **Keputusan:** D-07, D-08.
- **Pekerjaan:**
  - [ ] Enumerasi sumber berdasarkan root dan format yang dipilih, termasuk PNG serta subfolder OPL.
  - [ ] Catat identitas, filename asli, path relatif, tipe, checksum/revision sesuai rancangan.
  - [ ] Hubungkan setiap sumber dengan set/equipment awal tanpa menganggap folder menjelaskan seluruh tag di dalamnya.
  - [ ] Laporkan file yang tidak terbaca, diabaikan, duplikat, atau belum terklasifikasi.
- **Hasil:** manifest machine-readable beserta ringkasan pemeriksaan.
- **Diterima jika:** seluruh sumber dalam scope terhitung; setiap pengecualian dijelaskan; perbedaan dengan inventaris awal 98 file dapat direkonsiliasi.

### T2.2 — Finalkan data dictionary maintenance

- **Prasyarat:** T0.2, T2.1.
- **Keputusan:** D-09, D-10, D-06.
- **Pekerjaan:**
  - [ ] Rekam nama header asli, posisi sheet/kolom, contoh tipe nilai, nullability, dan satuan yang benar-benar ditemukan.
  - [ ] Petakan kolom ke schema SQL terpilih, termasuk raw value/lineage bila disepakati.
  - [ ] Tetapkan identitas record, aturan tanggal/formula/duplikasi, dan penanganan row invalid.
  - [ ] Identifikasi field atau mapping yang mendukung akses divisi dan metrik yang dipilih.
  - [ ] Catat selisih terhadap 211 row/31 kolom dan keputusan penyelesaiannya.
- **Hasil:** data dictionary serta spesifikasi transformasi import.
- **Diterima jika:** setiap kolom model memiliki sumber atau alasan metadata aplikasi yang jelas; tidak ada nama/tipe kolom maintenance yang diada-adakan.

### T2.3 — Implementasikan seeding maintenance yang dapat direkonsiliasi

- **Prasyarat:** T2.2, T1.5.
- **Keputusan:** D-09, D-25.
- **Pekerjaan:**
  - [ ] Buat migration/model `maintenance_records` berdasarkan dictionary yang disepakati.
  - [ ] Implementasikan `scripts/seed_maintenance.py` dengan pandas dan engine XLSX terpilih.
  - [ ] Terapkan transaksi, validasi per record, pelaporan error, dan mode import ulang yang disepakati.
  - [ ] Cocokkan record dan nilai penting terhadap sumber, termasuk null, tanggal, unit, serta formula.
  - [ ] Uji eksekusi ulang dan kegagalan di tengah import tanpa hasil ganda/parsial yang tidak terlapor.
- **Hasil:** data maintenance terimpor dengan laporan sumber, jumlah diterima/ditolak, dan transformasi.
- **Diterima jika:** jumlah dan nilai dapat direkonsiliasi; target 211 berlaku bila audit membenarkannya; tidak ada row hilang diam-diam atau perubahan untuk sekadar memenuhi angka brief.

### T2.4 — Tetapkan metadata dokumen dan mapping akses

- **Prasyarat:** T2.1; kebijakan role/divisi tersedia.
- **Keputusan:** D-06, D-07, D-12.
- **Pekerjaan:**
  - [ ] Tetapkan enum `doc_type`, equipment utama/terkait, judul, dan division access untuk sumber dalam scope.
  - [ ] Catat dasar klasifikasi dari mapping resmi atau pemeriksaan isi yang disepakati.
  - [ ] Tangani sumber bersama, dokumen multi-equipment, serta label yang belum dapat ditentukan.
  - [ ] Validasi format dan kelengkapan metadata sebelum sumber masuk retrieval.
- **Hasil:** mapping sumber-ke-akses dan metadata yang dapat dipakai semua indeks.
- **Diterima jika:** metadata tidak hanya menebak divisi berdasarkan filename; sumber tanpa klasifikasi mengikuti kebijakan eksplisit.

### T2.5 — Implementasikan ekstraksi PDF yang mempertahankan sumber

- **Prasyarat:** T1.2, T2.1, hasil audit T0.2.
- **Keputusan:** D-11, D-12, D-18.
- **Pekerjaan:**
  - [ ] Ekstrak halaman/teks dengan PyMuPDF sesuai tipe PDF aktual.
  - [ ] Deteksi halaman kosong/scan/tabel/layout yang memerlukan jalur tambahan.
  - [ ] Pertahankan page locator, teks sumber, heading, tag, angka, unit, dan struktur tabel sejauh metode terpilih mendukung.
  - [ ] Bedakan raw extraction dari teks yang dinormalisasi untuk retrieval.
  - [ ] Catat error dan kualitas per file/halaman; jalankan jalur tambahan sesuai keputusan, bukan melaporkan hasil kosong sebagai sukses penuh.
- **Hasil:** artefak ekstraksi PDF dan laporan kualitas.
- **Diterima jika:** sampel OPL, datasheet, drawing, C&E, dan plot plan dapat ditelusuri ke halaman asli, serta kehilangan informasi teridentifikasi.

### T2.6 — Implementasikan parsing PNG, drawing, dan kebutuhan spasial terpilih

- **Prasyarat:** T2.1, hasil T0.2, T2.5 untuk PDF yang membutuhkan metode tambahan.
- **Keputusan:** D-11, D-14, D-16, D-18.
- **Pekerjaan:**
  - [ ] Proses PNG P&ID menggunakan metode OCR/vision/layout yang dipilih.
  - [ ] Pertahankan label/tag, region/locator, dan bukti visual untuk informasi yang diekstrak.
  - [ ] Ekstrak struktur BOM/C&E/tabel atau konektivitas hanya sesuai scope dan kemampuan metode yang telah diuji.
  - [ ] Implementasikan representasi plot plan sesuai tingkat kebutuhan visual/lokasi/perhitungan yang disepakati.
  - [ ] Pisahkan informasi terbaca, ambigu, dan tidak tersedia; bandingkan sampel dengan sumber visual.
- **Hasil:** representasi sumber gambar/diagram dengan provenance.
- **Diterima jika:** PNG dalam scope benar-benar dapat berkontribusi pada fitur terpilih; OCR teks tidak diklaim sebagai pemahaman konektivitas penuh; koordinat/jarak tidak dibuat tanpa acuan.

### T2.7 — Bangun chunking, normalisasi tag, dan provenance

- **Prasyarat:** T2.4, T2.5, dan T2.6 untuk sumber terpilih.
- **Keputusan:** D-12, D-18.
- **Pekerjaan:**
  - [ ] Terapkan strategi chunk per prosedur/heading/halaman/tabel/region yang disepakati.
  - [ ] Pertahankan langkah, hubungan row/column, angka, serta satuan yang tidak boleh terpisah tanpa konteks.
  - [ ] Normalisasikan tag dan alias dengan pemetaan kembali ke bentuk sumber.
  - [ ] Sematkan metadata brief serta identitas/revision/locator tambahan yang telah dipilih.
  - [ ] Buat ID chunk dan laporan jumlah/ukuran yang mendukung indexing ulang.
- **Hasil:** chunk siap indeks, metadata tervalidasi, dan hubungan ke sumber asli.
- **Diterima jika:** setiap chunk memiliki scope dan provenance; kutipan tidak bergantung pada rekonstruksi kalimat model; tag baru tidak diciptakan saat normalisasi.

### T2.8 — Implementasikan embedding dan indexing Qdrant

- **Prasyarat:** T1.4, T2.7.
- **Keputusan:** D-12, D-16.
- **Pekerjaan:**
  - [ ] Konfigurasi collection `manufacturing_knowledge` sesuai dimensi/distance/version yang dipilih.
  - [ ] Buat embedding dokumen/query dengan model dan konfigurasi kompatibel.
  - [ ] Terapkan batching, retry terukur, rate handling, dan pencatatan usage yang tersedia.
  - [ ] Upsert point dengan ID stabil, metadata akses, equipment, tipe dokumen, dan source reference.
  - [ ] Validasi count, dimensi, payload, serta perilaku reindex dan embedding mismatch.
- **Hasil:** dense index terisi dan laporan indexing yang dapat direkonsiliasi.
- **Diterima jika:** query memakai embedding yang kompatibel; metadata filter tersedia; proses ulang tidak menggandakan chunk; biaya/jumlah token tidak diisi dengan angka perkiraan yang dilabeli aktual.

### T2.9 — Satukan pipeline ingestion dan status job

- **Prasyarat:** T1.5, T2.1, T2.4–T2.8 untuk format dalam scope.
- **Keputusan:** D-08, D-24.
- **Pekerjaan:**
  - [ ] Implementasikan jalur pipeline yang dapat dipanggil CLI dan upload Admin.
  - [ ] Simpan identitas job, sumber, actor, tahap, progres, hasil, serta error sesuai schema terpilih.
  - [ ] Terapkan retry/recovery/cancel sesuai keputusan eksekusi job.
  - [ ] Siapkan integrasi status lexical/graph untuk T4.1/T4.4 bila fitur tersebut aktif.
  - [ ] Definisikan kapan sumber searchable dan bagaimana kegagalan parsial dilaporkan.
- **Hasil:** service/job ingestion dan data monitor.
- **Diterima jika:** status tidak berhenti pada upload sukses; pengguna Admin dapat mengetahui sumber/tahap yang gagal; restart mengikuti perilaku recovery yang disepakati.

### T2.10 — Sinkronkan revision, ACL, deletion, dan invalidasi indeks

- **Prasyarat:** T2.9; T4.1/T4.3/T4.4 untuk jalur lexical/graph yang aktif.
- **Keputusan:** D-06, D-08, D-12, D-14, D-18, D-20.
- **Pekerjaan:**
  - [ ] Terapkan perubahan revision dan ACL pada registry sumber serta seluruh indeks terkait.
  - [ ] Tangani replace/delete/arsip sesuai kebijakan tanpa kehilangan asal jawaban historis yang masih harus dipertahankan.
  - [ ] Invalidasi cache bila dipakai serta definisikan hasil query saat update belum lengkap.
  - [ ] Uji akses file dan sitasi lama setelah revision/status/izin berubah.
  - [ ] Catat sumber yatim, point/edge lama, dan cara rekonsiliasinya.
- **Hasil:** lifecycle sumber konsisten lintas storage, SQL, dense, lexical, graph, dan history sesuai scope.
- **Diterima jika:** dokumen yang sudah tidak boleh diakses tidak muncul melalui jalur indeks atau sitasi lain; kebijakan historical reference dapat dibuktikan.

## Fase 3 — Auth, policy, dan knowledge API

### T3.1 — Implementasikan registrasi dan login

- **Prasyarat:** T1.3, T1.5.
- **Keputusan:** D-05, D-25.
- **Pekerjaan:**
  - [ ] Buat primitive hashing/verification dan token/session sesuai pilihan.
  - [ ] Implementasikan schema registrasi/login, validasi identitas, duplikasi, dan field yang boleh diisi pengguna.
  - [ ] Buat akun registrasi dengan status `pending` serta role/divisi sesuai kebijakan, bukan klaim bebas dari client.
  - [ ] Implementasikan `/register`, `/login`, dan pembacaan status akun di bawah prefix API terpilih.
  - [ ] Tambahkan alur password/email tambahan hanya bila dipilih pada D-05.
- **Hasil:** auth API dan helper keamanan bersama.
- **Diterima jika:** login valid/invalid, duplikasi, pending, dan status tambahan terpilih berperilaku sesuai kontrak; password tidak disimpan sebagai teks biasa.

### T3.2 — Implementasikan approval dan alokasi pengguna

- **Prasyarat:** T3.1, policy T3.4.
- **Keputusan:** D-05, D-06, D-24.
- **Pekerjaan:**
  - [ ] Buat endpoint daftar pending dan detail pendaftaran sesuai kewenangan.
  - [ ] Implementasikan approval, alokasi divisi, dan perubahan status/role yang diizinkan.
  - [ ] Terapkan validasi transisi dan transaksi agar dua tindakan Admin tidak menghasilkan state bertentangan.
  - [ ] Rekam actor, waktu, dan perubahan yang diperlukan audit; notifikasi mengikuti scope.
- **Hasil:** API administrasi pengguna.
- **Diterima jika:** hanya role berwenang dapat bertindak dan akun hasil approval mempunyai membership/status yang konsisten.

### T3.3 — Implementasikan lifecycle session dan perubahan izin aktif

- **Prasyarat:** T3.1.
- **Keputusan:** D-05, D-06, D-20.
- **Pekerjaan:**
  - [ ] Terapkan expiry, refresh, logout, dan revocation sesuai strategi session.
  - [ ] Definisikan cara backend memperoleh status/role/divisi efektif saat request.
  - [ ] Tangani perubahan status/membership ketika token masih berlaku.
  - [ ] Selaraskan error expired/invalid/pending/disabled dengan kontrak frontend.
- **Hasil:** session lifecycle dan resolved user context.
- **Diterima jika:** token lama mengikuti kebijakan perubahan akses yang dipilih; refresh/logout tidak menciptakan akses yang melampaui akun aktif.

### T3.4 — Buat policy akses bersama untuk semua sumber

- **Prasyarat:** T3.1, T3.3, mapping T2.4.
- **Keputusan:** D-06.
- **Pekerjaan:**
  - [ ] Implementasikan evaluasi role, status, division membership, dan document/record scope.
  - [ ] Definisikan antarmuka policy bagi katalog/file, Qdrant, lexical, graph, SQL, chat, dan attachment.
  - [ ] Tangani single/multi-division, sumber bersama, label kosong, serta batas Admin/Super Admin sesuai keputusan.
  - [ ] Buat fixture akses yang menunjukkan sumber boleh/tidak boleh per persona.
- **Hasil:** policy layer dan kontrak konteks akses.
- **Diterima jika:** scope berasal dari backend dan tidak dapat diperluas oleh filter client, tag dalam prompt, atau output model.

### T3.5 — Implementasikan akses file dan locator sitasi

- **Prasyarat:** T1.5, T2.1, T3.4; kontrak sitasi tersedia.
- **Keputusan:** D-08, D-18, D-25.
- **Pekerjaan:**
  - [ ] Resolve identitas sumber/revision ke file storage yang benar.
  - [ ] Implementasikan preview/download sesuai policy dan kebutuhan viewer terpilih.
  - [ ] Dukung page/region/source locator sesuai PDF, PNG, atau sumber tabular yang dipilih.
  - [ ] Definisikan respons untuk sumber hilang, revision lama, izin berubah, dan locator invalid.
  - [ ] Pastikan file yang dikembalikan ditentukan registry, bukan path arbitrer dari request/model.
- **Hasil:** knowledge file API terotorisasi.
- **Diterima jika:** request langsung dengan identitas sumber yang tidak diizinkan tetap ditolak; sumber valid membuka file/revision yang benar.

### T3.6 — Implementasikan katalog dan pencarian metadata dokumen

- **Prasyarat:** T1.5, T2.4, T3.4.
- **Keputusan:** D-06, D-08, D-24, D-25.
- **Pekerjaan:**
  - [ ] Buat listing/detail dokumen dengan pagination/filter/sort yang dipilih.
  - [ ] Terapkan scope pada hasil, jumlah, facet, equipment, judul, dan status.
  - [ ] Sediakan metadata yang diperlukan knowledge UI serta mode Admin sesuai batas katalog/isi.
  - [ ] Bedakan sumber belum siap, gagal, aktif, dan revision lain sesuai lifecycle.
- **Hasil:** API repository pengetahuan.
- **Diterima jika:** katalog tidak membocorkan metadata di luar scope yang disepakati dan konsisten dengan akses file sebenarnya.

### T3.7 — Verifikasi matriks akses end-to-end

- **Prasyarat:** T3.2–T3.6 dan jalur retrieval/history/attachment yang akan diuji.
- **Keputusan:** D-06, D-26.
- **Pekerjaan:**
  - [ ] Uji pending, approved tiap divisi, multi-divisi jika aktif, Admin, dan Super Admin.
  - [ ] Uji akses normal dan akses langsung lewat ID/URL file, row SQL, node/edge graph, chunk, session, serta attachment.
  - [ ] Uji perubahan ACL/role/divisi/status, sumber tanpa label, dan cache bila ada.
  - [ ] Periksa bahwa filter berlaku sebelum data masuk konteks LLM dan hasil agregasi.
- **Hasil:** bukti matriks akses dan daftar kegagalan yang perlu diperbaiki.
- **Diterima jika:** seluruh skenario yang disepakati lulus; menyembunyikan tombol frontend tidak dihitung sebagai bukti otorisasi backend.

## Fase 4 — Hybrid/graph RAG, SQL, dan respons AI

### T4.1 — Implementasikan dense, lexical, dan exact-tag candidate retrieval

- **Prasyarat:** T2.7, T2.8, T3.4.
- **Keputusan:** D-12, D-13.
- **Pekerjaan:**
  - [ ] Implementasikan pencarian dense pada Qdrant dengan filter akses wajib.
  - [ ] Bangun lexical index yang dipilih dari sumber/chunk/revision yang sama.
  - [ ] Tambahkan exact-tag matching/normalisasi sesuai kamus equipment/instrument.
  - [ ] Terapkan filter akses dan metadata pada setiap jalur sebelum kandidat digunakan.
  - [ ] Kembalikan source identity, skor asal, dan locator untuk fusion/evaluasi.
- **Hasil:** kandidat dense/lexical/exact-match yang dapat dibandingkan.
- **Diterima jika:** query tag dan query semantik teruji; lexical benar-benar dijalankan jika hybrid masuk scope; akses tidak hanya difilter setelah konteks terkumpul.

### T4.2 — Implementasikan fusion, ranking, dan reranking terpilih

- **Prasyarat:** T4.1, query acuan T0.3.
- **Keputusan:** D-13, D-26.
- **Pekerjaan:**
  - [ ] Gabungkan kandidat dengan metode fusion terpilih dan deduplikasi berdasarkan source/chunk/revision.
  - [ ] Terapkan top-k, threshold, prioritas exact tag, serta reranker bila dipilih.
  - [ ] Simpan parameter konfigurasi dan hasil evaluasi yang mendasari pemilihannya.
  - [ ] Bandingkan dense-only dan hybrid pada query acuan yang sama untuk memahami manfaat/biaya.
- **Hasil:** ranked evidence dan konfigurasi retrieval terukur.
- **Diterima jika:** hasil dapat direproduksi dari konfigurasi dan dataset uji; kenaikan kualitas tidak diklaim tanpa hasil evaluasi.

### T4.3 — Implementasikan model dan storage graph

- **Prasyarat:** T2.4, T2.7; storage/deployment terpilih tersedia.
- **Keputusan:** D-04, D-14.
- **Pekerjaan:**
  - [ ] Definisikan node, edge, arah, cardinality, identitas tag, serta sumber bukti sesuai keputusan.
  - [ ] Implementasikan storage/migration sesuai PostgreSQL atau graph engine yang dipilih.
  - [ ] Simpan provenance/revision dan informasi akses yang diperlukan evaluasi policy.
  - [ ] Definisikan constraint relasi, pembaruan sumber, serta query dasar graph.
- **Hasil:** schema graph dan antarmuka penyimpanan relasi.
- **Diterima jika:** model dapat mewakili hubungan yang dibutuhkan use case tanpa menyamakan co-occurrence tag dengan relasi teknis.

### T4.4 — Ekstrak dan ingest hubungan berbasis bukti

- **Prasyarat:** T4.3, ekstraksi relevan T2.5/T2.6, mapping sumber T2.4.
- **Keputusan:** D-07, D-11, D-14.
- **Pekerjaan:**
  - [ ] Implementasikan mapping/manual import/ekstraksi otomatis sesuai metode yang dipilih.
  - [ ] Hubungkan equipment, instrument, interlock, dan entitas tambahan yang disepakati.
  - [ ] Simpan bukti sumber untuk tiap edge serta status ketidakpastian sesuai keputusan.
  - [ ] Tangani alias, tag yang belum dikenali, relasi duplikat, dan bukti berbeda antar-revision.
  - [ ] Bandingkan sampel relasi dengan sumber dan query acuan; laporkan hubungan yang belum dapat diverifikasi.
- **Hasil:** graph terisi dengan evidence dan laporan ekstraksi.
- **Diterima jika:** setiap edge yang dipakai jawaban mempunyai sumber yang sesuai; tidak ada hubungan `Related_Interlock` yang dibuat hanya dari contoh tag brief.

### T4.5 — Implementasikan graph-augmented retrieval

- **Prasyarat:** T4.2, T4.4, T3.4.
- **Keputusan:** D-06, D-14, D-15.
- **Pekerjaan:**
  - [ ] Resolve entitas query ke node yang tersedia dengan penanganan ambiguitas.
  - [ ] Traverse sesuai batas depth/hasil dan tipe hubungan yang dipilih.
  - [ ] Terapkan policy pada node, edge, dan evidence sebelum hasil memperluas konteks.
  - [ ] Gabungkan evidence graph dengan ranking dokumen tanpa duplikasi atau hilangnya provenance.
  - [ ] Uji query graph acuan, hubungan hilang, dan jalur lintas divisi.
- **Hasil:** graph benar-benar memengaruhi evidence retrieval sesuai scope.
- **Diterima jika:** jawaban relasional dapat menunjukkan asal hubungan; traversal tidak memperluas akses melalui node/edge terlarang.

### T4.6 — Implementasikan analitik maintenance/Text-to-SQL

- **Prasyarat:** T2.3, T3.4, definisi metrik terpilih.
- **Keputusan:** D-06, D-10, D-17, D-18.
- **Pekerjaan:**
  - [ ] Implementasikan query template/semantic layer/SQL generation sesuai keputusan.
  - [ ] Terapkan scope row/kolom, koneksi baca-saja, batas hasil/waktu, dan validasi query sesuai pendekatan.
  - [ ] Terapkan formula, unit, timezone, interval, null handling, dan pembulatan yang telah disepakati.
  - [ ] Kembalikan hasil terstruktur serta provenance/filter/perhitungan yang diperlukan sitasi.
  - [ ] Uji hasil dengan perhitungan independen dari data acuan, termasuk tanpa record dan input ambigu.
- **Hasil:** `sql_service.py` dan format hasil analitik yang teruji.
- **Diterima jika:** angka dapat direproduksi dan hanya menggunakan data yang diizinkan; model tidak diberi keleluasaan write SQL atau formula rekaan.

### T4.7 — Implementasikan router dan penyusunan konteks RAG

- **Prasyarat:** T4.2 serta T4.5/T4.6 bila masuk scope.
- **Keputusan:** D-15, D-20.
- **Pekerjaan:**
  - [ ] Klasifikasikan kebutuhan dokumen, graph, SQL, atau kombinasi dengan mekanisme terpilih.
  - [ ] Tangani exact equipment, alias, pertanyaan lanjutan, multi-equipment, dan ambiguitas.
  - [ ] Susun konteks sesuai budget token, prioritas sumber, deduplikasi, dan aturan revision.
  - [ ] Sertakan rujukan sumber yang dapat diverifikasi generator/validator.
  - [ ] Perlakukan isi dokumen sebagai evidence; instruksi di dalam sumber tidak mengubah role, scope, atau perilaku tool aplikasi.
- **Hasil:** context assembly dan route trace yang dapat diuji.
- **Diterima jika:** query acuan menuju sumber yang tepat dan pemotongan konteks tidak menghilangkan informasi penting tanpa perilaku yang telah ditentukan.

### T4.8 — Implementasikan gateway model dan structured output

- **Prasyarat:** T1.3, schema T4.10; keputusan provider/model tersedia.
- **Keputusan:** D-16, D-17, D-19, D-24.
- **Pekerjaan:**
  - [ ] Buat client OpenAI/OpenRouter sesuai provider aktif dan peran masing-masing.
  - [ ] Verifikasi model/SDK terpilih mendukung schema serta modalitas yang dibutuhkan.
  - [ ] Terapkan structured output, timeout, retry, quota, dan fallback hanya jika dipilih.
  - [ ] Catat model/provider aktual, request status, serta usage yang disediakan API.
  - [ ] Uji output valid/invalid dan kegagalan provider menggunakan kasus yang sesuai, dengan panggilan nyata saat konfigurasi tersedia.
- **Hasil:** `llm_gateway.py` yang menyediakan respons sesuai kontrak terpilih.
- **Diterima jika:** output schema teruji pada konfigurasi aktual; provider alternatif tidak diasumsikan memiliki perilaku identik.

### T4.9 — Implementasikan penyusunan dan validasi sitasi

- **Prasyarat:** T2.7, T3.5; output SQL/graph jika aktif.
- **Keputusan:** D-15, D-18.
- **Pekerjaan:**
  - [ ] Petakan rujukan model/hasil retrieval ke identitas sumber/revision/locator yang benar.
  - [ ] Bangun snippet dari representasi sumber yang disepakati dan validasi kutipan.
  - [ ] Tangani PDF, PNG/region, serta workbook/SQL sesuai schema sumber terpilih.
  - [ ] Hubungkan citation dengan klaim/kartu/row/step sesuai granularitas yang dipilih.
  - [ ] Periksa akses akhir dan tangani sumber yang berubah/tidak tersedia.
- **Hasil:** citation resolver/validator dan payload Inspector.
- **Diterima jika:** judul, kutipan, halaman/region/record, dan file dapat ditelusuri; path atau snippet buatan model tidak diterima tanpa pencocokan.

### T4.10 — Finalkan schema empat komponen dan hasil non-komponen

- **Prasyarat:** keputusan kontrak dari T0.4 dan hasil sumber yang diperlukan.
- **Keputusan:** D-10, D-17, D-18, D-23.
- **Pekerjaan:**
  - [ ] Definisikan schema Pydantic dan tipe frontend dengan discriminant sesuai cardinality terpilih.
  - [ ] Rinci ProcedureChecklist, InterlockLogicCard, SparePartBOMTable, dan RootCauseCard.
  - [ ] Tentukan bentuk teks biasa/hasil SQL/multi-equipment bila dipilih.
  - [ ] Modelkan unknown/null, alert, fakta/hipotesis, no-evidence, clarification, dan versioning sesuai keputusan.
  - [ ] Buat contoh fixture bersumber atau sintetis berlabel untuk kasus valid dan invalid.
- **Hasil:** kontrak payload tervalidasi dan fixture lintas backend/frontend.
- **Diterima jika:** `details: {}` tidak lagi menjadi objek bebas untuk renderer; string daftar enum dengan `|` ditolak sebagai nilai runtime.

### T4.11 — Satukan alur jawaban berbasis sumber

- **Prasyarat:** T4.7–T4.10 serta jalur retrieval yang masuk scope.
- **Keputusan:** D-15, D-16, D-17, D-18.
- **Pekerjaan:**
  - [ ] Jalankan route, retrieval, context assembly, generation, schema validation, dan citation validation sebagai alur utuh.
  - [ ] Terapkan perilaku untuk bukti kurang, sumber konflik, pertanyaan ambigu, dan di luar dataset.
  - [ ] Gunakan hasil kalkulasi SQL sebagai sumber angka; bedakan fakta tercatat dan inferensi sesuai kebijakan.
  - [ ] Tangani respons invalid/refusal/timeout melalui hasil/error contract yang disepakati.
  - [ ] Verifikasi contoh end-to-end tiap bentuk jawaban terpilih.
- **Hasil:** service jawaban siap dihubungkan ke chat API.
- **Diterima jika:** jawaban tidak memaksakan kartu, equipment, alert, atau sitasi ketika sumber/kontrak tidak mendukungnya; klaim engineering yang disajikan mengikuti kebijakan bukti.

## Fase 5 — Session, streaming, dan multimodal API

### T5.1 — Implementasikan session dan penyimpanan message

- **Prasyarat:** T1.5, T3.4; schema jawaban terpilih.
- **Keputusan:** D-20, D-25.
- **Pekerjaan:**
  - [ ] Buat operasi session/history sesuai scope: create, list, detail, search, rename, delete, dan fitur tambahan terpilih.
  - [ ] Simpan message, final payload, schema version, source reference, usage, dan attachment sesuai kebijakan.
  - [ ] Terapkan ownership, akses administratif, serta perubahan izin pada history.
  - [ ] Definisikan status pesan saat queued/generating/complete/failed sesuai nama status yang disepakati.
- **Hasil:** chat persistence dan history API.
- **Diterima jika:** session pengguna lain tidak dapat diakses di luar kewenangan dan history dapat dirender sesuai versi payloadnya.

### T5.2 — Implementasikan transport jawaban terpilih

- **Prasyarat:** T4.11, T5.1.
- **Keputusan:** D-19, D-25.
- **Pekerjaan:**
  - [ ] Implementasikan request/response JSON final atau event transport yang disepakati.
  - [ ] Jika streaming, definisikan event progres/teks/final/error dan pengenal message/request.
  - [ ] Pisahkan output parsial dari final payload yang telah lolos validasi.
  - [ ] Sesuaikan buffering, koneksi, autentikasi, dan deployment proxy dengan transport terpilih.
- **Hasil:** chat endpoint dan kontrak transport yang dapat digunakan frontend.
- **Diterima jika:** browser dapat mengenali awal, progres, final, dan kegagalan tanpa menganggap fragmen JSON sebagai respons lengkap.

### T5.3 — Tangani cancel, disconnect, retry, dan konsistensi penyimpanan

- **Prasyarat:** T5.1, T5.2.
- **Keputusan:** D-19, D-20, D-24.
- **Pekerjaan:**
  - [ ] Terapkan perilaku pembatalan dan koneksi terputus sesuai kemampuan provider/transport.
  - [ ] Definisikan idempotensi request/retry agar pesan final tidak tersimpan ganda.
  - [ ] Rekam status akhir dan usage yang tersedia untuk request gagal/dibatalkan.
  - [ ] Uji request timeout, provider rate limit, JSON invalid, refresh browser, dan retry.
- **Hasil:** lifecycle request chat yang konsisten.
- **Diterima jika:** UI dan database menyepakati status message; kegagalan tidak tersimpan sebagai jawaban final yang valid.

### T5.4 — Implementasikan input gambar

- **Prasyarat:** T3.4, T4.8, T5.1; fitur gambar dipilih.
- **Keputusan:** D-20, D-21, D-16.
- **Pekerjaan:**
  - [ ] Buat upload gambar dengan validasi format, batas, kepemilikan, dan storage sesuai keputusan.
  - [ ] Hubungkan ke vision/extraction/retrieval sesuai tujuan input gambar.
  - [ ] Tangani equipment/tag ambigu melalui perilaku konfirmasi yang dipilih.
  - [ ] Bedakan attachment percakapan dan dokumen pengetahuan bersama sesuai lifecycle.
  - [ ] Uji gambar valid, tidak terbaca, di luar format/batas, dan akses lintas user.
- **Hasil:** image input API dengan jawaban sesuai kemampuan terpilih.
- **Diterima jika:** gambar memengaruhi pemrosesan secara nyata; sistem tidak menebak identitas equipment atau menjadikan attachment pengetahuan semua user tanpa kebijakan.

### T5.5 — Implementasikan input suara dan transkripsi

- **Prasyarat:** T1.3, T3.4, T5.1; fitur suara dipilih.
- **Keputusan:** D-22, D-16, D-20, D-23.
- **Pekerjaan:**
  - [ ] Implementasikan penerimaan audio sesuai format/durasi/ukuran yang dipilih.
  - [ ] Hubungkan transkripsi lokal/provider terpilih dengan pencatatan status dan usage yang tersedia.
  - [ ] Dukung preview/edit/transmit transcript sesuai alur produk.
  - [ ] Terapkan penyimpanan atau penghapusan audio sesuai keputusan.
  - [ ] Uji bahasa target, istilah teknis/tag, rekaman kosong, audio buruk, dan provider gagal.
- **Hasil:** transcript yang dapat digunakan sebagai input chat.
- **Diterima jika:** tombol suara bukan sekadar merekam; alur sampai pertanyaan berjalan dan kesalahan transkripsi bisa ditangani pengguna sesuai desain. Task TTS tambahan hanya dibuat bila dipilih secara eksplisit.

### T5.6 — Selaraskan kontrak API backend dan frontend

- **Prasyarat:** schema T4.10; endpoint auth, knowledge, chat yang sudah aktif.
- **Keputusan:** D-17, D-19, D-25.
- **Pekerjaan:**
  - [ ] Publikasikan OpenAPI/kontrak terpilih dengan prefix, auth, error, pagination, dan format transport.
  - [ ] Generate atau sinkronkan tipe frontend sesuai workflow yang disepakati.
  - [ ] Definisikan fetch wrapper untuk auth/session, request cancellation, upload, dan streaming bila aktif.
  - [ ] Uji contoh request/respons lintas service, termasuk validation error dan unauthorized.
- **Hasil:** kontrak integrasi yang konsisten dan client dasar.
- **Diterima jika:** frontend tidak perlu menebak shape `details`, event, atau error dari backend.

## Fase 6 — Antarmuka pengguna

### T6.1 — Susun design token dan state dasar UI

- **Prasyarat:** keputusan desain dan stack frontend.
- **Keputusan:** D-03, D-23.
- **Pekerjaan:**
  - [ ] Terapkan warna `#1E56A0` dan kanvas `#F4F7FA` pada token tema.
  - [ ] Pilih typography, ikon, spacing, border, dan library sesuai keputusan.
  - [ ] Definisikan button/input/focus/loading/empty/error state yang konsisten.
  - [ ] Terapkan bahasa/copy serta larangan karakter emotikon pada UI dan contoh respons.
- **Hasil:** fondasi visual untuk seluruh halaman.
- **Diterima jika:** warna dan karakter pengalaman sesuai brief; aset/font/komponen tambahan berasal dari pilihan yang dicatat.

### T6.2 — Bangun shell SlimRail, Sidebar, chat, dan Inspector

- **Prasyarat:** T6.1; keputusan perangkat dan navigasi.
- **Keputusan:** D-23, D-06.
- **Pekerjaan:**
  - [ ] Bangun `SlimRail.tsx`, Sidebar collapsible, ruang chat, dan panel kanan.
  - [ ] Terapkan navigasi role-aware dan indikator halaman/session aktif.
  - [ ] Terapkan perilaku responsif pada desktop/tablet/mobile yang masuk scope.
  - [ ] Uji keyboard/focus saat panel dibuka/ditutup dan layout saat pesan panjang.
- **Hasil:** workspace responsif yang dapat menampung chat dan sumber.
- **Diterima jika:** area input dan sumber tetap dapat digunakan pada perangkat target; visibility navigasi konsisten dengan role tanpa menggantikan otorisasi backend.

### T6.3 — Bangun halaman login, register, dan pending

- **Prasyarat:** T3.1–T3.3, T5.6, T6.1.
- **Keputusan:** D-05, D-23.
- **Pekerjaan:**
  - [ ] Implementasikan form dan validasi sesuai field identitas terpilih.
  - [ ] Tampilkan pending/approved serta status tambahan yang dipilih.
  - [ ] Tangani expired session, login gagal, identitas duplikat, dan error koneksi.
  - [ ] Implementasikan redirect dan pembaruan status setelah approval sesuai alur session.
- **Hasil:** halaman `(auth)/login`, `(auth)/register`, dan `(auth)/pending` terhubung API.
- **Diterima jika:** pengguna dapat menjalani alur pendaftaran sampai akses setelah approval; frontend tidak memberi akses hanya berdasarkan state lokal.

### T6.4 — Bangun composer percakapan teks/gambar/suara

- **Prasyarat:** T5.2, T5.6, T6.2; T5.4/T5.5 untuk modalitas aktif.
- **Keputusan:** D-19, D-21, D-22, D-23.
- **Pekerjaan:**
  - [ ] Implementasikan `ChatInput.tsx` untuk multiline text, submit, loading, serta cancel bila dipilih.
  - [ ] Tambahkan preview/remove attachment dan progres/error upload gambar bila aktif.
  - [ ] Implementasikan `audio.ts` untuk izin mic, recording, preview/transcript, dan error sesuai API browser yang dipilih.
  - [ ] Tangani batas input, kiriman kosong, upload belum siap, serta retry tanpa menggandakan message.
- **Hasil:** input multimodal sesuai fitur yang benar-benar aktif.
- **Diterima jika:** tiap kontrol memiliki alur end-to-end; kegagalan mic/upload/transkripsi memberikan state yang dapat dipahami.

### T6.5 — Bangun renderer message dan kontrak dinamis

- **Prasyarat:** T4.10, T5.2, T5.6, T6.1.
- **Keputusan:** D-17, D-19, D-23.
- **Pekerjaan:**
  - [ ] Implementasikan `MessageItem.tsx` untuk user message, summary, komponen, sitasi, dan status hasil terpilih.
  - [ ] Map discriminant ke komponen yang sesuai serta dukung cardinality/versioning yang dipilih.
  - [ ] Pisahkan UI partial/loading dari final payload tervalidasi.
  - [ ] Tangani payload tidak dikenal/error tanpa membuat data teknis pengganti.
  - [ ] Render teks/Markdown sesuai aturan format, tanpa mengeksekusi konten sumber sebagai kode.
- **Hasil:** renderer yang konsisten dengan schema backend.
- **Diterima jika:** fixture valid setiap jenis dirender; fixture invalid/unknown tertangani; tidak ada parsing string enum `a | b` sebagai nilai nyata.

### T6.6 — Implementasikan ProcedureChecklist

- **Prasyarat:** T4.10, T6.5.
- **Keputusan:** D-17, D-20, D-23.
- **Pekerjaan:**
  - [ ] Render judul, prasyarat, langkah berurutan, parameter, dan rujukan yang tersedia.
  - [ ] Pisahkan instruksi sumber dari status centang pengguna.
  - [ ] Implementasikan persistensi checklist hanya pada scope/state model yang disepakati.
  - [ ] Tangani refresh, langkah tanpa field opsional, serta revision sumber sesuai keputusan.
- **Hasil:** checklist interaktif dengan sumber langkah yang dapat dibuka.
- **Diterima jika:** urutan/parameter tidak berubah karena interaksi UI; status centang mengikuti kebijakan persistence dan tidak dianggap catatan pekerjaan resmi tanpa definisi produk tersebut.

### T6.7 — Implementasikan InterlockLogicCard

- **Prasyarat:** T4.10, T6.5.
- **Keputusan:** D-17, D-18, D-23.
- **Pekerjaan:**
  - [ ] Render cause, instrument, pembanding, setpoint/unit, effect, dan field logic lain yang disepakati.
  - [ ] Tampilkan kondisi majemuk/voting/delay hanya ketika payload memiliki bukti yang sesuai.
  - [ ] Hubungkan sumber per hubungan atau per tabel sesuai kontrak.
  - [ ] Bedakan unknown/tidak tersedia dari nilai nol/false atau alert normal.
- **Hasil:** kartu C&E yang menjaga makna data teknis.
- **Diterima jika:** angka, unit, hubungan, dan status alert sesuai payload tervalidasi; UI tidak menambahkan logika trip sendiri.

### T6.8 — Implementasikan SparePartBOMTable

- **Prasyarat:** T4.10, T6.5.
- **Keputusan:** D-17, D-18, D-23.
- **Pekerjaan:**
  - [ ] Render kolom BOM terpilih, equipment, drawing/revision, dan citation.
  - [ ] Tangani field tidak tersedia, quantity nol jika benar-benar ada, serta unit yang berbeda.
  - [ ] Terapkan sort/filter/copy/export hanya bila masuk scope.
  - [ ] Pertahankan hubungan row dengan nomor item dan locator sumber saat tabel diurutkan.
- **Hasil:** tabel suku cadang bersumber.
- **Diterima jika:** part number/material/quantity tidak ditambahkan frontend, dan row tetap dapat dilacak setelah interaksi tabel.

### T6.9 — Implementasikan RootCauseCard

- **Prasyarat:** T4.10, T6.5; hasil maintenance relevan.
- **Keputusan:** D-10, D-15, D-17, D-23.
- **Pekerjaan:**
  - [ ] Render kejadian, observasi, sebab tercatat, bukti, serta tindakan sesuai schema.
  - [ ] Pisahkan hipotesis/rekomendasi AI bila dipilih dari fakta sumber.
  - [ ] Tampilkan sumber record/dokumen dan keterbatasan data sesuai kontrak.
  - [ ] Gunakan confidence/alert hanya bila definisi dan nilai yang sah tersedia.
- **Hasil:** kartu RCA dengan asal informasi yang jelas.
- **Diterima jika:** korelasi atau hipotesis tidak terlihat sebagai root cause terkonfirmasi tanpa bukti sesuai kebijakan.

### T6.10 — Implementasikan citation chips dan Inspector

- **Prasyarat:** T3.5, T4.9, T6.2, T6.5.
- **Keputusan:** D-18, D-23.
- **Pekerjaan:**
  - [ ] Render citation chips yang terkait klaim/kartu/row sesuai schema.
  - [ ] Buka PDF pada halaman yang benar dan PNG pada gambar/region sesuai locator terpilih.
  - [ ] Tampilkan judul, revision, kutipan, serta sumber tabular/SQL dengan representasi yang sesuai.
  - [ ] Implementasikan highlight, download, atau navigasi tambahan sesuai pilihan viewer.
  - [ ] Tangani izin berubah, file hilang, halaman tidak valid, dan kegagalan loading.
- **Hasil:** pengguna dapat memeriksa sumber jawaban dari chat.
- **Diterima jika:** chip membuka sumber yang benar melalui API terotorisasi; PNG/SQL tidak diberi halaman PDF atau snippet fiktif.

### T6.11 — Bangun halaman repository pengetahuan

- **Prasyarat:** T3.5, T3.6, T6.1, T6.2.
- **Keputusan:** D-06, D-08, D-23, D-24.
- **Pekerjaan:**
  - [ ] Implementasikan listing/detail, filter equipment/tipe/revision/status sesuai scope.
  - [ ] Hubungkan preview dan download sesuai kewenangan.
  - [ ] Tampilkan status sumber yang belum siap/gagal sesuai keputusan ingestion.
  - [ ] Tangani pagination, empty state, loading, dan perubahan akses.
- **Hasil:** `/knowledge` terhubung katalog aktual.
- **Diterima jika:** data yang tampil sesuai backend dan file yang dapat dibuka konsisten dengan izin pengguna.

### T6.12 — Hubungkan Sidebar dengan history dan lifecycle chat

- **Prasyarat:** T5.1, T6.2, T6.5.
- **Keputusan:** D-20, D-23.
- **Pekerjaan:**
  - [ ] Implementasikan new session, daftar, pencarian, pemilihan, dan tindakan history yang dipilih.
  - [ ] Render pesan tersimpan beserta versi payload/sitasi dan status yang belum selesai.
  - [ ] Tangani refresh, pemindahan session, empty history, delete, dan kehilangan akses.
  - [ ] Pastikan context request berasal dari session yang tepat sesuai ownership.
- **Hasil:** Sidebar dan chat persistence terhubung.
- **Diterima jika:** riwayat dapat dipakai kembali tanpa mencampur user/session atau membuat source reference berubah diam-diam.

## Fase 7 — Admin dan Super Admin

### T7.1 — Bangun approval queue dan pengelolaan pengguna

- **Prasyarat:** T3.2, T3.4, T6.3.
- **Keputusan:** D-05, D-06, D-24.
- **Pekerjaan:**
  - [ ] Implementasikan `/admin/users` dengan daftar pending/detail dan alokasi divisi.
  - [ ] Sediakan tindakan status/role/bulk yang telah dipilih sesuai kewenangan.
  - [ ] Tangani validasi, konflik perubahan, loading, hasil tindakan, dan audit reference.
  - [ ] Verifikasi hasil approval dari sisi user dengan status/session aktual.
- **Hasil:** alur Admin menyetujui dan mengalokasikan pengguna.
- **Diterima jika:** tindakan UI dan API konsisten, termasuk batas Admin terhadap role yang lebih tinggi.

### T7.2 — Bangun upload dan monitor ingestion dokumen

- **Prasyarat:** T2.9, T3.4, T3.6; jalur indeks fitur aktif.
- **Keputusan:** D-08, D-24, D-25.
- **Pekerjaan:**
  - [ ] Implementasikan upload API Admin yang membuat dokumen/job dengan identitas actor.
  - [ ] Bangun `/admin/docs` untuk upload dan metadata equipment/tipe/divisi/revision sesuai policy.
  - [ ] Tampilkan progres/status per tahap, error, dan hasil indexing aktual.
  - [ ] Sediakan retry/cancel/reindex hanya sesuai kewenangan dan kemampuan pipeline terpilih.
  - [ ] Tangani batch, duplikasi, file tidak valid, serta restart jika masuk scope.
- **Hasil:** dokumen baru dapat masuk melalui aplikasi dan statusnya dapat ditelusuri.
- **Diterima jika:** dokumen yang diunggah tersedia pada retrieval hanya sesuai readiness/ACL yang disepakati; UI tidak sekadar mensimulasikan progres.

### T7.3 — Terapkan pengalaman katalog lintas divisi untuk Admin

- **Prasyarat:** T3.6, T6.11; keputusan batas akses Admin.
- **Keputusan:** D-06, D-24.
- **Pekerjaan:**
  - [ ] Gunakan komponen katalog bersama untuk tampilan lintas divisi yang diizinkan.
  - [ ] Bedakan kemampuan melihat metadata, isi, download, dan tindakan administrasi sesuai keputusan.
  - [ ] Tampilkan label divisi/akses dan revision tanpa menyiratkan kewenangan yang tidak dimiliki.
  - [ ] Uji Admin dan User pada sumber yang sama melalui API dan UI.
- **Hasil:** katalog Admin sesuai makna “seluruh divisi” yang telah diputuskan.
- **Diterima jika:** akses isi tidak diperluas otomatis hanya karena Admin dapat melihat judul katalog.

### T7.4 — Implementasikan audit query dan perubahan administratif

- **Prasyarat:** jalur auth/chat/dokumen yang aktif dan actor context.
- **Keputusan:** D-06, D-24, D-27.
- **Pekerjaan:**
  - [ ] Definisikan event/field audit terpilih untuk query dan tindakan administratif.
  - [ ] Catat waktu, actor, scope yang diperlukan, status, serta source/request reference sesuai keputusan.
  - [ ] Implementasikan API dan UI audit dengan filter/pagination serta akses role yang disepakati.
  - [ ] Terapkan aturan penyimpanan prompt/jawaban/data lain dan retensi sesuai pilihan.
  - [ ] Uji keberadaan event pada alur berhasil/gagal dan perlindungan akses audit.
- **Hasil:** audit trail yang dapat digunakan pihak berwenang.
- **Diterima jika:** event aktual dapat ditelusuri ke request/tindakan; field yang tidak dicatat tidak ditampilkan sebagai fakta.

### T7.5 — Implementasikan analitik token, biaya, dan quota terpilih

- **Prasyarat:** usage gateway T4.8 dan pipeline terpilih.
- **Keputusan:** D-04, D-16, D-24.
- **Pekerjaan:**
  - [ ] Catat usage berdasarkan provider/model/tugas dan actor sesuai data yang tersedia.
  - [ ] Agregasikan per user/divisi/periode sebagaimana dipilih.
  - [ ] Jika biaya uang diperlukan, gunakan tarif dengan sumber/tanggal yang dicatat dan bedakan estimasi dari usage aktual.
  - [ ] Implementasikan quota/batas anggaran serta perilaku UI jika dipilih.
  - [ ] Tampilkan dashboard Super Admin untuk metrik yang telah ditetapkan.
- **Hasil:** analitik penggunaan dan biaya yang dapat dijelaskan.
- **Diterima jika:** token, audio, embedding, dan biaya tidak dicampur tanpa unit; usage tidak tersedia tidak otomatis ditampilkan sebagai nol.

### T7.6 — Implementasikan konfigurasi gateway Super Admin

- **Prasyarat:** T4.8, T3.4, audit T7.4.
- **Keputusan:** D-05, D-16, D-24.
- **Pekerjaan:**
  - [ ] Tentukan field runtime-configurable sesuai keputusan: model/provider/routing/limit/parameter lain yang dipilih.
  - [ ] Bangun API dan layar Super Admin dengan validasi nilai serta penyimpanan config yang disepakati.
  - [ ] Terapkan efek perubahan pada request baru/aktif sesuai lifecycle terpilih.
  - [ ] Rekam perubahan dan tangani config/model tidak valid.
  - [ ] Jika key management dipilih, implementasikan penanganan rahasia sesuai desain server-side.
- **Hasil:** konfigurasi gateway yang dapat dikelola Super Admin.
- **Diterima jika:** perubahan aktual tercermin pada gateway dan tercatat; hanya role yang diizinkan dapat mengubahnya; setting environment dan runtime memiliki aturan prioritas jelas.

## Fase 8 — Verifikasi, evaluasi, dan delivery

### T8.1 — Jalankan pengujian terarah untuk integritas sistem

- **Prasyarat:** modul yang akan dirilis tersedia dan keputusan tooling/acceptance.
- **Keputusan:** D-25, D-26.
- **Pekerjaan:**
  - [ ] Satukan pengujian penting yang dibuat bersama modul: auth/ACL, import idempotent, schema, citation, lifecycle indeks, dan SQL.
  - [ ] Uji batas antar-service dengan data terisolasi sesuai strategi yang dipilih.
  - [ ] Gunakan kasus yang memverifikasi kebutuhan/batas perilaku, termasuk kasus negatif yang relevan.
  - [ ] Jalankan lint/type/build/test yang diwajibkan stack dan catat command, lingkungan, serta hasilnya.
  - [ ] Perbaiki kegagalan dan jalankan ulang bagian terkait; perluasan pengujian mengikuti perubahan atau masalah nyata.
- **Hasil:** laporan checks dan bukti integritas modul.
- **Diterima jika:** pemeriksaan relevan lulus dan kegagalan yang tersisa dicatat spesifik; test yang hanya meniru implementasi tidak menggantikan bukti perilaku produk.

### T8.2 — Evaluasi retrieval, graph, grounding, dan kalkulasi

- **Prasyarat:** T0.3, T4.11, sumber/index rilis tersedia.
- **Keputusan:** D-10, D-13, D-14, D-15, D-26.
- **Pekerjaan:**
  - [ ] Jalankan query acuan dengan role/divisi dan konfigurasi yang dicatat.
  - [ ] Nilai retrieval, citation correctness, ketepatan angka/unit/tag, serta dukungan klaim terhadap sumber.
  - [ ] Evaluasi kontribusi hybrid/graph bila diklaim sebagai fitur rilis.
  - [ ] Bandingkan hasil SQL dengan perhitungan acuan dan aturan missing data.
  - [ ] Catat sumber kegagalan: ekstraksi, metadata, retrieval, relasi, kalkulasi, generation, atau UI.
- **Hasil:** laporan evaluasi yang dapat direproduksi dan tindak lanjut terprioritaskan.
- **Diterima jika:** ambang yang disepakati tercapai atau gap dibahas sebagai hasil nyata; tidak ada klaim akurasi tanpa metode dan sampel uji.

### T8.3 — Verifikasi alur end-to-end pengguna dan administrator

- **Prasyarat:** Fase 3–7 untuk fitur rilis tersedia.
- **Keputusan:** D-06, D-17 sampai D-24, D-26.
- **Pekerjaan:**
  - [ ] Uji register → pending → approval → login/access sesuai lifecycle.
  - [ ] Uji query bersumber, empat komponen yang masuk scope, history, dan Inspector PDF/PNG/SQL sesuai kontrak.
  - [ ] Uji upload → ingestion → dokumen dapat dicari oleh user yang sesuai.
  - [ ] Uji input gambar/suara, streaming/cancel/retry, dan kegagalan terpilih.
  - [ ] Uji dashboard serta tindakan Admin/Super Admin pada perangkat/browser target.
- **Hasil:** bukti alur produk, bukan hanya screenshot halaman statis.
- **Diterima jika:** alur utama dapat diselesaikan dan data/status konsisten dari frontend hingga sumber/backend.

### T8.4 — Verifikasi performa dan perilaku kegagalan deployment

- **Prasyarat:** build rilis kandidat; lingkungan uji yang mewakili target.
- **Keputusan:** D-04, D-08, D-16, D-19, D-26, D-27.
- **Pekerjaan:**
  - [ ] Ukur latency awal respons/final, concurrency, waktu ingestion, dan penggunaan resource sesuai target.
  - [ ] Uji restart job/service, provider lambat/tidak tersedia, serta koneksi stream terputus.
  - [ ] Periksa konsistensi indeks/database dan hasil retry setelah kegagalan.
  - [ ] Ukur biaya dengan metode/tarif terpilih serta catat batas lingkungan uji.
- **Hasil:** laporan performa, failure behavior, dan konfigurasi operasi kandidat.
- **Diterima jika:** memenuhi target yang disepakati; hasil lokal tidak dinyatakan sebagai kapasitas produksi tanpa kondisi pengujian yang sesuai.

### T8.5 — Siapkan deployment dan dokumentasi operasional

- **Prasyarat:** konfigurasi rilis, hasil checks terkait, keputusan hosting.
- **Keputusan:** D-02, D-25, D-27.
- **Pekerjaan:**
  - [ ] Implementasikan delivery/CI/CD, build image, environment, domain/proxy sesuai scope rilis.
  - [ ] Dokumentasikan setup, migration, bootstrap, seeding, ingestion, dan cara menjalankan aplikasi dengan command teruji.
  - [ ] Siapkan backup/restore/rollback/retensi sesuai kebutuhan rilis yang dipilih.
  - [ ] Perbarui `.env.example`, API docs, data dictionary, manifest, diagram, dan decision log sesuai implementasi aktual.
  - [ ] Uji startup dari lingkungan bersih dan pemulihan yang termasuk acceptance.
- **Hasil:** aplikasi dapat diserahkan beserta runbook dan konfigurasi contoh.
- **Diterima jika:** pihak penerima dapat menjalankan langkah yang didokumentasikan; tidak ada instruksi yang mengandalkan credential, path, atau service yang tidak dijelaskan.

### T8.6 — Laksanakan UAT dan tutup milestone rilis

- **Prasyarat:** T8.1–T8.5 yang berlaku untuk rilis; validator tersedia.
- **Keputusan:** D-01, D-26, D-27, D-28.
- **Pekerjaan:**
  - [ ] Jalankan demo/UAT berdasarkan use case, role, sumber, dan acceptance yang disepakati.
  - [ ] Rekam hasil validator, issue, keterbatasan aktual, serta keputusan tindak lanjut.
  - [ ] Perbaiki penghambat penerimaan dan verifikasi ulang area terdampak.
  - [ ] Finalkan status task dengan tautan bukti dan pindahkan pekerjaan tertunda ke rilis berikutnya melalui keputusan scope.
  - [ ] Serahkan artefak proyek serta rangkuman konteks untuk kelanjutan sesi/tim.
- **Hasil:** keputusan penerimaan rilis dan dokumentasi kondisi aktual.
- **Diterima jika:** fitur yang diklaim tersedia mempunyai bukti; pekerjaan yang belum terverifikasi tidak ditandai selesai.

## 3. Pemetaan kebutuhan ke paket kerja

| Kebutuhan | Task utama |
| --- | --- |
| F-01 Registrasi/approval | T3.1–T3.3, T6.3, T7.1 |
| F-02 RBAC | T2.4, T3.4–T3.7, T2.10 dan penerapan scope pada setiap jalur retrieval |
| F-03 Repository | T3.5, T3.6, T6.10, T6.11, T7.3 |
| F-04 Ingestion/import | T0.2, T2.1–T2.10, T7.2 |
| F-05 Hybrid | T4.1, T4.2, T8.2 |
| F-06 Graph | T4.3–T4.5, T8.2 |
| F-07 JSON AI | T4.8–T4.11, T5.6, T6.5 |
| F-08 Rich UI | T4.10, T6.6–T6.9 |
| F-09 Citation/Inspector | T3.5, T4.9, T6.10 |
| F-10 Maintenance analytics | T2.2, T2.3, T4.6, T8.2 |
| F-11 Chat/history/streaming | T5.1–T5.3, T6.4, T6.5, T6.12 |
| F-12 Gambar/suara | T5.4, T5.5, T6.4 |
| F-13 Administrasi pengguna | T3.2, T7.1 |
| F-14 Administrasi dokumen | T2.9, T2.10, T7.2, T7.3 |
| F-15 Super Admin | T1.6, T7.4–T7.6 |

## 4. Jalur dependensi utama

```text
Scope dan audit sumber
  -> keputusan fondasi + acceptance + kontrak slice
  -> runtime/config/schema
  -> manifest + mapping ACL + import/ekstraksi
  -> dense/lexical/graph/SQL sesuai scope
  -> context assembly + gateway + schema + citation validation
  -> chat transport/persistence
  -> rich UI + Inspector + admin
  -> evaluasi + deployment + UAT
```

Desain UI dan schema dapat dikerjakan ketika keputusan terkait sudah tersedia; integrasi baru dianggap selesai setelah API dan sumber aktual terhubung. Task tidak memerlukan seluruh pertanyaan proyek dijawab sekaligus, tetapi dependensi lokalnya harus jelas.

## 5. Checklist penutupan setiap task

- [ ] Keputusan yang diperlukan sudah dicatat, termasuk perubahan baseline.
- [ ] Hasil kerja berada di lokasi/modul yang konsisten dengan repo.
- [ ] Kriteria penerimaan task memiliki bukti pemeriksaan yang relevan.
- [ ] Perubahan akses/kontrak/data diikuti penyesuaian jalur terkait.
- [ ] Fakta, sumber, usulan, dan keterbatasan masih dibedakan dengan jelas.
- [ ] Dokumentasi serta penghambat/tindak lanjut diperbarui.
- [ ] Status selesai hanya digunakan untuk pekerjaan yang benar-benar telah diverifikasi.
