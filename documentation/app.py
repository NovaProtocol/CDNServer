from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CDNServer Documentation")

_SITE_DIR = Path(__file__).resolve().parent / "site"


@app.get("/health")
async def health() -> dict[str, str]:
    """Liveness probe for the docs container."""
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=str(_SITE_DIR), html=True), name="site")
