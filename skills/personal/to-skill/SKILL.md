---
name: to-skill
description: Distill the current session into a reusable skill by extracting its repeatable core, checking it against the existing canon, then handing a clean brief to /write-a-skill. Use when the user says "/to-skill", "turn this into a skill", "make a skill out of what we just did", "capture this workflow", or wants to codify the behavior of the current interaction into a new skill.
---

# to-skill

Turn what *just happened* in this session into a reusable skill. Unlike `write-a-skill` (where you name the domain up front), this skill reads the transcript, figures out what's worth keeping, and only then delegates to `write-a-skill` to build it.

## Workflow

1. **Introspect the session.** Read back over the current conversation and identify the repeatable core:
   - The goal / class of task being solved
   - The sequence of actions taken (in order)
   - Which tools and **sub-skills** were invoked, and when
   - Decisions, heuristics, and gotchas applied along the way

2. **Distill.** Separate the reusable *pattern* from the session-specifics. Strip out this ticket, this file, this bug, this branch — keep the shape that generalizes. Draft a tight brief containing:
   - **Trigger** — when a future session should reach for this skill
   - **Steps** — the generalized action sequence
   - **Sub-skills / tools** — what it should call and in what order
   - **Gotchas** — failure modes and guardrails learned this session

3. **Canon check (advisory).** List `~/.claude/skills` and the project's `.claude/skills`, then compare the distilled behavior against them:
   - If an existing skill already covers it → say so and recommend *extending that skill* instead of creating a new one.
   - Give an honest **reuse estimate** (one-off / occasional / frequent).
   - This gate is advisory: surface the comparison and the recommendation, then defer to the user. Build unless they object.

4. **Confirm.** Present the distilled brief, the reuse estimate, and 2–4 name options (kebab-case, short, descriptive). Wait for the user to pick/approve or push back.

5. **Hand off.** Invoke `/write-a-skill` with the confirmed brief as its argument. Let `write-a-skill` own the actual authoring (structure, description, file layout, review). Do not re-implement that process here.

## Notes

- Keep the produced skill **universal and reusable** — the whole point of step 2 is that nothing session-specific leaks into it.
- If the session doesn't contain a genuinely repeatable pattern, say so plainly and recommend *not* creating a skill rather than manufacturing one.
- Prefer extending an existing skill over adding a near-duplicate to the canon.
