from app.db.supabase import get_supabase_client
from app.llm.registry import get_llm_provider


def get_db():
    """Get Supabase client dependency."""
    return get_supabase_client()


def get_llm():
    """Get LLM provider dependency."""
    return get_llm_provider()
