# Results

Every measured number about Sentinel. The README metrics table, the results report and the resume entry are copied from here and nowhere else.

Rules (rules.md §3): only real measurements; each with date, commit and the command that produced it; unmeasured stays `not measured`; misses are written down as misses.

Targets are the suggestions from `spec.md` §8. Report what you get.

## Engineering

| Metric | Target | Measured | Date | Commit | How (command / setup) | Step |
|---|---|---|---|---|---|---|
| SDK overhead per span | < 5 ms | not measured | | | | 2.8, 8.4 |
| Collector throughput | 500+ spans/s, one small instance | not measured | | | | 8.3 |
| Ingestion reliability (stored ÷ sent under load) | > 99.5% | not measured | | | | 8.3 |
| Integration time (friend, guide only) | < 30 min | not measured | | | | 8.7 |
| Test coverage, SDK | > 70% | not measured | | | | 8.4 |
| Test coverage, collector | > 70% | not measured | | | | 8.4 |

Load test machine (fill in with 8.3): CPU, RAM, where it ran.

## Detection effectiveness

| Metric | Target | Measured | Date | Commit | How | Step |
|---|---|---|---|---|---|---|
| Regression catch rate (broken versions blocked by CI) | ≥ 4 of 5 | not measured | | | | 8.8 |
| CI false alarm rate (neutral changes failed) | < 10% | not measured | | | | 3.5, 8.8 |
| Eval run-to-run noise (baseline ×5) | — | not measured | | | | 3.5 |
| Regression threshold chosen | — | not set | | | | 3.5 |
| Loop detector precision / recall | > 85% each | not measured | | | | 5.2 |
| Step blowout detector precision / recall | > 85% each | not measured | | | | 5.2 |
| Tool error streak detector precision / recall | > 85% each | not measured | | | | 5.2 |
| Time to detect (bad deploy → alert) | < 10 min | not measured | | | | 5.6 |
| Clustering quality (ARI, fresh batch) | > 0.6 | not measured | | | | 6.6 |
| Input drift: topic shift flagged within one window | yes | not measured | | | | 6.2 |
| Input drift: false alarms in 10 no-shift windows | — | not measured | | | | 6.2 |
| Quality drift flagged on bad-prompt traffic | yes | not measured | | | | 6.3 |

## Fault-injection matrix

One row per broken version (`architecture.md` §10). Fill in at 8.8.

| Version | Blocked by CI gate? | Detected in production by | Time to alert | Landed in its own cluster? |
|---|---|---|---|---|
| `a-bad-prompt` | not measured | | | |
| `a-no-retrieval` | not measured | | | |
| `a-wrong-model` | not measured | | | |
| `b-broken-tool` | not measured | | | |
| `b-loop` | not measured | | | |

The one-line version for interviews, once real: "I injected 5 known failure types; Sentinel caught [X] in CI and the rest within [Y] minutes in production."

## Evaluation quality

| Metric | Target | Measured | Date | Commit | How | Step |
|---|---|---|---|---|---|---|
| Human-labeled runs | 50–100 | 0 | | | | 4.4 |
| Judge–human agreement (held-out 40%) | > 80% | not measured | | | | 4.5 |
| Cohen's kappa (held-out) | — | not measured | | | | 4.5 |
| Judge consistency (same input ×3, score variance) | low | not measured | | | | 4.5 |
| Rubric revisions used | ≤ 3 | 0 | | | | 4.5 |
| Cost per 100 online evals | report actual | not measured | | | | 4.5 |

## Spend

| Week | LLM spend (USD) | Notes |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |

## Resume entry

Fill each bracket from the tables above at step 8.8. If a bracket's source is still `not measured`, delete that clause or mark the feature in progress.

> **Sentinel: Production Reliability Platform for LLM Agents** | Python, FastAPI, PostgreSQL, pgvector, OpenTelemetry, Redis, Docker, GitHub Actions
> - Built a framework-agnostic tracing SDK and multi-tenant collector capturing LLM, tool and retrieval spans with under [X] ms overhead, sustaining [N] spans/sec under load
> - Designed an evaluation pipeline combining CI regression gates on golden datasets with sampled LLM-as-judge scoring in production, calibrated to [X]% agreement with human labels
> - Implemented agent failure-mode detection, composite health scoring and SLO alerting; in fault-injection tests, caught [X] of [Y] broken versions before deployment
> - Built embedding-based failure clustering with LLM-generated root-cause summaries (ARI [X]) and input drift detection
> - Packaged as a one-command Docker deployment with a customer integration guide, enabling setup in under [X] minutes
