from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from apps.config import get_config

logger = structlog.get_logger("cdn")

# A response a shared cache may store only when the path is deliberately public
# (reference/conventions/caching.md). Version-pinned content paths are immutable.
_IMMUTABLE = "public, max-age=31536000, immutable"
_STATIC = "public, max-age=86400"
_HEALTH = "public, max-age=3600"
_HTML = "public, max-age=300"
_NO_STORE = "no-store"

_CONTROL_PREFIXES = ("/manage", "/api/")
_CONTENT_PREFIXES = ("/vendor/", "/custom-")
_RESERVED_LANGUAGES = ("material", "flat", "brutalism", "glassmorphism", "neomorphism")


def _is_content(path: str) -> bool:
    if path.startswith(_CONTENT_PREFIXES):
        return True
    return any(path.startswith(f"/{lang}/") for lang in _RESERVED_LANGUAGES)


class PermissiveCORSMiddleware(BaseHTTPMiddleware):
    """Public asset server: every response is fetchable from any origin.

    Starlette's CORSMiddleware only emits the header when the request carries an
    Origin, which is wrong for a public CDN — a plain GET of a kit must always be
    usable cross-origin."""

    _PREFLIGHT = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "86400",
    }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return Response(status_code=204, headers=self._PREFLIGHT)
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Echo X-Request-ID and bind it for structured logs."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
        try:
            response = await call_next(request)
        finally:
            structlog.contextvars.unbind_contextvars("request_id", "path")
        response.headers["X-Request-ID"] = request_id
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """One cache policy for every response.

    Debug caches nothing. In production an existing Cache-Control wins; otherwise the
    path class decides — control plane is never cacheable, version-pinned content is
    immutable, HTML is short-lived.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        path = request.url.path

        if path.startswith(_CONTROL_PREFIXES):
            response.headers["Cache-Control"] = _NO_STORE
            return response

        existing = response.headers.get("Cache-Control")
        if get_config().debug:
            if not existing or not any(d in existing for d in ("private", "no-store")):
                response.headers["Cache-Control"] = _NO_STORE
            return response

        if existing:
            return response

        if _is_content(path):
            response.headers["Cache-Control"] = _IMMUTABLE
        elif path.startswith("/static/"):
            response.headers["Cache-Control"] = _STATIC
        elif path in ("/health",):
            response.headers["Cache-Control"] = _HEALTH
        else:
            response.headers["Cache-Control"] = _HTML
        return response
