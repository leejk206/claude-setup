# Briefing template

This is the template the Moderator fills out and passes to each sub-agent when spawning them. Adapt freely — the goal is to give the agent everything it needs and nothing it doesn't.

---

## Template

```
You are participating in a council deliberation as the [AGENT NAME].

# Your role
[Paste the full content of agents/core/<name>.md or agents/pool/<name>.md here.]

# The user's question
[The actual question or topic. Paste the user's original request, or a clean restatement of what's being decided.]

# Project context
[Whatever context the Moderator has gathered: project background, the proposal under discussion, relevant constraints, attached docs, prior decisions. Keep this focused — pass what's relevant, not the whole conversation.]

# Working assumptions
[Any assumptions the Moderator made in Phase 0 when context was thin. The agent should treat these as the working basis and flag if they seem wrong.]

# What this round is for
[One of:
 - "Round 1: give your initial view per your role's output spec."
 - "Round N rebuttal: here are the other agents' positions from the prior round. Respond per your role's guidance on rebuttal rounds. Other agents' prior outputs follow."
 - "Targeted follow-up: [specific question the Moderator wants this agent to address]."]

# Other agents' prior outputs (rounds 2+ only)
[Paste the relevant outputs from prior rounds. Label each clearly: "From Red Team, Round 1: ..." etc.]

# Return format
Per your role's output spec. Be specific, be concrete, and stay in your role — don't drift into other roles' territory.
```

---

## Notes on filling this out

- **Keep "Project context" lean.** If you dump everything, the agent loses signal. Distill to what bears on the question.
- **Working assumptions matter.** If you made any in Phase 0, state them — the agents will calibrate against them, and Context Keeper may correct them.
- **For rebuttal rounds, include only relevant prior outputs.** If the agent is responding to a specific position, include that. Don't paste all prior rounds for every agent.
- **Don't tell the agent the conclusion you want.** They should reach their own view per their role. The Moderator synthesizes, not the agents.
