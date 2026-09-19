# 06 — Pertanyaan yang Perlu Kita Putuskan Bersama

## Cara menjawab

Seluruh pertanyaan di sini **TERBUKA** pada versi awal. Pernyataan pada brief tetap menjadi baseline; pertanyaan meminta konfirmasi, rincian yang hilang, atau penyelesaian gap yang ditemukan.

- Jawab menggunakan ID, misalnya `Q-SCP-01: demo hackathon`.
- Untuk pilihan teknis, boleh menjawab **minta rekomendasi dengan trade-off**. Rekomendasi nantinya tetap dicatat sebagai usulan sampai disepakati.
- Tidak harus menjawab semuanya sekaligus. Dahulukan pertanyaan pembuka, kemudian kelompok yang menjadi dependensi fitur berikutnya.
- Pertanyaan baru dapat muncul setelah workbook, slide deck, dan dokumen teknis diperiksa. Pertanyaan itu harus ditambahkan dengan bukti konteksnya.
- Jawaban yang baru menyelesaikan sebagian topik tidak otomatis menutup seluruh keputusan D-xx.

### Prioritas

| Kode | Kapan diperlukan |
| --- | --- |
| P0 | Untuk menetapkan arah, scope awal, dan fondasi sebelum implementasi terkait dimulai |
| P1 | Sebelum membangun fitur/kontrak yang bersangkutan |
| P2 | Sebelum evaluasi, deployment, atau penyerahan sesuai jenis rilis; dapat dipercepat bila memengaruhi arsitektur |

## Pertanyaan pembuka

Ini adalah urutan diskusi awal yang diusulkan, bukan jawaban default:

1. **Tahap dan tenggat:** proyek ini ditujukan untuk demo/hackathon, PoC, pilot internal, atau produksi; kapan harus siap? `Q-SCP-01`, `Q-SCP-02`.
2. **Scope rilis pertama:** fitur mana yang wajib masuk; apa tiga alur demo/penggunaan terpenting? `Q-SCP-04`, `Q-SCP-05`.
3. **Tim dan cara kerja:** siapa yang membangun dan apakah setelah dokumentasi saya juga mengimplementasikan kode? `Q-SCP-03`, `Q-WORK-01`.
4. **Stack:** apakah stack dalam brief wajib persis atau boleh ditinjau dengan alasan dan trade-off? `Q-STK-01`.
5. **Repo dan data:** aplikasi ditempatkan di root workspace atau subfolder; bagaimana lokasi dataset dijadikan konfigurasi? `Q-REP-01`, `Q-REP-02`.
6. **Deployment dan biaya:** dijalankan di mana, resource apa tersedia, dan berapa anggaran API/hosting? `Q-DEP-01` sampai `Q-DEP-03`.
7. **Sumber dan provider:** apa acuan requirement tertinggi, dan data apa yang boleh diproses provider eksternal? `Q-DATA-01`, `Q-DEP-04`.
8. **RBAC:** satu atau banyak divisi per user; apakah Admin boleh membaca isi semua divisi? `Q-RBAC-01`, `Q-RBAC-02`.
9. **Hybrid dan graph:** harus berfungsi pada rilis pertama, dan pertanyaan apa yang harus dibantu graph? `Q-HYB-01`, `Q-GRF-01`.
10. **Kontrak AI:** apakah boleh respons teks biasa, beberapa equipment, beberapa kartu, serta hasil SQL? `Q-JSON-01`, `Q-JSON-02`.
11. **Multimodal dan UI:** apakah gambar/suara wajib pada rilis pertama; bahasa serta perangkat utama apa? `Q-IMG-01`, `Q-VOC-01`, `Q-UI-01`, `Q-UI-03`.
12. **Ukuran keberhasilan:** siapa pemeriksa teknis dan contoh pertanyaan bersumber apa yang menjadi acceptance? `Q-QA-01`, `Q-QA-02`.

## A. Tujuan, scope, dan delivery — D-01

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-SCP-01 | P0 | Apa target rilis pertama: demo/hackathon, PoC, pilot internal, atau aplikasi produksi? Siapa pengguna/audiens rilis itu? |
| Q-SCP-02 | P0 | Kapan deadline dan milestone yang sudah mengikat? Apa bentuk penyerahan yang diwajibkan oleh penyelenggara/tim/stakeholder? |
| Q-SCP-03 | P0 | Berapa orang dalam tim, apa peran/kemampuan mereka, dan berapa kapasitas waktu yang tersedia? |
| Q-SCP-04 | P0 | Untuk F-01 sampai F-15 pada konteks proyek, mana yang wajib pada rilis pertama dan mana yang dijadwalkan kemudian? Khususnya auth/RBAC, repository, empat kartu, hybrid, graph, SQL, streaming, gambar, suara, dan dashboard Super Admin. |
| Q-SCP-05 | P0 | Apa tiga sampai lima pertanyaan atau alur kerja yang paling penting untuk diperagakan/diselesaikan pengguna? Equipment/divisi mana yang diprioritaskan? |
| Q-SCP-06 | P1 | Apakah ada integrasi sistem lain atau kebutuhan di luar brief yang benar-benar menjadi scope? Jika ada, sistem, data, dan arah integrasinya apa? |

## B. Workspace, repository, dan lokasi data — D-02

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-REP-01 | P0 | Apakah monorepo aplikasi menggunakan root `Caliber2026`, atau dibuat di subfolder `manufacturing-knowledge-hub/`? |
| Q-REP-02 | P0 | Apakah dataset tetap di `supporting_data/` lalu dibaca melalui konfigurasi/mount, atau harus memiliki layout `scripts/data/` seperti brief? Apakah ada batasan penggandaan/penyimpanan file? |
| Q-REP-03 | P1 | Apakah sudah ada repository remote, aturan branch, penamaan, dan file proyek lain yang harus menjadi acuan? |

## C. Baseline stack dan versi — D-03

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-STK-01 | P0 | Apakah Next.js 14, FastAPI, PostgreSQL 16, Qdrant, PyMuPDF, pandas, model embedding, dan `gpt-4o` pada brief merupakan ketentuan wajib atau rancangan awal yang boleh ditinjau? |
| Q-STK-02 | P1 | Apakah ada versi runtime/library yang diwajibkan? Jika tidak, apakah Anda ingin rekomendasi pin Python, Node.js, Next.js/React, Tailwind, ORM, dan Qdrant setelah pemeriksaan kompatibilitas? |
| Q-STK-03 | P1 | Adakah preferensi package manager dan lockfile untuk Python serta frontend, atau pilih berdasarkan reproducibility dan kebiasaan tim? |
| Q-STK-04 | P0 | Apakah empat container pada brief adalah batas mutlak, atau boleh bertambah bila graph, storage, atau ingestion membutuhkan service terpisah? |

## D. Lingkungan, kapasitas, dan biaya — D-04

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-DEP-01 | P0 | Rilis pertama dijalankan di laptop lokal, server internal/intranet, VPS, atau layanan cloud tertentu? Apa OS dan tooling yang tersedia, termasuk Docker/WSL bila relevan? |
| Q-DEP-02 | P0 | Berapa CPU, RAM, storage, dan GPU jika ada; berapa jumlah user total/concurrent serta proyeksi pertumbuhan dokumen? |
| Q-DEP-03 | P0 | Berapa anggaran hosting dan API untuk pembangunan, demo, dan operasi? Adakah batas biaya per user/hari/bulan atau per query? |
| Q-DEP-04 | P0 | Apakah dokumen, kutipan, gambar, audio, dan log pengguna boleh dikirim ke OpenAI/OpenRouter/provider lain? Jika hanya sebagian, jenis data dan provider yang diizinkan apa? |
| Q-DEP-05 | P1 | Bagaimana ketersediaan internet dari lingkungan target? Apakah ada kebutuhan berjalan saat koneksi/provider tidak tersedia, dan fitur apa yang tetap diperlukan? |

## E. Akun, autentikasi, dan session — D-05

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-AUTH-01 | P1 | Identitas login berupa email, username, employee ID, atau integrasi identitas perusahaan? Apakah email/password JWT dari brief cukup untuk rilis pertama? |
| Q-AUTH-02 | P1 | Field registrasi apa yang wajib? Apakah user boleh meminta divisi saat daftar, dan informasi mana yang ditetapkan hanya oleh Admin? |
| Q-AUTH-03 | P1 | Selain `pending` dan `approved`, apakah diperlukan rejected/disabled/suspended? Apa alur revisi pendaftaran, approval ulang, penonaktifan, dan notifikasinya? |
| Q-AUTH-04 | P0 | Bagaimana akun Super Admin pertama disediakan, dan siapa yang berwenang membuat Admin/Super Admin berikutnya? |
| Q-AUTH-05 | P1 | Bagaimana masa berlaku access token, refresh, logout, revocation, dan session ketika role/divisi/status berubah? Apakah bearer token pada brief wajib; bagaimana token disimpan/ditransport di browser? |
| Q-AUTH-06 | P1 | Apakah perlu verifikasi email, reset/change password, kebijakan password, serta pembatasan percobaan login? Library/algoritma hashing dapat saya rekomendasikan jika belum ada standar tim. |

## F. Role, divisi, dan batas akses — D-06

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-RBAC-01 | P0 | Satu user mempunyai satu atau beberapa divisi? Untuk multi-divisi, apakah akses merupakan gabungan hak masing-masing divisi atau memakai aturan lain? |
| Q-RBAC-02 | P0 | Akses Admin ke katalog seluruh divisi mencakup metadata saja, atau juga membaca file, download, chat, graph, dan analitik lintas divisi? |
| Q-RBAC-03 | P1 | Apakah Admin dapat mengubah role, memindahkan divisi, menonaktifkan user, melihat audit, dan menghapus dokumen; tindakan mana yang khusus Super Admin? |
| Q-RBAC-04 | P0 | Hak akses ditetapkan per dokumen, per chunk/halaman, per jenis dokumen, atau kombinasi? Jika satu dokumen memuat bagian terbatas, bagaimana akses ke file asli di Inspector? |
| Q-RBAC-05 | P1 | Siapa yang menetapkan `division_access`, bagaimana dokumen bersama ditandai, dan apa perilaku ketika label divisi tidak ada atau ambigu? |
| Q-RBAC-06 | P1 | Bagaimana maintenance record dibatasi per divisi? Adakah field sumber yang dapat dipakai, dan apakah agregat lintas divisi boleh terlihat? |
| Q-RBAC-07 | P1 | Bagaimana izin berlaku pada node/edge graph, hasil pencarian metadata, attachment, dan chat lama ketika akses pengguna atau sumber berubah? |
| Q-RBAC-08 | P1 | Apakah empat divisi tetap, atau Super Admin perlu menambah/mengubah divisi? Apakah ada kebutuhan lebih dari satu plant/proyek/tenant pada scope ini? |

## G. Otoritas dan pemetaan sumber — D-07

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-DATA-01 | P0 | Jika brief dan slide `Data Set Explanation...pptx` berbeda, mana acuan yang berlaku? Apakah ada dokumen requirement/rubrik lain yang harus dibaca? |
| Q-DATA-02 | P0 | Apakah delapan set dan workbook yang tersedia merupakan dataset lengkap untuk rilis pertama? Apakah PPTX ikut menjadi sumber jawaban atau hanya konteks proyek? |
| Q-DATA-03 | P1 | Adakah kamus equipment/instrument/interlock, mapping tipe dokumen-divisi, dan daftar revision resmi? Jika belum, siapa sumber konfirmasi mapping setelah audit dokumen? |
| Q-DATA-04 | P1 | Informasi safety matrix, SIL, dan RCA yang disebut brief berada di dokumen/kolom mana? Apakah ada file tambahan yang belum berada di workspace? |

## H. Dokumen, storage, dan ingestion lifecycle — D-08

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-DOC-01 | P1 | Format upload Admin apa yang didukung pada rilis pertama, berapa ukuran/jumlah file maksimal, dan apakah upload folder/batch diperlukan? |
| Q-DOC-02 | P1 | File asli dan attachment disimpan di volume filesystem atau object storage? Siapa yang boleh preview/download/export sumber? |
| Q-DOC-03 | P1 | Bagaimana dokumen baru, revision pengganti, arsip, penghapusan, dan perubahan ACL diperlakukan? Apakah jawaban lama tetap menunjuk revision lama? |
| Q-DOC-04 | P1 | Ingestion dijalankan sebagai proses backend, CLI, worker, atau antrean? Apa kebutuhan progres, retry, pembatalan, dan recovery setelah restart? |
| Q-DOC-05 | P1 | Bagaimana file duplikat dan import ulang ditangani: identik, isi berubah dengan nama sama, metadata berubah, atau dokumen sama di set berbeda? |
| Q-DOC-06 | P1 | Kapan dokumen dianggap siap dicari: setelah seluruh dense/lexical/graph selesai atau boleh parsial? Bagaimana kegagalan sebagian dan query saat reindex ditampilkan? |

## I. Workbook maintenance dan seeding — D-09

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-MNT-01 | P1 | Sheet/rentang mana yang menjadi sumber resmi? Apakah angka 211 record dan 31 kolom sudah pernah diverifikasi, dan apa acuan jika hasil audit berbeda? |
| Q-MNT-02 | P1 | Setelah header dibaca, apakah schema SQL harus mempertahankan seluruh nama/nilai asli, atau boleh memakai kolom normalisasi dengan mapping dan salinan nilai asli? |
| Q-MNT-03 | P1 | Apa aturan untuk tanggal, satuan, formula, cell kosong, row invalid, serta duplikasi? Adakah ID record resmi dan definisi satu kejadian maintenance? |
| Q-MNT-04 | P1 | Import ulang bersifat replace, append, atau update berdasarkan identitas record? Apakah lineage workbook/sheet/row dan laporan rekonsiliasi wajib tersedia di UI atau cukup artefak pipeline? |

## J. Analitik maintenance dan Text-to-SQL — D-10

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-SQL-01 | P1 | Hitungan/KPI apa yang benar-benar dibutuhkan? Untuk setiap metrik, apa formula, kolom sumber, unit, rentang waktu, timezone, dan aturan nilai kosongnya? |
| Q-SQL-02 | P1 | Apakah pertanyaan dibatasi pada query template/semantic layer, atau perlu SQL dinamis dari model? Adakah library/pendekatan yang diwajibkan? |
| Q-SQL-03 | P1 | Tabel, kolom, operasi agregasi, serta batas jumlah hasil/waktu eksekusi apa yang boleh dipakai jalur analitik baca-saja? |
| Q-SQL-04 | P1 | Hasil numerik disajikan sebagai narasi, tabel generik, kartu KPI, atau bentuk lain? Apakah pengguna perlu melihat formula/filter/query dan membuka record pembentuk hasil? |
| Q-SQL-05 | P1 | Bagaimana sumber dan hasil perhitungan diverifikasi, termasuk pembulatan, unit conversion, dan hasil tanpa record? Siapa yang mengesahkan definisi metrik? |

## K. Ekstraksi PDF, PNG, tabel, dan plot plan — D-11

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-EXT-01 | P1 | Apakah sudah ada informasi tentang PDF teks versus scan dan kualitas tabelnya, atau metode ekstraksi dipilih setelah audit sampel tiap jenis dokumen? |
| Q-EXT-02 | P0 | Untuk P&ID PNG, kemampuan yang dibutuhkan apa: melihat gambar, mencari label/tag, membaca isi diagram, atau menelusuri konektivitas dan relasi otomatis? |
| Q-EXT-03 | P1 | Seberapa terstruktur hasil GA/BOM, datasheet, dan C&E harus disimpan? Field, hubungan row/column, simbol, pembanding, serta satuan apa yang wajib dipertahankan? |
| Q-EXT-04 | P1 | Plot plan digunakan untuk preview/lokasi relatif, atau perlu koordinat, jarak, arah, dan navigasi spasial? Jika menghitung, sumber skala/koordinat otoritatifnya apa? |
| Q-EXT-05 | P1 | Adakah preferensi/batasan OCR lokal, layanan OCR, atau vision model? Bagaimana prioritas biaya, kualitas, waktu proses, dan akses provider? |
| Q-EXT-06 | P1 | Bagaimana hasil ekstraksi yang ambigu ditampilkan/disimpan, dan siapa yang dapat memvalidasi sampel tag, angka, BOM, maupun hubungan interlock? |

## L. Chunking, metadata, dan embedding — D-12

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-IDX-01 | P1 | Apakah ada aturan pemisahan berdasarkan halaman, heading, prosedur utuh, tabel, atau region diagram? Apakah ukuran/overlap chunk dipilih melalui evaluasi sampel? |
| Q-IDX-02 | P1 | Bagaimana equipment/instrument tag dinormalisasi, termasuk tanda hubung, underscore, case, alias, typo, dan tag terkait di luar equipment utama folder? |
| Q-IDX-03 | P1 | Apa enum `doc_type`, format `division_access`, identitas sumber/revision/chunk, dan locator halaman/gambar yang disepakati? Siapa yang menjaga kamus metadata? |
| Q-IDX-04 | P1 | Apakah `text-embedding-3-small` wajib? Dimensi, distance metric, collection/index version, batching, dan aturan re-embedding ketika model/config berubah perlu dipilih dengan batas biaya apa? |

## M. Hybrid search — D-13

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-HYB-01 | P0 | Apakah dense + lexical/exact-match retrieval harus benar-benar berfungsi pada rilis pertama? Query apa yang harus membuktikan manfaat hybrid? |
| Q-HYB-02 | P1 | Lexical index akan memakai sparse retrieval Qdrant, PostgreSQL full-text, atau pendekatan lain? Apakah ada pembatasan service/library? |
| Q-HYB-03 | P1 | Apakah fusion, top-k, threshold, dan reranker dipilih berdasarkan evaluasi, atau sudah ada ketentuan? Adakah target latency/biaya yang membatasi reranking? |
| Q-HYB-04 | P1 | Filter equipment, tipe dokumen, revision, rentang waktu, serta exact tag matching seperti apa yang diperlukan selain filter akses divisi? |

## N. Graph-augmented RAG — D-14

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-GRF-01 | P0 | Apakah graph retrieval wajib pada rilis pertama? Berikan contoh pertanyaan yang membutuhkan relasi equipment–instrument–interlock atau lintas equipment. |
| Q-GRF-02 | P1 | Graph disimpan sebagai tabel relasi PostgreSQL, graph database seperti Neo4j, atau pilihan lain? Adakah kebutuhan traversal yang menentukan pilihan ini? |
| Q-GRF-03 | P1 | Node/edge apa yang diperlukan, apa arah/makna relasinya, dan bagaimana `Related_Interlock` direpresentasikan? Apakah dokumen dan maintenance record juga menjadi node? |
| Q-GRF-04 | P1 | Relasi berasal dari mapping resmi, penandaan manual, ekstraksi otomatis, atau kombinasi? Bagaimana setiap edge menyimpan bukti dan menangani hubungan yang belum pasti? |
| Q-GRF-05 | P1 | Berapa kedalaman/jumlah hasil traversal, bagaimana hasil graph digabung ke ranking, serta bagaimana revision, ACL, dan bukti yang bertentangan memengaruhi edge? |

## O. Orkestrasi RAG dan grounding — D-15

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-RAG-01 | P1 | Bagaimana memilih jalur dokumen, SQL, graph, atau kombinasi? Adakah query tertentu yang selalu harus diarahkan ke sumber tertentu? |
| Q-RAG-02 | P0 | Saat sumber tidak cukup, pertanyaan ambigu, atau di luar dataset, apakah AI meminta klarifikasi, menyatakan bukti tidak tersedia, atau boleh menambah pengetahuan umum yang diberi label? |
| Q-RAG-03 | P1 | Jika dokumen saling berbeda atau revision tidak jelas, sumber mana yang diprioritaskan dan bagaimana perbedaannya ditampilkan? |
| Q-RAG-04 | P1 | Bolehkah AI melakukan inferensi, konversi satuan, dan saran teknis; bagaimana membedakan fakta sumber, perhitungan, hipotesis, serta data yang belum tersedia? |
| Q-RAG-05 | P1 | Berapa konteks percakapan/sumber yang digunakan dan bagaimana prioritas pemotongannya? Apakah prompt/routing perlu dapat dikonfigurasi per proyek/divisi? |

## P. Model dan gateway — D-16

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-LLM-01 | P0 | Apakah `gpt-4o` wajib, atau model dipilih setelah membandingkan kualitas, structured output, multimodal, latency, dan biaya? Adakah API account/model yang sudah tersedia? |
| Q-LLM-02 | P1 | Apa peran masing-masing OpenAI dan OpenRouter: provider utama, alternatif manual, routing per tugas, atau fallback otomatis? Apakah keduanya harus aktif? |
| Q-LLM-03 | P1 | Apakah generation, vision, graph extraction, dan transkripsi memakai model berbeda? Siapa yang menetapkan daftar provider/model yang boleh digunakan? |
| Q-LLM-04 | P1 | Berapa timeout, retry, limit token/context, rate/concurrency, dan quota yang diinginkan? Bagaimana UI menangani provider gagal, rate limit, atau budget habis? |

## Q. Kontrak JSON dan rich component — D-17

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-JSON-01 | P0 | Apakah kontrak boleh memuat respons teks saja dan tipe tambahan untuk spesifikasi/hasil SQL? Apa bentuk jawaban jika empat rich component tidak cocok? |
| Q-JSON-02 | P0 | Apakah satu respons bisa membahas banyak equipment dan menampilkan beberapa kartu? Jika ya, bagaimana urutan dan keterkaitan kartu dengan equipment/sitasi? |
| Q-JSON-03 | P1 | Apa schema untuk insufficient evidence, klarifikasi, konflik sumber, dan hasil kosong? Apakah status hasil dipisahkan dari error sistem? |
| Q-JSON-04 | P1 | Apakah perlu `schema_version`, field nullable, dan kompatibilitas history? Bagaimana enum/requiredness serta tipe backend–frontend dijaga konsisten? |
| Q-JSON-05 | P1 | Untuk checklist, field apa yang wajib, apakah langkah boleh disederhanakan dari sumber, dan apakah status centang disimpan per user/session/pekerjaan? |
| Q-JSON-06 | P1 | Untuk interlock, field apa yang wajib: cause, instrument, operator, setpoint/unit, voting, delay, effect, reset, dan citation per hubungan? Bagaimana field yang tidak tersedia ditampilkan? |
| Q-JSON-07 | P1 | Untuk BOM, kolom apa yang wajib, bagaimana quantity/unit/part number/material ditampilkan, serta bagaimana menangani drawing yang tidak memiliki BOM? |
| Q-JSON-08 | P1 | Untuk RCA, apakah hanya menampilkan sebab yang tercatat atau juga hipotesis/rekomendasi AI? Apa label dan bukti pembeda, serta apakah confidence score memang diperlukan? |
| Q-JSON-09 | P1 | Apa dasar `normal/warning/critical` dan apakah field alert wajib pada semua komponen? Bagaimana menyatakan severity tidak diketahui atau tidak relevan? |

## R. Sitasi dan Inspector — D-18

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-CIT-01 | P1 | Apakah `file_path` harus dipertahankan, atau kontrak boleh memakai identitas dokumen/revision dan URL yang diselesaikan backend? Apa perilaku preview/download yang dibutuhkan? |
| Q-CIT-02 | P1 | Sitasi cukup per pesan, atau harus terkait klaim, kartu, langkah, row BOM, dan edge interlock tertentu? |
| Q-CIT-03 | P1 | Bagaimana rujukan PNG, region diagram, row Excel, dan agregasi SQL direpresentasikan tanpa mengarang nomor halaman atau kutipan kalimat? |
| Q-CIT-04 | P1 | Definisi kutipan eksak mengacu ke teks dokumen visual, hasil ekstraksi mentah, atau normalisasi? Apakah perlu highlight region dan pembeda teks hasil OCR? |
| Q-CIT-05 | P1 | Nomor halaman memakai posisi PDF atau nomor tercetak? Bagaimana sitasi lama ditampilkan jika revision berubah, file dihapus, atau pengguna kehilangan akses? |

## S. Streaming dan error contract — D-19

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-STR-01 | P1 | Apakah streaming wajib pada rilis pertama? Jika ya, ada preferensi SSE, WebSocket, atau transport lain sesuai deployment? |
| Q-STR-02 | P1 | Apa yang ditampilkan bertahap: progres retrieval, teks narasi, atau komponen parsial? Kapan objek JSON dianggap final dan boleh disimpan/dirender penuh? |
| Q-STR-03 | P1 | Bagaimana schema error, timeout, output invalid, disconnect, cancel, retry, dan resume? Apa yang tersimpan ketika generation terhenti? |

## T. Session, history, dan attachment — D-20

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-CHAT-01 | P1 | Fitur history mana yang wajib: membuat session, judul otomatis/manual, rename, search, delete, export, atau sharing? Siapa yang boleh mengakses percakapan selain pemilik dan kewenangan Super Admin dari brief? |
| Q-CHAT-02 | P1 | Data chat apa yang disimpan: prompt, final JSON, teks parsial, retrieved context, citation snapshot/reference, attachment, usage, dan konfigurasi model? |
| Q-CHAT-03 | P1 | Bagaimana multi-turn context menangani pertanyaan lanjutan, perpindahan equipment, konteks terlalu panjang, serta sumber yang tidak lagi boleh diakses? |
| Q-CHAT-04 | P1 | Attachment hanya berlaku untuk satu pesan/session atau bisa menjadi pengetahuan bersama? Bagaimana kepemilikan, masa simpan, penghapusan, dan hubungan dengan dokumen Admin? |

## U. Input gambar — D-21

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-IMG-01 | P0 | Apakah attachment gambar wajib pada rilis pertama? Tujuannya membaca screenshot/drawing, mengenali label equipment, menjelaskan foto kondisi, atau mencari dokumen terkait? |
| Q-IMG-02 | P1 | Format, ukuran, resolusi, dan jumlah gambar per pesan apa yang didukung? Apakah input kamera langsung dibutuhkan? |
| Q-IMG-03 | P1 | Apakah tag yang dibaca dari gambar perlu dikonfirmasi pengguna sebelum retrieval ketika hasilnya ambigu? Bagaimana UI menampilkan batas informasi gambar? |
| Q-IMG-04 | P1 | Model/metode vision mana yang dipakai, apakah isi gambar bisa masuk indeks, dan aturan penyimpanan serta aksesnya bagaimana? |

## V. Input suara — D-22

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-VOC-01 | P0 | Apakah suara wajib pada rilis pertama? Setelah transkripsi, pengguna mengedit/menyetujui teks sebelum mengirim atau langsung menjadi pertanyaan? |
| Q-VOC-02 | P1 | Bahasa/dialek apa yang didukung, apakah campuran Indonesia–Inggris, dan seberapa penting transkripsi di lingkungan bising serta pembacaan equipment tag? |
| Q-VOC-03 | P1 | Browser, format audio, batas durasi/ukuran, preview, serta perilaku izin mic/cancel/retry apa yang diperlukan? |
| Q-VOC-04 | P1 | Speech-to-text menggunakan provider/model apa, dan apakah audio mentah disimpan? Apakah output suara/TTS juga termasuk scope, mengingat brief baru menyebut input suara? |

## W. UI, bahasa, dan interaksi — D-23

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-UI-01 | P0 | Bahasa UI dan jawaban AI apa: Indonesia, Inggris, atau mengikuti pengguna? Bagaimana istilah teknis asli, angka, tanggal, timezone, dan satuan ditampilkan? |
| Q-UI-02 | P1 | Apakah ada screenshot/Figma/referensi Gemini tertentu, logo, font, dan panduan brand yang harus dipakai selain dua warna dan larangan emotikon pada brief? |
| Q-UI-03 | P0 | Perangkat/browser utama apa: desktop control room, laptop, tablet, atau ponsel? Saat ruang sempit, bagaimana prioritas Sidebar, chat, dan Inspector? |
| Q-UI-04 | P1 | Adakah preferensi UI library, icon set, PDF viewer, dan komponen tabel? Apakah hanya light theme yang dibutuhkan pada rilis pertama? |
| Q-UI-05 | P1 | Interaksi selain centang apa yang dibutuhkan pada rich component: expand/collapse, sort/filter, copy, atau export? Mana yang menyimpan state? |
| Q-UI-06 | P1 | Apa kebutuhan keyboard navigation, focus, screen reader, ukuran teks/kontras, serta empty/loading/error state? Siapa yang meninjau copy dan contoh prompt awal? |

## X. Admin, Super Admin, audit, dan usage — D-24

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-ADM-01 | P1 | Apakah approval/alokasi divisi perlu bulk action, pencarian/filter, alasan keputusan, notifikasi, dan histori perubahan? |
| Q-ADM-02 | P1 | Informasi apa yang wajib pada katalog dan monitor ingestion: revision, ACL, equipment, jumlah halaman/chunk, status dense/lexical/graph, error, retry, atau biaya? |
| Q-ADM-03 | P1 | Audit mencatat prompt saja, jawaban, sumber yang diakses, perubahan akun/dokumen, konfigurasi model, atau seluruhnya? Field apa yang dapat dilihat setiap role? |
| Q-ADM-04 | P1 | Analitik token dikelompokkan per user/divisi/model/periode apa? Apakah perlu biaya uang, usage embedding/vision/audio, kuota, dan ekspor; apa sumber tarifnya? |
| Q-ADM-05 | P1 | Konfigurasi gateway yang dapat diubah Super Admin mencakup apa: provider, model, routing/fallback, limit, prompt, atau API key? Kapan perubahan berlaku dan bagaimana direkam? |

## Y. Konvensi engineering dan API — D-25

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-ENG-01 | P1 | Apa prefix/version API, format error, pagination/filter, request ID, dan strategi berbagi tipe backend–frontend? Adakah konvensi tim yang wajib? |
| Q-ENG-02 | P1 | Adakah preferensi SQLAlchemy sync/async, driver database, migration tool, konfigurasi connection pool, dan cara bootstrap data? |
| Q-ENG-03 | P1 | Framework test backend/frontend/E2E, formatter/linter, type checking, serta pemeriksaan build apa yang digunakan? Boleh dipilih berdasarkan stack final? |
| Q-ENG-04 | P1 | Bagaimana base URL frontend/backend, origin CORS, service health/readiness, dan konfigurasi dev/test/deployment ditentukan? |

## Z. Evaluasi dan acceptance — D-26

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-QA-01 | P0 | Pertanyaan uji dan sumber jawaban acuan apa yang paling penting? Adakah rubrik/demo script dari stakeholder atau penyelenggara? |
| Q-QA-02 | P0 | Siapa validator teknis untuk prosedur, interlock, BOM, RCA, dan hitungan maintenance? Siapa yang memutuskan hasil UAT diterima? |
| Q-QA-03 | P1 | Metrik dan ambang lulus apa untuk retrieval, citation correctness, grounding, JSON validity, akurasi hitungan, serta akses lintas role/divisi? |
| Q-QA-04 | P1 | Apa target latency awal stream/jawaban akhir, concurrency, waktu ingestion, dan batas biaya evaluasi? Bagaimana kondisi uji ditetapkan? |
| Q-QA-05 | P1 | Data uji boleh memakai sumber asli, salinan terisolasi, atau fixture sintetis berlabel? Berapa cakupan equipment, jenis dokumen, role, dan kasus gagal yang diperlukan? |

## AA. Deployment, retensi, dan handover — D-27

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-OPS-01 | P2 | Lingkungan dev/test/demo/prod apa yang diperlukan; siapa pemilik domain, konfigurasi HTTPS/reverse proxy, credential deployment, dan akses operasi? |
| Q-OPS-02 | P2 | Apa kebutuhan backup/restore PostgreSQL, Qdrant, sumber asli, dan attachment? Adakah target pemulihan, prosedur rollback, serta batas kehilangan data yang sudah ditetapkan? |
| Q-OPS-03 | P2 | Berapa retensi dokumen/revision, chat, gambar, audio, audit query, usage, dan hasil ekstraksi? Bagaimana perubahan/penghapusan merambat ke indeks dan backup? |
| Q-OPS-04 | P2 | CI/CD, container registry, monitoring/notifikasi error, serta release workflow apa yang dipakai? Siapa yang menjalankan rilis? |
| Q-OPS-05 | P2 | Artefak handover apa yang dibutuhkan: source code, dokumentasi API, data dictionary, manifest, runbook, demo script, hasil evaluasi, atau materi presentasi? |

## AB. Cara kerja supervisor — D-28

| ID | Prioritas | Pertanyaan |
| --- | --- | --- |
| Q-WORK-01 | P0 | Setelah dokumentasi dan keputusan awal, apakah saya juga mengerjakan implementasi, menyiapkan instruksi untuk developer lain, atau fokus review/supervisi? |
| Q-WORK-02 | P1 | Siapa pengambil keputusan produk, teknis, dan validasi domain; bagaimana task ditugaskan dan keputusan parsial dilaporkan? |
| Q-WORK-03 | P1 | Apakah susunan dokumen ini cukup sebagai sumber konteks lintas sesi, dan adakah format progress/estimasi/decision log yang diwajibkan tim? |

## Template jawaban awal

Isi bagian yang sudah diketahui; nilai kosong tetap **TERBUKA**.

```text
Tahap produk dan audiens:
Deadline dan hasil yang wajib diserahkan:
Tim/kapasitas:
Fitur wajib rilis pertama:
Tiga use case prioritas:
Stack wajib atau boleh ditinjau:
Lokasi root aplikasi dan data:
Target deployment/resource:
Anggaran hosting/API:
Aturan provider dan penggunaan sumber:
Satu/banyak divisi; hak lintas divisi Admin:
Hybrid/graph pada rilis pertama:
Respons teks/multi-equipment/multi-kartu/SQL:
Input gambar/suara:
Bahasa dan perangkat UI:
Validator dan acceptance:
Peran AI setelah perencanaan:
Jawaban ID pertanyaan lain:
```
