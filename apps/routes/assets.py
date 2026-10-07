from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from apps.db import get_sessionmaker
from apps.models import Asset
from apps.rehost import check_latest, refresh_asset
from apps.security import require_manage

router = APIRouter(prefix="/api/assets")

_EXT_RE = re.compile(r"\.(min\.)?(js|css|woff2?|ttf|otf|eot|json|svg|png|jpe?g|gif|map)$", re.I)
_VERSION_RE = re.compile(r"@(\d+(?:\.\d+){0,3})|/(\d+(?:\.\d+){0,3})/")


class AssetCreate(BaseModel):
    upstream_url: str
    name: str | None = None
    kind: str | None = None


def _derive_name(url: str) -> str:
    base = urlparse(url).path.rsplit("/", 1)[-1] or "asset"
    return _EXT_RE.sub("", base) or "asset"


def _derive_kind(url: str) -> str:
    ext = urlparse(url).path.rsplit(".", 1)[-1].lower()
    if ext == "js":
        return "js"
    if ext == "css":
        return "css"
    if ext in ("woff", "woff2", "ttf", "otf", "eot"):
        return "font"
    return "other"


def _derive_version(url: str) -> str:
    match = _VERSION_RE.search(url)
    return (match.group(1) or match.group(2)) if match else "latest"


def _public_url(asset: Asset) -> str:
    return f"/vendor/{asset.path}" if asset.path else ""


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
            "url": _public_url(a),
        }
        for a in rows
    ]


@router.post("", dependencies=[Depends(require_manage)])
async def create_asset(payload: AssetCreate) -> dict:
    """Rehost a URL the owner supplies and return the stable CDN path to use elsewhere."""
    url = payload.upstream_url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="upstream_url must be http(s)")
    name = (payload.name or "").strip() or _derive_name(url)
    kind = (payload.kind or "").strip() or _derive_kind(url)
    async with get_sessionmaker()() as session:
        clash = (
            await session.execute(select(Asset).where(Asset.name == name))
        ).scalar_one_or_none()
        if clash is not None:
            raise HTTPException(status_code=409, detail=f"an asset named {name!r} already exists")
        asset = Asset(
            name=name,
            kind=kind,
            upstream_url=url,
            current_version=_derive_version(url),
            path="",
        )
        session.add(asset)
        await session.flush()
        try:
            await refresh_asset(asset)
        except Exception as exc:  # noqa: BLE001 - surface any fetch failure to the owner
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"could not fetch upstream: {exc}") from exc
        await session.commit()
        return {
            "ok": True,
            "id": asset.id,
            "name": asset.name,
            "kind": asset.kind,
            "version": asset.current_version,
            "path": asset.path,
            "url": _public_url(asset),
        }


@router.post("/check", dependencies=[Depends(require_manage)])
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


@router.post("/{asset_id}/refresh", dependencies=[Depends(require_manage)])
async def refresh(asset_id: int) -> dict:
    async with get_sessionmaker()() as session:
        asset = await session.get(Asset, asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="asset not found")
        path = await refresh_asset(asset)
        await session.commit()
    return {"ok": True, "path": path, "url": f"/vendor/{path}"}
