---
name: recap
description: >
  Delivers a concise catch-up briefing for the current session. Scans the
  active conversation for unresolved questions, pending decisions, and
  in-progress work; checks recent git commits and open PRs; and searches
  recent session transcripts for context shifts from other chats. Outputs
  a natural re-entry summary covering: what we were doing, where the user
  left off, what's still open, and a recommended next step. Use when the
  user says "/recap", "where were we", "catch me up", "give me a recap",
  or returns after a break and wants a quick re-entry point.
---

# Recap

Deliver a concise re-entry briefing scoped to the current project and
conversation. Work the steps in order, then write the briefing — nothing else.

## Steps

### Step 1 — Scan this conversation

Read the current session top-to-bottom and identify:

- **Unresolved questions** — the user asked something and no clear answer landed
- **Pending decisions** — options were presented but no choice was made
- **In-progress work** — tasks started but not confirmed complete
- **Direction changes** — pivots, abandoned approaches, or contradicted earlier intent

### Step 2 — Check recent repo activity (run in parallel)

```bash
git log --oneline -10                       # recent commits
gh pr list --state open --limit 5           # open PRs
gh pr list --state merged --limit 3         # recently merged
```

Note any open PRs awaiting review, recently merged work that affects the
conversation, or uncommitted local changes (`git status --short`).

### Step 3 — Search recent sessions (optional)

Use `mcp__ccd_session_mgmt__search_session_transcripts` to look for:

- Decisions made in other chats that contradict or extend this session's direction
- Follow-ups flagged in other conversations but not yet acted on
- Context that would change the recommended re-entry point

Skip this step if the current conversation is clearly self-contained and
recent (same day, no cross-session references in the args).

### Step 4 — Synthesize and write the briefing

Cover these four things — in whatever order and form fits the situation:

1. **What we were doing** — the most recent concrete action (file edited, method
   written, PR pushed, decision made)
2. **Where you left off** — your closing intent: the last thing you asked,
   decided, or said before the session went quiet
3. **What's still open** — unresolved questions, pending PRs, uncommitted changes,
   outstanding decisions; be honest if nothing is open
4. **Where to start** — one specific, opinionated re-entry point, not a list

The format is yours to choose. Write prose if that's clearest; use bullets if
there are multiple open items worth scanning; use a header only if the briefing
is long enough to warrant it. Match the weight of the format to the weight of
the content — a short session shouldn't get a long structured report.

## Tone

- Tight and direct — no filler, no meta-narration ("After scanning, I found…")
- Honest: if nothing is unresolved, say so
- The re-entry recommendation should be opinionated — pick one thing
