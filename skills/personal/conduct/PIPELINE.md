# Agent prompt templates

Agents get the plan-file path, never plan contents pasted inline — the agent
reads it once from disk.

## Opus reviewer (standard tier)

One reviewer, after you've implemented and mechanical checks pass. Its value
is independence — it hasn't watched you rationalize your choices.

```
Agent(
  model: "opus",
  description: "Review implementation against plan",
  prompt: "Read the plan at <plan-path>. The conductor has implemented all
    work items; mechanical checks (tests/lint) already pass — do not re-run
    them. Review `git diff` and the changed files against:
    1. PLAN CONFORMANCE — each done-criterion actually met; no unplanned
       changes (scope drift); constraints respected.
    2. QUALITY BAR (from the plan) — name violations by principle:
       'SRP violation: <class> does X and Y', 'Metz: <method> is N lines /
       logic in initialize', 'side effect in functional core: <where>'.
       Not vague 'this is messy'.
    Return ONLY one of:
    - 'PASS' + one line per work item confirming what you checked
    - 'FAIL' + numbered findings: file:line, principle or criterion violated,
      what the code does vs what it should, suggested fix. Max 250 words.
    Your final message is data for an orchestrator, not prose for a human."
)
```

On FAIL: fix the findings yourself (you're the implementer), re-run
mechanical checks, request one re-review. A second FAIL means the plan and
the code disagree at a level worth the user's judgment — escalate with the
findings and your own read.

## Opus decomposition scout (before planning, either tier)

Use only when the design is genuinely cross-domain or multi-layer and you
cannot confidently decompose it yourself.

```
Agent(
  model: "opus",
  description: "Decompose cross-domain task",
  prompt: "Explore this codebase and write a decomposition for the task
    below to <scratchpad>/conduct-decomposition.md.
    Task: <user's prompt, restated>
    The file must contain:
    1. Work items — numbered, each independently implementable, with files
       to touch, exact change, done-criteria, and a runnable check command
    2. Dependency ordering between items
    3. Design decisions the conductor must make, with your recommendation
       and the tradeoff
    Be as thorough as the design requires — this file becomes part of the
    execution contract. Return ONLY the file path and a 3-line summary."
)
```

Review the decomposition file critically before adopting it — you are the
conductor, not a rubber stamp. Spot-check its claims about the code (a claim
that names a file or method is cheap to verify). Fold what survives into
your plan.

## Sonnet repair (large tier only)

Standard-tier repairs are yours. In a Workflow, repair goes to sonnet:

```
"Read the plan at <plan-path>. Fix ONLY these findings for work item <N>:
 <numbered findings>. Change nothing else. Run the item's mechanical check
 before reporting."
```
