# Workflow script — large tier

Use only when the plan has roughly 5+ *independent*, mechanically executable
work items. Parallelism is the entire justification for this tier — if items
are serial, you're on the standard tier no matter how many there are.
Because this skill directs the Workflow call, the user has opted in.

## Shape

```
fable plan (you)
  → Produce: sonnet agents fan out, one per item   (parallel barrier)
  → Verify: opus agents, mechanical checks first   (per item, parallel)
  → Repair: sonnet fix + opus re-verify, once      (failed items only)
  → single JSON report → fable final review (you)
```

**The barrier between Produce and Verify is load-bearing.** Producers share
one working tree; a verifier running `git diff` while another producer is
mid-mutation sees half-finished changes and reports false scope-drift
findings. Wait for all producers, then verify in parallel — verifiers only
read, so they can't race each other. If items touch overlapping files,
producers also need `isolation: 'worktree'`; prefer re-planning items to be
disjoint instead (worktrees cost setup time and complicate verification).

## Template

Pass `{ planPath, items }` as args. Keep the schemas — structured output is
what keeps agent chatter out of your context, and `blocked` is the escape
hatch that keeps a stuck producer from hallucinating a report.

```js
export const meta = {
  name: 'conduct-execute',
  description: 'Execute plan work items via sonnet producers + opus verifiers',
  phases: [
    { title: 'Produce', detail: 'sonnet agents, one per work item', model: 'sonnet' },
    { title: 'Verify', detail: 'opus agents check code against plan', model: 'opus' },
    { title: 'Repair', detail: 'one fix cycle for failed items' },
  ],
}

const PLAN = args.planPath
const ITEMS = args.items              // [{ id, summary, files, check }]

const PRODUCE_SCHEMA = {
  type: 'object',
  properties: {
    blocked: { type: 'boolean', description: 'true if the plan is wrong or impossible for this item' },
    blockedReason: { type: 'string' },
    filesChanged: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
    deviations: { type: 'string' },
    checkPassed: { type: 'boolean', description: 'result of the item\'s mechanical check command' },
  },
  required: ['blocked', 'filesChanged', 'summary', 'checkPassed'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    findings: { type: 'array', items: { type: 'string' } },
  },
  required: ['pass', 'findings'],
}

const produce = (item) => agent(
  `Read the plan at ${PLAN}. Implement work item ${item.id} (${item.summary})
   exactly as specified, meeting the plan's Quality bar. Run the item's
   mechanical check command and report the result as checkPassed. If the plan
   is wrong or impossible for this item, set blocked=true with the reason and
   change nothing.`,
  { label: `produce:${item.id}`, phase: 'Produce', model: 'sonnet', schema: PRODUCE_SCHEMA }
)

const verify = (item, report) => agent(
  `Read the plan at ${PLAN}. Verify work item ${item.id}. Producer reports:
   ${JSON.stringify(report)}.
   FIRST re-run the item's mechanical check command — if it fails, that is
   finding #1 and you may stop there.
   THEN read the changed files (expect changes ONLY in: ${item.files.join(', ')};
   anything else in git diff belongs to other work items — ignore it, but any
   change to this item's files beyond the plan is scope drift).
   Check done-criteria and the plan's Quality bar (name SRP/Metz violations by
   principle). findings: file:line + what the plan requires vs what the code does.`,
  { label: `verify:${item.id}`, phase: 'Verify', model: 'opus', schema: VERDICT_SCHEMA }
)

phase('Produce')
const reports = await parallel(ITEMS.map(item => () => produce(item)))  // BARRIER — see above

phase('Verify')
const results = await parallel(ITEMS.map((item, i) => async () => {
  const report = reports[i]
  if (!report) return { item: item.id, status: 'producer-failed' }
  if (report.blocked) return { item: item.id, status: 'blocked', reason: report.blockedReason }
  let verdict = await verify(item, report)
  if (!verdict.pass) {                      // one repair cycle
    const fix = await agent(
      `Read the plan at ${PLAN}. Fix ONLY these findings for work item ${item.id}:
       ${verdict.findings.join('; ')}. Change nothing else. Run the item's
       mechanical check before reporting.`,
      { label: `repair:${item.id}`, phase: 'Repair', model: 'sonnet', schema: PRODUCE_SCHEMA }
    )
    verdict = fix && !fix.blocked ? await verify(item, fix) : verdict
  }
  return { item: item.id, status: verdict.pass ? 'pass' : 'fail',
           files: report.filesChanged, findings: verdict.findings }
}))

return { results: results.filter(Boolean) }
```

Repair note: repairs and re-verifies for different items run concurrently
after the barrier. This is safe only because items are disjoint by
construction — which is why "independent items" is the tier's entry
criterion, not a nice-to-have.

## Final review (you, fable)

One JSON report comes back. `pass` items: trust them. `blocked` items: the
plan was wrong — that's your error to fix, and it may invalidate other
items' assumptions; re-check before shipping. `fail` / `producer-failed`
items: read the findings, skim only the flagged code, then either fix it
yourself (it's now a trivial-tier task) or surface it to the user. Run the
full test suite once at the end — per-item checks don't catch cross-item
integration breaks. Then summarize the run: items passed/failed/blocked,
files changed, anything needing the user's judgment.
