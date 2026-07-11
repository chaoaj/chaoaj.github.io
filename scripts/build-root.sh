#!/usr/bin/env bash
# Build the site with Zensical into site/ (the safe default output dir), then
# sync that output into the repo root so GitHub Pages can serve straight from
# the branch root.
#
# We deliberately never point Zensical's own site_dir at the repo root: its
# build wipes every non-hidden file/dir in site_dir on every run, and doing
# that directly at the root previously deleted docs/, zensical.toml, and
# everything else alongside it. Building to site/ first and using rsync here
# keeps that wipe scoped to a disposable directory, and the excludes below
# are the only thing standing between --delete and the repo's source files
# -- keep this list in sync with any new top-level source paths you add.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

zensical build --clean

# Paths rsync must never touch, whether or not they exist in site/.
protect=(
  .git/
  .venv/
  .cache/
  .claude/
  .gitignore
  .DS_Store
  docs/
  zensical.toml
  theme-template/
  scripts/
  README.md
  LICENSE
  sync.sh
  site/
)

exclude_args=()
for path in "${protect[@]}"; do
  exclude_args+=(--exclude "/$path")
done

rsync -a --delete "${exclude_args[@]}" site/ ./
