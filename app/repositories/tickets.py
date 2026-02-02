# app/repositories/tickets.py
from __future__ import annotations

import json
import datetime as dt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Ticket, TicketEvent


class TicketRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_ticket(
        self, title: str, description: str, customer_email: str | None
    ) -> Ticket:
        t = Ticket(title=title, description=description, customer_email=customer_email)
        self.session.add(t)
        await self.session.flush()  # get id
        return t

    async def get_ticket(self, ticket_id: int) -> Ticket | None:
        res = await self.session.execute(select(Ticket).where(Ticket.id == ticket_id))
        return res.scalar_one_or_none()

    async def update_ticket(self, ticket: Ticket, **fields) -> Ticket:
        for k, v in fields.items():
            setattr(ticket, k, v)
        ticket.updated_at = dt.datetime.now(dt.timezone.utc)
        await self.session.flush()
        return ticket

    async def add_event(
        self, ticket_id: int, event_type: str, actor: str, payload: dict
    ) -> None:
        ev = TicketEvent(
            ticket_id=ticket_id,
            event_type=event_type,
            actor=actor,
            payload=json.dumps(payload, ensure_ascii=False),
        )
        self.session.add(ev)
        await self.session.flush()
