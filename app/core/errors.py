# app/core/errors.py
from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "app_error"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": exc.code,
            "detail": exc.message,
            "status": exc.status_code,
        },
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    # Keine internen Details rausgeben (kein Trace, keine PII)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "about:blank",
            "title": "internal_error",
            "detail": "Unexpected error.",
            "status": HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )
