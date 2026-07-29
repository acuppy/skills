---
name: session-title
description: >
  Recommend a short list of titles for the current Claude session, derived from
  what the conversation is actually about. Applies a prefix taxonomy (ticket,
  release, review, proposal, debug, skill, exploration) and rejects
  context-free labels like "test review" or "QA plan". Use when the user says
  "/session-title", "title this", "name this session", "rename this chat", or
  wants a summary of the session condensed into a title.
---

# Session Title

Read the current conversation, decide what it is **about**, and offer a short
list of candidate titles. This is an **aside** — it interrupts nothing. No
preamble, no explanation of method, no follow-up questions. Output the list and
stop.

Do not run tools. The one exception: if a ticket ID is likely but not present in
the conversation, `git branch --show-current` may be checked once for it.

## Output shape

```
*Title options:*
1. `<candidate>`
2. `<candidate>`
3. `<candidate>`
```

Three candidates, ordered by confidence. Vary them meaningfully — a different
bucket, altitude, or angle each — not three rewordings of the same phrase. Two
is fine when the session is unambiguous. Never more than four.

Add at most **one** line after the list, only if genuinely needed (e.g. "No
ticket ID found in the branch or conversation — add one if there is one.").

`set_session_title` cannot rename the current session, so never attempt to
apply the choice. The user renames from the app; if they pick one, acknowledge
in a few words and return to whatever was in progress.

## Buckets

Pick the bucket that matches the session's dominant thread.

| Session is about | Shape | Example |
|---|---|---|
| Work on a ticket | `ID-####: <what changed>` | `ID-4102: CSV importer timeout guard` |
| Cutting/deploying a release | `REL-###: <scope or date>` | `REL-064: 03.11 deploy routine` |
| Reviewing someone's code | `Code review: <PR # or subject>` | `Code review: PR #218 rack-attack bump` |
| Writing a proposal/design doc | `Proposal: <subject>` | `Proposal: background-job retry policy` |
| Chasing a defect | `Debug: <symptom>` | `Debug: OAuth redirect loop after SSO` |
| Authoring/editing a skill | `Skill: <skill name or purpose>` | `Skill: session-title recommender` |
| Open-ended thinking, tradeoffs, options | `Explore: <the question>` | `Explore: websocket fan-out cost` |
| None of the above | plain descriptive phrase, no prefix | `Postgres connection pool tuning` |

Rules for the prefix:

- **Never invent an identifier.** Use `ID-####` / `REL-###` / `PR #` only when
  it appears in the conversation, a linked ticket/GitHub URL, the branch name,
  or a commit message. Otherwise drop the prefix and use another bucket.
- **One bucket, not two.** `ID-4102: Code review of importer fix` is a ticket
  title; pick the frame that dominates the session and let the rest go.
- A ticket ID replaces the need for a verb prefix — `ID-4102:` already says
  "work on a ticket."

## The empty-label test

Every candidate must pass: **swap in a different session's content — is the
title still true?** If yes, it carries no information. Strike it.

| Rejected | Why | Instead |
|---|---|---|
| `Test review` | true of a hundred sessions | `Code review: PR #218 rack-attack bump` |
| `QA plan` | names the artifact, not the subject | `ID-4102: CSV importer QA notes` |
| `Bug fix` / `Debugging session` | no symptom, no system | `Debug: OAuth redirect loop after SSO` |
| `Refactor` / `Code cleanup` | no target | `Postgres connection pool tuning` |
| `Investigation` / `Analysis` | no question | `Explore: websocket fan-out cost` |
| `Skill creation` | which skill? | `Skill: session-title recommender` |

The specific noun is the whole value: the subsystem, file, ticket, symptom, or
question. If a candidate has none of those, it is not a title.

## Choosing the subject

- **Weight the dominant thread, not the last message.** A session that spent 40
  turns on a migration and 3 on a typo is about the migration.
- **Name the outcome, not the activity** — `CSV importer timeout guard`, not
  `working on the importer`.
- **Use the codebase's own vocabulary** — the real class, job, or subsystem
  name (`ActiveJob`, `connection pool`, `OAuth callback`) over a generic
  description of it.
- **Mid-session is normal.** Title what has happened so far; do not speculate
  about where the session is heading.
- **Genuinely multi-topic session:** title the dominant thread and let one
  candidate cover the second, rather than fusing both with "and".

## Constraints

- **≤ 60 characters**, target 35–55. It gets truncated in the session list.
- Sentence case after the prefix. No trailing period.
- No `session`, `chat`, `Claude`, `conversation`, or date stamps in the title.
- No emoji.
- Nouns over gerunds — `OAuth redirect loop after SSO`, not `Fixing the login`.
