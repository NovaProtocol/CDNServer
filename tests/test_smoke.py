from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("DEPLOYMENT_TYPE", "debug")
os.environ.setdefault("SECRET_KEY", "x" * 32)
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./.test_cdn.db")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from apps import create_app  # noqa: E402

_DB = Path(".test_cdn.db")


@pytest.fixture()
def client():
    if _DB.exists():
        _DB.unlink()
    with TestClient(create_app()) as c:
        yield c
    if _DB.exists():
        _DB.unlink()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_landing(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Design-language kits" in resp.text


def test_parity_passes(client):
    resp = client.get("/api/parity")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_kit_served_with_cors(client):
    resp = client.get("/material/light/theme.css")
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "*"


def test_manage_renders(client):
    resp = client.get("/manage")
    assert resp.status_code == 200


def test_create_asset_requires_token(client):
    resp = client.post("/api/assets", json={"upstream_url": "https://example.com/x.js"})
    assert resp.status_code == 403


def test_create_asset_rejects_non_http(client):
    from apps.security import manage_token

    resp = client.post(
        "/api/assets",
        json={"upstream_url": "ftp://example.com/x.js"},
        headers={"X-Manage-Token": manage_token()},
    )
    assert resp.status_code == 400


def test_asset_list_exposes_public_url(client):
    resp = client.get("/api/assets")
    assert resp.status_code == 200
    assert all("url" in asset for asset in resp.json())
