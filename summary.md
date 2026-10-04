# Summary — Manufacturing Knowledge Hub (CALIBER2Ø26)

> Disusun 4 Oktober 2026 dari dokumen di `docs/`, `manufacturing-knowledge-hub/docs/`, dan pengecekan sebagian kode.
> Klaim "terbukti" berasal dari `VERIFICATION-LOG.md` (dicatat sendiri oleh tim/agen) dan **belum dijalankan ulang** saat rangkuman ini dibuat, kecuali yang ditandai *(dicek di kode)*.

---

## 1. Ringkasan singkat

**Manufacturing Knowledge Hub** adalah platform web AI (RAG) untuk pengetahuan operasional pabrik petrokimia. Studi kasusnya **PT Chandra Asri Pacific Tbk — SDK LLDPE Expansion Project** (Case 1 hackathon).
Operator dan engineer bertanya lewat chat bergaya Gemini. Sistem lalu:

1. mengambil bukti yang **boleh diakses** sesuai divisi pengguna,
2. menyusun jawaban JSON terstruktur dengan **sitasi** yang bisa dibuka,
3. menampilkan **rich component** (checklist SOP, logika interlock, tabel BOM, kartu RCA, tabel KPI).

| Atribut | Nilai |
| --- | --- |
| Target rilis | **PoC hackathon** (bukan produksi) — keputusan terkunci 1 Okt 2026 |
| Deadline submit | **4 Oktober 2026** (demo + slide + website prototype) |
| Tim (3 orang) | Hacker (build), Bisnis/Presentasi, Teknik Kimia (validator domain) |
| Status supervisor | **NO-GO rilis final, GO bersyarat demo terbatas** (`09-RELEASE-NOTES.md`, 1 Okt) |

---

## 2. Struktur workspace

```text
Caliber2026/
├── README.md                     # peta dokumen supervisi
├── docs/                         # dokumen perencanaan & supervisi (01–09)
├── supporting_data/              # dataset asli (read-only, 98 file)
└── manufacturing-knowledge-hub/  # aplikasi PoC (slice-1)
    ├── docker-compose.yml        # 4 service: postgres, qdrant, backend, frontend
    ├── backend/                  # FastAPI + SQLAlchemy + Alembic (6 migration)
    ├── frontend/                 # Next.js 14 + Tailwind
    ├── scripts/                  # manifest, seed, ingest, eval, validator pack
    ├── data/                     # manifest.json, division_map.json, eval_report.json
    ├── docs/                     # SCOPE, SLICE, AUDIT, RUNBOOK, VERIFICATION-LOG, dll.
    └── .github/workflows/ci.yml
```

### Dokumen kunci

| Dokumen | Isi |
| --- | --- |
| [01-PROJECT-CONTEXT](docs/01-PROJECT-CONTEXT.md) | Brief: fitur F-01–F-15, peran, divisi, alur, UI |
| [02-DATA-INVENTORY](docs/02-DATA-INVENTORY.md) | Inventaris 98 file + GAP-01..09 |
| [03-ARCHITECTURE-AND-DECISIONS](docs/03-ARCHITECTURE-AND-DECISIONS.md) | Stack ST-01..24, register keputusan D-01..D-28 |
| [04-AI-RESPONSE-CONTRACT](docs/04-AI-RESPONSE-CONTRACT.md) | Kontrak JSON jawaban AI |
| [05-DETAILED-BACKLOG](docs/05-DETAILED-BACKLOG.md) | 68 task (T0.1–T8.6) + kriteria terima |
| [06-OPEN-QUESTIONS](docs/06-OPEN-QUESTIONS.md) | Pertanyaan discovery Q-xxx |
| [07-SUPERVISION-REVIEW](docs/07-SUPERVISION-REVIEW.md) | Review 19 Sep: awalnya hanya 1/68 OK |
| [08-IMPLEMENTATION-STATUS](docs/08-IMPLEMENTATION-STATUS.md) | Checklist 68 task (45 OK, 17 sebagian, 2 salah, 4 belum) |
| [09-RELEASE-NOTES](docs/09-RELEASE-NOTES.md) | Keputusan go/no-go supervisor |
| [SCOPE](manufacturing-knowledge-hub/docs/SCOPE.md) / [SLICE](manufacturing-knowledge-hub/docs/SLICE.md) | Scope terkunci & desain slice-1 |
| [VERIFICATION-LOG](manufacturing-knowledge-hub/docs/VERIFICATION-LOG.md) | Bukti command + hasil + tanggal |

---

## 3. Dataset (`supporting_data/Case 1_ Manufacturing Knowledge Hub/`)

**Total 98 file:** 88 PDF, 8 PNG (P&ID), 1 XLSX (maintenance), 1 PPTX (penjelasan dataset).

### 8 set equipment (masing-masing 11 PDF: 7 OPL + datasheet, GA drawing, interlock, plot plan; + 1 PNG P&ID)

| Set | Tag | Equipment |
| --- | --- | --- |
| 01 | GA-1201A | Hexane Feed Pump |
| 02 | YD-2301 | Polymer Fluid Bed Dryer |
| 03 | DC-3401A | Catalyst Reduction Reactor |
| 04 | KC-4501 | Recycle Gas Compressor |
| 05 | EA-5601 | Solvent Heater |
| 06 | LV-6701 | Separator Level Control Valve |
| 07 | CT-7801 | Cooling Tower Cell Fan |
| 08 | FA-8901 | Reflux Accumulator Drum |

### Temuan audit ([AUDIT.md](manufacturing-knowledge-hub/docs/AUDIT.md))

- **Workbook maintenance terverifikasi 211 record × 31 kolom.** PK `WO_Number` (unik), ~25–28 WO per tag. Detail kolom ada di [DATA-DICTIONARY.md](manufacturing-knowledge-hub/docs/DATA-DICTIONARY.md).
- Kolom penting: `Equipment_Tag`, `Work_Type`, `Discipline` (dipakai untuk scope divisi), `Downtime_Hours`, `*_Cost_IDR`, `Root_Cause`, `Related_Interlock` (`SEQ-xxxx`).
- PDF sampel berupa teks digital asli (bukan scan). Halaman dengan < 50 karakter diberi flag `needs_ocr`.
- PNG P&ID tidak punya teks yang bisa diekstrak, jadi diproses lewat **vision** (deskripsi bertanda provenance). Konektivitas diagram tidak diekstrak.
- PPTX hanya menjadi konteks dan **tidak diindeks** sebagai sumber jawaban.
- Nama folder/file tidak konsisten (varian OPL, `P&ID SET 4.png`, dll.), sehingga diselesaikan via `pathlib` tanpa hard-code.

---

## 4. Peran, divisi, dan RBAC

| Peran | Kewenangan |
| --- | --- |
| **Super Admin** | Akses penuh, analitik token/biaya, audit, konfigurasi gateway LLM |
| **Admin** | Approve pendaftaran, alokasi divisi, upload dokumen, katalog lintas divisi |
| **User** | Operator/engineer: daftar → `pending` → disetujui → akses sesuai divisi |

**Divisi:** Mechanical · Electrical & Instrumentation · Process / Operations · HSE & Reliability.

- Aturan slice-1: **1 user = 1 divisi**. Admin/SuperAdmin bisa membaca semua.
- ACL dokumen diatur eksplisit via `data/division_map.json`. Yang belum dipetakan berstatus `UNREVIEWED`, bukan ditebak dari nama file.
- Baris maintenance: `Discipline` → divisi (Mechanical→Mech, Instrument/Electrical→E&I, Process→Process).
- Policy dipusatkan di `core/policy.py` dan dipakai di katalog, file viewer, Qdrant (pre-filter), graph, SQL, dan session.

---

## 5. Arsitektur & stack

```text
Browser ──► Next.js 14 (App Router, Tailwind) ──HTTP/SSE, cookie httpOnly──► FastAPI
                                                                            ├─ Auth/RBAC (JWT 24h + blocklist, bcrypt)
                                                                            ├─ Chat router: sql | vector | graph | combined
                                                                            ├─ Admin / SuperAdmin (audit, usage, gateway)
                                                                            ├─ PostgreSQL 16: user, chat, maintenance, documents, edges, jobs
                                                                            ├─ Qdrant v1.10.1: koleksi manufacturing_knowledge (1536, cosine)
                                                                            └─ OpenRouter: gpt-4o (primary), claude-sonnet-4.5 (fallback), embedding, vision
```

| Lapisan | Pilihan final (slice-1) |
| --- | --- |
| Backend | Python 3.11-slim (pinned digest), FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic (0001–0006) |
| Frontend | Node 20-alpine, Next 14.2.x, Tailwind 3.4.x, TypeScript |
| DB | `postgres:16-alpine@sha256:…` (16.15) |
| Vector | `qdrant/qdrant:v1.10.1` + `qdrant-client==1.10.1` |
| LLM | **OpenRouter saja**: `openai/gpt-4o`, fallback `anthropic/claude-sonnet-4.5` (claude-3.5-sonnet sudah pensiun) |
| Embedding | `openai/text-embedding-3-small` via OpenRouter (1536 dim) |
| Ekstraksi | PyMuPDF (PDF), pandas/openpyxl (XLSX), vision LLM (PNG) |
| Graph | Tabel relasional PostgreSQL (`KnowledgeEdge`), traversal 1–2 hop. **Tanpa Neo4j** |
| Retrieval | Dense + re-scoring lexical token-overlap + exact-tag + RRF. **Sparse/BM25 & reranker ditunda** |
| Budget | `BUDGET_USD_CAP` + `services/pricing.py`: saat cap tercapai, hanya LLM yang berhenti; jalur lexical/SQL tetap jalan |

### Peta modul backend (`backend/app/`)

- `api/`: `auth.py`, `admin.py` (approval, upload/jobs, audit, usage, gateway config), `chat.py` (ask, ask-stream SSE, upload gambar, transcribe, sessions), `knowledge.py` (katalog, file terotorisasi).
- `services/`: `vector_service` (embedding + search), `graph_service` (traversal + policy), `sql_service` (template SELECT-only, scope divisi, timeout 5 dtk), `llm_gateway` (retry/fallback/usage), `citation` (validasi sitasi berbasis registry), `pipeline`/`ingestion_service` (ekstraksi → chunk → embed), `pricing`.
- `core/`: `config`, `security`, `deps`, `policy`, `database`.

### Halaman frontend

`/login`, `/register`, `/pending`, `/chat`, `/knowledge`, `/knowledge/[id]`, `/admin/users`, `/admin/docs`.
Layout: SlimRail (`#1E56A0`), Sidebar riwayat (collapsible), area chat, Inspector di kanan. Kanvas `#F4F7FA`, tanpa emotikon.

---

## 6. Kontrak jawaban AI (`schemas/chat.py`, `SCHEMA_VERSION = "v1"`)

`ChatAnswer` berisi field berikut:

- `summary_text`, `equipment_tag`, `related_tags`
- `component_type`: salah satu dari `procedure_checklist`, `interlock_logic`, `bom_table`, `root_cause_card`, `kpi_table`, `clarification`, `text_only`
- `component_payload` { `title`, `alert_level` (normal/warning/critical), `details`, `insufficient_evidence` }
- `citations[]` { `document_id`, `document_title`, `page_number`, `snippet`, `source_type` (pdf/png/xlsx), `region`/`bbox`, `row_reference` }
- `sql_query`, `route`

Aturan penting:

- `details` divalidasi **per `component_type`** lewat `DETAIL_MODELS` di `model_validator` *(dicek di kode)*. Tipe field-nya masih `dict`, tetapi isinya tidak lagi bebas.
- Sitasi hanya diterima bila cocok dengan registry dokumen yang READY dan boleh diakses user. Sitasi yang tidak memenuhi syarat dibuang.
- Setpoint/quantity disimpan sebagai string agar "tidak diketahui" tidak tertukar dengan nilai `0`.
- Bila bukti kurang: `insufficient_evidence=true` tanpa angka rekaan (contoh: MTBF, karena formulanya belum disepakati).
- Isi dokumen diperlakukan sebagai DATA, bukan instruksi (mitigasi prompt-injection).

---

## 7. Alur utama

1. **Registrasi → approval:** user daftar dan berstatus `pending`. Admin approve dan mengalokasikan divisi, lalu user bisa login (cookie httpOnly).
2. **Ingestion:**
   - `build_manifest.py` mencocokkan 98 file.
   - `seed_maintenance.py` memasukkan 211 baris ke PostgreSQL (idempoten, lineage `import_batches`).
   - `ingest_docs.py` memproses PDF/PNG → chunk → embedding → Qdrant, dan membuat edge graph (`HAS_OPL`, interlock, dll.).
   - Upload admin melewati tabel `ingestion_jobs` (status PARSING → VECTORIZING → READY, bisa cancel/retry).
3. **Tanya-jawab:**
   - Router memilih jalur `sql` / `vector` / `graph` / `combined`.
   - Retrieval disaring sesuai akses, lalu konteks dirakit (budget 12k).
   - LLM gateway menghasilkan JSON yang divalidasi skema + sitasi, lalu dikirim lewat SSE (progress → final → done).
4. **Inspector:** klik citation chip membuka `knowledge/file/{id}` (otorisasi dicek ulang) dengan `#page=` untuk PDF, region untuk PNG, dan rows untuk XLSX.
5. **Multimodal:** upload gambar PNG/JPEG ≤ 5 MB (vision → `detected_tags`). Suara via MediaRecorder/WebSpeech → transkrip bisa diedit → kirim (tanpa TTS, audio tidak disimpan).

### Use case demo prioritas

1. Troubleshooting vibrasi **VSHH-4505** / trip **SEQ-4501** pada **KC-4501**.
2. Perencanaan seal pompa **GA-1201A** (BOM GA drawing + SOP isolasi).
3. Downtime/biaya **EA-5601** vs **YD-2301** via Text-to-SQL.

### Golden queries ([GOLDEN-QUERIES.md](manufacturing-knowledge-hub/docs/GOLDEN-QUERIES.md))

G-01..G-10 mencakup: graph/interlock, exact-tag, BOM, SQL KPI, akses ditolak, bukti kurang (MTBF), konflik revisi, dan pertanyaan ambigu → klarifikasi.
[EVAL-REPORT](manufacturing-knowledge-hub/docs/EVAL-REPORT.md) mencatat **6/6 route_ok + retrieval hit** (G-01..05, G-08) dengan embedding riil. **G-06, G-07, G-09, G-10 belum dievaluasi.** Belum ada sign-off validator Teknik Kimia.

---

## 8. Riwayat progres (garis waktu)

| Tanggal | Kejadian |
| --- | --- |
| 18 Sep | Discovery: dokumen 01–06 dibuat, semua keputusan D-xx masih TERBUKA |
| 19 Sep | Supervisi pertama: **1/68 OK**, 47 sebagian, 20 belum ada. Audit data mengonfirmasi 211×31 |
| 20 Sep | Status strict-05: **45 OK / 17 sebagian / 2 salah / 4 belum** |
| 28 Sep | Sesi lokal (sqlite): pytest 10 passed, run_checks 22/22, E2E HTTP 32/32, `npm run build` OK |
| 1 Okt | Sesi Docker: 4/4 service healthy, ingest 96 dokumen, eval riil. Tiga blocker diklaim diperbaiki, scope dikunci (PoC, OpenRouter-only), budget guard, VALIDATION-PACK untuk validator |
| 1 Okt | Release notes supervisor: NO-GO final, GO bersyarat demo |
| 4 Okt | **Deadline submit** |

---

## 9. Status blocker & gap (posisi terkini)

> `08-IMPLEMENTATION-STATUS.md` dan `09-RELEASE-NOTES.md` ditulis **sebelum** perbaikan yang tercatat di VERIFICATION-LOG #15–23 (sesi release 1 Okt). Tabel di bawah menggabungkan keduanya.

| Item | Status menurut 08/09 | Posisi terkini |
| --- | --- | --- |
| T4.5 graph bocor lintas divisi | Blocker | **Sudah diperbaiki.** Edge tanpa evidence yang terpetakan kini ditolak (deny), evidence workbook mengikuti disiplin baris WO *(dicek di `graph_service.py`)* |
| T2.10 archive tidak purge Qdrant | Blocker | Diklaim diperbaiki (purge seperti delete, terbukti di E2E). Belum dicek ulang di kode |
| T4.3 typo `HAS_INSTRUMENT` | Blocker | **False positive.** Ejaan sudah kanonis, ditambah tes regresi |
| T4.11 shadowing `model` | Bug | Sudah benar (`details_model`), ditambah tes anti-regresi |
| T4.10 `details` dict bebas | Wajib sebelum final | Divalidasi per tipe via `model_validator` + fixtures |
| T5.3 Idempotency-Key `/ask-stream` | Wajib | Diklaim sudah ditambahkan |
| T2.9/T7.2 tabel job, progres, cancel | Wajib | Diklaim ada (`ingestion_jobs`, migrasi 0006) |
| T1.2 lockfile backend | Wajib | `requirements.lock` ada |
| T2.6 vision di ingest PNG | Wajib | Diklaim tersambung (dengan fallback jujur) |
| T4.6 role DB read-only | Wajib | Didokumentasikan di RUNBOOK (belum diterapkan di compose) |
| T4.1 lexical independen | Wajib | **Ditunda resmi.** Lexical hanya re-scoring kandidat dense, sehingga recall terbatas |

### Masih terbuka / risiko untuk demo

- **E2E 5 item belum terbukti:**
  1. 404 file lintas divisi,
  2. agregat SQL lintas divisi,
  3. Inspector manual (PDF/PNG/XLSX),
  4. upload PNG manual,
  5. reopen riwayat di sidebar.
- **Validator/UAT:** sign-off tim Teknik Kimia atas G-01..G-10 (T0.3, T8.6) belum ada.
- **Matriks akses penuh** (T3.7) belum diuji end-to-end.
- **Graph:** tanpa konektivitas P&ID nyata. Relasi hanya dari OPL/interlock/maintenance.
- **Batasan path `!`:** `npm run build` gagal di path `! Hackathon` (keterbatasan webpack). Build lewat Docker atau salin ke path lain.
- **Keamanan config:** `.env` berisi `OPENROUTER_API_KEY` dan **tidak boleh di-commit**. `.env.example` memakai kredensial demo default.
- **Git:** sebagian besar kode aplikasi masih *untracked* (hanya docs yang ter-commit, 3 commit). Perlu commit sebelum submit.

### Saran saat demo (dari release notes)

Tampilkan hanya alur yang E2E-nya sudah `[x]`. Hindari pertanyaan lintas divisi via graph, dokumen ARCHIVED, dan retry stream ganda. Sampaikan item yang masih terbuka kepada juri.

---

## 10. Cara menjalankan (ringkas)

```bash
cd manufacturing-knowledge-hub
cp .env.example .env      # isi JWT_SECRET, OPENROUTER_API_KEY, BOOTSTRAP_ADMIN_* (sekali)
docker compose up --build -d
# backend http://localhost:8000/docs · frontend http://localhost:3000

alembic upgrade head
python scripts/build_manifest.py --source ../supporting_data --out data/manifest.json
python scripts/seed_maintenance.py --xlsx "../supporting_data/Case 1_ Manufacturing Knowledge Hub/Maintenance History (All Equipment).xlsx"
python scripts/ingest_docs.py --source ../supporting_data

pytest backend/tests -q
python backend/tests/run_checks.py
python scripts/eval_golden.py
```

Detail backup/restore dan role read-only ada di [RUNBOOK.md](manufacturing-knowledge-hub/docs/RUNBOOK.md).
