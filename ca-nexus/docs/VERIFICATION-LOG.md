# VERIFICATION-LOG — bukti command + result + tanggal (§7.4/DEL-V1)

Aturan: hanya item dengan baris log di bawah yang boleh dianggap terbukti.

## 2026-09-28 (sesi awal: sqlite lokal, tanpa Qdrant/LLM key)
1. `python -m py_compile` seluruh `backend/**/*.py` + `scripts/*.py` + `migrations/**/*.py` → OK.
2. `run_checks.py` → 22/22; `pytest` → 10 passed; `tsc --noEmit` bersih (setelah fix `audio.ts`).
3. `alembic upgrade head` (sqlite) → 13 tabel, v0004; manifest 98 reconciled; seed 211 + rerun.
4. E2E HTTP sqlite 32/32 (auth→KPI→SSE→transcribe→gateway→kuota→arsip→logout).
5. Runtime finds (diperbaiki): pin `bcrypt==4.0.1`, snapshot user + `expire_on_commit=False`,
   `_quota_err` NameError, urutan snapshot SSE, shadowing `model`→KpiDetails, workbook registry.
6. `npm run build` 9 route OK di salinan path tanpa `!` (`!` = batasan webpack, bukan bug kode);
   `package-lock.json` 217 KB.

## 2026-10-01 (sesi Docker: daemon direstart user, disk 17,9 GB, OPENROUTER key di .env)
7. `docker compose config` valid; **4/4 service healthy** (postgres, qdrant v1.10.1, backend, frontend).
8. Pin reproduksibel terverifikasi-run: `python:3.11-slim@sha256:e416…` (=3.11.16;
   tag 3.11.9-slim rusak di host ini), `postgres:16-alpine@sha256:7218…` (=16.15;
   tag 16.3-alpine entrypoint rusak), `qdrant:v1.10.1` (healthcheck bash `/dev/tcp`
   karena image tanpa wget/curl), `qdrant-client==1.10.1` (1.9.0 belum punya
   `query_points`; keduanya diverifikasi di PyPI + Docker Hub). Lifespan path migrasi diperbaiki.
9. `seed_maintenance.py` → 211 accepted; `ingest_docs.py` → **96/96 docs, 96 chunks**,
   8 PNG vision-pending; koleksi Qdrant terisi (dev embeddings — tanpa OpenAI key).
10. `eval_golden.py` (PG + Qdrant riil): G-01/G-02/G-03 hit, G-04/G-05 reproducible,
    G-08 unsupported — **6/6 route_ok**.
11. E2E HTTP container **32/32** + MTBF live → insufficient/unsupported +
    upload PDF → PARSING→READY + XLSX ditolak dengan pointer seed.
12. OpenRouter live: model brief `claude-3.5-sonnet` SUDAH PENSIUN (404 no endpoints);
    default diganti `anthropic/claude-sonnet-4.5` (200 terverifikasi) + `LLM_ORDER`
    openrouter-first + `max_tokens` 1500 + parser JSON toleran fence.
    Jawaban Claude grounded dan jujur pada evidence yang ada.
13. `run_checks.py` **25/25**; `pytest` **10 passed** (final).
14. Sisa jujur: retrieval bermakna butuh embedding OpenAI (dev embeddings non-semantik);
    UAT validator + demo interaktif (sisa DEL-V2/V3: uji abort/disconnect live,
    klik UI Inspector manual, UAT) menunggu sesi demo.

## 2026-10-01 (sesi release: 3 blocker + PROMPT-B/C/D)
15. Blocker T4.5: graph evidence tanpa mapping kini DENY (scope WO ikut disiplin
    baris, bukan blanket All); tes 3 persona hijau di `run_checks`.
    Blocker T2.10: archive purge Qdrant seperti delete (terbukti E2E hide).
    Blocker T4.11: sudah benar (`details_model`); tambah tes anti-regresi.
    T4.3: **FALSE POSITIVE** — scan byte-level seluruh repo: semua literal `HAS_*`
    kanonis + tes regresi; tidak ada typo untuk diperbaiki.
16. PROMPT-B: validator `details` di `ChatAnswer.model_validator` + fixtures
    valid/invalid; fallback `source_type` dari ekstensi; lexical=defer di SLICE;
    role read-only + GRANT di RUNBOOK; vision tersambung ke ingest (fallback jujur).
17. PROMPT-C: tabel `ingestion_jobs` (migrasi 0006) + progres/cancel kooperatif/retry
    + UI jobs; `requirements.lock` 68 baris dari venv bersih; Idempotency-Key di
    `/ask-stream` (replay + simpan); minors frontend (`RegForm`, key stabil, catch).
18. PROMPT-D: restart 4/4 healthy + counts identik; failure injection 208/3 + alasan
    per baris, tabel tetap 211; `EVAL-REPORT.md`; perf live (`me` 0,01 dtk, KPI ~10 dtk
    via Claude, unsupported 0,02 dtk, 5x konkurensi 200 semua); clean-boot `down -v` →
    up 4/4 → restore dump 581 KB (211/99/3, alembic 0006) → re-ingest 96 poin;
    E2E container final **32/32**; `run_checks` **29/29**.

## 2026-10-01 (keputusan tim CALIBER2Ø26 locked: PoC, deadline 4 Okt, OpenRouter-only)
19. Embedding via OpenRouter (`openai/text-embedding-3-small`, 1536, koleksi tetap) +
    generation `openai/gpt-4o` via OR + fallback `anthropic/claude-sonnet-4.5`
    (3.5-sonnet pensiun — deviasi tercatat); `LLM_ORDER` + `provider_order` runtime;
    vision ikut urutan provider; Qdrant terisi ulang vektor RIIL (1536 nonzero).
20. Eval semantik riil **6/6 route_ok + hit**; `EVAL-REPORT.md` diregenerasi.
21. Budget guard: `BUDGET_USD_CAP` + `services/pricing.py` + stop-LLM-saja (gratis
    jalan terus) + spend/cap di UI admin + `.env.example`; tes cap hijau.
22. `scripts/validate_assist.py` → `docs/VALIDATION-PACK.md` 10 kasus untuk validator
    Teknik Kimia (ringkasan + flag + checkbox + sign-off; AI tak menilai sendiri).
23. Temuan runtime sesi ini (diperbaiki): baris `BUDGET_USD_CAP`/`LLM_TIMEOUT_S`
    tergabung (hilang newline) → embed mati; restart discipline (mount live tapi
    import saat startup); sitasi model kosong → auto-attach evidence terambil;
    validasi sitasi longgar jujur (coerce null/enum + fuzzy 0.85 + snippet chunk);
    prompt wajibkan sitasi. Pack final: jawaban grounded + sitasi (interlock/KPI/BOM/
    clarification); E2E **32/32**; `run_checks` **31/31**; SCOPE/SLICE locked D-01.
