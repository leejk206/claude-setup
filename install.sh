#!/usr/bin/env bash
# claude-setup installer — copies my own skills + clones third-party skills from source.
# Third-party code is fetched from upstream (not vendored here), preserving attribution.
set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$SKILLS_DIR"

echo "==> Installing my own skills (council, memory-write-gate)"
for s in council memory-write-gate; do
  rm -rf "${SKILLS_DIR:?}/$s"
  cp -r "$REPO_DIR/skills/$s" "$SKILLS_DIR/$s"
  echo "    installed: $s"
done

echo "==> Cloning third-party skills from source"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

clone_skill () {  # repo_url  subpath_in_repo  dest_name  "attribution"
  local url="$1" sub="$2" name="$3" attrib="$4"
  git clone --depth 1 -q "$url" "$TMP/$name-src"
  rm -rf "${SKILLS_DIR:?}/$name"
  cp -r "$TMP/$name-src/$sub" "$SKILLS_DIR/$name"
  printf '# Third-party skill — installed from source\n\nSource: %s\nUpstream: %s (%s)\n\nDo not re-commit this as your own; keep attribution.\n' \
    "$attrib" "$url" "$sub" > "$SKILLS_DIR/$name/SOURCE.md"
  echo "    installed: $name  <-  $attrib"
}

clone_skill "https://github.com/mattpocock/skills"      "skills/productivity/caveman"      "caveman"                 "Matt Pocock"
clone_skill "https://github.com/hardikpandya/stop-slop" "."                                "stop-slop"               "Hardik Pandya"
clone_skill "https://github.com/addyosmani/agent-skills" "skills/spec-driven-development"  "spec-driven-development" "Addy Osmani"

cat <<'EOF'

==> Done. Manual steps:
  1) superpowers plugin (base framework — only ONE bootstrap-hook framework):
       /plugin marketplace add obra/superpowers-marketplace
       /plugin install superpowers@superpowers-marketplace
  2) Merge settings.example.json into ~/.claude/settings.json
     (note: "model": "sonnet" default; escalate to Opus explicitly).
  3) Restart Claude Code (or /clear) so new skills load.
EOF
