from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    app_name: str = "Lunara API"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    osrm_driving_base_url: str = "https://routing.openstreetmap.de/routed-car"
    osrm_walking_base_url: str = "https://routing.openstreetmap.de/routed-foot"
    osrm_cycling_base_url: str = "https://routing.openstreetmap.de/routed-bike"
    overpass_base_url: str = "https://overpass.private.coffee/api/interpreter"
    geocoder_user_agent: str = "LunaraLocalDev/0.1 (personal safety route prototype)"
    provider_timeout_seconds: float = 18.0
    supabase_url: str | None = None
    supabase_secret_key: SecretStr | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key and self.supabase_secret_key.get_secret_value())

@lru_cache
def get_settings() -> Settings:
    return Settings()
