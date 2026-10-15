#!/usr/bin/env bash
# Compare a project's .claude/commands/ against this template's.
#
# Toolchain drift is the same class of problem /prj-manage audits for images and
# dependencies: a project quietly falls behind the template, or the template falls
# behind a project where new workflow was proven. This reports both directions.
#
# Usage:  scripts/check-drift.sh <project-path> [template-path]
#         scripts/check-drift.sh /opt/myproject
set -uo pipefail

PROJECT="${1:-}"
TEMPLATE="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

if [[ -z "$PROJECT" ]]; then
  echo "usage: $(basename "$0") <project-path> [template-path]" >&2
  exit 2
fi

P_DIR="$PROJECT/.claude/commands"
T_DIR="$TEMPLATE/.claude/commands"

for d in "$P_DIR" "$T_DIR"; do
  [[ -d "$d" ]] || { echo "not a commands directory: $d" >&2; exit 2; }
done

same=0; differ=0; project_only=0; template_only=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  COMMAND DRIFT — $(basename "$PROJECT") vs template"
echo "  project : $P_DIR"
echo "  template: $T_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

printf '%-24s %-12s %s\n' "COMMAND" "STATUS" "DETAIL"
printf '%-24s %-12s %s\n' "-------" "------" "------"

while IFS= read -r f; do
  name="$(basename "$f")"
  t="$T_DIR/$name"
  if [[ -f "$t" ]]; then
    if diff -q "$f" "$t" >/dev/null 2>&1; then
      printf '%-24s %-12s %s\n' "$name" "in sync" "-"
      (( same++ ))
    else
      # +N/-N relative to the template
      added=$(diff "$t" "$f" | grep -c '^>' || true)
      removed=$(diff "$t" "$f" | grep -c '^<' || true)
      printf '%-24s %-12s %s\n' "$name" "DIFFERS" "+${added}/-${removed} lines vs template"
      (( differ++ ))
    fi
  else
    printf '%-24s %-12s %s\n' "$name" "PROJECT-ONLY" "not in template — port it upstream?"
    (( project_only++ ))
  fi
done < <(find "$P_DIR" -maxdepth 1 -name '*.md' | sort)

while IFS= read -r t; do
  name="$(basename "$t")"
  if [[ ! -f "$P_DIR/$name" ]]; then
    printf '%-24s %-12s %s\n' "$name" "MISSING" "in template, not in project"
    (( template_only++ ))
  fi
done < <(find "$T_DIR" -maxdepth 1 -name '*.md' | sort)

echo
echo "in sync: $same   differs: $differ   project-only: $project_only   missing: $template_only"
echo
if (( differ || project_only || template_only )); then
  echo "Drift found. Review each DIFFERS file in both directions before syncing —"
  echo "a project file ahead of the template is a candidate to port upstream, not to overwrite."
  echo "Diff one with:  diff -u $T_DIR/<file> $P_DIR/<file>"
  exit 1
fi
echo "No drift."
