from __future__ import annotations

from apps import content


def check_parity() -> dict:
    """Every main language/theme must expose exactly the canonical class set.

    A theme switch is a single <link> change, so a class missing in any kit would
    silently unstyle a component at runtime, this is the guard against that.
    """
    expected = set(content.canonical_classes())
    results: dict[str, dict] = {}
    ok = True
    for language in content.languages():
        for theme in content.THEMES:
            key = f"{language}/{theme}"
            if not content.theme_available(language, theme):
                results[key] = {"error": "kit missing"}
                ok = False
                continue
            classes = set(content.manifest(language, theme).get("classes", []))
            missing = sorted(expected - classes)
            extra = sorted(classes - expected)
            if missing or extra:
                ok = False
            results[key] = {
                "missing": missing,
                "extra": extra,
                "components": len(content.manifest(language, theme).get("components", [])),
            }
    return {"ok": ok, "expected_count": len(expected), "results": results}
