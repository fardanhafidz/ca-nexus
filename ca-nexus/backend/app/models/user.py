import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, func, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base
from ..core.config import DIVISIONS


def uid() -> str:
    return str(uuid.uuid4())


ROLE_CK = CheckConstraint("role IN ('super_admin','admin','user')", name="ck_users_role")
STATUS_CK = CheckConstraint("status IN ('pending','approved','rejected','disabled')", name="ck_users_status")
DIV_CK = CheckConstraint(
    "division IN ('Mechanical','Electrical & Instrumentation','Process / Operations','HSE & Reliability')",
    name="ck_users_division",
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (ROLE_CK, STATUS_CK, DIV_CK)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    full_name: Mapped[str] = mapped_column(String(200))
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # super_admin|admin|user
    division: Mapped[str] = mapped_column(String(100), default="Mechanical")
    division_requested: Mapped[str] = mapped_column(String(100), default="Mechanical")
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|approved|rejected|disabled
    quota_queries: Mapped[int | None] = mapped_column(Integer, nullable=True)  # T7.5 monthly cap, NULL = unlimited
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Division(Base):
    """Seeded reference table (T1.6): single source of valid division names."""
    __tablename__ = "divisions"
    name: Mapped[str] = mapped_column(String(100), primary_key=True)


class TokenBlocklist(Base):
    """Revoked JWT jti for logout (T3.3)."""
    __tablename__ = "token_blocklist"
    jti: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def seed_divisions(db) -> None:
    for name in DIVISIONS:
        if not db.get(Division, name):
            db.add(Division(name=name))
