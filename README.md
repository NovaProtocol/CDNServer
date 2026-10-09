# CDNServer

Shared design-language asset server for the projectnova stack — one source of truth for
front-end component CSS and rehosted third-party assets.

**Stack:** Python 3.14 + FastAPI + Granian · MySQL 8.4 · Caddy gateway · MkDocs docs
**Host:** `https://cdn.projectnova.download/`  ·  **Stack:** `cdn` (Dockhand env 4)
**Design language:** n/a — this is the kit server; it dogfoods `material`.

## What it serves

| Path | What |
|---|---|
| `/<language>/<theme>/theme.css` | the whole kit for one language+theme (tokens + components) |
| `/<language>/<theme>/tokens.css` | the `:root` design tokens only |
| `/<language>/<theme>/components/<component>.css` | one component, e.g. `.../components/button.css` |
| `/<language>/<theme>/manifest.json` | machine-readable class list (parity contract consumer) |
| `/vendor/<lib>/<version>/…` | rehosted third-party assets (version-pinned) |
| `/custom-<project>/…` | a genuine project one-off (excluded from parity + tracking) |
| `/` | public read-only landing: language endpoints + rehosted-asset list |
| `/manage` | **GateKeeper-gated** dashboard: asset tracking, refresh, parity checker |

Languages: `material`, `flat`, `brutalism`, `glassmorphism`, `neomorphism` × `light`/`dark`.
Every main language exposes the **same** class set (`cdn/schema.json` is the contract) so a theme
switch is a single `<link>` change.

## How it works

`caddy` (`:7080`) is the entry point and fans out by path to `cdn_main` and `cdn_documentation`
over the compose network. Gating happens in GateKeeper, not here — the local `Caddyfile` carries
zero `forward_auth`. The app is "naked behind the gate": no auth code.

## Quick Start

```bash
cd CDNServer
export DEPLOYMENT_TYPE=debug SECRET_KEY=change-me MYSQL_PASS=change-me MYSQL_USER=root MYSQL_DATABASE=cdnserver

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Tailwind for the dashboard templates (compiled, purged)
npm install
npm run build

python run.py          # dev server on :7081
pytest                 # tests
```

## Environment

See `.env.example`. There is no `.env` file; values come from compose interpolation
(`${VAR:?}`) or your shell. `/manage` is gated by GateKeeper, not by an app password.

## License

All rights reserved. See [LICENSE](LICENSE).
