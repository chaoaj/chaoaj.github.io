#!/usr/bin/env python3
"""Sync a built site/ directory into the repo root, deleting stale output
files but never touching known source paths.

This replaces an earlier rsync --delete based approach: rsync isn't
guaranteed to be on PATH (it wasn't on the machine this broke on), while
Python already is -- it's what runs Zensical itself. Same safety contract
as before: PROTECTED paths are never read, copied over, or deleted.
"""
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"

# Top-level paths (relative to REPO_ROOT) that must never be touched by the
# sync, whether or not they exist under site/. Keep this in sync with any
# new top-level source path you add to the repo.
PROTECTED = {
    ".git",
    ".venv",
    ".cache",
    ".claude",
    ".gitignore",
    ".DS_Store",
    "docs",
    "zensical.toml",
    "theme-template",
    "scripts",
    "README.md",
    "LICENSE",
    "sync.sh",
    "site",
}


def iter_site_relpaths():
    for path in SITE_DIR.rglob("*"):
        if path.is_file():
            yield path.relative_to(SITE_DIR)


def iter_root_relpaths():
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT)
        if rel.parts[0] in PROTECTED:
            continue
        if path.is_file():
            yield rel


def main():
    dry_run = "--dry-run" in sys.argv

    if not SITE_DIR.is_dir():
        print(f"error: {SITE_DIR} does not exist -- run `zensical build` first", file=sys.stderr)
        return 1

    site_files = set(iter_site_relpaths())
    root_files = set(iter_root_relpaths())

    to_delete = sorted(root_files - site_files)
    to_copy = sorted(site_files)

    for rel in to_delete:
        print(f"deleting {rel}")
        if not dry_run:
            (REPO_ROOT / rel).unlink()

    for rel in to_copy:
        dest = REPO_ROOT / rel
        src = SITE_DIR / rel
        print(f"copying {rel}")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    if not dry_run:
        # Remove directories left empty by deleted files (bottom-up), but
        # never touch a protected top-level path or site/ itself.
        for path in sorted(REPO_ROOT.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if not path.is_dir():
                continue
            rel = path.relative_to(REPO_ROOT)
            if not rel.parts or rel.parts[0] in PROTECTED:
                continue
            try:
                path.rmdir()
            except OSError:
                pass  # not empty

    print(f"{'would delete' if dry_run else 'deleted'} {len(to_delete)} stale file(s), "
          f"{'would copy' if dry_run else 'copied'} {len(to_copy)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
