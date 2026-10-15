#!/usr/bin/env bash
# Rebuild project-template.zip from the working tree.
#
# The zip is a BUILD ARTIFACT, not a source of truth. It must be regenerated whenever
# .claude/, the doc templates, or .gitignore change — otherwise someone bootstrapping
# from the zip silently gets an older toolchain than someone cloning the repo. That has
# already happened once: the zip shipped 7 command files while the tree had 9.
#
# Usage: scripts/build-zip.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

OUT="$REPO/project-template.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

ROOT="$STAGE/project-template"
mkdir -p "$ROOT/docs" "$ROOT/.claude/commands" "$ROOT/.claude/hooks"

# Root docs the bootstrap populates
for f in CLAUDE.md TASKS.md PROJECT_BRIEF.md PERMISSIONS.md BOOTSTRAP.md README.md; do
  cp "$REPO/$f" "$ROOT/$f"
done

cp "$REPO"/docs/*.md                   "$ROOT/docs/"
cp "$REPO"/.claude/commands/*.md       "$ROOT/.claude/commands/"
cp "$REPO"/.claude/settings.json       "$ROOT/.claude/"
cp "$REPO"/.claude/hooks/session-start.sh "$ROOT/.claude/hooks/"
chmod +x "$ROOT/.claude/hooks/session-start.sh"

# gitignore.template ships as .gitignore at the root of a bootstrapped project; it is
# named with a suffix here so it does not apply to this repo.
cp "$REPO/gitignore.template" "$ROOT/.gitignore"

rm -f "$OUT"
# `zip` is not installed on every host and nothing installs on the host (design
# principle 1), so prefer it when present and fall back to python3's zipfile.
if command -v zip >/dev/null 2>&1; then
  ( cd "$STAGE" && zip -rq "$OUT" project-template )
else
  python3 - "$STAGE" "$OUT" <<'PYZIP'
import os, sys, zipfile
stage, out = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for dirpath, _dirnames, filenames in os.walk(stage):
        for name in sorted(filenames):
            full = os.path.join(dirpath, name)
            arc = os.path.relpath(full, stage)
            info = zipfile.ZipInfo.from_file(full, arc)
            info.compress_type = zipfile.ZIP_DEFLATED
            # preserve the executable bit on the hook
            info.external_attr = (os.stat(full).st_mode & 0xFFFF) << 16
            with open(full, "rb") as fh:
                z.writestr(info, fh.read())
PYZIP
fi

cmd_tree=$(find "$REPO/.claude/commands" -maxdepth 1 -name '*.md' | wc -l)
cmd_zip=$(python3 -c "import zipfile,sys; print(sum(1 for n in zipfile.ZipFile(sys.argv[1]).namelist() if n.startswith('project-template/.claude/commands/') and n.endswith('.md')))" "$OUT")

echo "built $OUT"
echo "commands in tree: $cmd_tree   commands in zip: $cmd_zip"
if [[ "$cmd_tree" != "$cmd_zip" ]]; then
  echo "MISMATCH — zip does not match the working tree" >&2
  exit 1
fi
echo "zip matches the working tree."
