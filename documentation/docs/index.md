# CDNServer

Shared design-language asset server for the `*.projectnova.download` stack.

- **Kits:** `/<language>/<theme>/theme.css`. Every language exposes the same classes.
- **Vendor:** `/vendor/<lib>/<version>/…` rehosts third-party assets.
- **Landing:** `/` (public). The endpoint plus the asset list.
- **Manage:** `/manage`, gated by GateKeeper (a `custom_password` rule) and not by this app.

See `kits.md` and `rehosting.md`.
