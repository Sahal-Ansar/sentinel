# Implementation steps

57 steps: 4 setup + 53 build, grouped by the 8 weeks in `spec.md` §7. Do them in order. Each step is sized for one 1.5–2 hour session unless tagged.

**Tags**
- `[short]` under an hour; pair it with the next step if you have time
- `[long]` weekend session
- `[you]` needs your hands; an AI cannot do it for you (rules.md §4)

**Budget check.** 8 weeks at 5 weekday sessions + 1 weekend session is about 48 sessions for 57 steps. The `[short]` steps close most of that gap. Weeks 2, 7 and 8 are the tight ones. If a week ends with steps open, use the cut list; do not let the slip roll forward.

**Cut list** (cut in this order when behind)
1. ClickHouse/DuckDB analytics layer (not in these steps at all)
2. Next.js dashboard → Streamlit (replaces 7.2–7.8)
3. Quality drift — step 6.3 (keep input drift)
4. Second framework integration — step 2.5 falls back to manual spans in Agent B
5. Version comparison page — step 7.7

**Never cut:** tracing SDK, offline eval + CI gate, failure-mode detection, failure clustering, Docker setup, README.

**Weekly close** (end of every week, part of the weekend session)
1. Run the week's deliverable end to end and show it working.
2. Update `results.md` with anything measured that week.
3. You write the week's note in `journal.md`: what got built, what was hard, one thing you'd explain differently now. `[you]`
4. Tag the commit `week-N`.
5. If any step from this week is open, decide now: finish next week or cut.

---

## Phase 0 — Setup (before week 1)

### 0.1 Machine setup `[you]`
- Move the project out of OneDrive. Git repos, `.venv` and `node_modules` inside a synced folder cause sync conflicts and slow Docker mounts. Use `~/code/sentinel` inside WSL2 if you already work in WSL with VS Code, otherwise `C:\dev\sentinel`.
- Install: Docker Desktop (WSL2 backend), Git, `uv`, Node LTS.
- Copy `CLAUDE.md` and `plan/` to the new location.
- **Done when:** `docker compose version`, `git --version`, `uv --version` and `node --version` all print a version from the new project folder.

### 0.2 Repo scaffold
- `git init`, folder layout from `architecture.md` §2, `uv` workspace, `.gitignore`, `.gitattributes` (LF endings), `.env.example`, `Makefile`, `ruff` + `pre-commit`.
- Pick the final package name: check PyPI for the working name, record it in `decisions.md` D-004, use it everywhere.
- Public GitHub repo. `ci.yml` running lint + tests on every push.
- Fill in the Commands section of `CLAUDE.md`.
- **Done when:** first push shows a green CI run on GitHub.

### 0.3 Accounts and keys `[you]` `[short]`
- Choose the LLM provider (whichever you have credits for). Create an API key, set a monthly spending cap in the provider console.
- Put the key in `.env` and in GitHub Actions secrets. Check current model list and pricing; set `AGENT_MODEL` and `JUDGE_MODEL` to the cheapest tier that follows instructions reliably.
- Record the choice in `decisions.md` D-008.
- **Done when:** a one-off script makes one successful LLM call using only env vars, and the spending cap is visible in the console.

### 0.4 Compose skeleton `[short]`
- `docker-compose.yml` with `postgres` (pgvector image) and `redis`, healthchecks, named volumes.
- **Done when:** `make up` leaves both services healthy and `CREATE EXTENSION vector` succeeds.

---

## Week 1 — Demo agents and simulator

Goal: two working "customer" agents and a script that generates 100+ runs. No Sentinel code yet.

### 1.1 LLM wrapper `[short]`
- `demo_agents/common/llm.py`: one `complete()` function over the official provider SDK (so auto-instrumentation can hook it in week 2). Model from env. Opt-in SQLite response cache keyed on (model, messages, params). Daily budget counter that refuses calls past `LLM_DAILY_BUDGET_USD`.
- **Done when:** unit tests pass with a stubbed provider; the same call twice with `LLM_CACHE=1` makes one real request.

### 1.2 Fictional product docs
- Invent a small SaaS product. Write 30–40 short markdown docs for it with specific made-up facts: limits, prices, step-by-step procedures, error codes. A fictional product means the model cannot answer from its training data, so retrieval failures show up as wrong answers.
- **Done when:** corpus is committed, and 10 sanity questions are written whose answers exist only in the docs.

### 1.3 Agent A: RAG support bot
- Chunk and embed the corpus into pgvector. Retrieve top-k, answer with source citations, say "I don't know" when the docs don't cover it. Plain provider SDK, no framework. Config from `versions/a-v1.yaml`.
- **Done when:** the CLI answers at least 8 of the 10 sanity questions correctly with citations.

### 1.4 Agent B: tool-using research agent
- LangGraph agent with three tools: `search` (fixed local corpus), `calculator` (safe arithmetic, no `eval`), `db_query` (mock SQLite with fictional customers and orders). Step limit. Config from `versions/b-v1.yaml`.
- **Done when:** it completes at least 8 of 10 multi-step sanity tasks (each needing 2+ tool calls).

### 1.5 Broken versions `[short]`
- Add the five broken version files from `architecture.md` §10, driven by switches in the version YAML (no code forks).
- **Done when:** each broken version runs and visibly misbehaves in the way its name says.

### 1.6 Traffic simulator `[long]`
- Query bank per agent with categories: normal, edge case, adversarial, and a held-back "new topic" set for drift testing later.
- `simulate.py --agent --version --n --mix --concurrency --seed`. Tags each run with ground-truth metadata (`fault_label`, `query_category`). Writes a JSONL log for now.
- **Done when:** one command produces 100+ runs across both agents with a readable summary. **Week 1 deliverable.** Then run the weekly close.

---

## Week 2 — Tracing SDK and collector

Goal: runs from both agents appear as complete traces in the database. Heaviest week; 2.5 is the first thing to shrink if it overruns.

### 2.1 Span contract `[short]`
- Turn `architecture.md` §5 into Pydantic models in `collector/` and a JSON Schema file. Write `docs/span-schema.md` with one full example.
- **Done when:** the example validates; three deliberately malformed examples are rejected with clear errors.

### 2.2 SDK core
- `init()`, `@trace` for sync and async functions, `span()` context manager, span types, input/output capture with truncation, error capture. Built on the OpenTelemetry SDK. Console exporter for now.
- **Done when:** tests show correct parent/child nesting for sync, async and nested-decorator cases, and that nothing runs before `init()`.

### 2.3 Exporter and batching
- Custom exporter: serialize to the wire format, POST batches in a background thread, retry with backoff, bounded queue that drops oldest and counts drops, `flush()` and flush at exit.
- **Done when:** with the collector down, the host function still returns normally and nothing raises; against a fake server, every span of 1,000 arrives exactly once.

### 2.4 Auto-instrumentation: OpenAI and Anthropic
- `instrument_openai()` and `instrument_anthropic()` covering sync, async and streaming calls. Capture model, token counts, latency, time to first token. Cost from `pricing.yaml` (prices looked up today, dated in the file).
- **Done when:** an LLM call with zero manual span code produces an `llm` span with tokens and cost; a streaming call records TTFT.

### 2.5 LangGraph integration
- A LangChain callback handler that emits `llm`, `tool` (name + arguments) and node spans. Read the current LangGraph/LangChain callback docs first.
- **Done when:** one Agent B run produces a full span tree with no manual span code beyond `init()` and passing the handler.

### 2.6 PII redaction `[short]`
- Regex redactors for emails, phone numbers and card-like numbers, plus custom patterns. Applied before export. On by default.
- **Done when:** a test proves a raw email and phone number in inputs never appear in the exported payload.

### 2.7 Collector `[long]`
- SQLAlchemy models and the first Alembic migration for every table in `spec.md` §5 plus the changes in `architecture.md` §9.
- `POST /v1/spans`: API-key auth, validation, insert spans, run lifecycle from `architecture.md` §7, upsert agents and versions.
- CLI: create project, create key (shown once, stored hashed).
- **Done when:** integration tests pass for happy path, out-of-order spans, wrong key → 401, and project A cannot read project B's runs.

### 2.8 Wire it together
- Add the SDK to both agents. Point the simulator at the collector. Add collector to compose.
- First SDK overhead measurement: stubbed LLM with a fixed delay, 200 runs with and without the SDK, overhead per span. Record in `results.md`.
- **Done when:** after `make simulate`, a SQL query shows complete runs with correct span trees for both agents. **Week 2 deliverable.** Weekly close.

---

## Week 3 — Offline evaluation and CI gate

Goal: a PR with a deliberately worse prompt gets blocked by CI.

### 3.1 Golden datasets `[you]` `[long]`
- 40–80 examples per agent in `evals/datasets/*.jsonl`: input, expected output, tags; for Agent A also the doc that contains the answer. Cover normal, edge and "should refuse" cases.
- An AI may draft candidates. You read and fix every single one; a wrong expected answer poisons every number downstream.
- **Done when:** both files are committed and you have noted in `completed.md` that you reviewed every example.

### 3.2 Rule-based and reference evaluators
- One `Evaluator` interface returning score, passed, reasoning.
- Rule-based: valid JSON, tool-argument schema match, max length, forbidden content, required fields, citation present.
- Reference-based: normalized exact match for numeric answers (Agent B), semantic match for free text.
- **Done when:** unit tests cover a pass and a fail case for every evaluator.

### 3.3 LLM-as-judge
- Rubrics for correctness, helpfulness and groundedness (share of claims supported by the retrieved context). Structured output with reasoning before the score. Temperature 0. Cached.
- **Done when:** on 10 hand-picked cases (5 clearly good, 5 clearly bad) the judge separates them; the rubric text is in the repo.

### 3.4 Eval runner CLI
- `sentinel-eval run` (agent + version + dataset → scorecard as JSON and markdown, rows in `eval_results`), `compare` (against stored baseline), `baseline update`.
- **Done when:** scorecards exist for `a-v1` and `b-v1` and are committed as baselines.

### 3.5 Noise and threshold `[short]`
- Run the unchanged baseline 5 times. The spread between runs is the noise. Set the regression threshold above it and write the reasoning in `decisions.md`.
- **Done when:** the noise figure and chosen threshold are in `results.md`.

### 3.6 CI gate
- `eval-gate.yml`: on PRs touching agent code or version files, restore the response cache, run evals, post the scorecard as a PR comment, fail on regression. Budget cap in the workflow.
- Test with two PRs: one that swaps in the bad prompt, one neutral change.
- **Done when:** the bad-prompt PR is blocked and the neutral PR passes. Screenshot both. **Week 3 deliverable.** Weekly close.

---

## Week 4 — Online evaluation and judge calibration

Goal: quality scores attached to live runs, with a measured judge–human agreement number.

### 4.1 Workers `[short]`
- `worker` and `ticker` services in compose. Collector enqueues `on_run_complete`. Check whether the current RQ release has built-in periodic scheduling before writing the ticker.
- **Done when:** finishing a run logs a job executed by the worker within seconds.

### 4.2 Online eval sampling
- Per-project sample rate. Sampling decided by a hash of the run ID so it is repeatable. Runs the judge and rule evaluators, writes `eval_results` with the run ID. Daily cost cap.
- **Done when:** after 500 simulated runs, about 10% have scores and the cap demonstrably stops further calls when set low.

### 4.3 Labeling tool
- A minimal page or CLI: shows a run's input, output and retrieved context; you enter a 1–5 score and pass/fail. Judge score hidden so it cannot influence you. Writes `human_labels`.
- **Done when:** you can label one run in under 30 seconds.

### 4.4 Hand-label 50–100 runs `[you]` `[long]`
- Stratified sample: include runs from the broken versions, otherwise everything is a 5 and agreement means nothing.
- **Done when:** at least 50 labels exist, with at least 10 labeled fail.

### 4.5 Agreement and rubric iteration
- Split the labels: tune on 60%, report on the held-out 40%.
- Compute agreement rate, Cohen's kappa and a confusion matrix. Judge consistency: same input 3 times, score variance. Cost per 100 online evals.
- At most 3 rubric revisions. Write `docs/learn/cohens-kappa.md`.
- **Done when:** held-out agreement, kappa, consistency and cost are in `results.md`. **Week 4 deliverable.** Weekly close.

---

## Week 5 — Health score, failure modes, SLOs, alerts

Goal: introducing a looping bug triggers a red health score and a Slack alert.

### 5.1 Failure-mode detectors
- Pure functions over a run's spans: loop (same tool, near-identical arguments, 3+ times; define "near-identical" precisely), step blowout, tool error streak, abandonment, empty/degenerate output. Results in `run_flags`. Run on every completed run.
- **Done when:** unit tests with hand-built span fixtures cover a positive and a negative case for each detector.

### 5.2 Detector validation `[short]`
- Simulate runs with known injected loops and blowouts (ground truth in run metadata). Compare flags to truth: precision and recall per detector. Write `docs/learn/precision-recall.md`.
- **Done when:** precision and recall per detector are in `results.md`.

### 5.3 Metrics aggregation
- `compute_metrics` job: per agent version over the rolling window, everything in `spec.md` §6.1–6.4 → `metric_snapshots`. Write `docs/learn/percentiles.md`.
- **Done when:** snapshots for both agents match numbers recomputed by hand in SQL for one window.

### 5.4 Health score and SLOs
- Health score per `architecture.md` §11, weights configurable per project. SLO compliance and 7-day error budget. A paragraph for the README on why the default weights are what they are.
- **Done when:** tests cover missing-component rescaling and the under-20-runs case; `a-v1` scores green and `b-loop` scores red on simulated traffic.

### 5.5 Alert rules engine
- Rules (metric, condition, threshold, window, channel, cooldown) evaluated after each metrics tick. Slack and generic webhook delivery. Cooldowns. Auto-resolve when the metric recovers.
- **Done when:** tests prove a rule fires once, stays quiet during cooldown, and resolves.

### 5.6 Loop-bug demo `[you]` `[short]`
- Create a Slack incoming webhook. Switch simulator traffic from `b-v1` to `b-loop` and time it.
- **Done when:** health goes red and a Slack alert arrives; time from switch to alert is in `results.md`. **Week 5 deliverable.** Weekly close.

---

## Week 6 — Drift detection and root-cause clustering

Goal: a failures report that correctly groups injected failure types.

### 6.1 Input embeddings `[short]`
- `embed()` in `workers/embed.py`. `embed_run_input` job on every completed run. Backfill existing runs.
- **Done when:** every completed run has an embedding and a nearest-neighbour query returns sensibly similar inputs.

### 6.2 Input drift
- Baseline window vs current window: centroid cosine distance, permutation test for the p-value, new-topic share. Writes `drift_reports`. Write `docs/learn/drift-and-permutation-tests.md`.
- Validate both ways: 10 no-shift windows (count false alarms), then switch the simulator to the held-back new-topic queries.
- **Done when:** the topic shift is flagged within one window, and the false-alarm count out of 10 is in `results.md`.

### 6.3 Quality drift (first cut-list candidate among the steps)
- Rolling eval score, baseline vs current with Mann–Whitney U plus a minimum effect size. Write `docs/learn/mann-whitney.md`.
- **Done when:** switching traffic to `a-bad-prompt` is flagged; staying on `a-v1` is not.

### 6.4 Clustering pipeline
- Failed and low-quality runs → text (error message + final output + last tool call) → embed → UMAP → HDBSCAN → `failure_clusters`. Fixed seed. Skip gracefully when there are too few failures. Handle noise points. Write `docs/learn/umap-hdbscan.md`.
- **Done when:** the job runs on simulated failures and produces stable clusters across two runs with the same seed.

### 6.5 Cluster summaries
- Pick the most representative runs per cluster, send them to the LLM, get back a short label, plain-English summary and suggested fix as JSON. Rank clusters by size and recency.
- **Done when:** each cluster has a label a stranger would understand, and you agree with at least most of them on a read-through. `[you]` for the read-through.

### 6.6 Clustering validation `[long]`
- Simulate failures from all five broken versions with ground-truth labels in metadata. Tune `min_cluster_size` on one batch, then generate a fresh batch and compute Adjusted Rand Index on that. Write `docs/learn/adjusted-rand-index.md`.
- **Done when:** ARI on the fresh batch is in `results.md` and a markdown failures report is generated. **Week 6 deliverable.** Weekly close.

---

## Week 7 — Dashboard

Goal: a usable dashboard over real simulated data. Trace viewer and failure clusters first; they make the demo.

### 7.1 Read API
- Every endpoint in `architecture.md` §6, read-key auth, pagination, project scoping.
- **Done when:** tests pass for each endpoint, including a cross-project leak test per endpoint.

### 7.2 Dashboard scaffold `[short]`
- Next.js app, Tailwind, layout and navigation, typed API client, design tokens (type scale, spacing, status colors for green/yellow/red). Dashboard service in compose.
- **Done when:** the shell renders at `localhost:3000` with a live call to `/api/v1/overview`.

### 7.3 Trace viewer `[long]`
- Run list with filters (agent, version, status, flag, time). Run detail: waterfall timeline, span tree, per-span input/output, errors highlighted, tokens and cost per span, flags shown on the run.
- **Done when:** you can open a `b-loop` run and see the repeated tool calls at a glance.

### 7.4 Failures page
- Cluster cards: label, summary, suggested fix, size, trend. Click through to example runs in the trace viewer.
- **Done when:** from a cluster you reach a concrete failing trace in two clicks.

### 7.5 Overview page
- Health score per agent version with color status, SLO status with remaining error budget, cost this week, active alerts.
- **Done when:** the page reflects a simulated incident within a minute of it happening.

### 7.6 Evals and drift pages
- Evals: score trends, judge–human agreement, CI history. Drift: input and quality drift over time with flagged windows marked.
- **Done when:** both pages show real data from weeks 3–6.

### 7.7 Version comparison `[short]` (cut-list item 5)
- Two versions side by side: every metric with the difference highlighted.
- **Done when:** `a-v1` vs `a-bad-prompt` shows the quality drop clearly.

### 7.8 Polish
- Loading, empty and error states everywhere. Walk the interview story end to end: overview → health drop by version → failure cluster → trace → root cause. Fix whatever breaks the flow.
- **Done when:** that walkthrough works without touching the URL bar, and README screenshots are captured. **Week 7 deliverable.** Weekly close.

---

## Week 8 — Packaging, deployment, documentation

Goal: a stranger can clone and run it with one command.

### 8.1 Full Docker Compose
- Dockerfiles for collector, worker, ticker and dashboard. Migrations run on startup.
- **Done when:** a fresh clone in a new folder comes up fully with one command and no manual steps beyond copying `.env.example`.

### 8.2 Seed data
- Record span batches from a real simulated session (baseline traffic plus all five faults). Replay script that shifts timestamps across the past 7–14 days and posts to the collector. Costs nothing to re-run.
- **Done when:** a freshly seeded instance shows history, at least one incident, clusters and a drift flag.

### 8.3 Load test
- Locust against `POST /v1/spans`. Measure spans/second, p95 ingest latency and sent-vs-stored. Record the machine specs with the numbers.
- **Done when:** throughput and ingestion reliability are in `results.md`.

### 8.4 SDK packaging `[short]`
- Package metadata, README for the SDK, `pip install` from GitHub in a clean virtualenv. PyPI only if the name is free and you want it.
- Final SDK overhead measurement and test coverage.
- **Done when:** a clean venv installs the SDK and traces a 10-line script; overhead and coverage are in `results.md`.

### 8.5 Public demo deployment `[you]` `[long]`
- Compare current free/cheap tiers for a small VM or PaaS plus managed Postgres. Record the choice in `decisions.md` D-018. Deploy with seeded data, read-only key, ingestion disabled or rate-limited.
- **Done when:** the demo URL loads from a phone on mobile data.

### 8.6 README
- Problem, architecture diagram, screenshots, quickstart, metrics table copied from `results.md` (measured numbers only), design decisions drawn from `decisions.md` and `journal.md`, honest "what's not done" section.
- **Done when:** someone who has never seen the project can say what it does after 60 seconds on the README. Ask one person. `[you]`

### 8.7 Integration guide and friend test `[you]`
- `docs/integration-guide.md`: 5-minute quickstart written for an external engineering team.
- Have a friend integrate the SDK into a small script using only the guide. Time it. Fix what tripped them, note what you changed.
- **Done when:** the measured integration time is in `results.md`.

### 8.8 Final results, video, resume `[you]` `[long]`
- Final fault-injection run: all five broken versions through the CI gate, then the misses through production detection. Fill the matrix in `results.md`.
- `docs/results-report.md`: fault injection, load test, judge agreement.
- Record the 3–5 minute demo video following the 7.8 walkthrough.
- Fill the resume entry in `results.md` with real numbers.
- **Done when:** every box in `spec.md` §10's deliverables checklist is ticked or explicitly marked not done. **Week 8 deliverable.** Final weekly close.

---

## After week 8

Stretch goals from `spec.md` §9, only once everything above is done. Best value for the target roles, in order: A/B traffic splitting with significance testing, multi-agent tracing, automatic prompt rollback on red health.
