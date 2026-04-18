from functools import lru_cache
from supabase import create_client, Client
from app.core import config


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    config.require_supabase()
    return create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
