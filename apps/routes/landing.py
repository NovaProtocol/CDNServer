from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from apps import content
from apps.db import get_sessionmaker
from apps.models import Asset
from apps.templating import templates

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe, the one route Caddy proxies without a gate."""
    return {"status": "ok"}


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request) -> HTMLResponse:
    async with get_sessionmaker()() as session:
        assets = (await session.execute(select(Asset).order_by(Asset.name))).scalars().all()
    return templates.TemplateResponse(
        request,
        "landing.html",
        {"endpoints": content.endpoints(), "assets": assets, "custom": content.custom_kits()},
    )
