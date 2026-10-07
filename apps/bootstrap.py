from __future__ import annotations

import time

import structlog
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from apps.db import get_engine, get_sessionmaker
from apps.models import Asset, Base

logger = structlog.get_logger("cdn")

# Seed list for the rehosted third-party assets the stack relies on. current_version is
# what is present under cdn/vendor/<lib>/<version>/; latest_version is discovered by the
# refresh/check endpoints (Phase 3).
_SEED_ASSETS = [
    ("bootstrap-css", "css", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", "5.3.3"),
    ("bootstrap-js", "js", "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js", "5.3.3"),
    ("font-awesome-css", "css", "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css", "6.7.2"),
    ("leaflet-css", "css", "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css", "1.9.4"),
    ("leaflet-js", "js", "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js", "1.9.4"),
    ("alpine-js", "js", "https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js", "3.14.1"),
]


async def init_schema() -> None:
    """Create tables, tolerating MySQL's transient concurrent-DDL errors."""
    engine = get_engine()
    for attempt in range(1, 6):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break
        except OperationalError as exc:
            errno = getattr(exc.orig, "args", [None])[0]
            if errno not in (1050, 1061, 1684):
                raise
            time.sleep(0.5 * attempt)


async def seed_assets() -> None:
    async with get_sessionmaker()() as session:
        existing = {row[0] for row in (await session.execute(select(Asset.name))).all()}
        for name, kind, url, version in _SEED_ASSETS:
            if name in existing:
                continue
            session.add(
                Asset(
                    name=name,
                    kind=kind,
                    upstream_url=url,
                    current_version=version,
                    path=f"vendor/{name.split('-')[0]}/{version}/",
                )
            )
        await session.commit()
    logger.info("assets_seeded")
