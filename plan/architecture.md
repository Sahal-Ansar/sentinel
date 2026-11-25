# Architecture and locked decisions

`spec.md` says what Sentinel is. This file says how it gets built. Anything here is locked; changing it needs an entry in `decisions.md` first. Reasons for each choice are in `decisions.md` under the ID shown.

## 1. Locked decisions

| Area | Decision | ID |
|---|---|---|
| Python | 3.12, `uv` workspace for the monorepo, `ruff`, `pytest` | D-001 |
| Where things run | Everything in Docker Compose; repo outside OneDrive | D-002 |
| SDK internals | Built on the OpenTelemetry Python SDK (TracerProvider + BatchSpanProcessor) with a custom exporter that POSTs JSON to the collector | D-003 |
| Span attribute names | OpenTelemetry GenAI semantic conventions where they exist, `sentinel.*` for the rest | D-003 |
| Package name | `sentinel-obs` / import `sentinel_obs` | D-004 |
| Two agent setups | Agent A = plain provider SDK, no framework. Agent B = LangGraph. | D-005 |
| Agent A corpus | Docs for a fictional product, written for this project | D-006 |
| Agent B tools | `search` over a fixed local corpus, `calculator`, `db_query` on a mock SQLite DB. No live web search by default. | D-007 |
| LLM provider | Local Ollama (`anthropic` SDK against its Anthropic-compatible endpoint) until Claude API credits exist, then Claude; one provider at a time for agents + judge, behind a thin wrapper; provider and models set only by env var | D-008 |
| Queue | Redis + RQ, plus a small `ticker` process for periodic jobs | D-009 |
| Database | PostgreSQL + pgvector, SQLAlchemy 2.0 async, Alembic | D-010 |
| Embeddings | Local small 384-dim model through `fastembed` (ONNX); `sentence-transformers` as fallback. One `embed()` function hides the choice. | D-011 |
| Input drift test | Centroid cosine distance + permutation test for the p-value | D-012 |
| Quality drift test | Mann–Whitney U plus a minimum effect size | D-012 |
| Clustering | UMAP → `sklearn.cluster.HDBSCAN`, fixed seed | D-013 |
| Dashboard | Next.js (App Router) + Tailwind + Recharts. Streamlit is the fallback on the cut list. | D-014 |
| Dashboard auth | Per-project read key. No user accounts. | D-015 |
| CI eval cost | Response cache keyed on (model, prompt, input) restored in CI, so unchanged prompts cost nothing | D-016 |
| Seeding the demo | Record real span batches once, replay them with shifted timestamps | D-017 |
| Hosting | Decided in step 8.5 from the free tiers available that week | D-018 |

## 2. Repo layout

```
sentinel/
├── CLAUDE.md
├── README.md
├── Makefile
├── docker-compose.yml
├── .env.example
├── pyproject.toml              # uv workspace root
├── plan/                       # this folder
├── docs/
│   ├── learn/                  # plain-English explainers (rules.md §5)
│   ├── integration-guide.md    # customer-facing quickstart (8.7)
│   └── results-report.md       # fault injection, load test, judge agreement (8.8)
├── sdk/                        # the pip-installable package
│   └── src/sentinel_obs/
│       ├── __init__.py         # init, trace, span, flush
│       ├── tracer.py
│       ├── exporter.py
│       ├── redaction.py
│       ├── pricing.yaml
│       └── integrations/       # openai.py, anthropic.py, langchain.py
├── collector/
│   ├── app/                    # FastAPI: ingest + read API
│   ├── models/                 # SQLAlchemy models
│   └── migrations/             # Alembic
├── workers/
│   ├── jobs/                   # online_eval, detectors, metrics, drift, clustering, alerts
│   ├── ticker.py
│   └── embed.py
├── evals/
│   ├── datasets/               # golden sets, JSONL
│   ├── evaluators/             # rule, reference, judge
│   ├── baselines/              # stored scorecards the CI gate compares against
│   └── cli.py                  # sentinel-eval
├── demo_agents/
│   ├── common/                 # llm.py wrapper, cache
│   ├── rag_support/            # Agent A
│   ├── research/               # Agent B
│   ├── versions/               # one YAML per agent version, incl. broken ones
│   ├── corpus/                 # fictional product docs
│   └── simulate.py
├── dashboard/                  # Next.js
├── loadtest/                   # Locust
└── .github/workflows/          # ci.yml, eval-gate.yml
```

## 3. Services (docker-compose)

| Service | What | Port |
|---|---|---|
| `postgres` | pgvector image | 5432 |
| `redis` | queue | 6379 |
| `collector` | FastAPI: `/v1/*` ingest, `/api/v1/*` read | 8000 |
| `worker` | RQ worker running all jobs | — |
| `ticker` | enqueues periodic jobs | — |
| `dashboard` | Next.js | 3000 |

The demo agents and simulator are run on demand (`make simulate`), not as long-lived services.

## 4. SDK public surface

```python
import sentinel_obs as sentinel

sentinel.init(
    api_key="sk_sentinel_...",
    endpoint="http://localhost:8000",
    agent="rag-support",
    version="v1",            # version tag
    config={...},            # prompt hash, model, anything worth versioning
)

@sentinel.trace                      # root call = one run
def answer(question: str) -> str: ...

with sentinel.span("rerank", type="custom") as s:
    s.set_output(result)

sentinel.instrument_openai()         # or instrument_anthropic()
handler = sentinel.langchain_handler()   # pass in LangGraph config callbacks
sentinel.flush()
```

Guarantees: never raises into the host, never blocks the host, redaction on by default, bounded memory (queue drops oldest on overflow and counts drops).

## 5. Wire format

`POST /v1/spans` with header `Authorization: Bearer <api key>`. Body is a batch:

```json
{
  "agent": "rag-support",
  "version": "v1",
  "config": {"prompt_hash": "ab12…", "model": "…"},
  "spans": [
    {
      "trace_id": "32 hex chars",
      "span_id": "16 hex chars",
      "parent_span_id": null,
      "name": "answer",
      "span_type": "custom",
      "started_at": "2026-12-01T10:00:00.000Z",
      "ended_at": "2026-12-01T10:00:02.310Z",
      "input": {"question": "…"},
      "output": {"answer": "…"},
      "attributes": {
        "gen_ai.request.model": "…",
        "gen_ai.usage.input_tokens": 812,
        "gen_ai.usage.output_tokens": 96,
        "sentinel.cost_usd": 0.00021,
        "sentinel.tool.name": null,
        "sentinel.tool.args": null,
        "sentinel.ttft_ms": null
      },
      "error": null,
      "metadata": {"fault_label": null, "query_category": "normal"}
    }
  ]
}
```

- One trace = one run. The run ID is the trace ID.
- `span_type` is one of `llm | tool | retrieval | custom`.
- `error` is `null` or `{"type": "...", "message": "..."}`.
- `metadata` on the root span is copied to `runs.metadata_json`. The simulator uses it to carry ground-truth labels for validation. It is never fed to detectors or clustering.
- Inputs and outputs are truncated at a configurable size (default 8 KB per field).

## 6. Collector API

Ingest (API key, write scope):
- `POST /v1/spans`

Read (read key), all scoped to the key's project, all paginated:
- `GET /api/v1/overview`
- `GET /api/v1/agents`, `GET /api/v1/agents/{id}/versions`
- `GET /api/v1/runs` (filters: agent, version, status, flag, time range), `GET /api/v1/runs/{id}` (full span tree)
- `GET /api/v1/versions/compare?a=&b=`
- `GET /api/v1/evals/trends`, `GET /api/v1/evals/agreement`, `GET /api/v1/evals/ci-history`
- `GET /api/v1/failures/clusters`, `GET /api/v1/failures/clusters/{id}`
- `GET /api/v1/drift`
- `GET /api/v1/alerts`, `GET /api/v1/alert-rules`

Admin (CLI only, not HTTP): create project, create/rotate keys, create alert rule.

## 7. Run lifecycle

1. Spans arrive in batches, possibly out of order. Each is validated and inserted.
2. First span of an unseen trace creates the `runs` row with status `running`. Agent and agent version rows are upserted from the batch header.
3. When the root span (no parent) arrives, the run is finalized: status, latency, token/cost totals, step count, input text, final output.
4. Finalizing enqueues `on_run_complete(run_id)`.
5. A sweeper marks runs with no root span after 10 minutes as `timeout`.

Status is about execution, not correctness:
- `success` — root span ended without error and produced a final output
- `failed` — root span ended with an error
- `abandoned` — root span ended with no final output
- `timeout` — swept

A confidently wrong answer is `success` with a low quality score. That distinction is the point of the project; keep it sharp in the UI.

## 8. Background jobs

| Job | Trigger | Writes |
|---|---|---|
| `on_run_complete` | run finalized | fans out to the three below |
| `detect_failure_modes` | every completed run | `run_flags` |
| `embed_run_input` | every completed run | `runs.input_embedding` |
| `online_eval` | sampled runs (deterministic hash of run ID vs project sample rate) | `eval_results` |
| `compute_metrics` | ticker, every 60 s | `metric_snapshots` |
| `evaluate_alerts` | ticker, every 60 s, after metrics | `alerts`, Slack/webhook |
| `sweep_stale_runs` | ticker, every 60 s | `runs.status` |
| `detect_drift` | ticker, once per drift window | `drift_reports` |
| `cluster_failures` | ticker, hourly, and on demand | `failure_clusters` |

Metrics and alerts tick every 60 s so "time to detect under 10 minutes" is reachable. The drift window is configurable (weekly in production, minutes in tests) so "detected within one window" can be tested without waiting a week.

## 9. Data model: changes from spec.md §5

The spec's tables are used as written, plus these additions the spec needs but does not list:

| Change | Why |
|---|---|
| `runs.trace_id` (unique) | Links spans to runs before the root span arrives |
| `runs.metadata_json` | Ground-truth labels from the simulator for validation |
| `spans.attributes_json` | Keeps OTel attributes that have no dedicated column (e.g. TTFT) |
| `projects.read_key_hash` | Separate read-only key for the dashboard and public demo |
| New table `run_flags (id, run_id, flag_type, details_json, created_at)` | The spec has detectors but nowhere to store what they found |
| New table `metric_snapshots (id, project_id, agent_version_id, window_start, window_end, metrics_json, health_score, health_status, computed_at)` | The spec computes metrics on a schedule but has nowhere to store them; the dashboard and alerts read from here |
| `eval_results.agent_version_id`, `eval_results.ci_run_ref` (both nullable) | Needed for the CI history view and per-version eval trends |
| `failure_clusters.run_count_7d` | Ranking by recency |

Indexes: `runs(project_id, started_at)`, `runs(trace_id)`, `spans(run_id)`, `run_flags(run_id)`, `eval_results(run_id)`, `metric_snapshots(agent_version_id, window_end)`.

## 10. Agent versions and fault injection

Each agent version is one YAML file in `demo_agents/versions/` (prompt, model, parameters, fault switches). Changing a version file is what the CI gate watches.

| Version | Agent | What is broken | Expected to be caught by |
|---|---|---|---|
| `a-v1` | A | nothing (baseline) | — |
| `b-v1` | B | nothing (baseline) | — |
| `a-bad-prompt` | A | vague prompt, no grounding instruction | CI gate (correctness, groundedness) |
| `a-no-retrieval` | A | retrieval returns nothing | CI gate (groundedness) |
| `a-wrong-model` | A | misconfigured/weaker model setting | CI gate or online eval |
| `b-broken-tool` | B | `db_query` raises or returns garbage | CI gate, tool error streak detector |
| `b-loop` | B | instruction that causes repeated identical tool calls | Loop + step blowout detectors, health alert |

These five broken versions are the fault-injection set for `results.md`. "Expected to be caught by" is a hypothesis; record what actually happens.

## 11. Health score

Formula and default weights exactly as in `spec.md` §6.6, computed per agent version over a rolling window (default: last 200 runs or 24 h, whichever is smaller).

Details the spec leaves open:
- `normalized_quality_score` = (mean quality − 1) / 4, mapping the 1–5 judge scale to 0–1.
- `latency_slo_compliance` = share of runs in the window under the project's p95 latency target.
- `failure_mode_rate` = share of runs with at least one `run_flags` row.
- If a component has no data in the window (for example no sampled evals yet), drop it and rescale the remaining weights to sum to 1. Never treat missing as zero. Mark the score as partial.
- Fewer than 20 runs in the window: show the score as "not enough data", do not alert on it.

## 12. Environment variables

```
# shared
DATABASE_URL=
REDIS_URL=
# llm
LLM_PROVIDER=            # openai | anthropic (anthropic also covers Ollama through LLM_BASE_URL)
LLM_BASE_URL=            # empty for the Claude API; http://localhost:11434 for local Ollama
LLM_API_KEY=
AGENT_MODEL=
JUDGE_MODEL=
LLM_CACHE=1              # 1 in tests/CI/evals
LLM_DAILY_BUDGET_USD=
# sdk (in the demo agents)
SENTINEL_API_KEY=
SENTINEL_ENDPOINT=
# workers
ONLINE_EVAL_SAMPLE_RATE=0.10
DRIFT_WINDOW_MINUTES=
EMBEDDING_MODEL=
# alerts
SLACK_WEBHOOK_URL=
# dashboard
NEXT_PUBLIC_API_URL=
SENTINEL_READ_KEY=
```
