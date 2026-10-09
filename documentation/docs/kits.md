# Kits

Every main design language (`material`, `flat`, `brutalism`, `glassmorphism`, `neomorphism`)
exposes the same component classes for both themes, so switching theme is one `<link>` change.

`cdn/schema.json` is the parity contract: the canonical class set. `scripts/build_kits.py`
generates each `/<language>/<theme>/` bundle from `cdn/_shared/components/*` (theme-neutral) plus
that language's `tokens/`. The design language lives entirely in the tokens + `flavor.css`, so the
classes are identical by construction.

`GET /api/parity` (and the `/manage` page) reports any kit that drifts from the schema.
`custom-<project>/` kits are deliberate one-offs and are excluded from parity.
