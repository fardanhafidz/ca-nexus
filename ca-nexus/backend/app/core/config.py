from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://mkh:mkh_password@localhost:5432/mkh"
    # Internal compose URL vs host-accessible URL (T1.3: bedakan keduanya)
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_PUBLIC_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "manufacturing_knowledge"
    JWT_SECRET: str = "REPLACE-ME"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    # T-clean-1: httpOnly cookie transport (Bearer header still accepted as fallback)
    COOKIE_NAME: str = "mkh_token"
    COOKIE_SECURE: bool = False  # True in production (HTTPS); cross-domain needs Secure + SameSite=None (see .env.example)
    SOURCE_ROOT: str = "/app/supporting_data"
    FILE_STORAGE_ROOT: str = "/app/data"
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    LLM_PRIMARY: str = "openai/gpt-4o"  # D-16: generation via OpenRouter (JSON-capable)
    LLM_FALLBACK: str = "anthropic/claude-sonnet-4.5"
    LLM_ORDER: str = "openrouter,openai"  # team decision 2026-10-01: OpenAI unusable, OpenRouter first
    BUDGET_USD_CAP: float = 0.0  # D-16: 0 = unlimited; >0 stops LLM calls, free paths keep working
    LLM_TIMEOUT_S: int = 45
    LLM_MAX_RETRIES: int = 1
    CORS_ORIGINS: str = "http://localhost:3000"
    BOOTSTRAP_ADMIN_EMAIL: str = ""
    BOOTSTRAP_ADMIN_PASSWORD: str = ""
    BOOTSTRAP_ADMIN_EMPLOYEE_ID: str = "ADM-0001"
    BOOTSTRAP_ADMIN_DIVISION: str = "Mechanical"  # DEL-B4: must be one of DIVISIONS; re-runs skip existing email
    # Retrieval params actually consumed by services (T1.3)
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_TOP_K: int = 5
    # DEL-B8: hybrid mode + dense threshold (dense-only mode exists for comparison runs)
    HYBRID_MODE: str = "rrf"  # rrf | dense-only
    RETRIEVAL_MIN_DENSE: float = 0.0  # drop dense candidates below this cosine score (0 = off)

    def validate_for_providers(self) -> list[str]:
        problems: list[str] = []
        if self.JWT_SECRET in ("", "REPLACE-ME", "change-me-in-prod-demo-only", "change-me-in-prod"):
            problems.append("JWT_SECRET masih placeholder — isi secret acak min 32 char.")
        if not self.OPENAI_API_KEY and not self.OPENROUTER_API_KEY:
            problems.append("OPENAI_API_KEY dan OPENROUTER_API_KEY kosong — jawaban LLM nonaktif, fallback ekstraktif yang dipakai.")
        return problems


settings = Settings()
DIVISIONS = [
    "Mechanical",
    "Electrical & Instrumentation",
    "Process / Operations",
    "HSE & Reliability",
]
