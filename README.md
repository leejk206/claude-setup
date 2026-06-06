# claude-setup

My Claude Code setup — skills, config, and an install script.

**Philosophy:** *don't trust the model's judgment — enforce it with structure.* A judge with
a rubric, doubt before the answer, determinism outside the LLM, method constrained even when
usage is maxed. The pieces here lean that way.

> Personal setup, shared openly. Third-party skills are **installed from their source and
> attributed**, not re-published here.

## What's here (my own)
| skill | what |
|---|---|
| **council** | Multi-role deliberation — Steelman / Red Team / Context Keeper debate; a rubric-bound Moderator (separate context) judges and ends it. Generates dissent, then *judges* it. |
| **memory-write-gate** | Memory discipline from the finding that corruption enters at the *write* path: keep raw episodes primary, gate consolidation, invalidate dependent beliefs on a root change. `lint.py` flags stale dependents in a `[[link]]` memory store. |

## What it installs (third-party, from source — credit to the authors)
- **superpowers** — base skills library (TDD, debugging, code-review, planning, parallel agents). *Jesse Vincent (obra)* · `obra/superpowers-marketplace`
- **caveman** — ~75% output-token compression mode. *Matt Pocock* · `mattpocock/skills`
- **stop-slop** — prose anti-AI-tell judge (use as a judge, not always-on). *Hardik Pandya* · `hardikpandya/stop-slop`
- **spec-driven-development** — spec before code. *Addy Osmani* · `addyosmani/agent-skills`

## Install

**Prerequisites:** [Claude Code](https://claude.com/claude-code), `git`, `python3`.

### 1. Clone & run the installer
```bash
git clone https://github.com/leejk206/claude-setup
cd claude-setup
./install.sh
```
`install.sh` does:
- copies my own skills (**council**, **memory-write-gate**) into `~/.claude/skills/`
- clones the third-party skills (**caveman**, **stop-slop**, **spec-driven-development**)
  from their source repos into `~/.claude/skills/` (each gets a `SOURCE.md` with attribution)

### 2. Install the superpowers base plugin (one-time)
Run inside Claude Code:
```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```
(Only one bootstrap-hook framework — superpowers. Everything else is hookless.)

### 3. Apply settings
Merge `settings.example.json` into `~/.claude/settings.json` (don't blind-overwrite — keep your
own keys/hooks). Key line: `"model": "sonnet"` as the default; escalate to Opus explicitly.

### 4. Reload
Restart Claude Code or run `/clear` so the new skills load.

### Verify
```bash
ls ~/.claude/skills          # council, memory-write-gate, caveman, stop-slop, spec-driven-development
```
In Claude Code the skills show up by name (e.g. invoke `/council`, or `caveman` / `stop-slop`).

### Manual install (no script)
```bash
cp -r skills/council skills/memory-write-gate ~/.claude/skills/
# third-party, from source:
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mp && cp -r /tmp/mp/skills/productivity/caveman ~/.claude/skills/
git clone --depth 1 https://github.com/hardikpandya/stop-slop ~/.claude/skills/stop-slop
git clone --depth 1 https://github.com/addyosmani/agent-skills /tmp/ao && cp -r /tmp/ao/skills/spec-driven-development ~/.claude/skills/
```

### Uninstall
```bash
rm -rf ~/.claude/skills/{council,memory-write-gate,caveman,stop-slop,spec-driven-development}
```

## Notes
- **One bootstrap-hook framework only** (superpowers). Add other packs as *hookless* skills.
- **Token frugality**: each always-loaded skill costs cold-start tokens every session —
  install what you use, gate the rest.
- Third-party skills carry a `SOURCE.md` with their upstream + license.

## License
MIT (my own skills). Third-party skills retain their own licenses at their source.
