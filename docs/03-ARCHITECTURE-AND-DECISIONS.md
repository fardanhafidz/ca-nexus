# 03 — Arsitektur, Stack, dan Register Keputusan

## 1. Status rancangan

Dokumen ini memisahkan **stack dari brief**, **bagian yang belum dirancang**, dan **opsi supervisor**. Belum ada implementasi atau hasil pengujian kompatibilitas/model pada tahap dokumentasi ini.

Semua baris keputusan D-xx di bawah memiliki detail **TERBUKA**. Keberadaan keputusan terbuka tidak membatalkan kebutuhan eksplisit pada brief; keputusan tersebut melengkapi atau mengonfirmasi cara mewujudkannya.

## 2. Arsitektur baseline

```text
Browser
  |
  v
Frontend Next.js + Tailwind
  |  HTTP; auth dan transport streaming belum dirinci
  v
Backend FastAPI
  |-- Auth / status akun / RBAC
  |-- Session & message history
  |-- Knowledge catalog / akses file
  |-- Admin / Super Admin
  |-- Orkestrasi retrieval dan respons terstruktur
  |
  |-- PostgreSQL: user, division, chat, maintenance
  |-- Qdrant: collection manufacturing_knowledge
  |-- OpenAI / OpenRouter: gateway model sesuai pilihan
  |-- Penyimpanan file asli: belum dipilih
  |-- Lexical retrieval: belum dipilih
  |-- Graph storage / traversal: belum dipilih
  |-- OCR / vision / transkripsi: belum dipilih

Sumber awal di supporting_data/
  |-- seed_maintenance.py -> PostgreSQL
  |-- ingest_docs.py -> ekstraksi/chunk/embedding -> Qdrant
  |-- Jalur lexical / graph / PNG -> belum dirinci

Upload Admin -> ingestion job -> status monitor
              mekanisme eksekusi dan sinkronisasi belum dipilih
```

Empat container pada brief adalah PostgreSQL, Qdrant, backend, dan frontend. Belum jelas apakah empat container merupakan batas mutlak atau hanya konfigurasi awal. Pilihan graph database, object storage, atau worker terpisah dapat memengaruhi topologi tersebut.

## 3. Stack yang disebutkan dalam brief

| ID | Komponen | Baseline | Fungsi | Detail yang belum ditentukan |
| --- | --- | --- | --- | --- |
| ST-01 | Bahasa backend | Python **3.11+** | API dan pipeline data | Versi minor/patch yang dipin, base image, package manager |
| ST-02 | Framework API | FastAPI | Auth, chat, admin, knowledge | Versi, server ASGI, pola sync/async, lifecycle koneksi |
| ST-03 | Validasi data | Pydantic | Schema request/response dan rich component | Versi, strictness, error envelope, versioning schema |
| ST-04 | ORM | SQLAlchemy | User, divisi, chat, maintenance | Versi, driver PostgreSQL, sync/async, migration tool |
| ST-05 | Database relasional | `postgres:16-alpine` | Data terstruktur dan state aplikasi | Patch/digest, schema, timezone, koneksi, index, role database |
| ST-06 | Autentikasi | JWT dan password hashing | Identitas dan session | Library, algoritma hash/signature, TTL, refresh/revocation, tempat penyimpanan token |
| ST-07 | Framework frontend | Next.js **14**, App Router | Web app dan routing | Pin versi, apakah boleh meninjau versi lain, mode deployment |
| ST-08 | React | Digunakan oleh Next.js | UI component | Versi kompatibel dengan Next.js yang dipilih |
| ST-09 | TypeScript | Tersirat dari `.tsx`/`.ts` pada tree brief | Frontend bertipe | Versi dan konfigurasi type checking |
| ST-10 | Runtime JS dan dependency manager | Belum disebutkan | Menjalankan/membangun Next.js | Versi Node.js, npm/pnpm/yarn, lockfile |
| ST-11 | Styling | Tailwind CSS; `tailwind.config.js` | Tema dan layout | Versi, token desain, library komponen dan ikon |
| ST-12 | Infrastruktur lokal | Docker dan Docker Compose | Orkestrasi empat service awal | Versi tooling, port, healthcheck, volume, dev/prod profile |
| ST-13 | Vector database | `qdrant/qdrant:latest` | Penyimpanan embedding dan filter metadata | Versi/digest final, collection config, payload index, mekanisme hybrid |
| ST-14 | URL Qdrant | `http://qdrant:6333` | Koneksi internal jaringan Compose | Endpoint host/deployment, autentikasi bila dibutuhkan lingkungan |
| ST-15 | Collection | `manufacturing_knowledge` | Target indexing dokumen | Dimensi, distance metric, named/sparse vector, versioning |
| ST-16 | PDF extraction | PyMuPDF | Ekstraksi dokumen PDF | Versi, parser tabel, scan detection, OCR/vision fallback |
| ST-17 | Excel processing | pandas | Pembacaan workbook maintenance | Versi, engine XLSX, sheet, formula, tipe dan mapping kolom |
| ST-18 | Embedding | OpenAI `text-embedding-3-small` | Embedding dokumen/query | Dimensi konfigurasi, batching, versioning, batas biaya, kompatibilitas indeks |
| ST-19 | Model respons | OpenAI `gpt-4o` + structured outputs | Jawaban JSON sesuai kontrak | Alias/snapshot final, SDK, limit, verifikasi dukungan schema dan multimodal |
| ST-20 | Provider/gateway alternatif | OpenRouter | Orkestrasi akses LLM | Model/provider routing, primary/fallback, dukungan structured output per pilihan |
| ST-21 | Konfigurasi rahasia | `.env`; `OPENAI_API_KEY`, `OPENROUTER_API_KEY` | Konfigurasi backend/pipeline | Provider wajib/opsional, validasi config, pengaturan di deployment |
| ST-22 | Audio browser | Web Audio API | Input/olah audio pada frontend | Cara capture/record, format, speech-to-text, batas durasi |
| ST-23 | Akses API frontend | Fetch wrapper + bearer token | Komunikasi frontend-backend | Token transport/storage final, refresh, base URL, CORS |
| ST-24 | Viewing dokumen | Inspector PDF/PNG | Pratinjau sumber sitasi | Library viewer, page/region navigation, akses download |

Versi model, ketersediaan API, kompatibilitas SDK, dan dukungan structured outputs belum diuji. Nama model dalam brief tidak diperlakukan sebagai bukti bahwa setiap konfigurasi provider dapat menjalankan kontrak yang sama.

Web Audio API menangani pemrosesan audio di browser; alur perekaman dan transkripsi tetap memerlukan desain tersendiri. Penggunaan `getUserMedia`/`MediaRecorder` merupakan opsi implementasi, bukan stack yang sudah diputuskan.

## 4. Komponen yang masih perlu dipilih

Seluruh pilihan pada tabel ini berstatus **TERBUKA**. Nama teknologi adalah opsi pembahasan, bukan tambahan stack yang sudah disetujui.

| Area | Kebutuhan | Kandidat/pertimbangan |
| --- | --- | --- |
| Lexical search | Tag exact-match, singkatan industri, istilah, keyword | Sparse retrieval di Qdrant dengan encoder yang dipilih; PostgreSQL full-text; indeks BM25 lain |
| Fusion/reranking | Menggabungkan hasil dense dan lexical | RRF, weighted fusion, reranker opsional; pilih berdasarkan evaluasi |
| Graph | Menyimpan relasi dan sumber bukti | Tabel relasi PostgreSQL atau graph database seperti Neo4j; pertimbangkan kebutuhan traversal dan jumlah service |
| OCR/vision | Membaca PNG, PDF scan, simbol, tabel | OCR lokal, layanan OCR, atau vision model; ukur kualitas pada sumber aktual |
| Tabel/drawing | Mempertahankan row/column, label, satuan, konektivitas | Ekstraksi layout/tabel dan representasi terstruktur; OCR teks saja belum menjamin relasi diagram |
| Transkripsi | Mengubah suara menjadi pertanyaan | Layanan STT atau model lokal; bahasa, kebisingan, dan equipment tag perlu diuji |
| Storage file | Menyimpan dokumen asli, revisi, attachment | Volume filesystem atau object storage sesuai deployment |
| Eksekusi ingestion | Upload Admin memicu proses panjang | Proses/job dalam backend, worker terpisah, atau antrean; kebutuhan recovery menentukan pilihan |
| Migration | Menjaga schema relasional berversi | Tool kompatibel SQLAlchemy, misalnya Alembic; belum dipilih |
| API contract/tooling | Menyatukan schema backend/frontend | OpenAPI, tipe frontend hasil generate atau manual, error envelope, API versioning |
| Frontend libraries | Viewer, UI primitives, ikon, form, state, streaming | Pilih seperlunya setelah interaksi dan kompatibilitas ditetapkan |
| Testing/evaluation | RBAC, ingestion, AI, UI | Framework unit/integration/E2E serta format golden dataset belum dipilih |
| Observability | Audit query, token, error, latency | Data model dan dashboard; stack log/trace eksternal belum ditentukan |
| Delivery/operations | Build, deploy, backup, restore | CI/CD, hosting, monitoring, retensi mengikuti target rilis |

## 5. Prinsip rancangan yang diusulkan

Bagian ini berstatus **USULAN**, untuk dinilai bersama melalui keputusan terkait.

### 5.1 Konteks akses berasal dari backend

- Role, divisi, dan status efektif dihitung dari identitas/session yang divalidasi.
- Input pengguna atau output LLM tidak menjadi otoritas penentu `division_access`.
- Query dense, lexical, graph, SQL, file, dan history menerima konteks akses yang konsisten.
- Cache, bila dipakai, memperhitungkan izin dan revision sumber.
- Perubahan role/divisi/status memiliki aturan efek terhadap token aktif, percakapan tersimpan, indeks, dan sumber yang telah disitasi.

Keputusan terkait: D-05, D-06, D-08, D-20.

### 5.2 Identitas dokumen dipisahkan dari alamat storage

- Backend memetakan identitas sumber ke file/objek penyimpanan yang benar.
- Sitasi mengacu pada dokumen/revisi dan locator sumber yang tervalidasi.
- File viewer tetap memeriksa izin, termasuk ketika dipanggil langsung.
- `file_path` pada contoh brief perlu dikonfirmasi: tetap menjadi field kontrak yang diisi backend atau diganti referensi dokumen/URL terotorisasi.

Keputusan terkait: D-08, D-18. Tidak ada schema pengganti yang dianggap final pada dokumen ini.

### 5.3 Pengindeksan dapat ditelusuri dan diulang

- Manifest menghubungkan file, versi ekstraksi, chunk, embedding, lexical index, dan graph evidence.
- Import ulang memiliki aturan deduplikasi/idempotensi.
- Status sukses tidak hanya berarti upload selesai; definisi kesiapan indeks perlu disepakati.
- Perubahan/deletion sumber memiliki mekanisme invalidasi yang konsisten untuk seluruh jalur retrieval.
- Angka, tag, satuan, dan kutipan asli dipertahankan saat normalisasi.

Keputusan terkait: D-07 sampai D-14.

### 5.4 Output LLM divalidasi sebelum menjadi state UI final

- Gunakan schema yang membedakan payload setiap jenis komponen.
- Validasi nilai enum, field, rujukan, equipment, serta format sumber sesuai keputusan kontrak.
- Klaim engineering dan kalkulasi disertai bukti sumber yang tepat; bagian yang tidak didukung tidak diisi dengan nilai tebakan.
- Konten dokumen diperlakukan sebagai data sumber, bukan instruksi yang boleh mengubah izin, menjalankan aksi sistem, atau melewati kontrak.
- Tentukan respons untuk pertanyaan umum, tidak ada bukti, bukti bertentangan, input ambigu, output invalid, dan kegagalan provider.

Keputusan terkait: D-15 sampai D-19.

### 5.5 Kalkulasi maintenance dapat direproduksi

- Formula, filter waktu, unit, timezone, dan perlakuan nilai kosong ditetapkan sebelum dipakai model.
- SQL dijalankan dalam scope pengguna dan akses database baca-saja untuk jalur analitik.
- Hasil menyimpan informasi sumber/query atau representasi perhitungan yang disepakati.
- Jika model menyusun SQL, validasi mencakup struktur query dan cakupan data; sekadar mencari kata `SELECT` tidak cukup.
- Jika hasil agregasi tidak memiliki satu dokumen PDF, kontrak harus mampu merujuk sumber tabular secara jujur.

Keputusan terkait: D-06, D-09, D-10, D-18.

## 6. Trade-off utama untuk dibahas

| Topik | Opsi dan konsekuensi | Belum boleh diasumsikan |
| --- | --- | --- |
| Next.js/versi dependency | Mempertahankan versi brief menjaga kesesuaian rancangan; meninjau versi lain memerlukan pemeriksaan kompatibilitas dan dukungan | Otomatis memakai versi terbaru atau menyatakan versi brief sudah diverifikasi |
| Qdrant `latest` | Mengikuti tag bergerak berbeda dari pin versi/digest yang dapat direproduksi | `latest` selalu menghasilkan deployment identik |
| Empat container | PostgreSQL untuk relasi graph dapat memakai service yang ada; graph DB/worker/storage khusus dapat menambah service | Graph wajib Neo4j atau empat container wajib dipertahankan |
| Hybrid | Dense membantu relevansi semantik; lexical membantu istilah/tag; fusion dan bobot perlu dievaluasi | Vector search dengan metadata filter sudah merupakan hybrid search |
| Graph extraction | Mapping dari sumber yang ditinjau lebih terkendali; ekstraksi otomatis perlu bukti dan evaluasi tambahan | Kedekatan dua tag dalam teks otomatis membuktikan relasi interlock |
| PDF/PNG parsing | Text extraction, OCR, layout parsing, dan vision menangani bagian masalah yang berbeda | PyMuPDF text extraction otomatis membaca semua simbol atau konektivitas P&ID |
| SQL | Query template/semantic layer membatasi ruang pertanyaan; SQL hasil model lebih fleksibel dengan validasi lebih kompleks | Istilah Text-to-SQL telah menentukan library, formula, atau akses data |
| Streaming | Final JSON utuh lebih sederhana; event stream dapat memberi progres/teks sebelum hasil akhir tervalidasi | Fragmen JSON yang belum lengkap aman langsung dirender sebagai komponen final |
| Token browser | Bearer token dan cookie session memiliki implikasi transport/storage yang berbeda | JWT harus disimpan di localStorage atau penggunaan cookie membatalkan JWT |
| Model gateway | Satu provider menyederhanakan alur; routing/fallback memerlukan kesetaraan schema, pencatatan usage, dan aturan data | Tersedianya dua API key berarti failover otomatis sudah disetujui |

## 7. Register keputusan

Semua keputusan berikut **TERBUKA** pada versi awal. Kode kelompok Q-... merujuk ke [daftar pertanyaan](06-OPEN-QUESTIONS.md).

| ID | Keputusan | Baseline/ketidakjelasan | Pertanyaan | Dampak utama |
| --- | --- | --- | --- | --- |
| D-01 | Tahap produk, MVP, prioritas, tenggat, tim | Target produk luas; batas rilis pertama belum ada | Q-SCP-* | Seluruh prioritas dan milestone |
| D-02 | Root repo dan lokasi data | Tree `manufacturing-knowledge-hub/`; data aktual di `supporting_data/` | Q-REP-* | Struktur folder, mount, script, README |
| D-03 | Konfirmasi stack dan version pinning | Python 3.11+, Next.js 14, PostgreSQL 16, Qdrant latest, versi lain kosong | Q-STK-* | Dependency, Dockerfile, lockfile |
| D-04 | Deployment, kapasitas, provider data, anggaran | Empat service Compose dan provider eksternal disebut | Q-DEP-* | Infrastruktur, topologi, model, latency, biaya |
| D-05 | Identitas, lifecycle akun, password, session JWT | Register/login/pending/approved; detail session kosong | Q-AUTH-* | Models/auth API/halaman auth |
| D-06 | Batas role, divisi, ACL seluruh sumber | Admin katalog semua divisi; isi lintas divisi dan granularitas belum jelas | Q-RBAC-* | Seluruh jalur akses data |
| D-07 | Otoritas sumber dan pemetaan dataset | Delapan set dan workbook; slide deck ditemukan | Q-DATA-* | Manifest, mapping tag/divisi, evaluasi |
| D-08 | Storage, revision, ingestion lifecycle | Upload dan monitor ada; storage/job/delete belum dirinci | Q-DOC-* | Dokumen, pipeline, indeks, akses file |
| D-09 | Schema dan aturan import maintenance | 211 record/31 kolom hanya dari brief | Q-MNT-* | Models, import, lineage, kualitas data |
| D-10 | Analitik dan strategi Text-to-SQL | `sql_service.py` disebut tanpa schema metrik | Q-SQL-* | Query, validasi, komponen hasil, sitasi SQL |
| D-11 | Ekstraksi PDF/PNG, diagram, tabel, spasial | PyMuPDF untuk PDF; P&ID aktual PNG | Q-EXT-* | Parser, OCR/vision, kualitas engineering |
| D-12 | Chunking, tag, metadata, embedding | Lima metadata wajib dan model embedding disebut | Q-IDX-* | Collection, payload index, biaya reindex |
| D-13 | Lexical retrieval, fusion, reranker | Hybrid disebut, komponen lexical belum ada | Q-HYB-* | Retrieval dan evaluasi |
| D-14 | Graph schema, storage, bukti, traversal | Relasi tag disebut, graph service/storage belum ada | Q-GRF-* | Ingestion relasi, service graph, topologi |
| D-15 | Routing RAG, grounding, ambiguitas, konflik | Gateway/vector/SQL disebut; kebijakan respons belum lengkap | Q-RAG-* | Context assembly, jawaban, evaluasi |
| D-16 | Provider/model gateway dan perilaku kegagalan | `gpt-4o`, OpenAI, OpenRouter | Q-LLM-* | Structured output, multimodal, usage |
| D-17 | Schema JSON dan payload rich component | Satu equipment, satu komponen, `details: {}` | Q-JSON-* | Pydantic, TypeScript, renderer, SQL output |
| D-18 | Sitasi, locator sumber, Inspector | Judul/halaman/snippet/file_path; sumber PNG/SQL belum terwakili | Q-CIT-* | Kontrak, file API, viewer, provenance |
| D-19 | Streaming, protokol API, event dan error | Streaming disebut bersama JSON murni | Q-STR-* | Backend chat, SDK/client, renderer |
| D-20 | Session/history/attachment lifecycle | Session/message model dan sidebar disebut | Q-CHAT-* | Model chat, akses, retensi, UX |
| D-21 | Peran gambar yang diunggah pengguna | Attachment gambar disebut | Q-IMG-* | API upload, vision, retrieval, storage |
| D-22 | Perekaman suara, transkripsi, output audio | Web Audio API disebut; STT/TTS belum ada | Q-VOC-* | Browser API, model suara, biaya, UX |
| D-23 | Detail UI/UX, bahasa, perangkat, library | Warna/layout/empat komponen sudah disebut | Q-UI-* | Design system, responsive UI, interaksi |
| D-24 | Admin/Super Admin, audit, usage, gateway UI | Tugas peran disebut; cakupan layar dan metrik belum rinci | Q-ADM-* | API admin, audit model, dashboard |
| D-25 | Konvensi API dan tooling engineering | Struktur modul ada; detail library/migration/test belum dipilih | Q-ENG-* | Scaffold, migration, kontrak, build check |
| D-26 | Dataset evaluasi, acceptance, UAT | Belum ada target terukur atau query jawaban acuan | Q-QA-* | Release gate dan bukti kualitas |
| D-27 | Delivery, CI/CD, retensi, backup, operasional | Belum ada target host atau runbook | Q-OPS-* | Deployment dan handover |
| D-28 | Cara kerja supervisor dan pencatatan keputusan | Pengguna meminta supervisi dan dokumentasi detail | Q-WORK-* | Prioritas, penugasan, kesinambungan konteks |

## 8. Model domain yang perlu dirancang

Daftar ini adalah kebutuhan pemodelan konseptual, bukan definisi tabel final.

| Domain | Sudah disebut | Penambahan/rincian yang perlu diputuskan |
| --- | --- | --- |
| Identitas | User, Division, RBAC | Cardinality user-division, status tambahan, session/refresh, perubahan role |
| Percakapan | Session, Message | Output versi schema, attachment, citation snapshot/reference, status stream |
| Maintenance | `maintenance_records`, 31 kolom | Header aktual, primary key, original value, lineage, index, scope row |
| Dokumen | Upload, metadata chunk, katalog, viewing | Identitas dokumen/revisi, storage locator, ACL, extraction/index status |
| Retrieval | Qdrant chunk metadata | Lexical record, exact tag index, graph node/edge, provenance hubungan |
| Operasional | Audit query, analitik token, gateway config | Event schema, scope visibilitas, retention, usage per provider, pengaturan yang dapat diedit |

## 9. Konfigurasi yang perlu didokumentasikan saat implementasi

### Dari brief

- Port service dan kredensial PostgreSQL.
- URL Qdrant internal `http://qdrant:6333`.
- `OPENAI_API_KEY` dan `OPENROUTER_API_KEY`.
- `.env.example` sebagai contoh konfigurasi.

### Kandidat tambahan, belum menjadi nama environment final

- Source root dan lokasi storage dokumen/attachment.
- JWT/session settings dan allowed frontend origin.
- Model respons, embedding, vision, transkripsi, serta provider aktif.
- Collection/index version, chunking configuration, dan retrieval parameters.
- Limit request/file/audio, concurrency ingestion, timeout/retry.
- Logging/usage settings dan target deployment.

Nilai rahasia nyata tidak menjadi bagian dokumentasi contoh atau frontend bundle. Implementasi validasi environment bergantung pada provider dan fitur yang akhirnya dipilih.

## 10. Format pencatatan keputusan lanjutan

Gunakan format berikut setelah pengguna memberikan jawaban:

```text
ID: D-xx
Judul:
Status: TERBUKA / USULAN / DISEPAKATI / DIGANTI
Tanggal:
Pemberi keputusan:
Konteks dan sumber:
Pertanyaan yang dijawab:
Opsi yang dipertimbangkan:
Keputusan:
Alasan:
Konsekuensi dan trade-off:
File/kontrak/task terdampak:
Cara verifikasi:
Hal yang masih terbuka:
Menggantikan/digantikan oleh:
```

Perubahan baseline harus tercermin di konteks, kontrak, backlog, dan pertanyaan terkait. Estimasi durasi/biaya baru ditambahkan setelah scope, data, deployment, dan kapasitas tim diketahui.
