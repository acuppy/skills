---
name: inbox-sweep-format
description: Formats the owner's Inbox Sweep summary email with a fixed, Gmail-tested HTML template. The sweeping tool supplies the classified threads as JSON, and scripts/render.py produces the subject, HTML body and plain-text body byte-for-byte deterministically. Use whenever an inbox sweep, inbox triage summary or "Inbox Sweep" email is composed or sent, or when someone asks to change how the sweep email looks. Never hand-write the sweep email's HTML.
---

# Inbox Sweep format

The sweep email has one layout. It was tuned in Gmail web, on mobile and in print.
You decide what goes in each section. `scripts/render.py` decides how it looks.
Never write, edit or "touch up" the HTML yourself, because any change breaks the tested layout.

## Quick start

```bash
SKILL=~/.claude/skills/inbox-sweep-format   # or wherever this folder lives
python3 -I "$SKILL/scripts/render.py" sweep.json --out <tmpdir>
```

Then send one email to the account owner using the three files exactly as written:
- subject: `<tmpdir>/subject.txt` (strip the trailing newline)
- HTML body: `<tmpdir>/body.html`
- plain-text alternative: `<tmpdir>/body.txt`

With the Gmail connector, that is `send_message` with `subject`, `htmlBody` and `body`.
Send both bodies, because a plain-text-only send loses all formatting.

## Workflow

- [ ] **Classify every inbox thread** into exactly one bucket (rules below).
- [ ] **Write `sweep.json`** to match [references/schema.md](references/schema.md). Copy the shape of [examples/sample.json](examples/sample.json).
- [ ] **Render.** If the script exits 2, fix the listed fields and render again. Never work around the validator.
- [ ] **Send** the three files unchanged.

## Classification rules

These rules decide what reaches To do. They matter more than the layout.

1. **Check who holds the ball before you call something a to-do.** Read the last message in the thread.
   - The owner sent the last message → `handled` ("You replied Oct 22; ball is with Alex").
   - Someone else said "no action needed", or named another owner → `handled`, quoting who and what.
   - A broadcast such as release notes or a newsletter → `fyi`.
2. **Group repeats into one to-do.** The same alert for several apps, or the same notice received directly and through a group, becomes one item. Put the members in `detail` and set `received_at` to the list of timestamps, which renders as an age range. Link it with `search`.
3. **Fold related signals in.** If a to-do has Asana mentions or other threads about the same ticket, mention them in `detail` and add a `link` to a search for them. Don't list them twice.
4. **Write titles as actions.** "Grant Priya access to …", "Schedule Redis maintenance: 6 prod add-ons". Don't copy the raw subject line.
5. **Rank `todo` by urgency.** Order: people blocked on the owner, then production risk, then deadlines, then everything else. The renderer numbers the items in the order given.
6. **Watch for bad noise calls.** If a swept thread looks like it needs a person (an approval request, a personal note), move it to `todo` with detail "Was swept as noise; …". Otherwise list it under `swept.possible_misses`.
7. **Swept is counts only.** Give `by_source` totals. Never list swept threads one by one.

## What the renderer guarantees

- It computes all counts (to do, handled, FYI, swept) from the arrays, so the stat row, headers and subject always agree.
- It computes ages from `received_at` against `generated_at`. Don't send pre-formatted ages.
- It builds every Gmail link from `thread_id` or `search`. Don't send URLs.
- It HTML-escapes all text. Send plain text in every field, never markup.
- It keeps short hyphenated words ("add-ons") from splitting across lines, but leaves IDs such as TKT-1042 alone.
- If `todo` is empty, it shows "Nothing needs you right now." It omits the Already handled and FYI sections when they are empty.
- If `errors` > 0, it prints the error count in red in the footer.

## Changing the look

Only the owner can approve a format change. Edit `templates/*.html`, keep every style inline (Gmail drops `<style>` blocks), then re-render the example and compare it in Gmail before sending. Two traps to avoid:
- Draw accents with `border`, not a `background` on an empty cell, because Gmail and print drop those.
- Use only font weights 400, 600 or 700, because Gmail's fallback fonts have no 500.
