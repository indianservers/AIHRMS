from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta

from app.models.user import User


class AiRateLimitService:
    _hits: dict[str, deque[datetime]] = defaultdict(deque)

    @classmethod
    def check(cls, *, user: User, bucket: str, limit: int, window_seconds: int = 3600) -> bool:
        now = datetime.utcnow()
        key = f"{bucket}:{user.id}"
        window_start = now - timedelta(seconds=window_seconds)
        hits = cls._hits[key]
        while hits and hits[0] < window_start:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True

    @classmethod
    def limit_for_user(cls, user: User, *, normal: int = 30, admin: int = 100) -> int:
        if user.is_superuser:
            return admin
        role_name = (user.role.name if user.role else "").lower().replace(" ", "_")
        if role_name in {"admin", "super_admin", "developer"}:
            return admin
        return normal
