# DEL-I4 / T7.4 — Retention windows (slice-1 proposal, enforce per deployment)

| Data | Window | Enforcement | Note |
|---|---|---|---|
| Documents + revisions | Competition + evaluation period | manual (Admin delete/archive) | T2.10 endpoints; backups per RUNBOOK |
| Chat sessions/messages | Competition + evaluation period | manual (user delete) | ownership-checked deletes |
| Attachments (images) | Same as owning session | manual (deleted with session) | session-scoped, never global knowledge |
| Raw audio | Never stored server-side | by design (`/transcribe` returns transcript only) | see `chat.py:transcribe` |
| Audit logs | Competition + evaluation period | manual | filter/pagination in Admin UI |
| LLM usage rows | 365 days queryable, 30-day dashboard default | manual | per-provider/model/actor |
| Idempotency keys | 24 h validity window | manual purge (`DELETE FROM idempotency_keys WHERE created_at < now() - interval '7 days'`) | repeats outside window answer fresh |

Automated purge jobs are TERBUKA (no scheduler in slice-1); run the SQL above from
the runbook before handover, or record retention sign-off in UAT.
