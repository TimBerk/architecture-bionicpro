from functools import lru_cache
from redis import Redis
from keycloak import KeycloakOpenID

from src.config import get_settings, Settings
from src.storage import SessionStore
from src.client import build_keycloak_openid


@lru_cache
def settings() -> Settings:
    return get_settings()


@lru_cache
def redis_client() -> Redis:
    s = settings()
    return Redis.from_url(s.redis_url, decode_responses=True)


@lru_cache
def session_store() -> SessionStore:
    return SessionStore(redis_client(), settings())


@lru_cache
def keycloak_openid() -> KeycloakOpenID:
    return build_keycloak_openid(settings())
