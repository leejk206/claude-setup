#!/usr/bin/env bash
# claude-setup installer — copies my own skills + clones third-party skills from source.
# Third-party code is fetched from upstream (not vendored here), preserving attribution.
set -euo pipefail

SKILLS_DIR="${HOME}/.claude/skills"
HOOKS_DIR="${HOME}/.claude/hooks"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$SKILLS_DIR" "$HOOKS_DIR"

echo "==> Installing my own skills (council, memory-write-gate)"
for s in council memory-write-gate; do
  rm -rf "${SKILLS_DIR:?}/$s"
  cp -r "$REPO_DIR/skills/$s" "$SKILLS_DIR/$s"
  echo "    installed: $s"
done

echo "==> Installing hooks (complexity-escalate)"
for h in complexity-escalate.py; do
  cp "$REPO_DIR/hooks/$h" "$HOOKS_DIR/$h"
  chmod +x "$HOOKS_DIR/$h"
  echo "    installed: $h"
done

echo "==> Installing statusline (model · dir · git branch)"
cp "$REPO_DIR/statusline.sh" "${HOME}/.claude/statusline.sh"
chmod +x "${HOME}/.claude/statusline.sh"
echo "    installed: statusline.sh"

echo "==> Cloning third-party skills from source"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

clone_skill () {  # repo_url  subpath_in_repo  dest_name  "attribution"
  local url="$1" sub="$2" name="$3" attrib="$4"
  local cache="$TMP/repo-$(echo "$url" | tr -c 'A-Za-z0-9' '_')"
  [ -d "$cache" ] || git clone --depth 1 -q "$url" "$cache"   # clone each repo once, reuse
  rm -rf "${SKILLS_DIR:?}/$name"
  cp -r "$cache/$sub" "$SKILLS_DIR/$name"
  printf '# Third-party skill — installed from source\n\nSource: %s\nUpstream: %s (%s)\n\nDo not re-commit this as your own; keep attribution.\n' \
    "$attrib" "$url" "$sub" > "$SKILLS_DIR/$name/SOURCE.md"
  echo "    installed: $name  <-  $attrib"
}

clone_skill "https://github.com/mattpocock/skills"      "skills/productivity/caveman"      "caveman"                 "Matt Pocock"
clone_skill "https://github.com/mattpocock/skills"      "skills/productivity/handoff"      "handoff"                 "Matt Pocock"
clone_skill "https://github.com/mattpocock/skills"      "skills/productivity/grill-me"     "grill-me"                "Matt Pocock"
clone_skill "https://github.com/hardikpandya/stop-slop" "."                                "stop-slop"               "Hardik Pandya"
clone_skill "https://github.com/addyosmani/agent-skills" "skills/spec-driven-development"  "spec-driven-development" "Addy Osmani"

cat <<'EOF'

==> Done. Manual steps:
  1) superpowers plugin (base framework — only ONE bootstrap-hook framework):
       /plugin marketplace add obra/superpowers-marketplace
       /plugin install superpowers@superpowers-marketplace
  2) Merge settings.example.json into ~/.claude/settings.json
     ("model": "opusplan" = Opus in plan mode, Sonnet otherwise;
      UserPromptSubmit hook auto-escalates complex prompts to an Opus subagent;
      statusLine shows the live model; permissions.allow has read-only MCP entries).
  3) Restart Claude Code (or /clear) so new skills + hooks load.
EOF
