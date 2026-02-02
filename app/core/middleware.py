# app/core/middleware.py
from __future__ import annotations

import uuid
from typing import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from structlog.contextvars import bind_contextvars, clear_contextvars

log = structlog.get_logger()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Correlation-Id") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        clear_contextvars()

        corr_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        bind_contextvars(
            correlation_id=corr_id, path=str(request.url.path), method=request.method
        )

        log.info("request.start")
        try:
            response = await call_next(request)
            response.headers[self.header_name] = corr_id
            log.info("request.end", status_code=response.status_code)
            return response
        except Exception:
            log.exception("request.error")
            raise
        finally:
            clear_contextvars()
