# Sentinel: Production Reliability Platform for LLM Agents

**Project type:** Individual portfolio project · **Duration:** 8 weeks · **Target roles:** AI Engineer, Forward Deployed Engineer (FDE), ML Platform Engineer

---

## 1. Overview

### Problem statement
Teams are shipping LLM agents to production faster than they can tell whether those agents are working. Traditional monitoring (CPU, uptime, HTTP 500s) misses the failures that actually matter for agents:

- An agent returns a confident but wrong answer, and nothing errors out
- A prompt tweak improves one use case and silently breaks three others
- An agent gets stuck calling the same tool in a loop, burning tokens and money
- Users start asking new kinds of questions the system was never tested on
- Logs pile up, but nobody can tell *why* 15% of runs failed last week

### The pitch
Sentinel is a drop-in reliability layer that any team can integrate into an existing LLM or agent application in under an hour. It:

1. **Traces** every run step by step (LLM calls, tool calls, retrieval, errors)
2. **Evaluates** quality both before deployment (CI regression gates) and in production (sampled scoring)
3. **Monitors health** with agent-specific failure detection, SLOs and a composite health score
4. **Detects drift** in user inputs and output quality over time
5. **Diagnoses** failures by clustering them and summarizing root causes in plain English
6. **Alerts** the team when something degrades

### Goals
- Build a framework-agnostic SDK that works with at least two agent setups
- Catch quality regressions *before* they reach production via CI
- Turn raw failure logs into actionable, human-readable root causes
- Ship it as something a stranger could deploy with one command and a short guide

### Out of scope
- Replacing full commercial observability platforms
- Training or fine-tuning models
- Enterprise auth (SSO, RBAC beyond simple API keys)

---

## 2. Project Relevance

### Why this problem matters right now
Evaluation and observability are among the most discussed open problems in applied AI. Companies building with LLMs consistently report that getting a demo working is easy, but knowing whether it keeps working in production is hard. A project that addresses this shows you understand the gap between prototype and production.

### Relevance to AI Engineer roles
| Skill employers look for | Where Sentinel demonstrates it |
|---|---|
| Building with LLM APIs and agent frameworks | Two demo agents + SDK integrations |
| Evaluation design | Golden datasets, LLM-as-judge, rule-based checks, judge calibration |
| RAG understanding | Groundedness checks on the RAG demo agent |
| Applied ML beyond prompting | Embedding-based drift detection and failure clustering |
| Production thinking | SLOs, cost tracking, versioning, CI gates |

### Relevance to Forward Deployed Engineer roles
| FDE responsibility | Where Sentinel demonstrates it |
|---|---|
| Integrating into unfamiliar customer stacks | Framework-agnostic SDK, OpenTelemetry compatibility |
| Multi-customer deployments | Multi-tenant projects with isolated API keys |
| Diagnosing customer problems fast | Trace viewer + root-cause clustering |
| Writing for technical customers | Integration guide written for an external engineering team |
| Shipping, not just prototyping | Dockerized, deployed, documented |

---

## 3. System Architecture

### High-level flow
```
┌──────────────────────────┐
│  Customer's LLM / Agent  │
│  app + Sentinel SDK      │
└────────────┬─────────────┘
             │ spans (OTel format, batched, async)
             ▼
┌──────────────────────────┐        ┌──────────────────────┐
│  Collector API (FastAPI) │───────▶│  PostgreSQL          │
│  auth, validation,       │        │  projects, runs,     │
│  multi-tenant routing    │        │  spans, evals        │
└────────────┬─────────────┘        └──────────┬───────────┘
             │ enqueue                         │
             ▼                                 │
┌──────────────────────────┐                   │
│  Worker queue (Redis +   │◀──────────────────┘
│  RQ/Celery)              │
│  • online eval sampling  │
│  • health score compute  │
│  • drift detection       │
│  • failure clustering    │
│  • alert evaluation      │
└────────────┬─────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
┌──────────┐   ┌──────────────┐
│Dashboard │   │ Alerts       │
│(Next.js) │   │ Slack/webhook│
└──────────┘   └──────────────┘

Separately:  GitHub Actions ──▶ Offline Eval Runner ──▶ pass/fail on PR
```

### Component breakdown

#### 3.1 Tracing SDK (`sentinel-sdk`)
- Python package installable via pip
- `@sentinel.trace` decorator for any function; context manager for custom spans
- Auto-instrumentation wrappers for the OpenAI and Anthropic Python SDKs
- Integration for one agent framework (LangGraph recommended)
- Captures: inputs, outputs, model name, token counts, latency, cost, tool name and arguments, errors, parent/child relationships
- Batches spans and sends asynchronously so it never slows down the host app
- Configurable PII redaction (regex for emails, phone numbers, etc.) before data leaves the app
- Optional export to any OpenTelemetry backend

#### 3.2 Collector API
- FastAPI service, async endpoints
- API-key authentication per project (multi-tenant)
- Pydantic validation of incoming spans
- Writes raw spans, assembles them into runs, and enqueues background jobs

#### 3.3 Evaluation Engine
- *Offline:* runs a project's golden dataset against the agent, scores results, compares to the baseline, and fails the CI job if quality drops beyond a threshold
- *Online:* samples a configurable percentage of production runs (e.g. 10%) and scores them asynchronously
- Evaluator types:
  - **Rule-based:** valid JSON, schema match for tool arguments, max length, forbidden content, required fields
  - **LLM-as-judge:** rubric-based scoring for correctness, helpfulness, groundedness (for RAG)
  - **Reference-based:** compares against expected answer for golden datasets
- *Judge calibration:* a small human-labeled set (50–100 examples) to measure how often the judge agrees with a human

#### 3.4 Health and Drift Engine
- Agent failure-mode detectors (loops, step blowouts, tool error streaks, abandonment)
- Composite health score per agent version
- SLO tracking with error budgets
- Input drift: compare embedding distributions of this week's inputs vs. a baseline window
- Quality drift: track rolling eval scores and flag statistically significant drops

#### 3.5 Root-Cause Clustering
- Embed failed runs (error message + final output + last tool call)
- Reduce dimensions with UMAP, cluster with HDBSCAN
- For each cluster, send representative samples to an LLM to produce a short label and suggested fix
- Rank clusters by size and recency

#### 3.6 Dashboard
- Overview: health score per agent, SLO status, cost this week
- Trace viewer: step-by-step timeline of any run with inputs and outputs per span
- Version comparison: side-by-side metrics for two agent versions
- Evals page: score trends, judge agreement, CI history
- Failures page: clusters with summaries and example runs
- Drift page: input and quality drift over time

#### 3.7 Alerting
- Rules like "task success < 85% over last 50 runs" or "p95 latency > 10s for 15 minutes"
- Slack and generic webhook delivery, with cooldowns to prevent alert spam

#### 3.8 Demo Agents (the "customers")
- **Agent A, RAG support bot:** answers questions over a product documentation set; tests groundedness
- **Agent B, tool-using research agent:** uses web search, calculator and a mock database tool; tests tool-call reliability and loop behavior
- A traffic simulator script that generates realistic and adversarial queries, including deliberately broken prompt versions, so the dashboard has real data and real failures to show

---

## 4. Technology Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11+ | Standard for AI engineering; all LLM SDKs support it |
| SDK tracing format | OpenTelemetry | Industry standard; shows interoperability with existing tooling |
| API | FastAPI + Pydantic | Async, fast, auto-generated docs, strong validation |
| Database | PostgreSQL (+ pgvector) | Relational data + vector storage for embeddings in one place |
| Analytics (stretch) | ClickHouse or DuckDB | Fast aggregation queries over large span volumes |
| Background jobs | Redis + RQ (or Celery) | Async eval, clustering and drift jobs |
| LLM providers | OpenAI and/or Anthropic APIs | Demo agents and LLM-as-judge |
| Agent framework | LangGraph | Popular for stateful tool-using agents |
| Embeddings | sentence-transformers (local) or provider embeddings | Drift detection and clustering; local keeps cost at zero |
| ML | scikit-learn, UMAP, HDBSCAN, SciPy | Clustering and statistical drift tests |
| Frontend | Next.js + Recharts (or Streamlit for speed) | Professional dashboard; Streamlit if time is short |
| CI/CD | GitHub Actions | Offline eval regression gate on every PR |
| Packaging | Docker + Docker Compose | One-command setup for any "customer" |
| Hosting | Render, Railway or Fly.io; Neon/Supabase for Postgres | Free or cheap tiers suitable for a demo |
| Testing | pytest, httpx, Locust | Unit, integration and load testing |
| Alerts | Slack webhooks | Simple, realistic integration |

> **Tip:** if you're less comfortable with frontend work, use Streamlit and spend the saved time on the evaluation engine, which carries more weight in interviews.

---

## 5. Data Model

```
projects
  id, name, api_key_hash, created_at, settings_json

agents
  id, project_id, name, description

agent_versions
  id, agent_id, version_tag, prompt_hash, model_name, config_json, created_at

runs
  id, project_id, agent_version_id, status (success | failed | abandoned | timeout),
  started_at, ended_at, total_latency_ms, total_tokens, total_cost_usd,
  step_count, input_text, final_output, input_embedding (vector)

spans
  id, run_id, parent_span_id, span_type (llm | tool | retrieval | custom),
  name, started_at, ended_at, latency_ms, input_json, output_json,
  model_name, prompt_tokens, completion_tokens, cost_usd,
  tool_name, tool_args_json, error_type, error_message

eval_datasets
  id, project_id, name, created_at

eval_examples
  id, dataset_id, input, expected_output, tags

eval_results
  id, run_id (nullable), example_id (nullable), evaluator_name,
  evaluator_type (rule | judge | reference), score, passed, reasoning, created_at

human_labels
  id, run_id, label, score, labeled_by, created_at

failure_clusters
  id, project_id, computed_at, label, summary, suggested_fix, size, example_run_ids

drift_reports
  id, project_id, agent_id, window_start, window_end,
  drift_type (input | quality), statistic, p_value, is_drifting

alert_rules
  id, project_id, metric, condition, threshold, window, channel, cooldown_minutes

alerts
  id, rule_id, triggered_at, value, message, resolved_at
```

Index `runs(project_id, started_at)` and `spans(run_id)` since nearly every dashboard query filters on those.

---

## 6. Metrics Tracked by Sentinel

### 6.1 Performance
| Metric | Definition |
|---|---|
| Latency (p50 / p95 / p99) | End-to-end run time; also per span type |
| Time to first token | For streaming responses |
| Tokens per run | Prompt + completion tokens |
| Cost per run / per successful task | USD, using provider pricing table |
| Steps per run | Number of LLM + tool spans |

### 6.2 Reliability
| Metric | Definition |
|---|---|
| Task success rate | Runs with status = success / total runs |
| Tool-call success rate | Tool spans without error / total tool spans, per tool |
| Tool argument validity | Tool calls whose arguments match the tool's schema |
| Error rate by type | Rate limits, timeouts, parsing errors, tool exceptions |
| Retry rate | Repeated identical LLM or tool calls after failure |

### 6.3 Agent-specific failure modes
| Failure mode | Detection logic |
|---|---|
| Loop | Same tool called with near-identical arguments 3+ times in a run |
| Step blowout | Step count exceeds configured limit (e.g. 15) |
| Tool error streak | 3+ consecutive tool errors in a run |
| Abandonment | Run ends without a final output |
| Empty / degenerate output | Output empty, too short, or repeated text |

### 6.4 Quality
| Metric | Definition |
|---|---|
| Correctness score | LLM-as-judge or reference match, 1–5 or pass/fail |
| Groundedness | For RAG: share of claims supported by retrieved context |
| Format compliance | Rule-based checks passed |
| Judge–human agreement | Agreement rate or Cohen's kappa against human labels |

### 6.5 Drift
| Metric | Definition |
|---|---|
| Input drift | Distance between this window's input embeddings and baseline (e.g. centroid cosine distance, MMD, or a classifier two-sample test) |
| Quality drift | Drop in rolling eval score, tested with Mann–Whitney U or a simple threshold |
| New-topic share | Share of inputs far from any baseline cluster |

### 6.6 Composite Health Score (0–100)
A weighted score per agent version over a rolling window, for example:

```
health = 100 × (
    0.35 × task_success_rate
  + 0.25 × normalized_quality_score
  + 0.15 × tool_success_rate
  + 0.15 × latency_slo_compliance
  + 0.10 × (1 − failure_mode_rate)
)
```

- **Green:** 85–100 · **Yellow:** 65–84 · **Red:** below 65
- Make weights configurable per project, and explain in your README why you chose the defaults.

### 6.7 Example SLOs
- p95 latency under 8 seconds
- Task success rate above 90%
- Tool-call success rate above 95%
- Mean quality score at or above 4.0 out of 5
- Error budget tracked as remaining allowed failures in the current 7-day window

---

## 7. Implementation Plan (8 weeks)

Each week ends with something demonstrable. Commit regularly, since a healthy GitHub history is part of the portfolio.

### Week 1: Foundations and demo agents
- Set up the monorepo (`sdk/`, `collector/`, `workers/`, `dashboard/`, `demo_agents/`, `evals/`)
- Build Agent A (RAG support bot) and Agent B (tool-using research agent)
- Write the traffic simulator with normal, edge-case and adversarial inputs
- **Deliverable:** two working agents and a script that generates 100+ runs

### Week 2: Tracing SDK and collector
- Implement the decorator, context manager and span model
- Auto-instrument OpenAI/Anthropic calls; add LangGraph integration
- Async batching and PII redaction
- FastAPI collector with API-key auth and PostgreSQL storage
- **Deliverable:** runs from both agents appear as complete traces in the database

### Week 3: Offline evaluation and CI gate
- Create golden datasets (40–80 examples per agent)
- Build rule-based, reference-based and LLM-as-judge evaluators
- Eval runner CLI that outputs a scorecard and compares to the stored baseline
- GitHub Actions workflow that fails the PR on regression
- **Deliverable:** a PR with a deliberately worse prompt gets blocked by CI

### Week 4: Online evaluation and judge calibration
- Redis queue and workers
- Sample production runs and score them asynchronously
- Hand-label 50–100 runs; compute judge–human agreement; iterate on the judge rubric
- **Deliverable:** quality scores attached to live runs, with a measured agreement number

### Week 5: Health score, failure modes and SLOs
- Implement all failure-mode detectors
- Compute per-version metrics, health score and SLO compliance on a schedule
- Alert rules engine with Slack webhook and cooldowns
- **Deliverable:** introducing a looping bug triggers a red health score and a Slack alert

### Week 6: Drift detection and root-cause clustering
- Store input embeddings; implement windowed input drift and quality drift tests
- Build the clustering pipeline and LLM-generated cluster summaries
- Validate by injecting known failure types and checking they land in separate clusters
- **Deliverable:** a failures report that correctly groups injected failure types

### Week 7: Dashboard
- Overview, trace viewer, version comparison, evals, failures and drift pages
- Focus on the trace viewer and failure clusters first, since they make the best demo
- **Deliverable:** a usable dashboard over real simulated data

### Week 8: Packaging, deployment and documentation
- Dockerfiles + Docker Compose for the full stack
- Deploy a public demo instance with seeded data
- README with architecture diagram, screenshots and a metrics table
- Customer-facing integration guide (5-minute quickstart)
- Load test the collector; record results
- Record a 3–5 minute demo video
- **Deliverable:** a stranger can clone and run it with one command

### Weekly rhythm suggestion
- Weekdays: 1.5–2 hours of building
- Weekend: one longer session for the hardest piece of the week plus a written progress note (these notes become your blog post or README "design decisions" section later)

---

## 8. Project Success Metrics and Evaluation

These are the numbers you'll measure about Sentinel itself and put on your resume. Targets are suggestions; report whatever you actually achieve.

### Engineering metrics
| Metric | How to measure | Suggested target |
|---|---|---|
| SDK overhead | Agent latency with vs. without SDK, averaged over 200 runs | Under 5 ms per span |
| Collector throughput | Locust load test | 500+ spans/second on a single small instance |
| Ingestion reliability | Spans sent vs. stored under load | Above 99.5% |
| Integration time | Time a friend takes to integrate using only your guide | Under 30 minutes |
| Test coverage | pytest-cov on SDK and collector | Above 70% |

### Detection effectiveness (use fault injection)
Create a set of deliberately broken agent versions (bad prompt, broken tool, loop-inducing instruction, wrong model, retrieval disabled) and measure:

| Metric | How to measure | Suggested target |
|---|---|---|
| Regression catch rate | Share of broken versions blocked by CI gate | 4 of 5 or better |
| False alarm rate | CI failures on unchanged/neutral changes | Under 10% |
| Failure-mode detection precision/recall | Compare detector flags to known injected loops/blowouts | Above 85% each |
| Time to detect | Time from deploying a bad version to alert firing | Under 10 minutes |
| Clustering quality | Adjusted Rand Index between clusters and injected failure labels | Above 0.6 |
| Drift detection | Shift simulator traffic to a new topic; check if flagged | Detected within one window |

### Evaluation quality
| Metric | How to measure | Suggested target |
|---|---|---|
| Judge–human agreement | Agreement rate and Cohen's kappa on labeled set | Above 80% agreement |
| Judge consistency | Same input judged 3 times; score variance | Low variance |
| Eval cost | Cost per 100 online evaluations | Report actual figure |

### Fault injection is your secret weapon
Being able to say "I injected 5 known failure types, and Sentinel caught 4 in CI and the 5th within 6 minutes in production" is far more convincing than "I built a dashboard."

---

## 9. Risks, Scope Cuts and Stretch Goals

### Risks and mitigations
| Risk | Mitigation |
|---|---|
| API costs add up | Use cheaper models for agents and judges, cache responses, use local embeddings |
| Running out of time | Follow the cut list below; keep weekly deliverables small |
| Not enough realistic data | Traffic simulator + fault injection generates data on demand |
| LLM judge is unreliable | Calibrate against human labels and report agreement honestly |
| Frontend takes too long | Switch to Streamlit |

### Cut list (cut in this order if behind schedule)
1. ClickHouse/DuckDB analytics layer
2. Next.js dashboard → Streamlit
3. Quality drift (keep input drift)
4. Second framework integration
5. Version comparison page

**Never cut:** tracing SDK, offline eval + CI gate, failure-mode detection, failure clustering, Docker setup, README. These carry the project.

### Stretch goals
- Automatic prompt rollback when health turns red
- A/B traffic splitting between agent versions with statistical significance testing
- Cost-aware model routing suggestions ("80% of these queries succeed on the cheaper model")
- Grafana export via OpenTelemetry
- TypeScript SDK
- Multi-agent tracing (agents calling other agents)

---

## 10. Deliverables, Resume Entry and Interview Prep

### Final deliverables checklist
- [ ] Public GitHub repo with clean structure and commit history
- [ ] README: problem, architecture diagram, screenshots, metrics table, design decisions
- [ ] `sentinel-sdk` installable via pip (from GitHub or PyPI)
- [ ] Docker Compose one-command setup
- [ ] Live demo deployment with seeded data
- [ ] Integration guide for an external engineering team
- [ ] Results report: fault-injection results, load test, judge agreement
- [ ] 3–5 minute demo video
- [ ] Optional: a blog post on LinkedIn or Medium about what you learned evaluating agents

### Resume entry (replace bracketed values with real results)
> **Sentinel: Production Reliability Platform for LLM Agents** | Python, FastAPI, PostgreSQL, pgvector, OpenTelemetry, Redis, Docker, GitHub Actions
> - Built a framework-agnostic tracing SDK and multi-tenant collector capturing LLM, tool and retrieval spans with under [X] ms overhead, sustaining [N] spans/sec under load
> - Designed an evaluation pipeline combining CI regression gates on golden datasets with sampled LLM-as-judge scoring in production, calibrated to [X]% agreement with human labels
> - Implemented agent failure-mode detection, composite health scoring and SLO alerting; in fault-injection tests, caught [X] of [Y] broken versions before deployment
> - Built embedding-based failure clustering with LLM-generated root-cause summaries (ARI [X]) and input drift detection
> - Packaged as a one-command Docker deployment with a customer integration guide, enabling setup in under [X] minutes

### Interview talking points to prepare
1. **"How do you know an LLM judge is trustworthy?"** Calibration set, agreement and kappa, rubric iteration, variance checks.
2. **"Why not just use an existing tool?"** You built it to understand the problem deeply, and you can describe how your design compares and where existing tools would be the better production choice.
3. **"How would this scale to a large customer?"** Sampling, async queues, columnar storage, retention policies, partitioning by project.
4. **"A customer says their agent got worse last week. Walk me through it."** Dashboard → health drop by version → failure clusters → trace viewer → root cause. This is the FDE question, and your project answers it directly.
5. **"What was the hardest bug?"** Keep notes during the build so you have a real story.
6. **"What would you do differently?"** Have an honest answer ready; it signals maturity.

### Honesty note
Only put metrics on your resume that you actually measured. If something is still in progress by the deadline, describe it accurately ("in progress: drift detection"). Interviewers will dig into this project, and real numbers you can explain beat impressive numbers you can't.