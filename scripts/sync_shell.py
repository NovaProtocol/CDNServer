#!/usr/bin/env python3
"""Copy the canonical shared shell into every app that uses it.

The shell is one file — `shell/base.html` in this repo — and each app gets a
verbatim copy at `<templates>/_shell/base.html`, which its own thin `base.html`
extends. Apps are separate repositories, so a copy plus this script is the only
way to have one source of truth; run it whenever the shell changes and commit
the result in each app.

    python3 scripts/sync_shell.py            # write every copy
    python3 scripts/sync_shell.py --check    # fail if a copy is out of date
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SOURCE = HERE / "shell" / "base.html"

# app root -> its Jinja templates directory
TARGETS = {
    "Portfolio": "apps/templates",
    "TurfOps": "templates",
    "GateKeeper": "management/templates",
    "SolveSpace": "shared/templates",
    "MELEReviewSite": "web/templates",
    "NovaProtocol": "templates",
    "ServerDashboard": "dashboard/templates",
    "CDNServer": "templates",
}
PROJECTS = Path("/projects")

BANNER = (
    "{# GENERATED — do not edit. Copied from CDNServer/shell/base.html by\n"
    "   CDNServer/scripts/sync_shell.py. Edit the source and re-run the sync. #}\n"
)


def rendered() -> str:
    return BANNER + SOURCE.read_text()


def main() -> int:
    check = "--check" in sys.argv
    want = rendered()
    stale, written, missing = [], [], []

    for app, sub in TARGETS.items():
        tdir = PROJECTS / app / sub
        if not tdir.is_dir():
            missing.append(f"{app}: no templates dir at {tdir}")
            continue
        dest = tdir / "_shell" / "base.html"
        if check:
            if not dest.exists() or dest.read_text() != want:
                stale.append(f"{app}: {dest}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_text() == want:
            continue
        dest.write_text(want)
        written.append(str(dest.relative_to(PROJECTS)))

    for m in missing:
        print("skip " + m)
    if check:
        for s in stale:
            print("STALE " + s)
        print("shell copies up to date" if not stale else f"{len(stale)} stale")
        return 1 if stale else 0
    for w in written:
        print("wrote " + w)
    print(f"{len(written)} written, {len(TARGETS) - len(missing) - len(written)} already current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
