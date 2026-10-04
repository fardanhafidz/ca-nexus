"""T4.1/T4.2 — Dense + lexical + exact-tag retrieval with RRF fusion (Q-HYB-01..04).

Honest hybrid (docs/SLICE.md): dense Qdrant (server-side pre-filter by collection
payload) + in-house lexical token-overlap over the same candidate set +
exact-tag matching. Fused with Reciprocal Rank Fusion, deduplicated by chunk ID.
Sparse vectors / external BM25 remain TERBUKA.

Every path applies the division pre-filter BEFORE candidates reach the LLM context
(post-filtering alone is rejected by T4.1 acceptance).
"""
from __future__ import annotations
import logging, re
from collections import Counter
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from openai import OpenAI
from ..core.config import settings
from ..core import policy as access_policy

log = logging.getLogger("mkh.retrieval")
TAG_RE = re.compile(r"\b([A-Z]{1,4}[-_ ]?\d{3,5}[A-Z]?)\b")
COLLECTION = settings.QDRANT_COLLECTION
RRF_K = 60


def normalize_tag(t: str) -> str:
    return re.sub(r"[\s_]+", "-", t.strip().upper())


def extract_tags(text: str) -> list[str]:
    return sorted({normalize_tag(m.group(1)) for m in TAG_RE.finditer(text.upper())})


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def ensure_collection(dim: int | None = None):
    c = _client()
    try:
        c.get_collection(COLLECTION)
        return
    except Exception:
        from qdrant_client.models import VectorParams, Distance
        c.create_collection(COLLECTION, vectors_config=VectorParams(
            size=dim or settings.EMBEDDING_DIM, distance=Distance.COSINE))


def _check_dim(client: QdrantClient, vec: list[float]) -> None:
    try:
        info = client.get_collection(COLLECTION)
        want = info.config.params.vectors.size  # type: ignore[union-attr]
        if want != len(vec):
            raise ValueError(f"Embedding dim mismatch: index={want} query={len(vec)} — re-embed with {settings.EMBEDDING_MODEL}")
    except ValueError:
        raise
    except Exception:
        pass


LAST_EMBED_SOURCE = "dev"  # openai | openrouter | dev (see embed_source())


def embed_source() -> str:
    """Which embedding backend produced the last vectors (honesty for eval/demo)."""
    return LAST_EMBED_SOURCE


def _embed_openai(texts: list[str], timeout: int) -> list[list[float]]:
    import logging as _logging
    _log = _logging.getLogger("mkh.retrieval")
    client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=timeout)
    usage_total = 0
    out: list[list[float]] = []
    for i in range(0, len(texts), 32):
        for attempt in range(settings.LLM_MAX_RETRIES + 1):
            try:
                r = client.embeddings.create(model=settings.EMBEDDING_MODEL, input=texts[i:i + 32])
                usage_total += r.usage.total_tokens if r.usage else 0
                out.extend(d.embedding for d in r.data)
                break
            except Exception:
                if attempt >= settings.LLM_MAX_RETRIES:
                    raise
    _log.info("embed usage_tokens=%s model=%s", usage_total, settings.EMBEDDING_MODEL)
    return out


def _embed_openrouter(texts: list[str], timeout: int) -> list[list[float]]:
    """D-16: embeddings via OpenRouter (no OpenAI key). Model slug needs the
    openai/ prefix on OpenRouter; dimension must stay 1536 (collection unchanged)."""
    import httpx
    model = settings.EMBEDDING_MODEL
    if "/" not in model:
        model = f"openai/{model}"
    out: list[list[float]] = []
    for i in range(0, len(texts), 32):
        last: Exception | None = None
        for _ in range(settings.LLM_MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=timeout) as c:
                    r = c.post(
                        "https://openrouter.ai/api/v1/embeddings",
                        headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                        json={"model": model, "input": texts[i:i + 32]},
                    )
                    r.raise_for_status()
                    data = r.json()["data"]
                vecs = [row["embedding"] for row in data]
                break
            except Exception as e:
                last = e
        else:
            raise last or RuntimeError("embedding failed")
        out.extend(vecs)
    if out and len(out[0]) != settings.EMBEDDING_DIM:
        raise ValueError(f"Embedding dim {len(out[0])} != {settings.EMBEDDING_DIM} — collection unchanged required")
    log.info("embed via openrouter model=%s n=%d", model, len(texts))
    return out


def embed(texts: list[str]) -> list[list[float]]:
    global LAST_EMBED_SOURCE
    if not texts:
        return []
    timeout = settings.LLM_TIMEOUT_S
    if settings.OPENAI_API_KEY:
        LAST_EMBED_SOURCE = "openai"
        return _embed_openai(texts, timeout)
    if settings.OPENROUTER_API_KEY:
        LAST_EMBED_SOURCE = "openrouter"
        return _embed_openrouter(texts, timeout)
    # DEV-ONLY deterministic vectors so the pipeline runs without a key.
    # FORBIDDEN for eval/demo (team decision D-16); offline CI only.
    import hashlib
    LAST_EMBED_SOURCE = "dev"
    log.warning("No embedding key — using non-semantic dev embeddings (CI offline only, never eval/demo)")
    out = []
    for t in texts:
        h = hashlib.md5(t.encode()).digest()
        out.append([((b / 255.0) - 0.5) for b in h] + [0.0] * (settings.EMBEDDING_DIM - 16))
    return out


def upsert(points: list[dict]) -> None:
    from qdrant_client.models import PointStruct
    c = _client()
    c.upsert(COLLECTION, [PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"]) for p in points])


def _prefilter(role: str, division: str) -> Filter | None:
    """Server-side Qdrant filter. Users: division_access == division OR All.
    (Comma-list payloads can't be pre-filtered exactly → coarse `All` match +
    precise Python check in `_allowed`. Admins: no filter.)"""
    if access_policy.is_privileged(role):
        return None
    return Filter(should=[
        FieldCondition(key="division_access", match=MatchValue(value=division)),
        FieldCondition(key="division_access", match=MatchValue(value="All")),
    ])


def _allowed(payload: dict, division: str, role: str) -> bool:
    return access_policy.doc_visible(payload.get("division_access", "All"), division, role)


def _rrf(ranks: list[list[str]]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in ranks:
        for rank, pid in enumerate(ranking):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (RRF_K + rank + 1)
    return scores


def search(query: str, division: str, top_k: int | None = None, role: str = "user") -> list[dict]:
    """Return ranked evidence with per-source scores and locators (T4.1 acceptance)."""
    top_k = top_k or settings.RETRIEVAL_TOP_K
    c = _client()
    tags = extract_tags(query)
    vec = embed([query])[0]
    _check_dim(c, vec)
    prefilter = _prefilter(role, division)
    dense = c.query_points(COLLECTION, query=vec, limit=top_k * 4,
                           query_filter=prefilter, with_payload=True).points
    by_id: dict[str, dict] = {}
    for h in dense:
        p = h.payload or {}
        if not _allowed(p, division, role):
            continue
        by_id[str(h.id)] = {"score_dense": float(h.score), "payload": p, "id": str(h.id)}
    # Lexical token-overlap over the same candidate set (same source/chunk/revision)
    qtokens = Counter(tokenize(query))
    for pid, item in by_id.items():
        ctokens = Counter(tokenize(str(item["payload"].get("text", "")) + " " + str(item["payload"].get("equipment_tag", ""))))
        overlap = sum(min(qtokens[t], ctokens[t]) for t in qtokens)
        item["score_lexical"] = overlap / max(sum(qtokens.values()), 1)
    # Exact-tag channel
    for pid, item in by_id.items():
        p = item["payload"]
        ptags = {normalize_tag(str(p.get("equipment_tag", "")))}
        text = str(p.get("text", "")).upper()
        hits = [t for t in tags if t in ptags or t in text]
        item["score_tag"] = 1.0 if hits else 0.0
        item["matched_tags"] = hits
    dense_rank = sorted(by_id, key=lambda pid: -by_id[pid]["score_dense"])
    lex_rank = sorted(by_id, key=lambda pid: -by_id[pid]["score_lexical"])
    tag_rank = sorted(by_id, key=lambda pid: (-by_id[pid]["score_tag"], -by_id[pid]["score_dense"]))
    # DEL-B8: dense-only comparison mode + cosine threshold (config-recorded)
    if settings.HYBRID_MODE == "dense-only":
        fused = {pid: 1.0 / (RRF_K + rank) for rank, pid in enumerate(dense_rank)}
    else:
        fused = _rrf([dense_rank, lex_rank, tag_rank])
    # Exact-tag priority boost (configured, recorded)
    for pid in by_id:
        if by_id[pid]["score_tag"] > 0:
            fused[pid] += 0.05
    if settings.RETRIEVAL_MIN_DENSE > 0:
        fused = {pid: s for pid, s in fused.items()
                 if by_id[pid]["score_dense"] >= settings.RETRIEVAL_MIN_DENSE}
    ranked = sorted(fused, key=lambda pid: -fused[pid])[:top_k]
    return [{
        "id": pid, "score": fused[pid],
        "score_dense": by_id[pid]["score_dense"], "score_lexical": by_id[pid]["score_lexical"],
        "score_tag": by_id[pid]["score_tag"], "matched_tags": by_id[pid].get("matched_tags", []),
        "payload": by_id[pid]["payload"],
    } for pid in ranked]
