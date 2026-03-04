import os
import time
import urllib.parse
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import httpx

from src.di import settings, redis_client, session_store, keycloak_openid
from src.utils.cryptography import (
    gen_code_verifier,
    code_challenge_s256,
    gen_state,
    encrypt,
)
from src.utils.requests import gen_sid, set_cookie, clear_cookie


router = APIRouter()


@router.get("/auth/login")
async def auth_login():
    s = settings()
    r = redis_client()
    kc = keycloak_openid()

    state = gen_state()
    verifier = gen_code_verifier()
    challenge = code_challenge_s256(verifier)

    r.set(f"login:{state}", verifier, ex=300)

    base_url = kc.auth_url(
        redirect_uri=s.redirect_uri,
        scope="openid",
        state=state,
    )

    parsed = urllib.parse.urlparse(base_url)
    q = dict(urllib.parse.parse_qsl(parsed.query))
    q["code_challenge"] = challenge
    q["code_challenge_method"] = "S256"
    auth_url = urllib.parse.urlunparse(parsed._replace(query=urllib.parse.urlencode(q)))

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
async def auth_callback(code: str, state: str):
    s = settings()
    r = redis_client()
    store = session_store()
    kc = keycloak_openid()

    verifier = r.get(f"login:{state}")
    if not verifier:
        raise HTTPException(status_code=400, detail="Invalid state")
    r.delete(f"login:{state}")

    token_resp = kc.token(
        grant_type="authorization_code",
        code=code,
        redirect_uri=s.redirect_uri,
        code_verifier=verifier,
    )

    access_token = token_resp["access_token"]
    refresh_token = token_resp.get("refresh_token")
    expires_in = int(token_resp.get("expires_in", 60))

    if not refresh_token:
        raise HTTPException(
            status_code=500, detail="No refresh_token returned by Keycloak"
        )

    sid = gen_sid()
    payload = {
        "access_token": access_token,
        "access_exp": int(time.time()) + expires_in,
        "refresh_token_enc": encrypt(refresh_token),
    }
    store.create(sid, payload)

    resp = RedirectResponse(url=f"{s.frontend_base_url}/")
    set_cookie(resp, sid)
    return resp


@router.post("/auth/logout")
async def auth_logout(request: Request):
    s = settings()
    store = session_store()

    sid = request.cookies.get(s.cookie_name)
    resp = JSONResponse({"ok": True})
    if sid:
        store.delete(sid)
    clear_cookie(resp)
    return resp


@router.get("/auth/session")
async def auth_session(request: Request):
    s = settings()
    sid = request.cookies.get(s.cookie_name)
    if not sid:
        return JSONResponse({"authenticated": False}, status_code=200)

    sess = session_store().get(sid)
    if not sess:
        return JSONResponse({"authenticated": False}, status_code=200)

    return JSONResponse({"authenticated": True}, status_code=200)


@router.get("/auth/me")
async def auth_me(request: Request):
    s = settings()
    store = session_store()
    kc = keycloak_openid()

    sid = request.cookies.get(s.cookie_name)
    if not sid:
        raise HTTPException(status_code=401, detail="No session")

    sess = store.get(sid)
    if not sess:
        raise HTTPException(status_code=401, detail="No session")

    access_token = sess["access_token"]
    userinfo = kc.userinfo(access_token)

    return JSONResponse(
        {
            "sub": userinfo["sub"],
            "preferred_username": userinfo.get("preferred_username"),
            "email": userinfo.get("email"),
        }
    )
