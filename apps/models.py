from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Asset(Base):
    """A rehosted third-party asset.

    VARCHAR only — never a TEXT column here, so `server_default` is safe (MySQL 8.4
    rejects DEFAULT on TEXT/BLOB; see reference/docker/mysql.md).
    """

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False, default="other")
    upstream_url: Mapped[str] = mapped_column(String(500), nullable=False)
    current_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    latest_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    path: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
