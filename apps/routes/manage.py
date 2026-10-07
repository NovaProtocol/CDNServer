from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from apps.db import get_sessionmaker
from apps.models import Asset
from apps.parity import check_parity
from apps.security import manage_token
from apps.templating import templates

router = APIRouter()


@router.get("/manage", response_class=HTMLResponse)
async def manage(request: Request) -> HTMLResponse:
    """Admin dashboard. The gate lives in GateKeeper (a custom_password rule on this
    path) — the app is naked behind it and does no auth (reference/gatekeeper/)."""
    async with get_sessionmaker()() as session:
        assets = (await session.execute(select(Asset).order_by(Asset.name))).scalars().all()
    return templates.TemplateResponse(
        request,
        "manage.html",
        {"assets": assets, "parity": check_parity(), "manage_token": manage_token()},
    )
