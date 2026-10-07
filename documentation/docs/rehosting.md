# Rehosting

`/vendor/<lib>/<version>/…` serves third-party assets so no project depends on an external CDN.
Paths are version-pinned and immutable-cacheable; the `assets` table tracks each one's upstream
source, current version and (once checked) latest version.

`/manage` lists them with a **Refresh** action (`POST /api/assets/{id}/refresh`) that downloads the
upstream file into the writable vendor volume.
