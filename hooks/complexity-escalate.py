#!/usr/bin/env python3
"""
complexity-escalate.py — UserPromptSubmit hook.

결정적(deterministic) 복잡도 분류기. LLM 판단을 믿지 않고 규칙으로 점수를 매긴다.
점수가 임계값 이상이면 additionalContext를 주입해, 메인 루프(Sonnet)가 핵심 추론을
Opus 서브에이전트에 위임하도록 강제한다.

- 네트워크/API 키 불필요. 입력은 stdin의 hook JSON, 출력은 stdout의 hook JSON.
- 모든 판정은 ~/.claude/logs/complexity-escalate.log 에 JSONL로 남긴다 (임계값 튜닝용).
- 실패해도 절대 사용자 프롬프트를 막지 않는다 (조용히 통과).

튜닝: 아래 THRESHOLD / SIGNALS 가중치만 바꾸면 된다.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

# ── 튜닝 노브 ───────────────────────────────────────────────────────────────
THRESHOLD = 5          # 이 점수 이상이면 HIGH → 격상
MAX_PROMPT_LOG = 280   # 로그에 남길 프롬프트 앞부분 길이
LOG_PATH = os.path.expanduser("~/.claude/logs/complexity-escalate.log")

# 키워드 신호: (정규식, 가중치). 한글/영어 혼용. 무거운 추론을 시사하는 어휘.
KEYWORD_SIGNALS = [
    (r"\b(architect|architecture|refactor|migrat|race condition|concurren|"
     r"deadlock|algorithm|complexity|optimi[sz]e|profil|benchmark|"
     r"distributed|invariant|proof|prove|trade-?off|throughput|"
     r"backward[- ]compat|threat model|security audit)\b", 3),
    (r"(설계|아키텍처|리팩터|리팩토링|마이그레이션|동시성|교착|경쟁\s*상태|"
     r"알고리즘|복잡도|최적화|성능\s*개선|병목|증명|트레이드오프|불변식|"
     r"전면\s*개편|구조\s*개선|위협\s*모델|보안\s*감사)", 3),
    (r"\b(debug|root cause|why does|why is|investigate|diagnose|"
     r"design a|design the|compare|evaluate|reason about)\b", 2),
    (r"(왜\s|원인|근본\s*원인|디버그|진단|분석해|비교해|평가해|설계해|"
     r"검토해|심층|딥다이브|전략)", 2),
    (r"\b(build|implement|create) (a |an |the )?(system|service|pipeline|"
     r"framework|protocol|engine|compiler|parser|scheduler)\b", 2),
    (r"(시스템|파이프라인|프레임워크|프로토콜|엔진|컴파일러|스케줄러)\s*"
     r"(구현|구축|설계|만들)", 2),
]

# 다단계/조건을 시사하는 구조 신호.
STEP_PATTERNS = [
    (r"\b(step\s*\d|first.*then|after that|finally)\b", 1),
    (r"(단계|먼저.*그다음|그\s*후|마지막으로|순서대로|각각)", 1),
]


def score_prompt(prompt: str):
    """프롬프트 → (점수, 근거 리스트)."""
    reasons = []
    score = 0
    low = prompt.lower()

    # 1) 길이 신호
    words = len(prompt.split())
    if words >= 220:
        score += 3; reasons.append(f"length:{words}w(+3)")
    elif words >= 100:
        score += 2; reasons.append(f"length:{words}w(+2)")
    elif words >= 45:
        score += 1; reasons.append(f"length:{words}w(+1)")

    # 2) 코드/스택트레이스/파일경로 신호
    code_fences = prompt.count("```")
    if code_fences >= 2:
        score += 2; reasons.append("codeblock(+2)")
    if re.search(r"Traceback|Exception|at .+\(.+:\d+\)|panic:|\bError:\s", prompt):
        score += 2; reasons.append("stacktrace(+2)")
    file_hits = len(re.findall(r"\b[\w./-]+\.(py|ts|tsx|js|jsx|rs|go|sol|java|c|cpp|h)\b", prompt))
    if file_hits >= 3:
        score += 2; reasons.append(f"files:{file_hits}(+2)")
    elif file_hits >= 1:
        score += 1; reasons.append(f"files:{file_hits}(+1)")

    # 3) 키워드 신호
    for pat, w in KEYWORD_SIGNALS:
        if re.search(pat, low) or re.search(pat, prompt):
            score += w; reasons.append(f"kw(+{w})")

    # 4) 다단계 구조 신호
    for pat, w in STEP_PATTERNS:
        if re.search(pat, low) or re.search(pat, prompt):
            score += w; reasons.append(f"steps(+{w})")

    # 5) 질문 다수
    q = prompt.count("?") + len(re.findall(r"(까요\?|나요\?|ㅂ니까)", prompt))
    if q >= 3:
        score += 1; reasons.append(f"questions:{q}(+1)")

    return score, reasons


def log(record: dict):
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # 로깅 실패가 프롬프트를 막아선 안 됨


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)  # 파싱 실패 → 조용히 통과

    prompt = data.get("prompt", "") or ""
    if not prompt.strip():
        sys.exit(0)

    score, reasons = score_prompt(prompt)
    high = score >= THRESHOLD

    log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "session": data.get("session_id"),
        "score": score,
        "threshold": THRESHOLD,
        "decision": "HIGH" if high else "low",
        "reasons": reasons,
        "prompt_head": prompt[:MAX_PROMPT_LOG],
    })

    if not high:
        sys.exit(0)  # 단순 작업 → Sonnet 그대로

    context = (
        f"[complexity-router] 결정적 분류기가 이 프롬프트를 복잡도 HIGH로 판정했습니다 "
        f"(score={score} ≥ threshold={THRESHOLD}; 근거: {', '.join(reasons)}).\n"
        "정책: 핵심 추론·설계·디버깅·아키텍처 결정은 현재 메인 루프에서 직접 처리하지 말고 "
        "Agent 도구로 Opus 서브에이전트(model:'opus')에 위임해 수행한 뒤, 그 결과를 검토·통합하라. "
        "단순 조회·파일 편집·확인 같은 가벼운 후속 작업은 메인에서 그대로 진행해도 된다. "
        "이미 플랜 모드(Opus)라면 추가 위임은 생략 가능."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
