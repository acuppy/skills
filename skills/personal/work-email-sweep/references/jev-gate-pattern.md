# Jev Call-Site Construction Pattern (proven on call site #1, 2026-10-27)

Used by the work-email-sweep routine and reusable for any future Jev call site
(Asana Eisenhower sort is the next candidate). The `jev-decision-api` SKILL.md
carries the doctrine (judgments vs decisions, error≠answer, atomic questions);
this file carries the BUILD pattern.

1. **Read-only first.** v1 classifies and reports; state-changing actions stay
   separate and approval-gated (e.g. archive/move never happens without Adam's
   explicit word).
2. **Triple-gate risky classes.** A consequential action class (archive) requires
   ALL of: choice answer = the risky class, probability of that class ≥ 0.85,
   AND a companion noul (human_sender) < 0.2. A single choice answer alone is
   never enough.
3. **Error = safe side.** Per-item try/except; a Jev/API error counts the item
   toward the SAFE disposition (kept), prints loudly (ERROR-KEPT), and never
   becomes an answer.
4. **Fan out related judgments in ONE ask()** (e.g. disposition choice +
   human_sender noul) — one request per item, ~0.2s sleep between items to stay
   polite on rate limits.
5. **Empty live input ≠ untested.** When the real queue is empty at build time,
   push representative + hard cases through the SAME live code path (import the
   module; reuse its QUESTIONS/CONTEXT constants) and require correct
   classifications + gate behavior before wiring the cron. Verified 2026-10-27:
   4 synthetic cases → correct disposition, never-archive class (bank statement)
   kept, urgent surfaced despite low confidence, digest passed the triple gate.
6. **Persist a state file** (JSON: ts + per-item ids + disposition) for audit
   and calibration review (~/.hermes/cache/<call_site>_state.json).
7. **Wire as no_agent script cron** — deterministic, one-line success output,
   FAIL-loud failure line.

Live call site #1: `~/.hermes/scripts/jev_imbox_triage.py` (Hey imbox triage,
job 62e848569b49, 06:30 PT daily, read-only, triple-gate archive candidates,
never moves without Adam's approval). Cost per full sweep: ~$0.0001.