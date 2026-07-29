---
name: brief
description: Condense the previous verbose response into a tight, skimmable brief — bottom-line-up-front, key takeaways, and next actions only. When the brief contains a multi-step workflow, walk the user through it one step at a time. Use when the user says "/brief", "brief this", "too long", "tl;dr that", "cut the cruft", or wants the last answer trimmed to what actually matters.
---

# Brief

Rewrite the **immediately preceding assistant response** as a brief a busy person can extract value from in seconds. Do not add new information, re-run tools, or re-do the work — only compress what was already said.

## Output shape

Lead with the answer. Then only what's needed to act.

```
**Bottom line:** <one sentence — the single most important takeaway>

**Key points:**
- <fact / finding — one line each, no throat-clearing>
- <...>

**Next actions:**  ← only if actions exist
- <imperative, concrete>
```

Omit any section that has nothing real to say. If the original response was a direct answer to a question, one or two sentences may be the whole brief — don't pad it back into a template.

## Rules for cutting

- **BLUF** — the conclusion goes first, never last.
- **Cut all hedging and preamble** — "I think", "it seems", "let me", "great question", "as we discussed", "in order to", restating the question back.
- **Bullets over prose.** One idea per line. No paragraph should exceed ~2 lines.
- **Keep the signal:** numbers, file paths, commands, decisions, blockers, tradeoffs. **Drop:** rationale the user already knows, alternatives already rejected, narration of what was done.
- **Preserve meaning.** Aggressive ≠ lossy on anything load-bearing. If a caveat changes the decision, keep it (one line).
- Don't invent structure that wasn't there. If the original had no next actions, don't manufacture them.

## Workflow mode (auto)

If the brief contains a **sequential, multi-step process** the user is expected to act on (setup steps, a migration, an ordered checklist, "first… then… finally"), do NOT dump all steps at once. Instead:

1. State the goal + total step count in one line: `Workflow: <goal> — N steps. I'll go one at a time.`
2. Present **step 1 only** — the action, plus the one thing to watch for.
3. Ask: `Ready for the next step? (or tell me what happened / what's unclear)`
4. On confirmation, advance to the next step. If the user reports a problem or a question, resolve that before advancing.
5. After the last step, give a one-line wrap-up: what's now true / how to verify.

Trigger this only for steps the user performs in sequence. A flat list of independent facts, options, or findings is **not** a workflow — just brief it as bullets.

## Notes

- If there is no prior assistant response to condense (e.g. first turn), say so and ask what to briefify.
- Never soften the compression to "be safe" — the whole point is fewer words, faster comprehension.
