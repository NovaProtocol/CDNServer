from __future__ import annotations

import json
from pathlib import Path

from apps.config import CDN_ROOT

MAIN_LANGUAGES = ("material", "flat", "brutalism", "glassmorphism", "neomorphism")
THEMES = ("light", "dark")


def load_schema() -> dict:
    path = CDN_ROOT / "schema.json"
    return json.loads(path.read_text()) if path.exists() else {"tokens": [], "components": []}


def canonical_classes() -> list[str]:
    out: list[str] = []
    for component in load_schema().get("components", []):
        out.extend(component.get("classes", []))
    return out


def languages() -> list[str]:
    if not CDN_ROOT.exists():
        return []
    return [p.name for p in sorted(CDN_ROOT.iterdir()) if p.is_dir() and p.name in MAIN_LANGUAGES]


def custom_kits() -> list[str]:
    if not CDN_ROOT.exists():
        return []
    return [p.name for p in sorted(CDN_ROOT.iterdir()) if p.is_dir() and p.name.startswith("custom-")]


def kit_path(language: str, theme: str, *parts: str) -> Path:
    return CDN_ROOT.joinpath(language, theme, *parts)


def manifest(language: str, theme: str) -> dict:
    path = kit_path(language, theme, "manifest.json")
    return json.loads(path.read_text()) if path.exists() else {}


def theme_available(language: str, theme: str) -> bool:
    return kit_path(language, theme, "theme.css").exists()


def endpoints() -> list[dict]:
    out: list[dict] = []
    for language in languages():
        for theme in THEMES:
            if theme_available(language, theme):
                out.append(
                    {
                        "language": language,
                        "theme": theme,
                        "theme_css": f"/{language}/{theme}/theme.css",
                        "components": len(manifest(language, theme).get("components", [])),
                    }
                )
    return out
