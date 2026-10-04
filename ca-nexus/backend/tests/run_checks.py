"""T8.1 offline checks — stdlib only. Run: python backend/tests/run_checks.py
(no DB/Qdrant/LLM/network needed; missing third-party modules are stubbed).
"""
import json, os, runpy, sys, types

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

# ---- stubs for packages unavailable offline (docker image has the real ones) ----
_ps = types.ModuleType("pydantic_settings")


class _BaseSettings:
    # Mirrors backend/app/core/config.py defaults for offline checks.
    DATABASE_URL = "sqlite://"
    QDRANT_URL = "http://localhost:6333"
    QDRANT_PUBLIC_URL = "http://localhost:6333"
    QDRANT_COLLECTION = "manufacturing_knowledge"
    JWT_SECRET = "test-secret-please-rotate-0123456789abcdef"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24
    SOURCE_ROOT = "/tmp/mkh-src"
    FILE_STORAGE_ROOT = "/tmp/mkh-data"
    OPENAI_API_KEY = ""
    OPENROUTER_API_KEY = ""
    LLM_PRIMARY = "openai/gpt-4o"
    LLM_FALLBACK = "anthropic/claude-sonnet-4.5"
    LLM_ORDER = "openrouter,openai"
    LLM_TIMEOUT_S = 45
    LLM_MAX_RETRIES = 1
    BUDGET_USD_CAP = 0.0
    CORS_ORIGINS = "http://localhost:3000"
    BOOTSTRAP_ADMIN_EMAIL = ""
    BOOTSTRAP_ADMIN_PASSWORD = ""
    BOOTSTRAP_ADMIN_EMPLOYEE_ID = "ADM-0001"
    BOOTSTRAP_ADMIN_DIVISION = "Mechanical"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIM = 1536
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 100
    RETRIEVAL_TOP_K = 5
    HYBRID_MODE = "rrf"
    RETRIEVAL_MIN_DENSE = 0.0
    COOKIE_NAME = "mkh_token"
    COOKIE_SECURE = False

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def validate_for_providers(self):  # overridden in real Settings
        return []


_ps.BaseSettings = _BaseSettings
_ps.SettingsConfigDict = lambda **kw: dict(**kw)
sys.modules.setdefault("pydantic_settings", _ps)

_qc = types.ModuleType("qdrant_client")


class _QdrantClient:
    def __init__(self, *a, **k):
        raise RuntimeError("Qdrant unavailable offline")


_qc.QdrantClient = _QdrantClient
_qcm = types.ModuleType("qdrant_client.models")
for _n in ("Filter", "FieldCondition", "MatchValue", "PointStruct", "VectorParams", "Distance"):
    setattr(_qcm, _n, type(_n, (), {"__init__": lambda self, *a, **k: None}))
sys.modules.setdefault("qdrant_client", _qc)
sys.modules.setdefault("qdrant_client.models", _qcm)

_oa = types.ModuleType("openai")


class _OpenAI:
    def __init__(self, *a, **k):
        raise RuntimeError("OpenAI unavailable offline")


_oa.OpenAI = _OpenAI
sys.modules.setdefault("openai", _oa)

_pm = types.ModuleType("python_multipart")
_pm.__version__ = "0.0.20"  # satisfies fastapi's ensure_multipart_is_installed (real pkg in docker)
sys.modules.setdefault("python_multipart", _pm)


class _EmailNotValidError(Exception):
    pass


_ev = types.ModuleType("email_validator")


def _validate_email(email, **kw):
    if "@" not in str(email):
        raise _EmailNotValidError("invalid")
    return types.SimpleNamespace(normalized=str(email).lower())


_ev.validate_email = _validate_email
_ev.EmailNotValidError = _EmailNotValidError
sys.modules.setdefault("email_validator", _ev)

import importlib.metadata as _md
_real_version = _md.version


def _fake_version(name):
    if name == "email-validator":
        return "2.2.0"  # real package pinned in requirements; offline stub only
    return _real_version(name)


_md.version = _fake_version

_jose = types.ModuleType("jose")


class _Expired(Exception):
    pass


class _JWTError(Exception):
    pass


_jwt = types.SimpleNamespace(
    encode=lambda payload, *a, **k: f"tok.{payload.get('sub')}.{payload.get('jti')}",
    decode=lambda token, *a, **k: (
        (_ for _ in ()).throw(_Expired()) if token == "expired"
        else {"sub": "u1", "jti": "j1"} if token.startswith("tok.")
        else (_ for _ in ()).throw(_JWTError())),
)
_jose.jwt = _jwt
_jose.ExpiredSignatureError = _Expired
_jose.JWTError = _JWTError
sys.modules.setdefault("jose", _jose)

_checks = []


def check(name):
    def deco(fn):
        _checks.append((name, fn))
        return fn
    return deco


@check("sql single-SELECT + division scope (T4.6/T3.4)")
def _():
    from app.services import sql_service
    sql, params = sql_service.build_sql("total downtime EA-5601", "EA-5601",
                                        role="user", division="Mechanical")
    assert sql.strip().lower().startswith("select") and ";" not in sql, sql
    assert "discipline" in sql, "division scope missing"
    assert params == {"tag": "EA-5601"}
    sql_a, _ = sql_service.build_sql("total cost", None, role="super_admin", division="Mechanical")
    assert "1=1" in sql_a
    for bad in ["SELECT * FROM t; DROP TABLE t", "DELETE FROM maintenance_records",
                "SELECT * FROM maintenance_records LIMIT 500", "select 1; select 2"]:
        try:
            sql_service.validate(bad)
        except ValueError:
            continue
        raise AssertionError(f"should reject: {bad}")


@check("policy visibility + row scope (T3.4)")
def _():
    from app.core import policy
    assert policy.doc_visible("All", "Mechanical", "user")
    assert policy.doc_visible("Mechanical", "Mechanical", "user")
    assert not policy.doc_visible("Mechanical", "Process / Operations", "user")
    assert not policy.doc_visible("", "Mechanical", "user")
    assert policy.doc_visible("", "Mechanical", "admin")
    assert policy.row_visible("Mechanical", "Mechanical", "user")
    assert not policy.row_visible("Mechanical", "Process / Operations", "user")
    assert policy.row_visible("Mechanical", "Process / Operations", "admin")
    assert "Instrument" in policy.sql_discipline_filter("user", "Electrical & Instrumentation")


@check("stable chunk IDs (T2.7)")
def _():
    from app.services.pipeline import stable_chunk_id
    a = stable_chunk_id("abc", 1, 0)
    assert a == stable_chunk_id("abc", 1, 0)
    assert len({a, stable_chunk_id("abc", 1, 1), stable_chunk_id("def", 1, 0)}) == 3


@check("citation resolver drops unmapped/unauthorized/invalid (T4.9)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.maintenance import Document
    from app.services import citation as csvc
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="opl", doc_title="OPL.pdf",
                        file_path="a.pdf", division_access="Electrical & Instrumentation",
                        version="v1.0.0", status="READY", page_count=2))
        db.commit()
        base = {"document_title": "OPL.pdf", "page_number": 1, "snippet": "x",
                "file_path": "a.pdf", "source_type": "pdf"}
        assert csvc.resolve([dict(base)], db, "Mechanical", "user") == []  # wrong division
        assert csvc.resolve([dict(base, page_number=99)], db, "Electrical & Instrumentation", "user") == []
        assert csvc.resolve([{"document_title": "Nope.pdf", "snippet": "x"}], db, "Mechanical", "admin") == []
        ok = csvc.resolve([dict(base)], db, "Electrical & Instrumentation", "user",
                           retrieved_by_id={"c1": {"payload": {"text": "stored chunk text"}}})
        assert len(ok) == 1 and ok[0]["document_id"] == "d1"


@check("auth schema hardening without email-validator (T3.1)")
def _():
    # Static check (importing the model needs email-validator, present in docker):
    # proves the constraints exist in source.
    import ast
    src = open(os.path.join(ROOT, "app", "schemas", "auth.py"), encoding="utf-8").read()
    assert "EmailStr" in src, "email must use EmailStr"
    assert "min_length=8" in src, "password min length missing"
    assert "DivisionName" in src and "division_requested: DivisionName" in src, "division enum missing"
    assert "model_config" in src and "from_attributes" in src, "UserOut must use from_attributes"
    tree = ast.parse(src)
    assert any(isinstance(n, ast.ClassDef) and n.name == "RegisterIn" for n in ast.walk(tree))


@check("JWT expired vs invalid distinguished (T3.3)")
def _():
    from app.core.security import decode_token_sub, decode_token_jti, TokenError
    assert decode_token_sub("tok.u1.j1") == "u1"
    assert decode_token_jti("tok.u1.j1") == "j1"
    for tok, kind in (("expired", "expired"), ("garbage", "invalid")):
        try:
            decode_token_sub(tok)
        except TokenError as e:
            assert e.kind == kind, (tok, e.kind)
        else:
            raise AssertionError(f"should raise for {tok}")


@check("answer contract validates + details guarded (T4.10)")
def _():
    from app.schemas.chat import ChatAnswer, DETAIL_MODELS, SCHEMA_VERSION
    assert SCHEMA_VERSION == "v1"
    ans = ChatAnswer(summary_text="t", equipment_tag="KC-4501", component_type="interlock_logic",
                     component_payload={"title": "x", "alert_level": "critical",
                                        "details": {"interlock_id": "SEQ-4501", "causes": []}},
                     citations=[])
    DETAIL_MODELS["interlock_logic"](**(ans.component_payload.details or {}))
    try:
        ChatAnswer(summary_text="t", component_type="nope",  # type: ignore[arg-type]
                   component_payload={}, citations=[])
    except Exception:
        pass
    else:
        raise AssertionError("bad component_type must not validate")


@check("seed upsert dry-run on sqlite: 211 rows, rerun clean (T2.3)")
def _():
    import tempfile
    tmp = tempfile.mkdtemp(prefix="mkh_seed_")
    dbfile = os.path.join(tmp, "t.db")
    xlsx = os.path.abspath(os.path.join(
        ROOT, "..", "..", "supporting_data", "Case 1_ Manufacturing Knowledge Hub",
        "Maintenance History (All Equipment).xlsx"))
    if not os.path.exists(xlsx):
        print("    SKIP (workbook not beside repo in this layout)")
        return
    argv = sys.argv
    sys.argv = ["seed_maintenance.py", "--db", f"sqlite:///{dbfile}", "--xlsx", xlsx]
    try:
        runpy.run_path(os.path.join(ROOT, "..", "scripts", "seed_maintenance.py"), run_name="__main__")
        runpy.run_path(os.path.join(ROOT, "..", "scripts", "seed_maintenance.py"), run_name="__main__")
    finally:
        sys.argv = argv
    from sqlalchemy import create_engine, func
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.maintenance import MaintenanceRecord, ImportBatch, Document
    eng = create_engine(f"sqlite:///{dbfile}")
    with Session(eng) as db:
        n = db.query(func.count(MaintenanceRecord.wo_number)).scalar()
        batches = db.query(func.count(ImportBatch.id)).scalar()
        assert n == 211, f"expected 211, got {n}"
        assert batches == 2, f"expected 2 lineage batches, got {batches}"
        wb = db.query(Document).filter(Document.doc_type == "maintenance").first()
        assert wb is not None and wb.status == "READY", "workbook must be registered for SQL citations"


@check("cookie set httponly + deps accept cookie, reject missing (T-clean-1)")
def _():
    from fastapi import Response
    from app.api.auth import _set_auth_cookie
    r = Response()
    _set_auth_cookie(r, "tok.u1.j1")
    sc = r.headers["set-cookie"].lower()
    assert "httponly" in sc and "samesite=lax" in sc, sc
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from fastapi import Request
    from app.core.database import Base
    from app.models.user import User
    from app.core.deps import get_current_user
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.commit()
        req = Request({"type": "http", "method": "GET", "headers": [(b"cookie", b"mkh_token=tok.u1.j1")]})
        u = get_current_user(req, None, db)
        assert u.id == "u1"
        from fastapi import HTTPException
        try:
            get_current_user(Request({"type": "http", "method": "GET", "headers": []}), None, db)
        except HTTPException as e:
            assert e.status_code == 401
        else:
            raise AssertionError("missing credentials must 401")


@check("CSRF origin-check blocks cross-origin cookie mutations")
def _():
    import asyncio
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from app.main import csrf_origin_check
    from app.core.config import settings

    async def ok(req):
        return JSONResponse({"ok": True})

    async def run(origin: str | None):
        headers = [(b"cookie", b"mkh_token=tok.u1.j1")]
        if origin:
            headers.append((b"origin", origin.encode()))
        req = Request({"type": "http", "method": "POST", "headers": headers})
        return await csrf_origin_check(req, ok)

    good_origin = settings.CORS_ORIGINS.split(",")[0].strip().encode()
    assert asyncio.run(run(None)).status_code == 200  # same-origin (no header) passes
    assert asyncio.run(run(good_origin.decode())).status_code == 200
    assert asyncio.run(run("http://evil.example")).status_code == 403


@check("session rename/search/delete API (T5.1)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.user import User
    from app.models.maintenance import ChatSession, ChatMessage
    from app.api import chat as chat_api
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.add(ChatSession(id="s1", user_id="u1", title="Vibration KC-4501"))
        db.add(ChatSession(id="s2", user_id="u1", title="BOM GA-1201A"))
        db.commit()
        me = db.get(User, "u1")
        assert len(chat_api.sessions(db=db, user=me)) == 2
        assert len(chat_api.sessions(q="vibration", db=db, user=me)) == 1
        r = chat_api.rename_session("s1", {"title": "Trip SEQ-4501"}, db=db, user=me)
        assert r["title"] == "Trip SEQ-4501"
        try:
            chat_api.rename_session("s1", {"title": ""}, db=db, user=me)
        except Exception as e:
            assert getattr(e, "status_code", 0) == 400
        else:
            raise AssertionError("empty title must 400")
        assert chat_api.delete_session("s2", db=db, user=me) == {"ok": True}
        assert db.get(ChatSession, "s2") is None


@check("knowledge detail respects scope + READY (T3.6)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from fastapi import HTTPException
    from app.core.database import Base
    from app.models.user import User
    from app.models.maintenance import Document
    from app.api import knowledge as kn
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="interlock", doc_title="IL.pdf",
                        file_path="x.pdf", division_access="Electrical & Instrumentation",
                        version="v1.0.0", status="READY", page_count=1))
        db.add(Document(id="d2", equipment_tag="GA-1201A", doc_type="drawing", doc_title="GA.pdf",
                        file_path="y.pdf", division_access="Mechanical",
                        version="v1.0.0", status="PARSING", page_count=0))
        db.commit()
        me = db.get(User, "u1")
        try:
            kn.document_detail("d1", db=db, user=me)
        except HTTPException as e:
            assert e.status_code == 404
        else:
            raise AssertionError("cross-division detail must 404")
        try:
            kn.document_detail("d2", db=db, user=me)
        except HTTPException as e:
            assert e.status_code == 409
        else:
            raise AssertionError("non-READY detail must 409 for users")


@check("document archive hides + delete removes + audit (T2.10)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.user import User
    from app.models.maintenance import Document, AuditLog
    from app.api import admin as admin_api, knowledge as kn
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="a1", full_name="A", employee_id="E9", email="a@x.io",
                    password_hash="x", role="admin", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="opl", doc_title="OPL.pdf",
                        file_path="a.pdf", division_access="All",
                        version="v1.0.0", status="READY", page_count=1))
        db.commit()
        admin = db.get(User, "a1")
        user = db.get(User, "u1")
        assert admin_api.archive_doc("d1", db=db, user=admin)["status"] == "ARCHIVED"
        assert len(kn.list_docs(db=db, user=user)["items"]) == 0  # hidden from users
        got = kn.list_docs(db=db, user=admin)["items"]
        assert len(got) == 1 and got[0]["status"] == "ARCHIVED"  # admins monitor non-READY
        from fastapi import HTTPException
        try:
            kn.get_file("d1", db=db, user=user)
        except HTTPException as e:
            assert e.status_code in (404, 409)
        else:
            raise AssertionError("archived file must not serve")
        assert admin_api.delete_doc("d1", db=db, user=admin)["ok"] is True
        assert db.get(Document, "d1") is None
        assert db.query(AuditLog).filter(AuditLog.action == "admin.doc.delete").count() == 1
        assert admin_api._bump_version("v1.0.0") == "v1.0.1"
        assert admin_api._bump_version("junk") == "v1.0.0"


@check("gateway validation + runtime apply, admin-only (T7.6)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from fastapi import HTTPException
    from app.core.database import Base
    from app.models.user import User
    from app.api import admin as admin_api
    from app.services import llm_gateway
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="s1", full_name="S", employee_id="E0", email="s@x.io",
                    password_hash="x", role="super_admin", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.add(User(id="a1", full_name="A", email="a@x.io", employee_id="E9",
                    password_hash="x", role="admin", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.commit()
        sup, adm = db.get(User, "s1"), db.get(User, "a1")
        try:
            admin_api.put_gateway({"primary_model": "gpt-4o", "fallback_model": "x",
                                   "timeout_s": 999, "max_retries": 1}, db=db, user=sup)
        except HTTPException as e:
            assert e.status_code == 400
        else:
            raise AssertionError("timeout 999 must 400")
        r = admin_api.put_gateway({"primary_model": "gpt-4o-test", "fallback_model": "alt",
                                   "timeout_s": 30, "max_retries": 2}, db=db, user=sup)
        assert r["effective"]["primary_model"] == "gpt-4o-test"
        assert llm_gateway.effective()["timeout_s"] == 30
        llm_gateway.apply_runtime()  # reset-ish path must not crash
        got = admin_api.get_gateway(db=db, user=sup)
        assert got["stored"]["updated_by"] == "s@x.io"


@check("quota enforced + usage summary math (T7.5)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from fastapi import HTTPException
    from app.core.database import Base
    from app.models.user import User
    from app.models.maintenance import ChatSession, ChatMessage, LLMUsage
    from app.api import chat as chat_api, admin as admin_api
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved", quota_queries=1))
        db.add(ChatSession(id="s1", user_id="u1", title="t"))
        db.add(ChatMessage(session_id="s1", role="assistant", text="a",
                           status="complete", schema_version="v1"))
        db.add(LLMUsage(user_id="u1", provider="openai", model="gpt-4o", ok=True, latency_ms=10))
        db.add(LLMUsage(user_id="u1", provider="openai", model="gpt-4o", ok=False, latency_ms=5))
        db.commit()
        me = db.get(User, "u1")
        try:
            chat_api._check_quota(db, me)
        except HTTPException as e:
            assert e.status_code == 429
        else:
            raise AssertionError("quota 1 with 1 used must 429")
        me.quota_queries = None
        chat_api._check_quota(db, me)  # unlimited passes
        summary = admin_api._usage_summary(db, 30)
        assert summary["total_answers"] == 2
        slot = summary["by_model"][0]
        assert slot["answers"] == 2 and slot["failures"] == 1
        assert slot["est_cost_usd"] == admin_api.estimate_cost("openai", "gpt-4o", 2)


@check("idempotent /ask repeat returns stored answer, no duplicates (DEL-B6)")
def _():
    from sqlalchemy import create_engine, func
    from sqlalchemy.orm import Session
    from fastapi import Request
    from app.core.database import Base
    from app.models.user import User
    from app.models.maintenance import ChatMessage, ChatSession, IdempotencyKey
    from app.api import chat as chat_api
    from app.schemas.chat import ChatAsk
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    stored = {"summary_text": "stored", "equipment_tag": "KC-4501", "component_type": "text_only",
              "component_payload": {"title": "t", "alert_level": "normal", "details": {}},
              "citations": []}
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.add(IdempotencyKey(user_id="u1", key="k1", session_id="s9", answer_json=stored))
        db.commit()
        me = db.get(User, "u1")
        req = Request({"type": "http", "method": "POST",
                       "headers": [(b"idempotency-key", b"k1")]})
        ans = chat_api.ask(ChatAsk(message="anything"), req, db=db, user=me)
        assert ans.summary_text == "stored"
        assert db.query(func.count(ChatMessage.id)).scalar() == 0  # no duplicate messages


@check("WAV over 120s rejected; short WAV passes gate (DEL-B11)")
def _():
    import asyncio, io, wave
    from fastapi import HTTPException, UploadFile
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.user import User
    from app.api import chat as chat_api

    def wav(seconds: int) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(8000)
            w.writeframes(b"\x00\x00" * 8000 * seconds)
        return buf.getvalue()

    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.commit()
        me = db.get(User, "u1")
        try:
            asyncio.run(chat_api.transcribe(UploadFile(filename="long.wav", file=io.BytesIO(wav(121))), me))
        except HTTPException as e:
            assert e.status_code == 400 and "120" in str(e.detail)
        else:
            raise AssertionError("121s wav must 400")
        # 1s wav passes the duration gate (then hits no-key hint path offline)
        r = asyncio.run(chat_api.transcribe(UploadFile(filename="short.wav", file=io.BytesIO(wav(1))), me))
        assert "hint" in r or "text" in r


@check("route trace + clarification fixture + bbox citation (DEL-B9/B14)")
def _():
    from app.api.chat import _route_trace
    assert _route_trace("total downtime across all equipment")["route"] == "sql"
    assert _route_trace("total downtime EA-5601")["route"] == "combined"
    assert _route_trace("hello there")["route"] == "vector"
    t = _route_trace("VSHH-4505 trip on KC-4501")
    assert t["route"] == "graph" and "KC-4501" in t["tags"]
    from app.schemas.chat import ChatAnswer, DETAIL_MODELS
    ans = ChatAnswer(summary_text="Which one?", component_type="clarification",
                     component_payload={"title": "Ambiguous", "alert_level": "normal",
                                        "details": {"question": "Which equipment?",
                                                    "options": ["KC-4501", "GA-1201A"]}},
                     citations=[])
    DETAIL_MODELS["clarification"](**(ans.component_payload.details or {}))
    from app.schemas.chat import Citation
    c = Citation(document_title="P&ID SET 4.png", file_path="x.png", source_type="png",
                 region="full-image", bbox=[0.1, 0.2, 0.5, 0.6])
    assert c.bbox == [0.1, 0.2, 0.5, 0.6]


@check("ingest tag aliases resolve, unknown skipped (DEL-B13)")
def _():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ingest_docs", os.path.join(ROOT, "..", "scripts", "ingest_docs.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.resolve_tag("KC-4501 pump")[0] == "KC-4501"
    tag, alias = mod.resolve_tag("vibration on KC 4501 unit")
    assert tag == "KC-4501" and alias is True
    assert mod.resolve_tag("hello world") == ("", False)


@check("PDF extraction closes handle + flags tables/scans (DEL-B3)")
def _():
    import fitz
    from app.services import ingestion_service as ing
    doc = fitz.open()
    p0 = doc.new_page()
    p0.insert_text((72, 72), "Hello OPL KC-4501 vibration monitoring procedure step one two three")
    doc.new_page()  # empty page → scan-like
    import tempfile
    tmp = tempfile.mkdtemp(prefix="mkh_pdf_")
    fp = os.path.join(tmp, "t.pdf")
    doc.save(fp)
    doc.close()
    from pathlib import Path
    pages = ing.extract_pdf(Path(fp))
    assert len(pages) == 2
    assert pages[0]["needs_ocr"] is False and "table_count" in pages[0]
    assert pages[1]["needs_ocr"] is True


@check("migration chain linked 0001-0004 (DEL-B1)")
def _():
    import re
    d = os.path.join(ROOT, "migrations", "versions")
    revs = {}
    for f in os.listdir(d):
        if f.endswith(".py"):
            src = open(os.path.join(d, f), encoding="utf-8").read()
            r = re.search(r"^revision\s*=\s*['\"](.+)['\"]", src, re.M).group(1)
            down = re.search(r"^down_revision\s*=\s*(.+)$", src, re.M).group(1).strip().strip("'\"")
            revs[r] = down
    assert revs.get("0001_initial") in ("None", "none", ""), revs
    chain, cur = ["0001_initial"], "0001_initial"
    nxt = {v: k for k, v in revs.items()}
    while cur in nxt:
        cur = nxt[cur]
        chain.append(cur)
    assert chain == ["0001_initial", "0002_lifecycle_usage_gateway", "0003_edge_relation",
                     "0004_idempotency", "0005_edge_dst", "0006_jobs"], chain


@check("unagreed metric routes to unsupported, never template (G-08)")
def _():
    from app.services import sql_service
    from app.api.chat import _route_trace
    assert sql_service.unagreed_metric("MTBF CT-7801") is True
    assert sql_service.unagreed_metric("total downtime EA-5601") is False
    assert _route_trace("MTBF CT-7801")["route"] == "unsupported"
    assert _route_trace("MTTR pump GA-1201A")["route"] == "unsupported"


@check("provider order openrouter-first + payload shape (LLM_ORDER)")
def _():
    from app.services import llm_gateway
    from app.core import config as cfg
    assert llm_gateway.effective()["provider_order"].split(",")[0] == "openrouter"
    # OpenRouter tried first when only its key exists (mock transport, no network)
    cfg.settings.OPENROUTER_API_KEY = "test-key"
    cfg.settings.OPENAI_API_KEY = ""
    seen = {}

    class FakeResp:
        text = '{"choices": [{"message": {"content": \'{"ok": true}\'}}]}'

        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": '{"ok": true}'}}]}

    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, headers=None, json=None):
            seen["url"] = url
            seen["auth"] = headers.get("Authorization", "")
            seen["model"] = json["model"]
            assert isinstance(json["messages"], list) and json["messages"], "messages required"
            return FakeResp()

    llm_gateway.httpx.Client = FakeClient
    try:
        payload, provider, model = llm_gateway.generate_with_meta("hi")
    finally:
        cfg.settings.OPENROUTER_API_KEY = ""
    assert provider == "openrouter", provider
    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["auth"] == "Bearer test-key"
    assert payload == {"ok": True}
    # No keys at all -> deterministic fallback, no network
    payload, provider, model = llm_gateway.generate_with_meta("hi")
    assert (provider, model) == ("none", "fallback-extractive")


@check("gateway JSON tolerant to fences/whitespace/empty (OpenRouter)")
def _():
    from app.services import llm_gateway as gw
    assert gw._as_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert gw._as_json('  \n {"a": 1}  ') == {"a": 1}
    assert gw._as_json('') == {} and gw._as_json(None) == {} and gw._as_json('   ') == {}
    try:
        gw._as_json('not json at all')
    except Exception:
        pass
    else:
        raise AssertionError("garbage must still raise (retryable)")


@check("relation literals canonical, no typos (T4.3 regression)")
def _():
    import re
    GOOD = {"HAS_INTERLOCK", "HAS_INSTRUMENT", "HAS_OPL", "HAS_WO", "PROTECTS"}
    root = os.path.join(ROOT, "..")
    pat = re.compile(r"HAS_[A-Z]+")
    bad = []
    for dirpath, _, files in os.walk(root):
        if "__pycache__" in dirpath or "node_modules" in dirpath:
            continue
        for f in files:
            if f.endswith((".py", ".md", ".json", ".ts", ".tsx")):
                s = open(os.path.join(dirpath, f), encoding="utf-8", errors="replace").read()
                for m in set(pat.findall(s)):
                    if m not in GOOD:
                        bad.append((f, m))
    assert not bad, bad


@check("usage records provider/model strings, never classes (T4.11)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.user import User
    from app.models.maintenance import LLMUsage
    from app.api import chat as chat_api
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        db.commit()
        me = db.get(User, "u1")
        ans, provider, model, ok = chat_api._answer("hello pump", db, me)
        assert isinstance(provider, str) and isinstance(model, str), (provider, model)
        row = db.query(LLMUsage).first()
        assert row is not None and isinstance(row.model, str), row
        assert "Details" not in row.model and "class" not in row.model.lower()


@check("graph denies unmapped evidence, scopes WO rows (T4.5)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.maintenance import KnowledgeEdge, MaintenanceRecord, Document
    from app.services import graph_service as gs
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(MaintenanceRecord(wo_number="WO-1", equipment_tag="KC-4501",
                                 discipline="Instrument", related_interlock="SEQ-4501"))
        db.add(KnowledgeEdge(src_tag="KC-4501", dst_tag="SEQ-4501",
                             relation="HAS_INTERLOCK", evidence_doc="Maintenance History:WO-1"))
        db.add(KnowledgeEdge(src_tag="KC-4501", dst_tag="MYSTERY",
                             relation="HAS_INTERLOCK", evidence_doc="mystery-note"))
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="interlock",
                        doc_title="IL.pdf", file_path="il.pdf",
                        division_access="Electrical & Instrumentation",
                        version="v1.0.0", status="READY", page_count=1))
        db.add(KnowledgeEdge(src_tag="KC-4501", dst_tag="IL.pdf",
                             relation="HAS_OPL", evidence_doc="IL.pdf:v1.0.0"))
        db.commit()
        # Mechanical must NOT see Instrument WO edge, mystery edge, or E&I doc edge
        mech = {(g["src"], g["dst"]) for g in
                gs.neighbors(db, "KC-4501", division="Mechanical", role="user")}
        assert ("KC-4501", "SEQ-4501") not in mech, mech
        assert ("KC-4501", "MYSTERY") not in mech, mech
        assert ("KC-4501", "IL.pdf") not in mech, mech
        # E&I sees all three mapped edges, never the mystery one
        ei = {(g["src"], g["dst"]) for g in
              gs.neighbors(db, "KC-4501", division="Electrical & Instrumentation", role="user")}
        assert ("KC-4501", "SEQ-4501") in ei, ei
        assert ("KC-4501", "IL.pdf") in ei, ei
        assert ("KC-4501", "MYSTERY") not in ei, ei
        # Admin sees mapped edges (still never mystery)
        adm = {(g["src"], g["dst"]) for g in gs.neighbors(db, "KC-4501", division="", role="admin")}
        assert ("KC-4501", "SEQ-4501") in adm and ("KC-4501", "MYSTERY") not in adm


@check("answer fixtures valid/invalid (T4.10)")
def _():
    import json as _json
    from app.schemas.chat import ChatAnswer
    path = os.path.join(ROOT, "..", "tests", "fixtures_chat.json")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), "fixtures_chat.json")
    for case in _json.load(open(path, encoding="utf-8")):
        try:
            ChatAnswer(**case["payload"])
            ok = True
        except Exception:
            ok = False
        assert ok == case["valid"], case["name"]


@check("budget cap stops LLM, free paths continue (D-16)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.core import config as cfg
    from app.models.user import User
    from app.models.maintenance import LLMUsage
    from app.api import chat as chat_api
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(User(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                    password_hash="x", role="user", division="Mechanical",
                    division_requested="Mechanical", status="approved"))
        for _ in range(3):
            db.add(LLMUsage(user_id="u1", provider="openrouter",
                            model="openai/gpt-4o", ok=True, latency_ms=1))
        db.commit()
        me = db.get(User, "u1")
        old = cfg.settings.BUDGET_USD_CAP
        cfg.settings.BUDGET_USD_CAP = 0.005  # 3 answers x 0.004 = 0.012 > cap
        try:
            _, provider, model, _ = chat_api._answer("hello pump", db, me)
        finally:
            cfg.settings.BUDGET_USD_CAP = old
        assert (provider, model) == ("none", "budget-stopped"), (provider, model)


@check("citation fuzzy title + snippet from chunk, never model text (T4.9)")
def _():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.maintenance import Document
    from app.services import citation as csvc
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="opl",
                        doc_title="OPL-KC-4501-05 Crosshead_Vibration_Monitoring_VSHH_4505.pdf",
                        file_path="opl.pdf", division_access="All",
                        version="v1.0.0", status="READY", page_count=1))
        db.commit()
        hits = {"h1": {"payload": {"doc_title": "OPL-KC-4501-05 Crosshead_Vibration_Monitoring_VSHH_4505.pdf",
                                   "text": "STORED CHUNK TEXT"}}}
        # Slightly-off model spelling still resolves to the registry row...
        out = csvc.resolve([{"document_title": "OPL-KC-4501-05 Crosshead Vibration Monitoring VSHH 4505",
                             "page_number": 1, "snippet": "model words",
                             "file_path": "", "source_type": "pdf"}],
                           db, "Mechanical", "user", hits)
        assert len(out) == 1 and out[0]["document_id"] == "d1"
        # ...with the snippet taken from the stored chunk, not the model.
        assert out[0]["snippet"] == "STORED CHUNK TEXT", out[0]["snippet"]
        # Far-off titles still drop.
        assert csvc.resolve([{"document_title": "Totally Different Manual",
                              "snippet": "x", "file_path": "", "source_type": "pdf"}],
                            db, "Mechanical", "user", hits) == []


@check("manifest reconciles 98 files (T2.1)")
def _():
    manifest = os.path.join(ROOT, "..", "data", "manifest.json")
    assert os.path.exists(manifest), "run scripts/build_manifest.py first"
    rep = json.load(open(manifest, encoding="utf-8"))
    assert rep["reconciled"] is True, rep["by_suffix"]
    assert rep["total"] == 98, rep["total"]


def main() -> int:
    failed = 0
    for name, fn in _checks:
        try:
            fn()
        except Exception as e:
            failed += 1
            print(f"FAIL {name}: {type(e).__name__}: {e}")
        else:
            print(f"PASS {name}")
    print(f"{len(_checks) - failed}/{len(_checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
