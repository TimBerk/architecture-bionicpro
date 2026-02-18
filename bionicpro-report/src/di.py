import httpx
from fastapi import HTTPException, Header, status, Request

from src.models import CurrentUser
from src.config import settings


async def get_current_user(request: Request) -> CurrentUser:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                f"{settings.AUTH_BASE_URL}/auth/me", cookies=request.cookies
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Incorrect user data")

    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = r.json()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=500, detail="Auth response missing user data")

    return CurrentUser(email=email)
