#!/usr/bin/env python3
"""Claude Code statusline — model · dir · git branch.

opusplan은 플랜모드=Opus / 실행=Sonnet으로 모델을 바꾸므로, 지금 어느 모델인지
한눈에 보이도록 모델명을 맨 앞에 둔다. stdin으로 statusline JSON을 받는다.
"""
import json
import os
import sys


def git_branch(d):
    # .git/HEAD를 직접 읽어 subprocess 없이 빠르게 브랜치명 추출
    cur = os.path.abspath(d)
    while True:
        head = os.path.join(cur, ".git", "HEAD")
        if os.path.isfile(head):
            try:
                with open(head, encoding="utf-8") as f:
                    ref = f.read().strip()
                if ref.startswith("ref: refs/heads/"):
                    return ref[len("ref: refs/heads/"):]
                return ref[:7]  # detached HEAD → 짧은 SHA
            except Exception:
                return None
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def main():
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:
        data = {}

    model = (data.get("model") or {}).get("display_name") or \
            (data.get("model") or {}).get("id") or "?"
    ws = data.get("workspace") or {}
    cur_dir = ws.get("current_dir") or data.get("cwd") or os.getcwd()
    name = os.path.basename(cur_dir.rstrip("/")) or cur_dir

    parts = [f"⏺ {model}", name]
    br = git_branch(cur_dir)
    if br:
        parts.append(f"⎇ {br}")

    style = (data.get("output_style") or {}).get("name")
    if style and style != "default":
        parts.append(f"[{style}]")

    print("  ".join(parts))


if __name__ == "__main__":
    main()
