"""T4.7/T4.11 — Routed, validated, citation-checked answering (D-15/D-17/D-18).

Route → scoped retrieval (policy-filtered BEFORE context) → generation →
Pydantic validation → citation resolution → persistence (single-encoded JSON).
Document content is evidence only: it never changes role/scope/tool behavior.
"""
import json, logging, re, uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.deps import get_current_user
from ..core.config import settings
from ..core import policy as access_policy
from ..models.maintenance import ChatSession, ChatMessage, AuditLog, IdempotencyKey
from ..schemas.chat import (
    ChatAsk, ChatAnswer, Citation, ComponentPayload, DETAIL_MODELS, SCHEMA_VERSION,
)
from ..services import vector_service, sql_service, graph_service, llm_gateway, citation as citation_svc

log = logging.getLogger("mkh.chat")
router = APIRouter(prefix="/chat", tags=["chat"])
STORE = Path(settings.FILE_STORAGE_ROOT)

TOKEN_BUDGET_CHARS = 12000
ATTACHMENTS = STORE / "attachments"


def _history(db: Session, sid: str) -> str:
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == sid).order_by(ChatMessage.created_at.desc()).limit(6).all()
    return "\n".join(f"{m.role}: {m.text[:500]}" for m in reversed(msgs))


def _get_session(db: Session, sid: str | None, user, message: str) -> ChatSession:
    if not sid:
        s = ChatSession(user_id=user.id, title=message[:80])
        db.add(s)
        db.commit()
        db.refresh(s)
        return s
    s = db.get(ChatSession, sid)
    if not s or (s.user_id != user.id and not access_policy.is_privileged(user.role)):
        raise HTTPException(403, "Session not authorized")
    return s


RELATION_CUES = re.compile(
    r"(protect|interlock|trip|connected|related|relation|sensor of|instrument of|caused by|leads to|triggers?)", re.I)


def _route_trace(message: str) -> dict:
    """DEL-B14: formal classification with trace (route + signals)."""
    tags = vector_service.extract_tags(message)
    if sql_service.unagreed_metric(message):
        return {"route": "unsupported", "tags": tags, "wants_sql": False,
                "hybrid_mode": settings.HYBRID_MODE,
                "reason": "metric formula unagreed (G-08)"}
    wants_sql = sql_service.needs_sql(message)
    relational = len(tags) > 1 or bool(RELATION_CUES.search(message))
    if wants_sql and not tags:
        route = "sql"
    elif wants_sql:
        route = "combined"
    elif tags and relational:
        route = "graph"
    elif tags:
        route = "vector"  # single equipment tag, no relation asked (G-03)
    else:
        route = "vector"
    return {"route": route, "tags": tags, "wants_sql": wants_sql,
            "relational": relational, "hybrid_mode": settings.HYBRID_MODE}


def _route(message: str) -> str:
    return _route_trace(message)["route"]


def _check_quota(db: Session, user) -> None:
    """T7.5 monthly per-user answer cap (NULL quota = unlimited)."""
    quota = getattr(user, "quota_queries", None)
    if not quota:
        return
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = db.query(ChatMessage).join(ChatSession, ChatMessage.session_id == ChatSession.id).filter(
        ChatSession.user_id == user.id, ChatMessage.role == "assistant",
        ChatMessage.created_at >= month_start).count()
    if used >= quota:
        raise HTTPException(429, f"Monthly query quota reached ({quota}). Contact an administrator.")


def _record_usage(db: Session, user, provider: str, model: str, ok: bool, ms: int) -> None:
    from ..models.maintenance import LLMUsage
    db.add(LLMUsage(user_id=user.id, provider=provider, model=model, ok=ok, latency_ms=ms))


def _answer(message: str, db: Session, user, attachment_text: str = "") -> tuple[ChatAnswer, str, str, bool]:
    from types import SimpleNamespace
    # DEL-V2 runtime find: snapshot request-user attrs up front. Mid-request
    # commits must never break downstream access via detached instances.
    u = SimpleNamespace(id=user.id, division=user.division, role=user.role,
                        email=user.email, full_name=user.full_name)
    full_query = (message + "\n" + attachment_text).strip()
    tags = vector_service.extract_tags(full_query)
    primary = tags[0] if tags else None
    trace = _route_trace(message)
    route = trace["route"]
    if route == "unsupported":
        # G-08: unagreed metric — honest insufficient-evidence, no number invented.
        no_ev = ChatAnswer(
            summary_text=("This metric has no agreed formula in slice-1 "
                          "(see docs/DATA-DICTIONARY.md). No value was computed."),
            equipment_tag=primary, component_type="text_only",
            component_payload=ComponentPayload(title="Unsupported metric", alert_level="warning",
                                               details={}, insufficient_evidence=True),
            citations=[], route="unsupported")
        _record_usage(db, u, "none", "unsupported-metric", True, 0)
        return no_ev, "none", "unsupported-metric", True

    sql_rows, sql_text = [], None
    if route in ("sql", "combined"):
        try:
            sql_text, params = sql_service.build_sql(message, primary, role=u.role, division=u.division)
            sql_rows = sql_service.run(db, sql_text, params, role=u.role, division=u.division)
        except Exception:
            log.exception("analytic query failed")
            sql_rows, sql_text = [], None

    try:
        hits = vector_service.search(full_query, u.division, top_k=settings.RETRIEVAL_TOP_K, role=u.role)
    except Exception:
        log.exception("vector retrieval unavailable — continuing without document evidence")
        hits = []
    by_id = {h["id"]: h for h in hits}
    graph_ctx = graph_service.neighbors(db, primary, depth=2, division=u.division, role=u.role) \
        if primary else []

    evidence_parts = []
    _seen_ev = set()
    for h in hits:
        p = h["payload"]
        key = (p.get("doc_title"), p.get("page_number"))  # DEL-B14: dedup repeated chunks
        if key in _seen_ev:
            continue
        _seen_ev.add(key)
        evidence_parts.append(
            f"- [{p.get('doc_title')} p.{p.get('page_number')} | {p.get('equipment_tag')}] "
            f"{(p.get('text', '')[:800])}")
    evidence = "\n".join(evidence_parts)
    if sql_rows:
        evidence += f"\nSQL result ({sql_text}):\n{json.dumps(sql_rows[:10])}\n"
    if graph_ctx:
        evidence += "\nGraph relations:\n" + "\n".join(
            f"{g['src']} --{g['relation']}--> {g['dst']} (ev: {g['evidence']})" for g in graph_ctx[:10])
    evidence = evidence[:TOKEN_BUDGET_CHARS]  # T4.7 context budget, retrieval-priority order kept

    import time as _time
    _t0 = _time.time()
    from ..services.pricing import monthly_spend
    _spend, _ = monthly_spend(db)
    if settings.BUDGET_USD_CAP > 0 and _spend >= settings.BUDGET_USD_CAP:
        # D-16 budget rule: stop LLM spend; SQL/extractive/lexical paths keep working free.
        log.warning("budget cap reached ($%s); LLM skipped", settings.BUDGET_USD_CAP)
        raw, provider, model, llm_ok = {}, "none", "budget-stopped", False
    else:
        try:
            raw, provider, model = llm_gateway.generate_with_meta(
                llm_gateway.build_user_prompt(full_query, evidence, ""))
            llm_ok = True
        except Exception:
            log.exception("llm gateway failed")
            raw, provider, model, llm_ok = {}, "none", "fallback-extractive", False
    _llm_ms = int((_time.time() - _t0) * 1000)

    if not raw:
        if sql_rows:
            raw = {
                "summary_text": f"Computed from {len(sql_rows)} grouped record(s). Query executed transparently.",
                "equipment_tag": primary, "component_type": "kpi_table",
                "component_payload": {"title": "Maintenance KPI", "alert_level": "normal",
                                      "details": {"rows": sql_rows[:10], "query": sql_text or ""}},
                "citations": [{"document_title": "Maintenance History (All Equipment).xlsx",
                               "snippet": f"{len(sql_rows)} grouped rows",
                               "file_path": "Maintenance History (All Equipment).xlsx",
                               "source_type": "xlsx",
                               "row_reference": ", ".join(str(r.get('equipment_tag', '')) for r in sql_rows[:5])}],
                "sql_query": sql_text,
            }
        elif hits:
            p = hits[0]["payload"]
            _fp = str(p.get("file_path", ""))
            _st = "png" if _fp.lower().endswith(".png") else "xlsx" if _fp.lower().endswith((".xlsx", ".xls")) else "pdf"
            raw = {
                "summary_text": (p.get("text", "")[:600] or "Relevant evidence found; open Inspector for full source."),
                "equipment_tag": p.get("equipment_tag") or primary,
                "component_type": "text_only",
                "component_payload": {"title": p.get("doc_title", ""), "alert_level": "normal",
                                      "details": {}, "insufficient_evidence": False},
                "citations": [{"document_title": p.get("doc_title", ""),
                               "page_number": p.get("page_number") if _st == "pdf" else None,
                               "snippet": (p.get("text", "")[:300]), "file_path": _fp,
                               "source_type": _st, "chunk_id": hits[0]["id"]}],
            }
        else:
            raw = {
                "summary_text": "Technical evidence not found in authorized sources. No values were estimated.",
                "equipment_tag": primary, "component_type": "text_only",
                "component_payload": {"title": "No evidence", "alert_level": "warning",
                                      "details": {}, "insufficient_evidence": True},
                "citations": [],
            }
    raw["route"] = route
    raw.setdefault("schema_version", SCHEMA_VERSION)
    try:
        ans = ChatAnswer(**raw)
    except Exception as e:
        log.warning("model output failed validation (%s); recovering as insufficient-evidence",
                    str(e)[:300].replace("\n", " "))
        ans = ChatAnswer(
            summary_text=str((raw or {}).get("summary_text", "The model returned an invalid response."))[:2000],
            equipment_tag=primary, component_type="text_only",
            component_payload=ComponentPayload(title="Recovered", alert_level="warning",
                                               details={}, insufficient_evidence=True),
            citations=[], route=route)
    # Details were already validated per component_type by ChatAnswer's
    # model_validator; invalid model output recovered above. No free objects.
    # Citation resolution against registry + current access (T4.9)
    ans.citations = [Citation(**c) for c in citation_svc.resolve(
        [c.model_dump() for c in ans.citations], db, u.division, u.role, by_id)]
    if not ans.citations and hits and not ans.component_payload.insufficient_evidence:
        # Model omitted citations: attach top retrieved evidence directly.
        # Still registry-bound (resolver validates access/locators); never invented.
        auto = []
        for h in hits[:2]:
            p = h["payload"]
            auto.append({"document_title": p.get("doc_title", ""),
                         "page_number": p.get("page_number"),
                         "snippet": (p.get("text", "")[:300]), "file_path": p.get("file_path", ""),
                         "source_type": "pdf", "chunk_id": h["id"]})
        ans.citations = [Citation(**c) for c in citation_svc.resolve(
            auto, db, u.division, u.role, by_id)]
    _record_usage(db, u, provider, model, llm_ok, _llm_ms)
    return ans, provider, model, llm_ok


@router.post("/ask", response_model=ChatAnswer)
def ask(body: ChatAsk, req: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    from types import SimpleNamespace
    _check_quota(db, user)
    u = SimpleNamespace(id=user.id, division=user.division, role=user.role,
                        email=user.email, full_name=user.full_name)
    idem = (req.headers.get("Idempotency-Key") or "")[:100]
    if idem:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        hit = db.query(IdempotencyKey).filter(
            IdempotencyKey.user_id == user.id, IdempotencyKey.key == idem,
            IdempotencyKey.created_at >= cutoff).first()
        if hit and hit.answer_json:
            payload = hit.answer_json
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    payload = None
            if payload:
                try:
                    return ChatAnswer(**payload)
                except Exception:
                    log.warning("stored idempotent answer no longer validates; answering fresh")
    s = _get_session(db, body.session_id, u, body.message)
    attachment_text = ""
    attachment_url = None
    if body.attachment_id:
        meta = _attachment_meta(body.attachment_id, u.id)
        if not meta:
            raise HTTPException(403, "Attachment not authorized")
        attachment_text = meta.get("vision_text", "")
        attachment_url = meta.get("url")
    user_msg = ChatMessage(session_id=s.id, role="user", text=body.message,
                           attachment_url=attachment_url, status="complete",
                           schema_version=SCHEMA_VERSION)
    db.add(user_msg)
    db.commit()
    ans, _, _, _ = _answer(body.message, db, u, attachment_text)
    db.add(ChatMessage(session_id=s.id, role="assistant", text=ans.summary_text,
                       payload_json=ans.model_dump(mode="json"), status="complete",
                       schema_version=SCHEMA_VERSION))
    db.add(AuditLog(actor=u.email, action="chat.ask", user_name=u.full_name,
                    division=u.division, equipment_tag=ans.equipment_tag or "",
                    query=body.message[:1000], status="ok", ref_id=s.id))
    if idem:
        db.add(IdempotencyKey(user_id=u.id, key=idem, session_id=s.id,
                              answer_json=ans.model_dump(mode="json")))
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return ans


@router.post("/ask-stream")
async def ask_stream(body: ChatAsk, req: Request, db: Session = Depends(get_db),
                     user=Depends(get_current_user)):
    """T5.2 SSE: progress → final validated JSON → done. Partials are never valid answers.
    DEL-B6: client disconnects are detected; the partial run is stored as failed
    (never as a valid final) and audited as an error."""
    from types import SimpleNamespace
    u = SimpleNamespace(id=user.id, division=user.division, role=user.role,
                        email=user.email, full_name=user.full_name)
    idem = (req.headers.get("Idempotency-Key") or "")[:100]
    if idem:
        # DEL-C (T5.3): stream retries with the same key replay the stored final
        # instead of duplicating user messages.
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        hit = db.query(IdempotencyKey).filter(
            IdempotencyKey.user_id == u.id, IdempotencyKey.key == idem,
            IdempotencyKey.created_at >= cutoff).first()
        if hit and hit.answer_json:
            payload = hit.answer_json
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    payload = None
            replay = None
            if payload:
                try:
                    replay = ChatAnswer(**payload)
                except Exception:
                    log.warning("stored idempotent answer no longer validates; answering fresh")
            if replay is not None:
                def _replay():
                    yield "event: final\ndata: {}\n\n".format(replay.model_dump_json())
                    yield "event: done\ndata: {}\n\n"
                return StreamingResponse(_replay(), media_type="text/event-stream",
                                         headers={"X-Request-Id": uuid.uuid4().hex,
                                                  "X-Idempotent-Replay": "true",
                                                  "Cache-Control": "no-cache"})
    try:
        _check_quota(db, u)
    except HTTPException as e:
        detail = e.detail  # bind now: `e` is deleted when the except block exits

        def _quota_err():
            yield f"event: error\ndata: {json.dumps({'error': detail})}\n\n"
        return StreamingResponse(_quota_err(), media_type="text/event-stream")
    s = _get_session(db, body.session_id, u, body.message)
    db.add(ChatMessage(session_id=s.id, role="user", text=body.message, status="complete",
                       schema_version=SCHEMA_VERSION))
    db.commit()
    req_id = uuid.uuid4().hex

    async def gen():
        yield f"event: progress\ndata: {json.dumps({'request_id': req_id, 'stage': 'retrieval'})}\n\n"
        if await req.is_disconnected():
            _store_failed("client disconnected before answer")
            return
        try:
            ans, _, _, _ = _answer(body.message, db, u)
        except Exception:
            log.exception("stream answer failed")
            yield f"event: error\ndata: {json.dumps({'request_id': req_id, 'error': 'Answer failed — please retry.'})}\n\n"
            return
        if await req.is_disconnected():
            _store_failed("client disconnected during answer")
            return
        db.add(ChatMessage(session_id=s.id, role="assistant", text=ans.summary_text,
                           payload_json=ans.model_dump(mode="json"), status="complete",
                           schema_version=SCHEMA_VERSION))
        db.add(AuditLog(actor=u.email, action="chat.ask", user_name=u.full_name,
                        division=u.division, equipment_tag=ans.equipment_tag or "",
                        query=body.message[:1000], status="ok", ref_id=s.id))
        if idem:
            db.add(IdempotencyKey(user_id=u.id, key=idem, session_id=s.id,
                                  answer_json=ans.model_dump(mode="json")))
        try:
            db.commit()
        except Exception:
            db.rollback()
            yield f"event: error\ndata: {json.dumps({'request_id': req_id, 'error': 'Answer failed — please retry.'})}\n\n"
            return
        yield f"event: final\ndata: {ans.model_dump_json()}\n\n"
        yield "event: done\ndata: {}\n\n"

    def _store_failed(reason: str) -> None:
        try:
            db.add(ChatMessage(session_id=s.id, role="assistant",
                               text=f"Answer interrupted ({reason}).",
                               status="failed", schema_version=SCHEMA_VERSION))
            db.add(AuditLog(actor=u.email, action="chat.ask", user_name=u.full_name,
                            division=u.division, query=body.message[:1000],
                            status="error", ref_id=s.id))
            db.commit()
        except Exception:
            db.rollback()
        log.info("stream %s interrupted: %s", req_id, reason)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"X-Request-Id": req_id, "Cache-Control": "no-cache"})


def _attachment_meta(aid: str, user_id: str) -> dict | None:
    sidecar = ATTACHMENTS / f"{aid}.json"
    if ".." in aid or "/" in aid or not sidecar.exists():
        return None
    try:
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
    except Exception:
        return None
    if meta.get("user_id") != user_id:
        return None
    return meta


@router.post("/attachments")
async def upload_attachment(file: UploadFile = File(...),
                            db: Session = Depends(get_db), user=Depends(get_current_user)):
    """T5.4 real upload: PNG/JPEG ≤ 5 MB, session-scoped (never global knowledge)."""
    from ..services import llm_gateway as gateway
    name = (file.filename or "").lower()
    if not name.endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(400, "Supported image formats: PNG, JPEG")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(400, "Image exceeds 5 MB limit")
    if len(data) == 0:
        raise HTTPException(400, "Empty image")
    ATTACHMENTS.mkdir(parents=True, exist_ok=True)
    aid = uuid.uuid4().hex
    ext = ".png" if name.endswith(".png") else ".jpg"
    (ATTACHMENTS / f"{aid}{ext}").write_bytes(data)
    mime = "image/png" if ext == ".png" else "image/jpeg"
    try:
        vision_text = gateway.vision_extract_tags(data, mime=mime)
    except Exception:
        log.exception("vision failed")
        vision_text = ""
    if not vision_text:
        vision_text = f"Image {file.filename} stored but unreadable by vision — mention equipment tags in text."
    (ATTACHMENTS / f"{aid}.json").write_text(json.dumps(
        {"user_id": user.id, "filename": file.filename, "vision_text": vision_text,
         "url": f"attachment:{aid}{ext}"}), encoding="utf-8")
    detected = vector_service.extract_tags(vision_text)
    return {"attachment_id": aid, "vision_text": vision_text,
            "detected_tags": detected, "needs_confirmation": len(detected) != 1}


@router.get("/sessions")
def sessions(q: str = "", db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = db.query(ChatSession)
    if not access_policy.is_privileged(user.role):
        query = query.filter(ChatSession.user_id == user.id)
    if q:
        esc = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(ChatSession.title.ilike(f"%{esc}%", escape="\\"))
    ss = query.order_by(ChatSession.created_at.desc()).limit(50).all()
    return [{"id": s.id, "title": s.title, "created_at": str(s.created_at)} for s in ss]


def _own_session(db: Session, sid: str, user) -> ChatSession:
    s = db.get(ChatSession, sid)
    if not s or (s.user_id != user.id and not access_policy.is_privileged(user.role)):
        raise HTTPException(403, "Not authorized")
    return s


@router.patch("/sessions/{sid}")
def rename_session(sid: str, body: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = _own_session(db, sid, user)
    title = str((body or {}).get("title", "")).strip()
    if not (1 <= len(title) <= 120):
        raise HTTPException(400, "Title must be 1..120 characters")
    s.title = title
    db.commit()
    return {"id": s.id, "title": s.title}


@router.delete("/sessions/{sid}")
def delete_session(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = _own_session(db, sid, user)
    db.query(ChatMessage).filter(ChatMessage.session_id == s.id).delete()
    db.delete(s)
    db.commit()
    return {"ok": True}


@router.get("/sessions/{sid}")
def session_detail(sid: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.get(ChatSession, sid)
    if not s or (s.user_id != user.id and not access_policy.is_privileged(user.role)):
        raise HTTPException(403, "Not authorized")
    msgs = db.query(ChatMessage).filter(ChatMessage.session_id == sid).order_by(ChatMessage.created_at).all()
    out = []
    for m in msgs:
        payload = m.payload_json
        if isinstance(payload, str):  # legacy double-encoded rows
            try:
                payload = json.loads(payload)
            except Exception:
                payload = None
        out.append({"role": m.role, "text": m.text, "payload": payload,
                    "status": m.status, "schema_version": m.schema_version,
                    "attachment": m.attachment_url})
    return {"id": s.id, "title": s.title, "messages": out}


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), user=Depends(get_current_user)):
    """T5.5 Whisper with validation (format/duration/size); client previews/edits before send.

    Retention: raw audio is NOT stored server-side — only the transcript returns to
    the client (see docs/RETENTION.md). DEL-B11: 120 s enforced for WAV (measurable
    offline via stdlib); other containers rely on the 10 MB cap + client-side
    MediaRecorder limit (see lib/audio.ts), documented as a limit, not a guarantee.
    """
    name = (file.filename or "").lower()
    if not name.endswith((".webm", ".wav", ".mp3", ".m4a", ".ogg")):
        raise HTTPException(400, "Supported audio: webm, wav, mp3, m4a, ogg (≤ 10 MB, ≤ 120 s)")
    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(400, "Audio exceeds 10 MB limit")
    if len(data) == 0:
        raise HTTPException(400, "Empty audio — record again")
    if name.endswith(".wav"):
        import io
        import wave
        try:
            with wave.open(io.BytesIO(data)) as w:
                seconds = w.getnframes() / (w.getframerate() or 1)
        except Exception:
            raise HTTPException(400, "Unreadable WAV — record again")
        if seconds > 120:
            raise HTTPException(400, f"Audio {seconds:.0f}s exceeds the 120 s limit — record a shorter clip")
    if not settings.OPENAI_API_KEY:
        return {"text": "", "hint": "Use browser Web Speech API (no server key configured)."}
    from openai import OpenAI
    import io
    client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.LLM_TIMEOUT_S)
    try:
        r = client.audio.transcriptions.create(model="whisper-1", file=(file.filename or "audio.webm", io.BytesIO(data)))
    except Exception:
        log.exception("whisper failed")
        raise HTTPException(502, "Transcription provider failed — retry or type instead")
    return {"text": r.text}
