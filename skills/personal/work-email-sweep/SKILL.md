---
name: work-email-sweep
description: >
  Adam's work Gmail (adam.cuppy@chapterone.org) recurring noise sweep — script-as-mover
  (NO Gmail filter): daily Jev-classified triage that archives known noise, labels signal
  Sweep/Do, never touches humans/protected senders. Covers the shipped architecture,
  quota discipline, verification recipe, calibration loop, and hard constraints
  (organize-only). Use for any task touching work inbox triage, the work_sweep.py
  script, cron 80ffbc246c8b, or Asana ticket 1219954523473744 ("Design inbox triage").
category: personal-assistant
---

# Work Email Sweep (adam.cuppy@chapterone.org)

GOAL (Asana ticket 1219954523473744): reduce inbox noise, bubble up only critical
signals, save Adam's daily email-management time.

## Shipped architecture (settled 2026-10-27 after adversarial review)

**Script-as-mover. NO server-side Gmail filter.** `~/.hermes/scripts/work_sweep.py`
runs workdays 06:40 PT (cron 80ffbc246c8b, no_agent, apply mode, after the 06:00 digest;
cron `script` field = bare `work_sweep.py` — NO args in the field, apply is the script's
default mode; verify via `cronjob action=run` after any cron-layer change):

1. **Deterministic sender routing (no model, no drift):**
   - AUTO_ARCHIVE bots (truth lives elsewhere): noreply/no-reply@asana.com,
     heroku.security.notifications, notifications@github.com, hello/notifications@vanta.com,
     sheets/docs-dl-notification@google.com → Swept label + archive.
   - PROTECTED (never touched, reported as human): @chapterone.org humans,
     docusign.net, paycom, Google security alerts, Zoom/Heroku billing.
   - Everything else → Jev judgment.
2. **Jev judges the gray zone** (call-site pattern: `references/jev-gate-pattern.md`):
   disposition choice (signal/noise/unsure) + actionable noul. Signal → Sweep/Do label,
   STAYS in inbox. Noise → Swept + archive. Unsure/error → stays in inbox, reported.
3. **Reply-state detection = v4 open-queue model (re-vectored 2026-10-29).** A
   Sweep/Do thread leaves the daily re-list only when Adam replies on it
   (auto-detected: newest thread message from a chapterone.org sender) or the
   Label_8 sticker is stripped from the thread — the explicit done-mark for
   non-email completions. Approving in Paycom / answering in Asana does NOT clear
   it; the item keeps re-listing with growing age = the intended nag (flag to
   Adam if he wants stale items auto-swept instead). The summary email now shows
   the FULL open Sweep/Do queue (age-tagged) merged with the run's new items —
   never a per-run delta. Bit live 2026-10-29: under the old delta-only model the
   email said "2 to do" while the label held ~15 open threads accumulated across
   runs; Adam noticed the email-vs-label mismatch.
4. **Failure posture (the architecture's core decision):** script dies → unprocessed
   mail PILES UP in the inbox (loud, visible). A Gmail filter would invert this to
   silent burial — the exact risk the ticket flagged. Report-only validation also
   can't catch false negatives; week-1 calibration works because the noise is still
   in Adam's own inbox next to the script's calls.
5. **Failure posture leg 3 — interrupt-safety (added v4, 2026-10-29):** a kill
   (tool timeout, ctrl-C) can no longer produce silent loss. A KeyboardInterrupt
   handler flushes the state file AND emits a partial summary email whenever
   mutations already happened (that's the only case where dying quietly loses
   information; a kill during pure scanning stays silent). Bit live 2026-10-29:
   a 120s foreground-timeout run archived ~12 threads, then died before
   state-save + summary — those threads sat in Sweep/Do with no email ever
   naming them.

## v4 summary contract (full open queue, 2026-10-29)

The "Inbox Sweep ·" email is the authoritative daily view of Adam's open work
queue, not a per-run report:

- **TO DO = the full open Sweep/Do queue** (every thread still carrying Label_8,
  age-tagged by received date, newest-first) merged with threads newly classified
  this run. Subject count = open queue size, NOT today's delta.
- **Self-healing:** because the open queue is re-read from the label every run,
  any past gap (interrupted run, missed summary) re-surfaces on the next email
  automatically. No backfill scripts needed — do not write cosmetic backfills.
- **Open-set fetch detail:** `messages?maxResults=100&labelIds=Label_8` (the
  labelIds filter param works with the raw ID; `q=label:<ID>` does NOT — q=
  grammar matches label NAMES only). Skip summaries (subject-prefix check) and
  threads whose newest message is from Adam (he replied = in-flight or done).
- **Rendered via** the inbox-sweep-format skill's renderer; schema in its
  references/schema.md (todo/handled/fyi/swept fields, ISO-8601-PT timestamps).

## v3.1 (2026-10-29, Adam-approved) — full-queue email + interrupt safety

- **OPEN-SET RE-LIST (headline behavior change):** every apply run re-lists the
  ENTIRE open Sweep/Do queue in the summary email (fetch `messages?labelIds=<Sweep/Do ID>`,
  dedupe by threadId, skip summaries/own-mail/already-handled), merges the run's
  newly-classified todos in, sorts newest-first. The email IS the open queue —
  subject counts always agree with the label. Fixes the 10-29 complaint (email
  said "2 to do", label held ~15): the email previously reported only the run's
  delta; accumulated open items vanished from view while still pending.
- **Done-marker:** a thread leaves the re-list when (a) Adam replied last
  (existing handled-detection), or (b) Label_8 is stripped from the thread —
  the explicit "done" gesture for work handled outside email (Paycom approval
  in-app, Asana comment in-app). Items re-appear daily with growing age until
  one of those fires = the nag behavior the age-in-days spec implies.
- **INTERRUPT SAFETY:** KeyboardInterrupt mid-run → `_emergency_summary()`:
  flushes state + emits a partial summary whenever mutations already happened
  (killed runs stay honest); a kill during pure scanning stays silent (nothing
  lost). Incident 2026-10-29 11:07: a 120s foreground tool-timeout killed the
  run AFTER ~12 archive mutations but BEFORE summary + state-save — those
  threads appeared in the label and in NO email until the re-list self-healed it.
- **API pattern:** label filtering MUST use `messages.list?labelIds=<raw ID>` —
  the `q=` grammar only matches label display NAMES ("Sweep/Do"), never `Label_N`.
- Open-queue fetch capped `maxResults=100`; queue >100 means triage the queue.

## Non-negotiable constraints
- Work email = ORGANIZE-ONLY: never send/reply/forward/draft-from this account.
- Never trash/spam/delete. Archive = remove INBOX only (reversible via label:Swept).
- Asana side READ-ONLY: never call notification mark-read/update routes.
- Error ≠ answer: any per-thread failure = thread stays in inbox, reported as UNSURE.
- Wrong-noise is worse than wrong-signal; unsure defaults to surfacing.

## Verified rails (live-probed 2026-10-27)
- Work Gmail REST via `~/.google-mcp-work/adam.cuppy@chapterone.org.json` token +
  force-refresh (same auth pattern as kim_sched_watch.py) — NOT the MCP server, to
  dodge its shared quota pool.
- MCP rail `google-workspace-chapter-one` for ad-hoc/interactive use:
  search_gmail_messages, batch_modify_gmail_message_labels (whole threads + system
  labels), get_gmail_thread_content, manage_gmail_label (flat args: action/name/
  label_id — NOT a nested label object).
- Labels: Sweep/Do = `Label_8`, Swept = `Label_10` (created 2026-10-27), Sweep/Plan =
  `Label_9` (UNUSED — design cut to one signal label).
- Asana notification emails collapse PER-TASK (one thread = many notification messages);
  thread is the triage unit.
- Asana notifications API: see `ops/asana-connectivity` (route, workspace param required,
  story.text-only).

## Quota discipline (learned live: naive design 403'd)
Gmail API per-user quota is SHARED with the MCP server. Hard rules now in the script:
sender-scoped list queries (no all-threads listing), metadata-format GETs
(`format=metadata&metadataHeaders=From&metadataHeaders=Subject`), Jev GETs capped
(25/run), mutations capped (12/run) + paced (4s), quota 403/429 = graceful backoff
(exit 0, state preserved, next run continues). A 403 "Quota exceeded" on labels+search
while profile/messages succeed = quota, NOT a scopes problem — don't chase auth.

## Verification recipe (updated for v4; reuse on any change)
1. Report-mode run: counts + full classification list, zero mutations.
2. Apply run: check the archived count line.
3. Independent verify pass: `label:Swept` count == swept-classified archived;
   `label:Swept in:inbox` == 0 (archived really left the inbox).
4. Email-vs-label MUST agree: the summary's TO DO count == live
   `labelId=Label_8` open-queue size (minus summary/self threads). Under v4
   delta-only reporting this check was exactly what caught the Oct-29 bug
   (email said 2, label held ~15). Keep it as the standing acceptance gate.
5. State file `.work_sweep_state.json` + `.work_sweep_log.jsonl` written.
6. **Never verify an apply run with a foreground tool timeout smaller than the
   run's worst-case duration** (Jev pace + mutation pacing makes runs exceed
   120s easily — run background+poll, or timeout=300+). The Oct-29 interrupted
   verification run is the cautionary tale: it mutated Gmail then died before
   reporting, and the unreported batch read as "the sweep is mislabeling."

## Calibration loop (ongoing)
Week-1 watch items observed in the first live runs: Vanta threads split signal/noise
inconsistently (one flagged, digest/controls-attention noise-classed — borderline);
Salesforce/Heroku/Twilio renewal notices borderline (relationship mail vs robot mail);
Asana COMMENT mentions are noise-classed (correct default; tighten to mention-only if
a real ask ever gets archived). **Open flag (2026-10-29, awaiting Adam's veto):**
vendor marketing routed through `dev.admin@chapterone.org` ("via Dev Admin / Owners"
— Cloudflare, DNSimple product announcements) gets todo treatment because the
chapterone.org domain is blanket-protected; if Adam confirms, route the
"via Dev Admin / Owners" sender class through Jev judgment instead of protection.
Adam's veto data from glancing at label:Swept is the
only calibration source the script can't generate — prompt for it after 2-3 days.

## Pitfalls
- (2026-10-29) Killed mid-run ≠ failure-rollback: Gmail mutations already sent
  persist; only the summary/state are lost. The interrupt handler covers this;
  the open-set re-list is the belt-and-suspenders that heals ANY silent gap.
- Gmail q= vs labelIds: `q=label:Sweep/Do` matches NAMES only. Script-side
  filtering uses `labelIds=Label_N` (raw IDs) — don't mix them up.
- Marketing via protected senders: DNSimple/Cloudflare promos arrive "via
  Dev Admin / Owners" <dev.admin@chapterone.org> → blanket-protection makes
  them TODO forever. Calibration option (Adam's call, not yet applied):
  subject-route know-promo subjects to Jev instead of blanket protection.
- Asana story enrichment (if calibration demands it): `references/asana-story-matching.md`.
- The ticket's original filter-first design and its Phase-1 v0 prompt (story
  archaeology, business-day math, Sweep/Plan aging) are SUPERSEDED — do not resurrect.
- Hardcoding a label ID before creating the label = 400s (Swept was initially written
  as Label_91 before the label existed; real ID Label_10). Always create-then-read ID.
- Report-run signals aren't retro-labeled once state marks them done — they sit in the
  inbox (which IS the mechanism); don't write cosmetic label backfills.
- Asana story.resource_subtype is NOT returned by the notifications API — story.text only.
- Idempotency: the state file's `known` map (thread_id -> cls/from/subject/ts/note)
  skips re-processing already-classified threads; Swept threads won't reappear in inbox
  listings (already archived) — state + inbox query double as the dedupe gate.
- **Summary-email send is self-addressed via the one authorized exception to
  organize-only (Adam, 2026-10-28):** nothing else may ever send from work email.
  If the script's send call fails on quota it retries 3x with 65s waits — keep that
  contract when editing.