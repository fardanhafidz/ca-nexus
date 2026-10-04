"""T1.5 — Alembic environment (versioned migrations; replaces bare create_all)."""
from logging.config import fileConfig
import os, sys
from sqlalchemy import engine_from_config, pool
from alembic import context

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.database import Base  # noqa: E402
import app.models.user, app.models.maintenance  # noqa: E402,F401

config = context.config
if config.get_main_option("sqlalchemy.url", "").startswith("driver://"):
    config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL", "postgresql+psycopg2://mkh:mkh_password@localhost:5432/mkh"))
if fileConfig and config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
