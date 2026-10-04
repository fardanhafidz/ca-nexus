import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core.config import settings, DIVISIONS
from .core.database import engine, Base, SessionLocal
from .models import user as _u, maintenance as _m
from .api import auth, chat, knowledge, admin
from .core.security import hash_password
from .models.user import User, seed_divisions

log = logging.getLogger("mkh")
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]


def _migrate() -> None:
    """DEL-B1: Alembic is the only deploy path. create_all survives solely for
    sqlite dev/test databases (tests + local runs without postgres)."""
    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
        log.info("sqlite database: schema via create_all (dev/test only)")
        return
    import os
    from alembic.config import Config
    from alembic import command
    cfg = Config()
    cfg.set_main_option("script_location", os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "migrations")))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(cfg, "head")
    log.info("alembic upgrade head applied")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _migrate()
    db = SessionLocal()
    try:
        seed_divisions(db)
        email = settings.BOOTSTRAP_ADMIN_EMAIL
        password = settings.BOOTSTRAP_ADMIN_PASSWORD
        if email and password:
            if not db.query(User).filter(User.email == email).first():
                division = settings.BOOTSTRAP_ADMIN_DIVISION
                if division not in DIVISIONS:
                    log.error("BOOTSTRAP_ADMIN_DIVISION %r invalid — skipped", division)
                else:
                    db.add(User(full_name="Super Admin", employee_id=settings.BOOTSTRAP_ADMIN_EMPLOYEE_ID,
                                email=email, password_hash=hash_password(password),
                                role="super_admin", division=division,
                                division_requested=division, status="approved"))
                    db.commit()
                    log.warning("Bootstrapped super admin %s (change password immediately; re-runs skip existing email)", email)
        elif email and not password:
            log.error("BOOTSTRAP_ADMIN_EMAIL set without BOOTSTRAP_ADMIN_PASSWORD — skipped")
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    for problem in settings.validate_for_providers():
        log.warning("CONFIG: %s", problem)
    yield


app = FastAPI(title="Manufacturing Knowledge Hub", version="0.3.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # httpOnly cookie transport (T-clean-1); origins stay explicit, never "*"
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def csrf_origin_check(req: Request, call_next):
    """CSRF guard for cookie-authenticated mutations: the browser only attaches
    the auth cookie to requests the API can verify came from our own origins."""
    if req.method in ("POST", "PUT", "PATCH", "DELETE") and req.cookies.get(settings.COOKIE_NAME):
        origin = req.headers.get("origin") or req.headers.get("referer", "")
        if origin and not any(origin.startswith(o) for o in origins):
            return JSONResponse({"detail": "Cross-origin request refused"}, status_code=403)
    return await call_next(req)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"ok": True}
