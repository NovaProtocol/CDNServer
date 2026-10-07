from __future__ import annotations

from fastapi import APIRouter

from apps.parity import check_parity

router = APIRouter(prefix="/api")


@router.get("/parity")
async def parity() -> dict:
    """Theme parity across every main design language (custom-* kits excluded)."""
    return check_parity()
