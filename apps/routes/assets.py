from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from apps.db import get_sessionmaker
from apps.models import Asset
from apps.rehost import check_latest, refresh_asset

router = APIRouter(prefix="/api/assets")


@router.get("")
async def list_assets() -> list[dict]:
    async with get_sessionmaker()() as session:
        rows = (await session.execute(select(Asset).order_by(Asset.name))).scalars().all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "kind": a.kind,
            "upstream_url": a.upstream_url,
            "current_version": a.current_version,
            "latest_version": a.latest_version,
            "path": a.path,
        }
        for a in rows
    ]


@router.post("/check")
async def check_all() -> dict:
    """Refresh every asset's latest_version from its upstream registry."""
    updated = 0
    async with get_sessionmaker()() as session:
        assets = (await session.execute(select(Asset))).scalars().all()
        for asset in assets:
            latest = await check_latest(asset)
            if latest and latest != asset.latest_version:
                asset.latest_version = latest
                updated += 1
            asset.checked_at = datetime.now(timezone.utc)
        await session.commit()
    return {"ok": True, "updated": updated}


@router.post("/{asset_id}/refresh")
async def refresh(asset_id: int) -> dict:
    async with get_sessionmaker()() as session:
        asset = await session.get(Asset, asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="asset not found")
        path = await refresh_asset(asset)
        await session.commit()
    return {"ok": True, "path": path}
