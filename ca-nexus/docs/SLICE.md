# T0.4 — Desain Slice Pertama (mengikat implementer)

Keputusan: D-02, D-03, D-04, D-05, D-06, D-17, D-18, D-19, D-25.

- Root repo: `manufacturing-knowledge-hub/` di workspace `Caliber2026`; dataset tetap di
  `supporting_data/` via `SOURCE_ROOT` + mount read-only (tanpa duplikasi 98 file).
- Stack: Python 3.11-slim, Node 20-alpine, Next 14.2.x, Tailwind 3.4.x, SQLAlchemy 2.0.x,
  Pydantic v2, Qdrant v1.10.1, PyMuPDF, pandas/openpyxl, embedding
  `openai/text-embedding-3-small` via OpenRouter (1536, cosine, koleksi tetap) +
  generation `openai/gpt-4o` via OpenRouter, fallback `anthropic/claude-sonnet-4.5`
  (D-16 locked 2026-10-01; tanpa OpenAI key; dev-embedding acak dilarang eval/demo).
- Deployment slice: 4 container Compose lokal; URL internal `http://qdrant:6333` vs host
  `http://localhost:6333` dibedakan via `QDRANT_URL` / `QDRANT_PUBLIC_URL`.
- ACL: 1 user = 1 divisi; Admin/SuperAdmin baca penuh; dokumen `division_access` eksplisit
  via `data/division_map.json` + kebijakan `UNREVIEWED` (tidak tebak dari filename).
- Session: JWT Bearer 24h + refresh/logout/revocation (blocklist); kredensial bootstrap
  dari secret, bukan default keras.
- Schema slice: `ChatAnswer` v1 + 6 `component_type` + `citation` registry-only;
  streaming SSE + JSON final; error envelope generik (tanpa traceback/provider leak).
- Masih TERBUKA: sparse vector, reranker, Neo4j, OCR lokal vs vision cost, TTS,
  CI/CD, backup/retensi. (Usage/kuota + gateway runtime-config SUDAH masuk slice-1.)
- DITUNDA resmi (lihat `docs/SCOPE.md`): reranker eksternal, multi-card, error-envelope
  terpisah, persistensi checklist backend, sitasi per-row otomatis, tracking revisi
  per-edge, purge retensi otomatis.
- T4.1 LEXICAL = re-scoring token-overlap di atas himpunan kandidat dense yang sama
  (bukan indeks sparse/BM25 independen). Konsekuensi recall yang jujur: query yang
  tidak mirip vektor tidak akan muncul lewat jalur lexical; sparse/BM25 DITUNDA.
