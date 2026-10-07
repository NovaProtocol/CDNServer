# CDNServer

Shared design-language asset server for the `*.projectnova.download` stack.

- **Kits:** `/<language>/<theme>/theme.css` — every language exposes the same classes.
- **Vendor:** `/vendor/<lib>/<version>/…` — rehosted third-party assets.
- **Landing:** `/` (public) — the endpoint + asset list.
- **Manage:** `/manage` — gated by GateKeeper (a `custom_password` rule), not by this app.

See `kits.md` and `rehosting.md`.
