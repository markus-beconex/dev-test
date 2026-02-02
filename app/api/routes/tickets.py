# app/api/routes/tickets.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.tickets import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_actor(x_user: str | None) -> str:
    # Für Test: einfacher Header. In echt: Auth/JWT.
    return x_user or "anonymous"


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3)
    customer_email: str | None = None


class TicketPatch(BaseModel):
    status: str | None = None
    severity: str | None = None
    comment: str | None = None


@router.post("")
async def create_ticket(
    body: TicketCreate,
    session: AsyncSession = Depends(get_session),
    x_user: str | None = Header(default=None, alias="X-User"),
):
    svc = TicketService(session)
    ticket_id = await svc.create(
        body.title, body.description, body.customer_email, actor=get_actor(x_user)
    )
    return {"id": ticket_id}


@router.patch("/{ticket_id}")
async def patch_ticket(
    ticket_id: int,
    body: TicketPatch,
    session: AsyncSession = Depends(get_session),
    x_user: str | None = Header(default=None, alias="X-User"),
):
    svc = TicketService(session)
    await svc.patch(
        ticket_id,
        actor=get_actor(x_user),
        status=body.status,
        severity=body.severity,
        comment=body.comment,
    )
    return {"ok": True}


@router.delete("/{ticket_id}/personal-data")
async def delete_personal_data(
    ticket_id: int,
    session: AsyncSession = Depends(get_session),
    x_user: str | None = Header(default=None, alias="X-User"),
):
    svc = TicketService(session)
    await svc.delete_personal_data(ticket_id, actor=get_actor(x_user))
    return {"ok": True}
