#!/usr/bin/env bash
# Build the site with Zensical into site/ (the safe default output dir), then
# sync that output into the repo root so GitHub Pages can serve straight from
# the branch root.
#
# We deliberately never point Zensical's own site_dir at the repo root: its
# build wipes every non-hidden file/dir in site_dir on every run, and doing
# that directly at the root previously deleted docs/, zensical.toml, and
# everything else alongside it. Building to site/ first and syncing here
# keeps that wipe scoped to a disposable directory. The sync itself is done
# by sync_site_to_root.py (plain Python stdlib, no rsync dependency) --
# see PROTECTED in that file for what it will never touch or delete; keep
# it in sync with any new top-level source path you add.
set -euo pipefail

cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

zensical build --clean

python3 scripts/sync_site_to_root.py
