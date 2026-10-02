# Jev (TypeSafe AI "System One" model) — evaluation plan

*2026-10-02. Source: https://typesafe.ai/blog/introducing-system-one-models-and-jev (early access). Status: candidate instrument, to be evaluated behind the firm's A/B discipline; not a dependency.*

## What it is
A model that takes unstructured state and returns **typed, calibrated probabilistic decisions** (choice among up to 255 options with honest probabilities) in 70–500 ms, at ~$0.042 per million input tokens. Trained with "Reinforcement Learning for Calibrated Decisions"; outputs are type-safe by construction (no free text, so no malformed output). Early access; one founder (ex-OpenAI); benchmarks are the vendor's own.

## Where it could fit (all are "smart if-statements" the firm already needs)
| Seat | Today | With Jev | Why it fits |
|---|---|---|---|
| Agent Watch judgment conditions | Sonnet session per stock reading digests (the largest cost line) | Per-minute or per-tick typed decision "is judgment condition J met? p=…" | Latency and cost are the constraint; calibrated p feeds our scoring directly |
| Watch-event triage | Rule Watch invokes a Sonnet session on every event | Jev classifies `escalate / act / ignore` first; the Execution Agent session runs only when needed | Cuts invocations; fail-open to the current path |
| Catalyst tagging | Haiku batch | Jev enum + calibrated strength/novelty | Cheaper, faster, probability we can calibrate |
| Scanner prioritisation | Sonnet scoring | Jev ranking among ≤255 candidates | High-cardinality choice is its stated use |
| Process-adherence judge (Coach) | LLM-judge pass | Jev typed rubric scores | Cheap, consistent |

## Where it does not fit
Writing strategy books, theses, recalibration rationale, reviews, committee decisions — anything that must carry reasoning the dossier records (constitution I.1 requires reasoning with each decision; Jev returns probabilities, not explanations). Jev is an instrument an agent cites, never the decider of record. It also cannot sit inside the execution service (constitution VI.1: no model calls on the execution path); it belongs on the agent/watch side as a judgment instrument with fail-open semantics.

## Risks
Early access and single-vendor dependency for an always-on firm; self-reported benchmarks; "can't hallucinate" means type-safe, not correct; calibration under market distribution shift is unproven; API locality and data handling for Indian market text unknown; terms of use to be read by the Broker/Regulatory Compliance Officers (data sent to a third party is announcements and features, never credentials or positions).

## Evaluation plan (Research Lab + Skill Engineer, Phase 2)
1. Join early access; read terms; confirm no order or account data leaves the firm.
2. Build `instruments:jev_decide(schema, state)` behind a feature flag with fail-open to the current path, logging latency, cost and `known_at`.
3. Shadow arm first: Jev runs beside Sonnet on judgment conditions and event triage for ≥ 300 decisions; score calibration (reliability), agreement, latency, cost.
4. Promote per seat only if calibration is at least as good as the incumbent and cost per decision is lower; record the decision in the investment committee minutes; keep the incumbent as fallback.
