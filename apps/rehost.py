from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import httpx

from apps.config import CDN_ROOT, VENDOR_DIR
from apps.models import Asset


def _store_path(asset: Asset, filename: str) -> Path:
    version = asset.current_version or "unversioned"
    lib = asset.name.split("-")[0]
    return VENDOR_DIR / lib / version / filename


async def refresh_asset(asset: Asset) -> str:
    """Download the pinned upstream file and store it under vendor/<lib>/<version>/.

    Writes to the writable vendor dir (a volume in the stack), not the baked image.
    Returns the stored path (relative to the vendor root)."""
    filename = asset.upstream_url.rsplit("/", 1)[-1] or "asset"
    dest = _store_path(asset, filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(asset.upstream_url)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
    asset.path = str(dest.relative_to(VENDOR_DIR))
    asset.updated_at = datetime.now(timezone.utc)
    return asset.path


async def seed_vendor() -> None:
    """Populate the writable vendor dir from the baked image on first boot."""
    baked = CDN_ROOT / "vendor"
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    if not baked.exists() or any(VENDOR_DIR.iterdir()):
        return
    import shutil

    shutil.copytree(baked, VENDOR_DIR, dirs_exist_ok=True)


_NPM = re.compile(r"cdn\.jsdelivr\.net/npm/((?:@[^/]+/)?[^/@]+)@([^/]+)", re.I)
_CDNJS = re.compile(r"cdnjs\.cloudflare\.com/ajax/libs/([^/]+)/", re.I)


async def check_latest(asset: Asset) -> str:
    """Ask the upstream for its latest version (npm registry / cdnjs API).

    Best-effort: an unknown source or an unreachable registry returns the current
    latest_version unchanged."""
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        npm = _NPM.search(asset.upstream_url)
        if npm:
            resp = await client.get(f"https://registry.npmjs.org/{npm.group(1)}/latest")
            if resp.status_code == 200:
                return str(resp.json().get("version") or asset.latest_version)
        cdnjs = _CDNJS.search(asset.upstream_url)
        if cdnjs:
            resp = await client.get(
                f"https://api.cdnjs.com/libraries/{cdnjs.group(1)}", params={"fields": "version"}
            )
            if resp.status_code == 200:
                return str(resp.json().get("version") or asset.latest_version)
    return asset.latest_version
