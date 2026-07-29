---
name: be-critical
description: Deliver a direct, unsugarcoated critique of the approach, plan, or design currently under discussion — challenge assumptions, surface downstream risks, and offer concrete alternatives. Use when the user says "be critical", "/be-critical", "poke holes in this", "tear this apart", "what's wrong with this plan", or wants an honest adversarial review of an approach before committing to it.
---

# Be Critical

Review the approach/plan currently under discussion in this conversation and deliver a direct, critical assessment. No sugar coating, no compliment sandwich, no hedging.

## What to review

The most recent approach, plan, design, or decision being discussed — whether proposed by the user or by Claude. If multiple candidates exist and it's ambiguous which one, ask one clarifying question first; otherwise proceed.

## Output structure (in this order)

1. **Critical review** — 2–4 sentences. Lead with the single biggest problem. State your verdict plainly (e.g. "This is the wrong layer for this logic" not "there might be some concerns").

2. **Challenged assumptions** — Bullet list of the load-bearing assumptions the approach rests on, and why each is questionable or unverified. Skip assumptions that are actually sound.

3. **Downstream risks if you proceed anyway** — Short summary of second/third-order consequences of moving forward against this advice: maintenance cost, schema/API lock-in, naming debt, testing burden, migration pain. Be specific to this approach, not generic.

4. **Alternatives** — 3–5 direct alternatives, one line each: what it is and the key tradeoff. Rank them; mark your recommendation.

## Rules

- **Brief and direct.** The whole response should fit on one screen. Complete sentences, but no throat-clearing or preamble.
- **Do not compliment a poor approach.** No "great start, but…" softeners. If it's weak, say it's weak and why.
- **Critical ≠ contrarian.** If the approach is genuinely sound, say so plainly and name the residual risks — don't invent objections to seem tough.
- **Name the principle being violated** where one applies (SRP, coupling, functional core / imperative shell, canonical Rails patterns) rather than saying "this is messy."
- **Ground claims in the actual code/context** when available — cite the file or constraint that makes the objection real, not hypothetical.
- **This is an assessment, not a fix.** Deliver the critique and stop; don't start implementing an alternative unless asked.
