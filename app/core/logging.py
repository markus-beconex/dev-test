# app/core/logging.py
from __future__ import annotations

import logging
import re
import sys
from typing import Any, Mapping

import structlog

_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]{1,})@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def mask_email(value: str) -> str:
    # "max.mustermann@example.com" -> "ma***@example.com"
    m = _EMAIL_RE.search(value)
    if not m:
        return value
    local, domain = m.group(1), m.group(2)
    keep = local[:2]
    return f"{keep}***@{domain}"


def redact_pii(_, __, event_dict: Mapping[str, Any]) -> dict[str, Any]:
    # Redaction: mask emails in strings + selected fields
    def _redact(obj: Any) -> Any:
        if isinstance(obj, str):
            # mask any email occurrences inside text
            return _EMAIL_RE.sub(lambda mm: mask_email(mm.group(0)), obj)
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if k.lower() in {
                    "email",
                    "customer_email",
                    "password",
                    "token",
                    "authorization",
                }:
                    if isinstance(v, str):
                        out[k] = (
                            "***redacted***" if k.lower() != "email" else mask_email(v)
                        )
                    else:
                        out[k] = "***redacted***"
                else:
                    out[k] = _redact(v)
            return out
        if isinstance(obj, list):
            return [_redact(x) for x in obj]
        return obj

    return dict(_redact(dict(event_dict)))


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            redact_pii,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
