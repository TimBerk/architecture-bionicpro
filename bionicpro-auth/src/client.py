from keycloak import KeycloakOpenID

from src.config import Settings


def build_keycloak_openid(settings: Settings) -> KeycloakOpenID:
    return KeycloakOpenID(
        server_url=settings.keycloak_base_url.rstrip("/") + "/",
        realm_name=settings.keycloak_realm,
        client_id=settings.client_id,
        client_secret_key=settings.client_secret,
        verify=True,
        timeout=30,
    )
