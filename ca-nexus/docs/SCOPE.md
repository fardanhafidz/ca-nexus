# T0.1 — Scope Rilis (LOCKED D-01/D-28 oleh tim CALIBER2Ø26, 1 Oktober 2026)

Status: DISEPAKATI untuk babak ini. Klaim semantik penuh DITUNDA (lihat keputusan embedding).
Keputusan terkait: D-01, D-28. Pertanyaan: Q-SCP-01..06.

## Keputusan terkunci
- Target: PoC hackathon Manufacturing Knowledge Hub (BUKAN produksi).
- Deadline submit: 4 Oktober 2026 (3 hari). Artefak wajib: demo + slide presentasi + website prototype.
- Tim (3 orang): Hacker (build + integrasi), Bisnis/Presentasi (slide + script + narasi),
  Teknik Kimia (validator teknis + akurasi domain industri).
- Slice rilis = slice-1 di bawah: 4 container lokal, graph relasional PG (tanpa Neo4j),
  suara tanpa TTS, usage/gateway bertahap.
- Validator: tim Teknik Kimia menilai G-01..G-10 + rumus + sign-off UAT (D-26).
  AI hanya asisten validator (ringkasan + flag beda); tanpa tanda tangan = belum selesai.
- Embedding/generation: OpenRouter saja (tanpa OpenAI key) — generation
  `openai/gpt-4o`, embedding `openai/text-embedding-3-small` (1536, koleksi tetap),
  fallback `anthropic/claude-sonnet-4.5` (3.5-sonnet pensiun — deviasi tercatat).
  Dev-embedding acak DILARANG untuk evaluasi/demo (CI offline saja).
- Budget: quota + usage per query di halaman admin; stop saat mendekati budget,
  sisanya lexical/exact-tag gratis.

## Tahap (usulan awal, kini terkunci di atas)
PoC hackathon (fungsional, bukan produksi). Audiens: juri teknis + operasional.
Penyerahan: repo + video demo + deck (batas gabungan ≤ 10 MB — klaim panitia, belum terverifikasi).
Tim: terkunci di atas (Hacker, Bisnis/Presentasi, Teknik Kimia sebagai validator).

## F-01–F-15: masuk / tunda (usulan slice pertama)
| ID | Fitur | Slice-1 |
|---|---|---|
| F-01 registrasi+approval | Masuk (dasar; tanpa notifikasi email) |
| F-02 auth+RBAC | Masuk (JWT + filter backend; refresh/logout bertahap) |
| F-03 repository | Masuk (katalog + viewer terotorisasi) |
| F-04 ingestion/import | Masuk (PDF/PNG→Qdrant; XLSX→PG; PPTX konteks saja) |
| F-05 hybrid | Masuk (dense + lexical token-overlap + exact-tag + RRF; sparse vector ditunda) |
| F-06 graph | SEBAGIAN (relasional PG 1–2 hop; tanpa Neo4j) |
| F-07 JSON terstruktur | Masuk |
| F-08 4 rich component | Masuk |
| F-09 sitasi+Inspector | Masuk (registry-only, per T4.9) |
| F-10 analitik SQL | Masuk (template read-only + scope divisi) |
| F-11 chat/history | Masuk (JSON final + SSE; tanpa WS) |
| F-12 multimodal | SEBAGIAN (gambar upload+vision; suara STT→edit→kirim; tanpa TTS) |
| F-13 admin users | Masuk |
| F-14 admin docs | Masuk |
| F-15 super admin | SEBAGIAN (akses penuh + counts; usage/biaya + gateway-config bertahap) |

## Use case prioritas (usulan, terkait T0.3)
1. Troubleshooting vibrasi VSHH-4505 / trip SEQ-4501 pada KC-4501 (OPL-KC-4501-05 + interlock).
2. Perencanaan seal pompa GA-1201A (BOM GA drawing + SOP isolasi).
3. Downtime/biaya EA-5601 & YD-2301 via Text-to-SQL.

## Penundaan resmi slice-1 (tercatat, bukan diam-diam — DEL-B8/B9/F5/F6)
- Reranker eksternal + sparse vectors: retrieval = dense + lexical token-overlap + exact-tag + RRF.
- Multi-card per respons + error-envelope JSON terpisah: satu komponen + `insufficient_evidence` + banner error generik.
- Checklist persistence backend: state centang session-UI saja (reset saat refresh), bukan work-record resmi.
- Sitasi per-row otomatis dari LLM: header tabel menampilkan `source` bila payload menyediakannya; granuralitas per-row penuh ditunda.
- Per-edge revision/access tracking: edge membawa `evidence_doc` (+ versi dokumen bila dari ingest); histori revisi per relasi ditunda.
- Token login httpOnly cookie (disahkan; lihat `.env.example` `COOKIE_SECURE`).
- Purge retensi otomatis: manual per `docs/RETENTION.md` (tanpa scheduler di slice-1).
