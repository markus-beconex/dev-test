# app/main.py
from __future__ import annotations

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine
from app.db.models import Base
from app.core.logging import configure_logging
from app.core.middleware import CorrelationIdMiddleware
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.api.routes.tickets import router as tickets_router
from app.db.session import get_session

configure_logging()

app = FastAPI(title="Ticket Service")

app.add_middleware(CorrelationIdMiddleware)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.include_router(tickets_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready(session: AsyncSession = Depends(get_session)):
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}
