import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..core.database import get_db
from ..core.config import settings
from ..core.security import (
    hash_password, verify_password, create_token,
    decode_token_sub, decode_token_jti, TokenError,
)
from ..models.user import User, TokenBlocklist
from ..models.maintenance import AuditLog
from ..schemas.auth import RegisterIn, LoginIn, UserOut
from ..core.deps import get_current_user

log = logging.getLogger("mkh.auth")
router = APIRouter(prefix="/auth", tags=["auth"])


def _out(u: User) -> UserOut:
    return UserOut.model_validate(u)


def _set_auth_cookie(resp: Response, token: str) -> None:
    resp.set_cookie(settings.COOKIE_NAME, token, httponly=True, samesite="lax",
                    secure=settings.COOKIE_SECURE, path="/",
                    max_age=settings.JWT_EXPIRE_HOURS * 3600)


@router.post("/register", response_model=UserOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(or_(User.email == body.email, User.employee_id == body.employee_id)).first()
    if exists:
        raise HTTPException(400, "Email or Employee ID already registered")
    u = User(
        full_name=body.full_name, employee_id=body.employee_id, email=body.email,
        password_hash=hash_password(body.password), role="user",
        division=body.division_requested, division_requested=body.division_requested, status="pending",
    )
    db.add(u)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(400, "Email or Employee ID already registered")
    db.refresh(u)
    db.add(AuditLog(actor=u.email, action="auth.register", user_name=u.full_name,
                    division=u.division_requested, status="pending", ref_id=u.id))
    db.commit()
    log.info("register %s pending", u.email)
    return _out(u)


@router.post("/login")
def login(body: LoginIn, resp: Response, db: Session = Depends(get_db)):
    u = None
    if body.employee_id:
        u = db.query(User).filter(User.employee_id == body.employee_id).first()
    if not u and body.email:
        u = db.query(User).filter(User.email == body.email).first()
    if not u or not verify_password(body.password, u.password_hash):
        log.warning("login failed for %s", body.employee_id or body.email)
        raise HTTPException(401, "Invalid credentials")
    if u.status != "approved":
        raise HTTPException(403, f"Account status: {u.status}")
    token = create_token(u.id)
    _set_auth_cookie(resp, token)
    return {"access_token": token, "token_type": "bearer", "user": _out(u).model_dump()}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return _out(user)


@router.post("/refresh")
def refresh(resp: Response, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Re-issue token only if account still approved (T3.3: permission changes apply)."""
    db.refresh(user)
    if user.status != "approved":
        raise HTTPException(403, f"Account status: {user.status}")
    token = create_token(user.id)
    _set_auth_cookie(resp, token)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    resp: Response,
    req: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    """Revoke the presenting token (header or cookie) via blocklist + clear cookie."""
    raw = creds.credentials if creds else req.cookies.get(settings.COOKIE_NAME, "")
    if not raw:
        raise HTTPException(401, "Missing credentials")
    try:
        jti = decode_token_jti(raw)
        _ = decode_token_sub(raw)
    except TokenError:
        raise HTTPException(401, "Invalid token")
    if not db.get(TokenBlocklist, jti):
        db.add(TokenBlocklist(jti=jti))
        db.commit()
    resp.delete_cookie(settings.COOKIE_NAME, path="/")
    return {"ok": True}
