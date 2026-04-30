import json
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Logs all mutating API requests to the audit_logs table."""

    AUDIT_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method not in self.AUDIT_METHODS:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Fire-and-forget audit log (non-blocking)
        try:
            await self._log_request(request, response.status_code, duration_ms)
        except Exception:
            pass  # Never let audit failures break the API

        return response

    async def _log_request(self, request: Request, status_code: int, duration_ms: int):
        from app.db.session import SessionLocal
        from app.models.audit import AuditLog
        from app.core.security import verify_access_token

        user_id = None
        try:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                payload = verify_access_token(auth[7:])
                if payload:
                    user_id = int(payload.get("sub", 0)) or None
        except Exception:
            pass

        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                method=request.method,
                endpoint=str(request.url.path),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                status_code=status_code,
                duration_ms=duration_ms,
            )
            db.add(log)
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
