import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    keycloak_base_url: str = os.environ["KEYCLOAK_BASE_URL"].rstrip("/")
    keycloak_realm: str = os.environ["KEYCLOAK_REALM"]
    client_id: str = os.environ["KEYCLOAK_CLIENT_ID"]
    client_secret: str = os.environ["KEYCLOAK_CLIENT_SECRET"]

    redirect_uri: str = os.environ["AUTH_REDIRECT_URI"]

    redis_url: str = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    cookie_name: str = os.environ.get("AUTH_COOKIE_NAME", "bionicpro_session")
    cookie_secure: bool = os.environ.get("AUTH_COOKIE_SECURE", "true").lower() == "true"
    cookie_samesite: str = os.environ.get("AUTH_COOKIE_SAMESITE", "lax")
    session_ttl_seconds: int = int(os.environ.get("SESSION_TTL_SECONDS", "3600"))
    token_enc_key: str = os.environ["TOKEN_ENC_KEY"]

    bionicpro_api_base_url: str = os.environ["BIONICPRO_API_BASE_URL"].rstrip("/")
    frontend_base_url: str = os.environ.get(
        "FRONTEND_BASE_URL", "http://localhost:3000"
    ).rstrip("/")


def get_settings() -> Settings:
    return Settings()
