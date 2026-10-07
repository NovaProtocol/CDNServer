#!/usr/bin/env python3
"""Generate each design-language kit's per-theme bundle + manifest from source.

Source layout (authored):
  cdn/schema.json                     the parity contract
  cdn/_shared/components/<c>.css      theme-neutral components (use var(--ui-*))
  cdn/<lang>/tokens/<theme>.css       the :root token values for that language+theme
  cdn/<lang>/flavor.css               optional per-language overrides

Generated (committed, served at /<lang>/<theme>/…):
  cdn/<lang>/<theme>/tokens.css
  cdn/<lang>/<theme>/components/<c>.css
  cdn/<lang>/<theme>/theme.css        the bundle (tokens + flavor + components)
  cdn/<lang>/<theme>/manifest.json    component + class list (parity consumer)

Every language shares the same component CSS, so the class set is identical by
construction — the design language lives entirely in the tokens + flavor.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDN = ROOT / "cdn"
SHARED = CDN / "_shared" / "components"
MAIN_LANGUAGES = ("material", "flat", "brutalism", "glassmorphism", "neomorphism")
THEMES = ("light", "dark")

_CLASS_RE = re.compile(r"\.(ui-[a-zA-Z0-9_-]+)")


def _classes(css: str) -> set[str]:
    return set(_CLASS_RE.findall(css))


def build() -> int:
    schema = json.loads((CDN / "schema.json").read_text())
    canonical = {c for comp in schema["components"] for c in comp["classes"]}
    components = sorted(p.name for p in SHARED.glob("*.css"))
    component_css = {name: (SHARED / name).read_text() for name in components}

    failures = 0
    for language in MAIN_LANGUAGES:
        lang_dir = CDN / language
        tokens_dir = lang_dir / "tokens"
        if not tokens_dir.exists():
            continue
        flavor = (lang_dir / "flavor.css").read_text() if (lang_dir / "flavor.css").exists() else ""
        for theme in THEMES:
            tokens = tokens_dir / f"{theme}.css"
            if not tokens.exists():
                continue
            out = lang_dir / theme
            (out / "components").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(tokens, out / "tokens.css")
            if flavor:
                (out / "flavor.css").write_text(flavor)
            for name, css in component_css.items():
                (out / "components" / name).write_text(css)

            imports = "".join(f"@import url('./components/{n}?v=4');\n" for n in components)
            dark_css = (tokens_dir / "dark.css").read_text() if (tokens_dir / "dark.css").exists() else tokens.read_text()
            light_path = tokens_dir / "light.css"
            light_css = light_path.read_text() if light_path.exists() else ""
            light_scoped = light_css.replace(":root", '[data-theme="light"]', 1)
            # @import must precede all rules or the browser drops it.
            bundle = imports + dark_css + "\n" + light_scoped + "\n"
            if flavor:
                bundle += flavor + "\n"
            (out / "theme.css").write_text(bundle)

            classes = set()
            for css in component_css.values():
                classes |= _classes(css)
            classes |= _classes(flavor)
            manifest = {
                "language": language,
                "theme": theme,
                "components": components,
                "classes": sorted(classes),
            }
            (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

            missing = canonical - classes
            extra = classes - canonical
            status = "OK" if not missing and not extra else f"MISMATCH missing={sorted(missing)} extra={sorted(extra)}"
            if missing or extra:
                failures += 1
            print(f"  {language}/{theme}: {len(components)} components, {len(classes)} classes — {status}")

    if failures:
        print(f"parity FAILED for {failures} kit(s)")
        return 1
    print("parity OK across generated kits")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
