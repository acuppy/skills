---
name: conduct
description: Orchestrates a coding prompt across a model hierarchy — fable reasons, plans, and implements; opus agents provide independent review and cross-domain thoughtwork; sonnet agents produce code only for parallelizable work items; all work is verified mechanically first, then against the plan, with final review by fable. Use when the user invokes /conduct, asks to "orchestrate" a task, or wants a large prompt executed via structured delegation.
---

# Conduct — tiered model orchestration

You (the main loop, fable) are the conductor. Be honest about what
delegation buys: **context-window hygiene** (your window stays clean for
judgment) and **parallelism**. It does NOT save tokens on small serial work —
every sub-agent pays full context-establishment cost re-exploring what you
already know. So the default is: you implement, agents judge. Delegate
production only when work items are independent and parallelizable.

## Step 1 — Triage by decision density, not file count

Decision density = judgment calls per change. A 1-file concurrency fix is
dense; a 12-file mechanical rename is sparse.

| Tier | Signals | Action |
|------|---------|--------|
| **Trivial** | Obvious edit, zero design decisions | Do it yourself. No plan file, no agents. Stop here. |
| **Standard** | Real design decisions, but serial work — items depend on each other or there are few of them | You implement; one opus agent reviews. See Step 3. |
| **Large** | Many (roughly 5+) *independent* work items, mechanically executable once specified | Workflow: sonnet producers in parallel. See [WORKFLOW.md](WORKFLOW.md). |

When in doubt, pick the smaller tier.

## Step 2 — Build the plan (fable-only work)

For standard and large tiers, write a plan file to the scratchpad
(e.g. `<scratchpad>/conduct-plan.md`). **The plan file is the contract** —
sub-agents share no conversation context. Include:

- **Goal** — the user's intent in your words
- **Work items** — numbered; per item: files, exact change, done-criteria
- **Mechanical checks** — a runnable command per item (rspec path, rubocop,
  type check). Every done-criterion that CAN be a command MUST be a command.
- **Constraints** — conventions, files NOT to touch
- **Quality bar** — SRP per class/method, Sandi Metz heuristics (small
  methods, small classes, message-passing), side effects isolated at the
  shell. Reviewers enforce this, so state it here.

If the design is genuinely cross-domain and you can't confidently decompose
it, spawn one opus scout ([PIPELINE.md](PIPELINE.md)) to write a
decomposition file; review it critically before adopting it into the plan.

**Re-triage after planning.** If the plan came out as 1–2 straightforward
items, the task was trivial-tier all along — tear up the ceremony and just
do it. Don't run orchestration because you already wrote a plan file.

## Step 3 — Standard tier: fable implements, opus reviews

1. **Implement (you)** — your context is already hot; you are the strongest
   model available. Write the code per your own plan.
2. **Mechanical checks (you)** — run every command from the plan's
   Mechanical checks section. Fix failures before spending any LLM review.
3. **Review** — spawn one opus agent (`Agent(model: "opus")`, template in
   [PIPELINE.md](PIPELINE.md)) with the plan path. It verifies plan
   conformance AND code quality (the plan's Quality bar). Its value is
   independence: it hasn't watched you rationalize your choices.
4. **Repair (you, once)** — fix findings yourself, re-run mechanical checks,
   one re-review. Still failing → surface findings to the user with your
   read on whether plan or code is at fault; don't loop.

## Step 4 — Large tier: Workflow

Follow [WORKFLOW.md](WORKFLOW.md): sonnet producers fan out over independent
work items, a barrier, then opus verifiers (mechanical checks first), one
repair cycle, single JSON report back for your final review. (Skill-directed
Workflow use is an authorized opt-in.)

## Rules (all tiers)

- Pass **file paths, not file contents**, between agents.
- Agents return **conclusions, not transcripts** — structured output schemas,
  and every schema needs a `blocked` escape hatch so a stuck agent can say so.
- **Mechanical checks before LLM judgment** — a test run costs ~zero;
  an opus code-read is the most expensive verification instrument you have.
- Trust PASS; spot-check FAIL. Never re-read what a verifier confirmed.
- Hierarchy: you (fable) own intent, planning, implementation on serial work,
  and the final call. Opus owns independent judgment. Sonnet owns parallel
  production. Don't invert it.
