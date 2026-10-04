from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
# DEL-V2 runtime find: expire_on_commit=False — endpoint commits mid-request
# (session/message/audit rows); expiring the request user on every commit caused
# DetachedInstanceError refreshes downstream. Fresh data still comes from db.get().
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
