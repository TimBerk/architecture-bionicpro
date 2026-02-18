import json
from typing import Any, Optional
from redis import Redis

from src.config import Settings


class SessionStore:
    def __init__(self, redis: Redis, settings: Settings):
        self.r = redis
        self.s = settings

    def _key(self, sid: str) -> str:
        return f"sess:{sid}"

    def create(self, sid: str, payload: dict[str, Any]) -> None:
        self.r.set(self._key(sid), json.dumps(payload), ex=self.s.session_ttl_seconds)

    def get(self, sid: str) -> Optional[dict[str, Any]]:
        raw = self.r.get(self._key(sid))
        if not raw:
            return None
        return json.loads(raw)

    def update(self, sid: str, payload: dict[str, Any]) -> None:
        self.create(sid, payload)

    def delete(self, sid: str) -> None:
        self.r.delete(self._key(sid))

    def replace(self, old_sid: str, new_sid: str) -> Optional[dict[str, Any]]:
        payload = self.get(old_sid)
        if payload is None:
            return None
        self.r.delete(self._key(old_sid))
        self.create(new_sid, payload)
        return payload
