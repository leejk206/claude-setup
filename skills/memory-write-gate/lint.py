#!/usr/bin/env python3
"""
lint.py — stale-dependent detector for a [[link]]-based memory store.
Part of the `memory-write-gate` skill (jk_lee, from /research/memory-validity).

A memory store where facts are files and dependencies are `[[name]]` links (e.g. Claude
Code auto-memory). When a ROOT fact changes, memories that DEPEND on it can go stale. This
flags, for each link A→B, the case where B (root) was modified MORE RECENTLY than A
(dependent) — i.e. A may not reflect B's current state. Also flags orphan links (→ missing
file). It only REPORTS; you decide what to revise (that's the gate).

Usage:
  python3 lint.py [memory_dir]
  # default: ./memory if it exists, else the dir of this command's cwd
"""
import os
import re
import sys

LINK = re.compile(r"\[\[([^\]]+)\]\]")


def find_default_dir() -> str:
    for c in ("memory", "."):
        if os.path.isdir(c) and any(f.endswith(".md") for f in os.listdir(c)):
            return c
    return "."


def stem(name: str) -> str:
    return os.path.splitext(os.path.basename(name))[0].strip()


def main() -> None:
    d = sys.argv[1] if len(sys.argv) > 1 else find_default_dir()
    if not os.path.isdir(d):
        print(f"not a directory: {d}")
        sys.exit(1)

    files = {}  # stem -> (path, mtime)
    for fn in os.listdir(d):
        if fn.endswith(".md"):
            p = os.path.join(d, fn)
            files[stem(fn)] = (p, os.path.getmtime(p))

    stale, orphan = [], []
    for s, (path, mtime) in files.items():
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for raw in set(LINK.findall(text)):
            target = stem(raw)
            if target == s:
                continue
            if target not in files:
                orphan.append((os.path.basename(path), raw))
                continue
            root_mtime = files[target][1]
            if root_mtime > mtime + 1:  # root changed AFTER this dependent
                stale.append((os.path.basename(path), os.path.basename(files[target][0])))

    print(f"memory-write-gate lint · {d} · {len(files)} memories\n")
    if stale:
        print(f"⚠️  {len(stale)} possibly-stale dependent(s) — root changed after dependent:")
        for dep, root in sorted(stale):
            print(f"    {dep}  ← depends on  {root}  (review {dep})")
    else:
        print("✅ no stale dependents (no root is newer than something that links it)")
    if orphan:
        print(f"\n🔗 {len(orphan)} orphan link(s) → missing target:")
        for src, tgt in sorted(orphan):
            print(f"    {src}  → [[{tgt}]]  (no such memory)")
    print("\n(flags only — revise per the gate; root change ⇒ check/invalidate dependents)")


if __name__ == "__main__":
    main()
