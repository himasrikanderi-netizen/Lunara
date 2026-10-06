"""Server-only Supabase client. Never return or log the secret key."""

from supabase import Client, create_client
from supabase.client import ClientOptions
from app.config import Settings


class DatabaseUnavailable(RuntimeError):
    """Persistent report storage cannot be used right now."""


def make_supabase_client(settings: Settings) -> Client:
    if not settings.supabase_configured:
        raise DatabaseUnavailable("Supabase report storage is not configured")
    url = settings.supabase_url or ""
    if not url.startswith("https://"):
        raise DatabaseUnavailable("SUPABASE_URL must be an HTTPS project URL")
    try:
        return create_client(
            url,
            settings.supabase_secret_key.get_secret_value(),
            options=ClientOptions(postgrest_client_timeout=12, schema="public"),
        )
    except Exception as exc:
        raise DatabaseUnavailable("Supabase client could not be initialized") from exc
