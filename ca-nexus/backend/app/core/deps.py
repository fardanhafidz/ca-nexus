from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
from ..core.security import decode_token_sub, decode_token_jti, TokenError
from ..models.user import User, TokenBlocklist

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    req: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    # T-clean-1: httpOnly cookie primary, Bearer header fallback
    raw = creds.credentials if creds else req.cookies.get(settings.COOKIE_NAME, "")
    if not raw:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    req.state.auth_via_cookie = not bool(creds)
    try:
        sub = decode_token_sub(raw)
        jti = decode_token_jti(raw)
    except TokenError as e:
        if e.kind == "expired":
            raise HTTPException(status_code=401, detail="Token expired — please log in again")
        raise HTTPException(status_code=401, detail="Invalid token")
    if jti and db.get(TokenBlocklist, jti):
        raise HTTPException(status_code=401, detail="Token revoked — please log in again")
    user = db.get(User, sub)  # fresh fetch per request: role/division/status changes apply immediately
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.status != "approved":
        raise HTTPException(status_code=403, detail=f"Account status: {user.status}")
    return user


def require_role(*roles: str):
    def check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden for role")
        return user

    return check
