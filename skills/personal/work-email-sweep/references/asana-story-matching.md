# Asana Story-Text Matching Fallback (deferred enrichment, designed 2026-10-27)

Not wired in v1 — work_sweep.py classifies on the Gmail message snippet only.
If week-1+ calibration shows Jev misjudging Asana notification emails because
snippets are ambiguous ("Small correction to the AC5 test steps above." is
unjudgeable from the snippet), this is the designed escalation path:

## Why it's deferred
The snippet usually suffices, and every enrichment adds a second API surface
(Asana REST) + quota + failure modes. Only add it on evidence of misses.

## The mechanism (all rails already verified live 2026-10-27)
1. Asana notification emails carry the task ticket ID in the subject
   (`ID-####: <title>`) — extract mechanically with a regex.
2. Task gid lookup: the subject's ID is the Asana custom-ID, not the gid —
   resolve via the Asana REST search: `GET /workspaces/<WS>/tasks/search`
   with the ID text, or keep a small ID→gid cache in the sweep state file.
3. Pull the full story via the notifications API (route + workspace-param +
   story.text caveats in `ops/asana-connectivity`): the story text IS the
   full comment content the snippet truncates.
4. Feed the full story.text to Jev as additional state (keep the original
   question set — richer state, same contract). The "who commented last"
   ownership check (did Adam already respond in Asana?) can ride the same
   request as a noul.
5. Everything stays READ-ONLY on the Asana side — no mark-read, no updates.

## When to trigger
- A real ask gets archived as noise (Adam reports it via the label:Swept glance),
- or unsure-rate on Asana-sender threads stays >0 across a full week.

Both signals mean the snippet starves the judgment — this reference is the
fix that doesn't change the architecture (same single-source Gmail design,
one enrichment join, no matching heuristics on timestamps).