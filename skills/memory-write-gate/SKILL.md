---
name: memory-write-gate
description: Use when writing, updating, consolidating, or auditing agent memory. Enforces jk_lee's memory-validity findings — corruption enters at the WRITE path, not retrieval. Keep raw episodes primary, gate consolidation, and on a root-fact change INVALIDATE dependent beliefs (don't latest-write-wins). Run `lint.py` to detect stale dependents in a [[link]]-based memory store. Invoke before compaction/overwrite or to audit memory health.
---

# memory-write-gate

A discipline for *writing* memory, from jk_lee's research (`/research/memory-validity`):
continuous LLM consolidation drops memory utility *below no-memory*, and naive overwrite
leaves dependent beliefs stale. Strong models only **delay** corruption, they aren't immune.
So the engineering goes on the **write path**, not retrieval.

## The gate (apply on every memory write)
1. **Raw episodes are primary.** Keep the original record. A summary is a derived view, not
   a replacement — never delete the source to save space.
2. **Gate consolidation.** Do NOT auto-compress/merge on every turn. Consolidate only on an
   explicit trigger (e.g. end of a work item), and keep the pre-consolidation raw.
3. **Dependency-aware invalidation.** When a *root fact* changes, do NOT just overwrite it
   and move on — find memories that DEPEND on it ([[links]] to it) and mark them for review.
   Latest-write-wins silently strands dependents (his runs: ~89% left stale).
4. **Measure, don't assume.** Periodically check that memory still helps (vs no-memory). If
   recall quality drops, the consolidation is the suspect.

## Behavior for the model (when this skill is active)
- Updating a memory file: **append/revise, don't destructively rewrite**; preserve the
  fact's origin. Avoid lossy "compress everything" passes.
- Changing a fact other memories reference: run `lint.py` (or manually) to find dependents
  via `[[name]]` links and update/flag them in the same change.
- Suspicious recall: suspect the write/consolidation path first, not retrieval.

## lint.py — stale-dependent detector
Scans a [[link]]-based memory store (file-per-fact with `[[name]]` links, e.g. Claude Code
auto-memory). For each link A→B, if B (the root) was modified **more recently** than A (the
dependent), A may now be stale relative to B.

```bash
python3 ~/.claude/skills/memory-write-gate/lint.py <memory_dir>
# default dir: the current project's memory/ if found
```
It reports `dependent ← root` pairs where the root is newer (stale risk), plus orphan links
(point to a missing file). It only *flags* — you decide what to revise (that's the gate).

## Scope
Applies to file-based memory with `[[links]]` (Claude Code auto-memory) and to any external
engine (Mem0/agentmemory/Letta): if you run one, use it **retrieval-only with capture/
consolidation gated** — the engines optimize retrieval, which is not where the bug is.
