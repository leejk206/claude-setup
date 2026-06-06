---
name: council
description: A deliberation skill that convenes multiple specialized sub-agents to debate a planning decision or evaluate whether a project is heading in the right direction. Use this skill whenever the user invokes `/council`, or when they ask for a thorough review, second opinion, or directional check on a plan, design, proposal, or in-progress project — even if they don't say "council" explicitly. Triggers include phrases like "review my plan", "is this the right direction", "what are we missing", "stress-test this idea", "should we do X or Y", "deep dive on this decision".
---

# Council

A skill that runs a multi-agent deliberation to (a) reach a conclusion on a planning question, or (b) judge whether the current project direction is sound.

You play the role of the **Moderator** throughout. You spawn other agents as parallel sub-tasks, read their outputs, decide what to do next, and at the end write the synthesis the user actually sees.

---

## When this skill triggers

The primary trigger is `/council`, optionally with arguments:

- `/council <topic>` — convene the council on a topic
- `/council --with <agent1>,<agent2> <topic>` — pre-summon specific Layer 2 agents alongside the core

Also trigger this skill when the user clearly wants a thorough multi-angle review of a plan/decision even without typing `/council`. When in doubt, ask if they want a council session.

---

## The roster

### Layer 1 — Core (always called)

Defined in `agents/core/`:

- **Steelman Advocate** (`steelman.md`) — constructs the strongest possible case for the proposal
- **Red Team** (`red-team.md`) — finds weaknesses, simulates failure paths
- **Context Keeper** (`context-keeper.md`) — holds project facts, architecture, prior decisions; corrects factual errors

### Layer 2 — Pool (summoned as needed)

Defined in `agents/pool/`:

- **User Advocate** (`user-advocate.md`) — real-user perspective
- **Pragmatist** (`pragmatist.md`) — execution feasibility, resources, priorities
- **First Principles** (`first-principles.md`) — what problem are we actually solving?
- **Analogist** (`analogist.md`) — comparable cases, prior art
- **Constraint Challenger** (`constraint-challenger.md`) — questions assumed-fixed constraints
- **Skeptical Stakeholder** (`skeptical-stakeholder.md`) — outside reviewer / investor / boss perspective
- **Confidence Calibrator** (`confidence-calibrator.md`) — checks whether confidence levels are justified
- **Cost** (`cost.md`) — cost angle (money, time, complexity, opportunity)

You (Moderator) do not need a separate file — your instructions are this SKILL.md.

---

## Workflow

### Phase 0 — Context sufficiency check

Before convening anyone, judge whether the current conversation has enough context to deliberate meaningfully. The purpose of this skill is **planning conclusions or directional judgments**, so you need at least a rough sense of:

- What is being decided or evaluated
- What "good" would look like for this user

You do **not** need a formal checklist filled in. Use judgment. If the picture is roughly clear, proceed. If something critical is missing, ask the user with **free-form questions targeting only the critical gap(s)** — do not hand them a form. Examples of "critical gaps" that warrant asking:

- The topic is too vague to debate (e.g. "/council my project" with no further info)
- The judgment criteria are completely opaque ("/council should we ship this?" — ship to whom, for what?)

Examples of "good enough to proceed":
- The conversation already covered the project background
- The user attached a planning doc or shared a clear proposal
- The user's previous messages make the question concrete

When in doubt, **lean toward proceeding** and state your working assumptions at the top of Phase 1, so the agents and the user can correct them if wrong.

### Phase 1 — Round 1: Initial opinions

Spawn the three core agents in parallel as sub-tasks. Give each the same **briefing** (see `templates/briefing.md`):

- The user's question / topic
- The project context (as you have it)
- Your stated working assumptions, if any
- That agent's role file (read its `agents/core/<name>.md`)

Wait for all three to return. Read their outputs.

If the user pre-specified Layer 2 agents via `--with`, spawn them in Round 1 too.

### Phase 2 — Rounds 2–4: Rebuttals and depth

After each round, decide:

1. **Stop and synthesize** — if the picture is clear, disagreements are well-mapped, or no new insight is emerging.
2. **Summon Layer 2** — if a specific angle is missing (e.g. nobody is asking whether users actually want this → summon User Advocate).
3. **Another rebuttal round** — if there's a sharp disagreement worth pushing on. Brief each agent with the prior round's other-agent opinions and ask them to respond/refine.

**Hard cap: 4 rounds total.** If you hit Round 4 and still feel unresolved, write the synthesis honestly: "The council did not converge on X. Here's where the disagreement sits."

Layer 2 agents can be summoned in any round, not just Round 1. You can also re-summon a core agent for a focused follow-up.

### Phase 3 — Synthesis

Write the final output (see "Output format" below). This is what the user sees as your reply. The intermediate sub-agent outputs are not shown to the user directly — you summarize them.

---

## Spawning sub-agents

Each agent is a parallel sub-task. When spawning, the sub-task receives:

1. The agent's role file content (read `agents/core/<name>.md` or `agents/pool/<name>.md`)
2. The briefing (built from `templates/briefing.md`)

Spawn agents for a given round **in parallel** (single message, multiple tool calls). Do not run them serially — that wastes turns and they should not see each other's current-round outputs until the next round.

If you are running in an environment without sub-agent / Task tool support, fall back to simulating each agent yourself in sequence, clearly labeling each persona's output internally before synthesizing. This is degraded mode but still useful.

---

## Output format

Use this exact structure for the final reply:

```
# Council verdict: <one-line conclusion>

## Conclusion
<2–5 paragraphs. The actual answer to the user's question. Concrete and decisive where possible; honest about unresolved points where not.>

## Key issues debated
<Organized by issue, not by agent. For each major point of contention or insight:>

### Issue 1: <name of the issue>
- **Where the council aligned**: <if there was alignment>
- **Where it split**: <positions and who held them, briefly>
- **What tipped the synthesis**: <why the conclusion came out the way it did on this issue>

### Issue 2: ...

## Assumptions and caveats
<Any working assumptions you made in Phase 0, and any caveats about the limits of this council session — e.g. "didn't have access to current user data", "assumed timeline is Q3", etc.>

## Council composition
<List which agents participated and over how many rounds. One line.>
```

Keep the conclusion section first and tight — that's what the user reads first. The issues section is where the substance lives.

---

## Important behaviors

- **Don't reveal sub-agent raw output.** Synthesize. The user wants a verdict and the substance, not a transcript dump.
- **Don't be diplomatic when there's a clear answer.** If the council clearly thinks the plan is misguided, say so. If it clearly thinks it's strong, say so. The point of a council is decisiveness through deliberation, not hedging.
- **Quote agents sparingly and only when the exact wording matters** — usually the issues section can be in your own words.
- **Stay in Moderator voice in the final output.** The agents are internal machinery; the user is talking to you.
- **If context was insufficient and you asked the user**, do not proceed until they answer. Don't run the council on half-context.
