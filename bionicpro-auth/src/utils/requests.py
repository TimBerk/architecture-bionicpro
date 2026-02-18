import os
import time
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx

from src.di import settings, session_store, keycloak_openid
from src.utils.cryptography import (
    encrypt,
    decrypt,
)


def gen_sid() -> str:
    return os.urandom(24).hex()


def set_cookie(resp: Response, sid: str) -> None:
    s = settings()
    resp.set_cookie(
        key=s.cookie_name,
        value=sid,
        httponly=True,
        secure=s.cookie_secure,
        samesite=s.cookie_samesite,
        max_age=s.session_ttl_seconds,
        path="/",
    )


def clear_cookie(resp: Response) -> None:
    s = settings()
    resp.delete_cookie(s.cookie_name, path="/")


def refresh_if_needed(sid: str, sess: dict) -> dict:
    kc = keycloak_openid()
    store = session_store()

    now = int(time.time())
    access_exp = int(sess["access_exp"])

    if now < access_exp - 10:
        return sess

    refresh_token = decrypt(sess["refresh_token_enc"])
    token_resp = kc.refresh_token(refresh_token)

    new_access = token_resp["access_token"]
    new_refresh = token_resp.get("refresh_token", refresh_token)
    expires_in = int(token_resp.get("expires_in", 60))

    sess["access_token"] = new_access
    sess["access_exp"] = now + expires_in
    sess["refresh_token_enc"] = encrypt(new_refresh)
    store.update(sid, sess)
    return sess
