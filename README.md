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

## Hooks (my own)
| hook | what |
|---|---|
| **complexity-escalate** | `UserPromptSubmit` hook — a **deterministic** complexity classifier (length, code/stacktrace, file count, keywords, multi-step, question count; no LLM, no network). When a prompt scores `>= THRESHOLD`, it injects context telling the main loop to delegate the heavy reasoning to an **Opus subagent** — so a Sonnet/opusplan baseline auto-escalates on hard prompts. Every decision is logged to `~/.claude/logs/complexity-escalate.log` (JSONL) for threshold tuning. The model can't be swapped mid-session, so this routes *reasoning*, not the main-loop model. Pairs with `"model": "opusplan"` (Opus in plan mode, Sonnet otherwise). |

## Statusline (my own)
`statusline.sh` — shows `⏺ <model>  <dir>  ⎇ <branch>` in the status bar. Model name comes
first on purpose: with `opusplan` the model flips between Opus (plan mode) and Sonnet
(execution), so you want to see at a glance which one is live. Reads `.git/HEAD` directly
(no subprocess), degrades gracefully when fields are missing.

## What it installs (third-party, from source — credit to the authors)
- **superpowers** — base skills library (TDD, debugging, code-review, planning, parallel agents). *Jesse Vincent (obra)* · `obra/superpowers-marketplace`
- **caveman** — ~75% output-token compression mode. *Matt Pocock* · `mattpocock/skills`
- **handoff** — compact the current conversation into a handoff doc for a fresh agent (context-limit lifeline). *Matt Pocock* · `mattpocock/skills`
- **grill-me** — relentless one-at-a-time interview to stress-test a plan/design (lighter than council). *Matt Pocock* · `mattpocock/skills`
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
- copies my own hooks (**complexity-escalate**) into `~/.claude/hooks/` (executable)
- copies my **statusline** (`statusline.sh`) into `~/.claude/` (executable)
- clones the third-party skills (**caveman**, **handoff**, **grill-me**, **stop-slop**, **spec-driven-development**)
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
own keys/hooks). Key pieces:
- `"model": "opusplan"` — Opus in plan mode, Sonnet for execution.
- the `UserPromptSubmit` hook wiring `complexity-escalate.py` — auto-escalates complex prompts.
- `"statusLine"` wiring `statusline.sh` — shows the live model.
- `permissions.allow` — read-only MCP entries (playwright snapshot/screenshot/console, pal chat)
  so those stop prompting. Tune to your own usage; never allowlist write/exec tools.

Prefer Sonnet-always with no auto-escalation? Set `"model": "sonnet"` and drop the hook block.

### 4. Reload
Restart Claude Code or run `/clear` so the new skills + hooks load.

### Verify
```bash
ls ~/.claude/skills          # council, memory-write-gate, caveman, handoff, grill-me, stop-slop, spec-driven-development
```
In Claude Code the skills show up by name (e.g. invoke `/council`, or `caveman` / `handoff`).

### Manual install (no script)
```bash
cp -r skills/council skills/memory-write-gate ~/.claude/skills/
mkdir -p ~/.claude/hooks && cp hooks/complexity-escalate.py ~/.claude/hooks/ && chmod +x ~/.claude/hooks/complexity-escalate.py
cp statusline.sh ~/.claude/statusline.sh && chmod +x ~/.claude/statusline.sh
# third-party, from source:
git clone --depth 1 https://github.com/mattpocock/skills /tmp/mp
cp -r /tmp/mp/skills/productivity/{caveman,handoff,grill-me} ~/.claude/skills/
git clone --depth 1 https://github.com/hardikpandya/stop-slop ~/.claude/skills/stop-slop
git clone --depth 1 https://github.com/addyosmani/agent-skills /tmp/ao && cp -r /tmp/ao/skills/spec-driven-development ~/.claude/skills/
```

### Uninstall
```bash
rm -rf ~/.claude/skills/{council,memory-write-gate,caveman,handoff,grill-me,stop-slop,spec-driven-development}
rm -f ~/.claude/hooks/complexity-escalate.py ~/.claude/statusline.sh
# then remove the UserPromptSubmit hook + statusLine blocks from ~/.claude/settings.json
```

### Tune the complexity router
- Threshold / keyword weights: edit the constants at the top of `complexity-escalate.py`.
- Decision log (every prompt's score + reasons): `~/.claude/logs/complexity-escalate.log`.

## Notes
- **One bootstrap-hook *framework* only** (superpowers). Skills stay hookless; the only extra
  hook is the small standalone `complexity-escalate` (a single `UserPromptSubmit` script).
- **Token frugality**: each always-loaded skill costs cold-start tokens every session —
  install what you use, gate the rest.
- Third-party skills carry a `SOURCE.md` with their upstream + license.

## License
MIT (my own skills). Third-party skills retain their own licenses at their source.
