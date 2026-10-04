# T7.5 — LLM Rate Reference (NOT a bill)

Status: EXAMPLE rates for order-of-magnitude estimates in `/admin/usage`.
**Override `estimate_cost` in `backend/app/api/admin.py` with contract rates
before any billing or chargeback use.** Record source + date below when changed.

| Provider | Model | Assumed blended cost/answer (USD) | Source | Date |
|---|---|---|---|---|
| openai | gpt-4o | 0.004 | EXAMPLE placeholder | 2026-09-20 |
| openrouter | anthropic/claude-sonnet-4.5 | 0.005 | EXAMPLE placeholder | 2026-09-20 |
| (other) | (other) | 0.004 fallback | EXAMPLE placeholder | 2026-09-20 |

Method: cost is estimated per persisted assistant answer (`llm_usage` rows),
not per token — token accounting per request is TERBUKA (needs provider usage
fields persisted per call).
