from __future__ import annotations

import hashlib
import hmac

from fastapi import Header, HTTPException

from apps.config import get_config


def manage_token() -> str:
    """A stable token derived from SECRET_KEY, embedded in the gated /manage page.

    Mutating API routes require it in `X-Manage-Token`. The page itself is behind the
    GateKeeper `custom_password` rule, so only an unlocked session ever receives the
    token — this is what keeps `/api/*` from being an open, unauthenticated write
    surface (it is otherwise public behind the gate)."""
    key = get_config().SECRET_KEY.encode()
    return hmac.new(key, b"cdn-manage-v1", hashlib.sha256).hexdigest()


def require_manage(x_manage_token: str | None = Header(default=None)) -> None:
    if not x_manage_token or not hmac.compare_digest(x_manage_token, manage_token()):
        raise HTTPException(status_code=403, detail="forbidden")
