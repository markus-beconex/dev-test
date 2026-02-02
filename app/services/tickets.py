# app/services/tickets.py
from __future__ import annotations

import datetime as dt
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.repositories.tickets import TicketRepo

log = structlog.get_logger()


class TicketService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TicketRepo(session)
        self.session = session

    async def create(
        self, title: str, description: str, customer_email: str | None, actor: str
    ) -> int:
        # Logging: keine PII als fields – structlog redaction hilft, aber besser gar nicht loggen.
        log.info("ticket.create", title=title)

        t = await self.repo.create_ticket(
            title=title, description=description, customer_email=customer_email
        )
        await self.repo.add_event(t.id, "ticket_created", actor, {"title": title})

        await self.session.commit()
        return t.id

    async def patch(
        self,
        ticket_id: int,
        actor: str,
        status: str | None,
        severity: str | None,
        comment: str | None,
    ) -> None:
        t = await self.repo.get_ticket(ticket_id)
        if not t:
            raise AppError("Ticket not found", status_code=404, code="ticket_not_found")

        fields = {}
        if status:
            fields["status"] = status
        if severity:
            fields["severity"] = severity

        if fields:
            await self.repo.update_ticket(t, **fields)
            await self.repo.add_event(
                ticket_id, "ticket_updated", actor, {"fields": fields}
            )

        if comment:
            # Kommentar ist potentiell PII-haltig -> nicht in Logs
            await self.repo.add_event(
                ticket_id, "comment_added", actor, {"comment": comment[:200]}
            )

        await self.session.commit()

    async def delete_personal_data(self, ticket_id: int, actor: str) -> None:
        t = await self.repo.get_ticket(ticket_id)
        if not t:
            raise AppError("Ticket not found", status_code=404, code="ticket_not_found")

        t.customer_email = None
        t.personal_data_deleted_at = dt.datetime.now(dt.timezone.utc)
        await self.repo.add_event(
            ticket_id, "personal_data_deleted", actor, {"fields": ["customer_email"]}
        )

        await self.session.commit()
