import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path)


def _require(key: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        raise RuntimeError(
            f"Required environment variable '{key}' is not set. "
            f"Add it to backend/.env"
        )
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


SUPABASE_URL: str = _optional("SUPABASE_URL")
SUPABASE_SERVICE_KEY: str = _optional("SUPABASE_SERVICE_KEY")
SUPABASE_STORAGE_BUCKET: str = _optional("SUPABASE_STORAGE_BUCKET", "item-images")
OPENAI_API_KEY: str = _optional("OPENAI_API_KEY")
SERPAPI_API_KEY: str = _optional("SERPAPI_API_KEY")

# Comma-separated list of allowed CORS origins.
# Default covers local desktop dev. Add LAN IP origin here for phone testing.
# Example: CORS_ORIGINS=http://localhost:3000,http://192.168.1.42:3000
_cors_raw: str = _optional("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS: list[str] = [o.strip() for o in _cors_raw.split(",") if o.strip()]


def require_supabase() -> None:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in backend/.env"
        )


def require_openai() -> None:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY must be set in backend/.env")


def require_serpapi() -> None:
    if not SERPAPI_API_KEY:
        raise RuntimeError("SERPAPI_API_KEY must be set in backend/.env")
