"""T7.5 budget — shared rates + monthly spend (admin API + chat enforcement)."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

# EXAMPLE rates (USD per persisted answer). Override with contract rates before
# any billing use. Source/date recorded in docs/PRICING.md.
RATES: dict[tuple[str, str], float] = {
    ("openai", "gpt-4o"): 0.004,
    ("openrouter", "openai/gpt-4o"): 0.004,
    ("openrouter", "anthropic/claude-sonnet-4.5"): 0.005,
}
FALLBACK_RATE = 0.004


def estimate_cost(provider: str, model: str, answers: int) -> float:
    return round(RATES.get((provider, model), FALLBACK_RATE) * answers, 4)


def monthly_spend(db: Session) -> tuple[float, int]:
    """Returns (est_usd, answer_count) for the trailing 30 days."""
    from ..models.maintenance import LLMUsage
    since = datetime.now(timezone.utc) - timedelta(days=30)
    rows = db.query(LLMUsage).filter(LLMUsage.created_at >= since).all()
    total = 0.0
    for r in rows:
        if r.provider == "none":
            continue  # fallback/unsupported paths cost nothing
        total += estimate_cost(r.provider, r.model, 1)
    return round(total, 4), len(rows)
