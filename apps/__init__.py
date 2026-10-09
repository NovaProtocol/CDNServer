from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.config import CDN_ROOT, STATIC_DIR, VENDOR_DIR, get_config
from apps.errors import install_error_handlers
from apps.middleware import CacheControlMiddleware, PermissiveCORSMiddleware, RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    from apps.bootstrap import init_schema, seed_assets
    from apps.rehost import seed_vendor

    await init_schema()
    await seed_assets()
    await seed_vendor()
    yield


def create_app() -> FastAPI:
    """Build the application, called once by wsgi.py and once per test."""
    config = get_config()

    app = FastAPI(title="CDNServer", debug=config.debug, lifespan=lifespan)

    # Innermost first: CORS ends up outermost so it decorates error responses too.
    app.add_middleware(CacheControlMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(PermissiveCORSMiddleware)
    install_error_handlers(app)

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount("/vendor", StaticFiles(directory=str(VENDOR_DIR)), name="vendor")

    from apps.routes.assets import router as assets_router
    from apps.routes.landing import router as landing_router
    from apps.routes.manage import router as manage_router
    from apps.routes.parity import router as parity_router

    app.include_router(assets_router)
    app.include_router(parity_router)
    app.include_router(manage_router)
    app.include_router(landing_router)

    # Catch-all LAST: the design-language kits + custom-<project> trees. The routers
    # and the /static + /vendor mounts above win for their prefixes.
    if CDN_ROOT.exists():
        app.mount("/", StaticFiles(directory=str(CDN_ROOT), html=True), name="cdn-kits")

    return app
