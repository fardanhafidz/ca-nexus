# 07 — Supervisi Implementasi vs Backlog (Read-Only, Tanpa Coding)

**Tanggal supervisi:** 19 September 2026
**Scope:** `manufacturing-knowledge-hub/` vs `docs/05-DETAILED-BACKLOG.md` (68 task T0.1–T8.6), brief pada `docs/01-PROJECT-CONTEXT.md`, kontrak pada `docs/04-AI-RESPONSE-CONTRACT.md`, arsitektur pada `docs/03-ARCHITECTURE-AND-DECISIONS.md`, inventaris pada `docs/02-DATA-INVENTORY.md`.
**Peran:** supervisor saja. Tidak ada kode yang diubah pada pass ini. File ini adalah instruksi koreksi untuk coding agent.
**Metode:** baca statis seluruh backend/frontend/scripts/infra (58 file), `py_compile` 20 file Python, cek keberadaan `.env`, cek daftar file frontend. Tidak menjalankan Docker/DB/Qdrant/LLM karena keputusan D-03/D-04/D-16 masih TERBUKA dan kredensial provider tidak tersedia.

## 1. Hasil uji read-only

| Uji | Hasil | Makna |
| --- | --- | --- |
| `py_compile` 20 file `backend/app/**` + `scripts/*.py` | `PY_COMPILE_OK` | Sintaks Python lolos; bukan bukti runtime/DB/Qdrant/LLM. |
| `Test-Path .env` di `manufacturing-knowledge-hub/` | `False` | Tidak ada secret lokal yang terbawa; `.env.example` masih berisi kredensial demo default — jangan `cp` begitu saja untuk prod. |
| Inventaris frontend `frontend/src` | 22 file ditemukan | Struktur chat/knowledge/admin/auth/layout/rich-components/lib lengkap secara nama file. |
| Docker Compose up / pytest / `npm build` / panggilan OpenAI/Qdrant | Tidak dijalankan | Di luar batas supervisi read-only + keputusan TERBUKA. Coding agent wajib menjalankan dan mencatat bukti saat koreksi. |

## 2. Ringkasan eksekutif

- **OK penuh: 1 / 68** — hanya `T3.1` (register/login dasar: bcrypt, `pending`, duplikat, 403 pending).
- **SEBAGIAN: 47 / 68** — scaffold/fitur dasar ada, tetapi acceptance backlog belum terpenuhi (detail di bawah).
- **MISS: 20 / 68** — belum ada implementasi yang memenuhi acceptance: `T0.1`, `T0.2`, `T0.3`, `T0.4`, `T2.1`, `T2.4`, `T2.6`, `T2.10`, `T3.3`, `T4.2`, `T4.9`, `T5.2`, `T5.3`, `T5.4`, `T7.5`, `T7.6`, `T8.1`, `T8.2`, `T8.3`, `T8.4`, plus `T8.5`/`T8.6` belum dapat dinyatakan selesai.
- Pola miss terbesar: discovery T0 dilewati, klaim `hybrid` tanpa lexical/fusion, `page_number` hardcode, chunk/Qdrant ID acak, filter divisi pasca-retrieval, SQL/graph tanpa scope divisi, sitasi LLM diteruskan mentah, streaming/SSE belum ada, upload gambar hanya string hint, audit/usage/gateway-config belum ada, migration Alembic dideklarasikan tapi tidak dipakai.
- Tidak ada bagian yang boleh ditandai `DIVERIFIKASI` pada pass ini kecuali `T3.1` untuk alur dasar saja (dengan catatan hardening masih kurang).

Legenda: `[OK]` = acceptance dasar terpenuhi; `[SEBAGIAN]` = ada implementasi tetapi ada gap acceptance; `[MISS]` = belum memenuhi acceptance / belum ada.

## 3. Checklist per task + note koreksi untuk coding agent

### Fase 0 — Discovery (fondasi yang dilewati; wajib dilengkapi sebelum klaim rilis)

| Task | Status | Temuan | Koreksi (coding agent) |
| --- | --- | --- | --- |
| T0.1 scope rilis | [MISS] | Tidak ada artefak scope F-01–F-15, tenggat, tim, use case prioritas. | Buat catatan keputusan D-01/D-28; tandai tiap F-01–F-15 masuk/tunda; jangan asumsikan jadwal dari nama folder hackathon. |
| T0.2 audit sumber | [MISS] | Tidak ada laporan isi PPTX/workbook/sampel PDF/PNG; `maintenance.py:12` menulis `verified 211 rows` tanpa bukti, bertentangan dengan `docs/02` yang menyatakan 211/31 masih BRIEF. | Audit representatif + locator sumber; buktikan atau koreksi 211/31; pisahkan terverifikasi vs interpretasi. |
| T0.3 golden query | [MISS] | Tidak ada query acuan/rubric/validator. | Susun query per fitur/divisi/equipment + kasus exact-tag, lintas sumber, angka, akses-ditolak, bukti-kurang, konflik; tanpa persen sukses sebelum evaluasi. |
| T0.4 desain slice | [MISS] | Tidak ada baseline slice pertama yang mengikat D-02–D-06/D-17–D-19/D-25. | Catat root repo, stack/version, deployment, ACL, session, schema slice; tandai kontrak yang belum final. |

### Fase 1 — Monorepo, config, infra

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T1.1 struktur + dataset | [SEBAGIAN] | Scaffold `backend/frontend/scripts` ada; mount `../supporting_data:ro` ada di `docker-compose.yml:49`. README `--source supporting_data` salah bila CWD=`manufacturing-knowledge-hub/`; penanganan spasi/`&`/underscore/variasi OPL belum didokumentasikan. | Perbaiki README path + quoting; dokumentasikan variasi folder OPL; uji resolve path dari kedua CWD. |
| T1.2 dependency | [SEBAGIAN] | Pin `==` backend/scripts dan pin eksak frontend ada; `qdrant:v1.9.0` baik. Belum ada lockfile; `python:3.11-slim` dan `node:20-alpine` tanpa patch/digest; tanpa bukti install/import/build. | Tambah lockfile; pin patch/digest; catat hasil install/import/build bersih. |
| T1.3 config env | [SEBAGIAN] | `config.py` punya collection benar `manufacturing_knowledge`, JWT 24h, 4 divisi, OpenAI/OpenRouter. Tanpa validasi wajib per provider/fitur; tanpa beda URL internal vs host; tanpa param embedding/chunk/retrieval/timeout; default berisi kredensial demo (`change-me...`, `Admin123!`). | Tambah validator + pesan actionable; bedakan `qdrant:6333` vs host; pindah default rahasia ke placeholder; tambah param yang dipakai fitur aktif. |
| T1.4 Compose | [SEBAGIAN] | 4 service + volume + `depends postgres healthy` ada. Health hanya postgres; qdrant `service_started`; backend/frontend tanpa health; `6334` hardcode; `NEXT_PUBLIC_*` tanpa `build.args` sehingga tidak masuk `npm run build`; tanpa bukti startup/restart/persistensi. | Tambah health qdrant/backend/frontend; perbaiki port/args; tambah profil dev/prod; uji startup/restart/persistensi dan catat command. |
| T1.5 schema + migration | [SEBAGIAN] | Model user/chat/document/edge/audit ada. Tanpa migration (Alembic ada di requirements tapi `create_all` di `main.py:21-35`); tanpa FK (`ChatSession.user_id`, `ChatMessage.session_id`); tanpa CheckConstraint role/status/divisi; bug tipe `models/user.py:22` (`created_at: str`), `maintenance.py:13-15` (`str` vs `DateTime`), `payload_json: Text` bukan JSONB. | Buat Alembic `env.py` + migration awal; tambah FK/cascade/index; perbaiki tipe; ganti `on_event(startup)` deprecated dengan `lifespan` + `try/rollback`. |
| T1.6 bootstrap | [SEBAGIAN] | Idempoten (cek email dulu) OK. Kredensial default keras; `division="Mechanical"` hardcode `main.py:31`; tanpa seed role/divisi configurable. | Ambil kredensial dari secret terotorisasi; seed divisi/role sesuai keputusan; dokumentasikan aturan re-run. |

### Fase 2 — Data preparation / ingestion

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T2.1 manifest | [MISS] | Tanpa file/kode manifest, checksum, revision; tanpa laporan unread/duplikat; selisih 98 file belum direkonsiliasi. | Buat manifest machine-readable + ringkasan; rekonsiliasi terhadap inventaris awal. |
| T2.2 dictionary | [MISS] | Tanpa dictionary; hanya `COLMAP` 31 kolom di `seed_maintenance.py:13-29`; default sheet terpotong `"Maintenance History (All Equipm"` (`:36`). | Rekam header/sheet/tipe/null/satuan/formula; petakan ke schema + lineage; catat selisih 211/31. |
| T2.3 seeding | [SEBAGIAN] | Seed + edge WO/interlock ada; satu `commit`. Destruktif (`delete+insert` `:49-53`); coerce diam-diam jadi NULL tanpa error report; tanpa rekonsiliasi/uji gagal-tengah. | Ganti truncate dengan mode import disepakati (upsert/replace terkontrol); tambah validasi per-record + laporan diterima/ditolak; uji rerun + failure injection. |
| T2.4 metadata/ACL | [MISS] | `DIVISION_BY_TYPE` menebak divisi dari filename (`ingest_docs.py:11-15,75`); melanggar acceptance "tidak menebak dari filename". | Ganti dengan mapping resmi/pemeriksaan isi; definisikan kebijakan unlabeled/multi-equipment/sumber bersama. |
| T2.5 ekstraksi PDF | [SEBAGIAN] | PyMuPDF per-page + chunk ada. Tanpa deteksi scan/tabel/layout; tanpa beda raw vs normalized; tanpa laporan kualitas; bug `ingest_docs.py:89,101` (`FAILED` lalu dioverwrite `READY`). | Tambah deteksi + jalur tambahan sesuai keputusan; simpan raw vs normalized; perbaiki bug status; laporkan kualitas per file/halaman. |
| T2.6 PNG/drawing/spasial | [MISS] | `describe_png` hanya stub (`ingestion_service.py:25-27`); `vision_extract_tags` (`llm_gateway.py:70-88`) tidak pernah dipanggil pipeline; tanpa OCR/layout/BOM/konektivitas/region/plot-plan. | Implementasikan OCR/vision/layout terpilih; simpan label/region/bukti; pisahkan terbaca vs ambigu vs tidak-tersedia; jangan klaim OCR teks = pemahaman konektivitas. |
| T2.7 chunking/provenance | [SEBAGIAN] | Chunk + normalisasi tag + payload akses ada. Split kata naif 1000/100; potong `[:50]` diam-diam; `admin.py:104` `page_number:1` hardcode; ID acak tanpa provenance stabil. | Perbaiki strategi chunk; ID stabil; perbaiki `page_number` per halaman; hapus truncate diam-diam; simpan revision/locator. |
| T2.8 embedding Qdrant | [SEBAGIAN] | Collection/dimensi/model benar bila ada key. ID acak → reindex ganda; filter divisi pasca-retrieval (`vector_service.py:61-62`, `must` kosong `:52-56`); tanpa batch/retry/usage/mismatch-check; fallback hash non-semantik; `c.search()` deprecated. | Pakai ID stabil; pindah ke Qdrant pre-filter; tambah batch/retry/usage; tangani embedding mismatch; migrasi ke `query_points`. |
| T2.9 pipeline/status | [SEBAGIAN] | CLI + upload `BackgroundTasks` + status `PARSING/VECTORIZING/READY/FAILED` ada. Tanpa retry/cancel/progress; tanpa integrasi lexical/graph; definisi searchable kabur; `extract_pdf` dipanggil 2x (`admin.py:90-93`); `.xlsx` masuk stub PNG (`:94-95`). | Tambah retry/cancel/progress; definisikan readiness; perbaiki duplikasi PDF + routing XLSX; siapkan hook lexical/graph bila aktif. |
| T2.10 revision/ACL/invalidasi | [MISS] | Nol kode; hanya `version="v1.0.0"` statis. | Implementasikan replace/delete/arsip + propagasi ke registry/SQL/dense/lexical/graph/history + uji sitasi lama. |

### Fase 3 — Auth, policy, knowledge API

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T3.1 register/login | [OK dasar] | Bcrypt, `pending`, cek duplikat, 403 pending — lolos dasar. | Hardening: `EmailStr`, min-length password, enum divisi, rate-limit/lockout, audit login; perbaiki `UserOut(**u.__dict__)` yang rapuh. |
| T3.2 approval | [SEBAGIAN] | List/approve/reject ada. Tanpa detail user, ubah role, bulk, validasi transisi, audit actor/waktu, beda admin vs super_admin. | Tambah transisi valid + transaksi + audit + batas peran. |
| T3.3 session lifecycle | [MISS] | Hanya expiry 24h; tanpa refresh/logout/revocation; token hanya `sub+exp` (`security.py:17-19`); `except` menelan beda expired vs invalid (`:25-27`); `utcnow()` deprecated. | Implementasikan refresh/logout/revocation; sertakan klaim yang dibutuhkan; bedakan error; pakai `timezone-aware datetime`. |
| T3.4 policy akses | [SEBAGIAN] | Katalog/file/vector terfilter; user fresh-fetch tiap request (bagus). SQL tanpa scope divisi (bypass); graph tanpa policy; hanya `user.division` tunggal. | Terapkan scope di SQL (read-only + filter divisi), graph node/edge/evidence, chat/attachment/history; definisikan multi-divisi + sumber bersama/label kosong. |
| T3.5 file/locator | [SEBAGIAN] | Registry-only + komentar D-18 bagus. Melayani non-READY; tanpa revision; tanpa locator page/region; `file_path` absolut dari DB berisiko (`knowledge.py:45`); LIKE tanpa escape (`:31`). | Filter `READY` + revision; tambah locator; kunci ke registry; escape LIKE; definisikan respons hilang/revision-lama/izin-berubah. |
| T3.6 katalog | [SEBAGIAN] | Filter tag/type/q + `visible()` OK. Tanpa pagination/sort/facet; tampilkan non-READY. | Tambah pagination/sort/facet + status lifecycle; pastikan konsisten dengan akses file. |
| T3.7 matriks akses | [MISS→SEBAGIAN parsial] | Belum ada bukti matriks end-to-end. | Uji pending/divisi/multi/Admin/SuperAdmin + akses langsung ID/URL/row/node/chunk/session + perubahan ACL + pastikan filter sebelum konteks LLM. |

### Fase 4 — Retrieval, graph, SQL, respons AI

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T4.1 dense/lexical/exact | [SEBAGIAN] | Dense + regex boost + filter ada. Klaim `Hybrid` salah: tanpa lexical/BM25/sparse; tanpa Qdrant pre-filter. | Implementasikan lexical terpilih dari sumber/chunk/revision sama + exact-tag + pre-filter; kembalikan identity/skor/locator. |
| T4.2 fusion/rerank | [MISS] | Tidak ada. | Implementasikan fusion + dedup + top-k/threshold + reranker bila dipilih; simpan config; bandingkan dense-only vs hybrid. |
| T4.3 model graph | [SEBAGIAN] | Tabel edge ada. Typo `HAS_INSTRUMENT` (`maintenance.py:86`); tanpa constraint/revision/access/provenance. | Perbaiki typo; definisikan node/edge/arah/cardinality + constraint + provenance/revision/akses. |
| T4.4 ingest relasi | [SEBAGIAN] | Edge WO/interlock dari `Related_Interlock` + evidence ada. Tanpa edge dokumen (`HAS_OPL`); tanpa alias/unknown/duplikat/revision. | Lengkapi mapping/manual/otomatis terpilih; tangani alias + bukti-berbeda; laporkan unverified. |
| T4.5 graph retrieval | [SEBAGIAN] | BFS 2-hop ada (`graph_service.py:6-20`). Tanpa disambiguasi/policy/dedup; hanya arah `src->dst`. | Tambah entity resolution + policy sebelum perluasan konteks + dedup + uji lintas-divisi. |
| T4.6 SQL analitik | [SEBAGIAN] | Template cost/frequency/downtime + `LIMIT 50` ada. Tanpa koneksi read-only; tanpa scope divisi; tanpa formula/unit/timezone/null; `ALLOWED` tak dipakai + `FORBIDDEN` semu (`sql_service.py:6,22-23,39-40`); error ditelan (`chat.py:47`). | Kunci read-only + scope + batas hasil/waktu + validasi nyata; definisikan formula/unit/timezone; kembalikan provenance; uji tanpa-record + ambigu. |
| T4.7 router/konteks | [SEBAGIAN] | Routing SQL + assembly evidence + history 6 pesan ada. Tanpa budget/dedup/trace/revision; tanpa prompt-injection guard selain narasi. | Tambah klasifikasi + budget + dedup + route trace; perlakukan isi dokumen sebagai evidence (tanpa ubah role/scope/tool). |
| T4.8 gateway | [SEBAGIAN] | Primer `gpt-4o json_object` + fallback OpenRouter + timeout 45 ada. Tanpa validasi schema/retry/quota/usage; `response_format` OpenRouter belum tentu setara; `KeyError` generik (`:61`); hardcode `image/jpeg` (`:83`). | Validasi structured-output; tambah retry/quota/usage + catat model/provider aktual; uji valid/invalid + failure nyata bila key tersedia. |
| T4.9 sitasi | [MISS] | Sitasi LLM diteruskan mentah (`chat.py:105-112`); tanpa resolver/validator; default `source_type="pdf"` rapuh (`chat.py:80-83`, `schemas/chat.py:16`). | Petakan ke registry/revision/locator; bangun snippet dari representasi disepakati; validasi kutipan + akses akhir; tangani PNG/region + SQL/row. |
| T4.10 schema komponen | [SEBAGIAN] | 6 tipe (`4 brief + text_only/kpi_table`) + `sql_query` + `insufficient_evidence` bagus. `details: dict` masih bebas; tanpa per-type schema/versioning/multi-equipment/multi-card/clarification/error-envelope/`document_id`/`citation_id`/`row_reference`/`bbox`. | Definisikan Pydantic diskriminan + TS mirror + fixture valid/invalid bersumber; tolak string enum `a\|b`. |
| T4.11 alur jawaban | [SEBAGIAN] | End-to-end + fallback deterministik + audit ada. Validasi dangkal; tanpa cek sitasi; `payload_json` double-encoded (`chat.py:114`); error provider bocor ke user (`:99`). | Satukan route→retrieval→assembly→generation→schema→citation validation; tangani bukti-kurang/konflik/ambigu/out-of-dataset; perbaiki encoding + error envelope. |

### Fase 5 — Session, streaming, multimodal API

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T5.1 session store | [SEBAGIAN] | Create/list/detail + ownership OK. Tanpa rename/delete/search; tanpa `schema_version`/usage/attachment lifecycle; tanpa status `queued/generating/complete/failed`. | Lengkapi operasi + status + ownership/admin + render versi payload. |
| T5.2 transport | [MISS] | Hanya JSON sync; tanpa SSE/WS; frontend `chat/page.tsx` hanya `await api(/ask)` tanpa partial vs final. | Implementasikan transport terpilih + event progres/teks/final/error + ID request/message; pisahkan partial vs final tervalidasi. |
| T5.3 cancel/retry | [MISS] | Tidak ada. | Tambah cancel/disconnect/retry + idempotensi agar tidak ganda + status akhir + uji timeout/rate-limit/invalid/refresh. |
| T5.4 gambar | [MISS] | Hanya `image_tag_hint: str`; `vision_extract_tags` tak dipakai; file tidak pernah di-upload (frontend hanya kirim nama file). | Buat upload + validasi + storage + kepemilikan; hubungkan ke vision/retrieval; konfirmasi tag ambigu; bedakan attachment vs pengetahuan bersama. |
| T5.5 suara | [SEBAGIAN] | `/transcribe` Whisper + hint Web Speech ada. Tanpa validasi format/durasi/ukuran, preview/edit/transmit, kebijakan simpan/hapus audio, usage. | Lengkapi sesuai keputusan D-22; uji bahasa target + tag teknis + kosong/buruk/gagal. |
| T5.6 kontrak API | [SEBAGIAN] | Prefix `/api/v1` + OpenAPI otomatis ada. Tanpa tipe generate/sync, fetch wrapper lengkap, error envelope, pagination, transport doc; frontend menebak `details:any`. | Publikasikan kontrak + sinkronkan tipe + fetch wrapper (auth/cancel/upload/streaming) + uji lintas service termasuk 401/validation-error. |

### Fase 6 — Frontend

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T6.1 token/state | [SEBAGIAN] | Warna `industrial:#1E56A0` + `canvas:#F4F7FA` benar; tanpa emoji di kode (bagus). Tanpa token typography/spacing/radius; tanpa button/input/focus/loading/empty/error state. | Lengkapi design token + state; terapkan larangan emotikon pada copy/contoh juga. |
| T6.2 shell | [SEBAGIAN] | SlimRail+Sidebar+chat+Inspector terangkai `flex h-screen`. Tanpa collapsible, role-aware, indikator aktif, responsif tablet/mobile, keyboard/focus. | Tambah navigasi role-aware + active + collapsible + responsif + a11y. |
| T6.3 auth pages | [SEBAGIAN] | Form login/register/pending ada. Login kirim `employee_id`+`email` ambigu; tanpa deteksi pending→`/pending`; tanpa beda expired/disabled/401; tanpa validasi/loading; token `localStorage`; pending statis tanpa polling. | Perbaiki payload login; tangani status; tambah validasi/loading/error spesifik; pindah token ke httpOnly cookie; polling `/me` di pending. |
| T6.4 composer | [SEBAGIAN] | Teks OK. Enter selalu submit (tanpa Shift+Enter); tanpa preview/remove/progress/error upload; tanpa cancel/limit; `audio.ts` hanya WebSpeech `en-US` tanpa MediaRecorder/preview/edit. | Tambah multiline + attachment UI + cancel + batas; implementasikan audio sesuai API terpilih (ID/EN + tag teknis). |
| T6.5 renderer | [SEBAGIAN] | Diskriminan 4 komponen + `kpi_table` + chips `[{i+1}]` ada. Tanpa partial/final, Markdown, `alert_level`/`equipment_tag`/`insufficient_evidence`, unknown-handling (diam), versioning; `key` index. | Pisahkan loading/partial/final; render status hasil; tangani unknown/invalid tanpa data rekaan; tambah Markdown aman + sanitizer. |
| T6.6 checklist | [SEBAGIAN] | Render + centang lokal ada. Tanpa prasyarat/parameter/rujukan per-langkah; persistensi memori (reset saat refresh); `key=i`; fallback `JSON.stringify`. | Tambah field sumber; pisahkan instruksi vs state user; persistensi sesuai scope; tangani refresh/revision. |
| T6.7 interlock | [SEBAGIAN] | Tabel generik tampil. Tanpa field eksplisit cause/instrument/comparator/setpoint/unit/effect, voting/delay bersyarat, sitasi per-hubungan, label `unknown` (hanya `??""`). | Render field kontrak; tampilkan voting/delay hanya bila berbukti; bedakan unknown vs `0`/`false`/`normal`. |
| T6.8 BOM | [SEBAGIAN] | Tabel generik tampil. Tanpa kolom drawing/revision/citation, beda missing vs `0`, sort/filter/export, traceability row. | Kunci kolom + locator; pertahankan row identity saat sort; tambah interaksi hanya bila scope. |
| T6.9 RCA | [SEBAGIAN] | Nilai plus: pisah `Anomaly / Recorded cause / AI hypothesis (unverified) / Recommendation`. Tanpa event/record-id, bukti, keterbatasan, confidence/alert terdefinisi. | Tambah sumber record/dokumen + batas data; pakai confidence/alert hanya bila terdefinisi. |
| T6.10 chips/Inspector | [SEBAGIAN] | Chips + snippet ada. Link `file-by-path?path=` tanpa `Authorization` (akan 401); bukan `file/{id}` terotorisasi; tanpa `#page=`, region PNG, SQL/row, revision/`document_id`, highlight/download/navigasi, error handling; `w-96` fixed. | Pakai `file/{id}` + Bearer; tambah locator PDF/PNG/SQL + revision; tangani hilang/izin-berubah/invalid; perbaiki responsif/Esc. |
| T6.11 repository | [SEBAGIAN] | List + `?q=` + kolom + empty state ada. Tanpa pagination/filter/status-ingestion/detail; token di URL (`?token=` bocor ke log). | Tambah filter/pagination/detail/status; pindah ke `Authorization` header; bedakan preview/download. |
| T6.12 Sidebar history | [SEBAGIAN] | New/list/open ada. Tanpa search/rename/delete/status/pagination. | Lengkapi lifecycle + render versi payload/sitasi + ownership. |

### Fase 7 — Admin / Super Admin

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T7.1 approval queue | [SEBAGIAN] | Approve/reject pending ada. Tanpa alokasi divisi (wajib backlog), detail/bulk/role-change/loading/konflik/audit-ref; tanpa batas Admin vs SuperAdmin. | Tambah alokasi divisi + bulk + validasi + audit; verifikasi dari sisi user. |
| T7.2 upload/monitor | [SEBAGIAN] | Upload + stats + list status ada. Bypass `api()` (raw `fetch`); tanpa error handling/progress per-tahap/retry/cancel/reindex/duplikat/batch. | Satukan client; tampilkan progres aktual per tahap; tambah retry/cancel/reindex; tangani duplikat/invalid/restart. |
| T7.3 katalog lintas-divisi | [MISS] | Tanpa komponen katalog bersama; tanpa beda metadata vs isi. | Gunakan katalog bersama + label divisi/revision; uji Admin vs User pada sumber sama. |
| T7.4 audit | [SEBAGIAN] | `AuditLog` chat-only minimal. Tanpa audit admin, API/UI, status/ref, filter/pagination, retensi. | Definisikan event/field + API/UI + akses peran + uji berhasil/gagal. |
| T7.5 usage/biaya | [MISS] | Hanya `stats` count. Tanpa usage/cost/quota/dashboard. | Catat usage per provider/model/tugas/actor; bedakan estimasi vs aktual; tambah quota bila dipilih. |
| T7.6 gateway config | [MISS] | Env-only; tanpa API/UI runtime config. | Bangun API/layar SuperAdmin + validasi + efek lifecycle + audit perubahan + prioritas env vs runtime. |

### Fase 8 — Verifikasi / delivery

| Task | Status | Temuan | Koreksi |
| --- | --- | --- | --- |
| T8.1 checks integritas | [MISS] | Tanpa laporan lint/type/build/test. | Satukan test modul + antar-service + kasus negatif; catat command/env/hasil; perbaiki + rerun. |
| T8.2 evaluasi RAG | [MISS] | Tanpa evaluasi tercatat. | Jalankan golden query + nilai retrieval/citation/angka/dukungan klaim + kontribusi hybrid/graph + SQL vs acuan. |
| T8.3 E2E | [MISS] | Tanpa bukti alur. | Uji register→approval→login→query→komponen→history→Inspector→upload→multimodal→admin. |
| T8.4 performa/failure | [MISS] | Tanpa metrik/uji. | Ukur latency/concurrency/ingestion/resource + restart/provider-gagal/stream-putus + biaya. |
| T8.5 deployment/runbook | [SEBAGIAN] | README/compose/Dockerfile/`.env.example` ada. Command ambigu; tanpa CI/CD/backup/rollback/retensi; tanpa uji bersih; `NEXT_PUBLIC` bug; default kredensial demo. | Perbaiki runbook + uji dari lingkungan bersih; tambah backup/restore/rollback/retensi sesuai rilis. |
| T8.6 UAT/penutupan | [MISS] | Tanpa hasil validator/UAT. | Jalankan demo/UAT + rekam issue/batas/tindak lanjut; finalkan status hanya dengan bukti. |

## 4. Temuan clean-code / best-practice lintas modul (untuk coding agent)

1. **Keamanan token & file:** token di `localStorage` + `?token=` di URL (`knowledge/page.tsx`); Inspector tanpa `Authorization`; `CORS allow_credentials` + split origin di `main.py:12`; `file_path` absolut dari DB (`knowledge.py:45`). Perbaiki ke httpOnly cookie/`Authorization` header + registry-only + validasi path.
2. **Error handling:** `except Exception: return None` (`security.py`), `except: sql_rows=[]` (`chat.py:47`), `except` tanpa logging (`admin.py:110-116`), `catch{}` senyap frontend, `UserOut(**u.__dict__)` rapuh. Bedakan expired/invalid/pending, log failure ingestion, jangan bocorkan `Provider error` ke user (`chat.py:99`).
3. **Deprecated/API usang:** `on_event(startup)` (`main.py:21`), `datetime.utcnow()` (`security.py:18`), `pydantic-settings Config` (`config.py:22-23`), `c.search()` Qdrant (`vector_service.py:57`), `future=True` SQLAlchemy. Migrasi ke API kini.
4. **Duplikasi pipeline:** logika CLI (`ingest_docs.py`) vs upload (`admin.py:_ingest_one`) berbeda (per-page vs `page_number:1`, `[:50]` ganda, XLSX salah rute). Satukan ke satu service ingestion.
5. **Frontend robustness:** `any[]`, `key={i}`, `JSON.stringify` fallback, duplikasi fetch (auth/admin-docs bypass `api()`), tanpa tipe `Answer` bersama, tanpa `AbortController`/SSE helper, tanpa Markdown/sanitizer/test-runner. Satukan client + tipe generate + normalisasi error.
6. **Data integrity:** `payload_json` double-encoded (`chat.py:114`), kolom `Text` untuk JSON, tipe tanggal salah, tanpa FK/cascade, tanpa migration. Perbaiki ke JSONB/FK/migration + encode sekali.
7. **Dokumentasi vs implementasi:** README `mkh` mengklaim idempoten umup dan path yang ambigu; komentar `verified 211 rows` menyesatkan; docstring `Hybrid` tidak sesuai kode. Selaraskan komentar/README dengan perilaku aktual.

## 5. Prioritas koreksi yang disarankan (coding agent)

**P0 (sebelum klaim demo/akses):** T0.1–T0.4, T2.1, T2.2, T2.4, T3.3, T3.4 (SQL/graph scope), T4.9, T6.10 auth/locator, T7.1 alokasi divisi, T8.3 E2E dasar.
**P1 (sebelum klaim hybrid/graph/AI):** T2.5–T2.9, T4.1, T4.2, T4.6, T4.8, T4.10, T5.1–T5.6, T6.5–T6.9, T7.2, T8.1–T8.2.
**P2 (sebelum handover):** T1.2 lockfile, T1.4 health/prod profile, T1.5 migration, T2.10 invalidasi, T7.4–T7.6, T8.4–T8.6.

## 6. Batasan supervisi ini

- Checklist di atas memakai bukti baca-statis + `py_compile`; bukan verifikasi runtime.
- Setiap task `[SEBAGIAN]`/`[MISS]` harus dilengkapi coding agent dengan bukti perintah, log, dan sampel sebelum status boleh naik ke `DIVERIFIKASI`.
- Backlog asli `docs/05-DETAILED-BACKLOG.md` tidak diubah; kotak `[ ]` di sana tetap acuan pekerjaan, bukan klaim selesai.
