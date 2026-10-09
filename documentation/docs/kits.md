# Kits

Every main design language (`material`, `flat`, `brutalism`, `glassmorphism`, `neomorphism`)
exposes the same component classes for both themes, so switching theme is one `<link>` change.

`cdn/schema.json` is the parity contract: the canonical class set. `scripts/build_kits.py`
generates each `/<language>/<theme>/` bundle from `cdn/_shared/components/*` (theme-neutral) plus
that language's `tokens/`. The design language lives entirely in the tokens + `flavor.css`, so the
classes are identical by construction.

The shared components are `alert`, `badge`, `banner`, `button`, `card`, `footer`, `input`,
`navbar`, `select`, `table` and `tabs`. `banner` is the full-width sticky notice strip
(`.ui-banner`, with `--info` / `--warn` / `--danger` tones) that sits under the navbar; every
value is a `--ui-*` token, so it recolours with the rest of the page under the theme switch.

`GET /api/parity` (and the `/manage` page) reports any kit that drifts from the schema.
`custom-<project>/` kits are deliberate one-offs and are excluded from parity.
