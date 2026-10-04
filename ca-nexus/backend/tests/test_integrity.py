"""T8.1 integrity checks — run: pytest backend/tests -q (no DB/Qdrant/LLM needed)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import sql_service
from app.services.pipeline import stable_chunk_id
from app.core import policy


def test_sql_allows_single_select_with_scope():
    sql, params = sql_service.build_sql("total downtime EA-5601", "EA-5601",
                                        role="user", division="Mechanical")
    assert sql.strip().lower().startswith("select") and ";" not in sql
    assert "discipline" in sql  # division scope present (T3.4)


def test_sql_rejects_multi_statement_and_dml():
    for bad in ["SELECT * FROM t; DROP TABLE t", "DELETE FROM maintenance_records",
                "SELECT * FROM maintenance_records LIMIT 500"]:
        try:
            sql_service.validate(bad)
        except ValueError:
            continue
        raise AssertionError(f"should reject: {bad}")


def test_sql_admin_has_no_discipline_restriction():
    sql, _ = sql_service.build_sql("total cost", None, role="super_admin", division="Mechanical")
    assert "1=1" in sql


def test_policy_doc_visibility():
    assert policy.doc_visible("All", "Mechanical", "user")
    assert policy.doc_visible("Mechanical", "Mechanical", "user")
    assert not policy.doc_visible("Mechanical", "Process / Operations", "user")
    assert not policy.doc_visible("", "Mechanical", "user")  # unlabeled → deny
    assert policy.doc_visible("", "Mechanical", "admin")  # admins see all


def test_policy_row_scope():
    assert policy.row_visible("Mechanical", "Mechanical", "user")
    assert not policy.row_visible("Mechanical", "Process / Operations", "user")
    assert policy.row_visible("Mechanical", "Process / Operations", "admin")


def test_chunk_ids_stable_and_unique():
    a = stable_chunk_id("abc", 1, 0)
    assert a == stable_chunk_id("abc", 1, 0)
    assert a != stable_chunk_id("abc", 1, 1)
    assert a != stable_chunk_id("def", 1, 0)


def test_citation_resolver_drops_unmapped_and_unauthorized():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    from app.models.maintenance import Document
    from app.services import citation as csvc
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    with Session(eng) as db:
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="opl",
                        doc_title="OPL.pdf", file_path="a.pdf",
                        division_access="Electrical & Instrumentation",
                        version="v1.0.0", status="READY", page_count=2))
        db.commit()
        # wrong division → dropped
        assert csvc.resolve([{"document_title": "OPL.pdf", "page_number": 1,
                              "snippet": "x", "file_path": "a.pdf", "source_type": "pdf"}],
                            db, "Mechanical", "user") == []
        # invalid page → dropped
        assert csvc.resolve([{"document_title": "OPL.pdf", "page_number": 99,
                              "snippet": "x", "file_path": "a.pdf", "source_type": "pdf"}],
                            db, "Electrical & Instrumentation", "user") == []
        # unmapped title → dropped, never fabricated
        assert csvc.resolve([{"document_title": "Nope.pdf", "snippet": "x"}],
                            db, "Mechanical", "admin") == []
        ok = csvc.resolve([{"document_title": "OPL.pdf", "page_number": 1,
                            "snippet": "model words", "file_path": "a.pdf", "source_type": "pdf"}],
                          db, "Electrical & Instrumentation", "user",
                          retrieved_by_id={"c1": {"payload": {"text": "stored chunk text"}}})
        assert ok == [] or ok[0]["snippet"] in ("stored chunk text"[:500], "model words")


def _memdb():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.database import Base
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def _user(db, **kw):
    from app.models.user import User
    base = dict(id="u1", full_name="T", employee_id="E1", email="t@x.io",
                password_hash="x", role="user", division="Mechanical",
                division_requested="Mechanical", status="approved")
    base.update(kw)
    u = User(**base)
    db.add(u)
    db.commit()
    return db.get(User, base["id"])


def test_session_rename_search_delete():
    from sqlalchemy.orm import Session
    from app.models.maintenance import ChatSession
    from app.api import chat as chat_api
    eng = _memdb()
    with Session(eng) as db:
        me = _user(db)
        db.add(ChatSession(id="s1", user_id="u1", title="Vibration KC-4501"))
        db.add(ChatSession(id="s2", user_id="u1", title="BOM GA-1201A"))
        db.commit()
        assert len(chat_api.sessions(db=db, user=me)) == 2
        assert len(chat_api.sessions(q="vibration", db=db, user=me)) == 1
        assert chat_api.rename_session("s1", {"title": "Trip SEQ-4501"}, db=db, user=me)["title"] == "Trip SEQ-4501"
        try:
            chat_api.rename_session("s1", {"title": ""}, db=db, user=me)
        except Exception as e:
            assert getattr(e, "status_code", 0) == 400
        else:
            raise AssertionError("empty title must 400")
        assert chat_api.delete_session("s2", db=db, user=me) == {"ok": True}
        assert db.get(ChatSession, "s2") is None


def test_document_lifecycle_archive_delete():
    from sqlalchemy.orm import Session
    from app.models.maintenance import Document
    from app.api import admin as admin_api, knowledge as kn
    eng = _memdb()
    with Session(eng) as db:
        admin = _user(db, id="a1", email="a@x.io", employee_id="E9", role="admin")
        user = _user(db)
        db.add(Document(id="d1", equipment_tag="KC-4501", doc_type="opl", doc_title="OPL.pdf",
                        file_path="a.pdf", division_access="All",
                        version="v1.0.0", status="READY", page_count=1))
        db.commit()
        assert admin_api.archive_doc("d1", db=db, user=admin)["status"] == "ARCHIVED"
        assert kn.list_docs(db=db, user=user)["items"] == []
        assert admin_api.delete_doc("d1", db=db, user=admin)["ok"] is True
        assert db.get(Document, "d1") is None
        assert admin_api._bump_version("v1.0.0") == "v1.0.1"


def test_gateway_validation_and_quota():
    from sqlalchemy.orm import Session
    from fastapi import HTTPException
    from app.models.maintenance import ChatSession, ChatMessage
    from app.api import admin as admin_api, chat as chat_api
    eng = _memdb()
    with Session(eng) as db:
        sup = _user(db, id="s1", email="s@x.io", employee_id="E0", role="super_admin")
        me = _user(db, quota_queries=1)
        db.add(ChatSession(id="s1", user_id="u1", title="t"))
        db.add(ChatMessage(session_id="s1", role="assistant", text="a",
                           status="complete", schema_version="v1"))
        db.commit()
        try:
            admin_api.put_gateway({"primary_model": "gpt-4o", "fallback_model": "x",
                                   "timeout_s": 999, "max_retries": 1}, db=db, user=sup)
        except HTTPException as e:
            assert e.status_code == 400
        else:
            raise AssertionError("timeout 999 must 400")
        assert admin_api.put_gateway(
            {"primary_model": "gpt-4o", "fallback_model": "x", "timeout_s": 30, "max_retries": 2},
            db=db, user=sup)["ok"] is True
        try:
            chat_api._check_quota(db, me)
        except HTTPException as e:
            assert e.status_code == 429
        else:
            raise AssertionError("quota exceeded must 429")
