# Decision log

Why things are the way they are. This becomes the README's "design decisions" section and your answers to "why did you…" in interviews.

Add an entry whenever a decision is made or changed. Never rewrite an old entry; add a new one that supersedes it.

```
## D-0XX Title — YYYY-MM-DD
- Decision:
- Why:
- Rejected:
- Revisit if:
```

---

## D-001 Python 3.12, uv workspace, ruff, pytest — 2026-11-25
- Decision: one `uv` workspace for `sdk/`, `collector/`, `workers/`, `evals/`, `demo_agents/`.
- Why: one lockfile, fast installs, and the SDK stays a separately installable package with its own minimal dependencies.
- Rejected: separate repos (too much overhead for one person); pip + requirements files (no lockfile discipline).
- Revisit if: `uv` workspaces get in the way of installing the SDK straight from GitHub.

## D-002 Everything runs in Docker Compose; repo lives outside OneDrive — 2026-11-25
- Decision: all services run in containers. The repo moves out of the OneDrive folder before `git init`.
- Why: RQ workers need `fork()` and do not run natively on Windows. OneDrive syncing `.git`, `.venv` and `node_modules` causes conflicts and slow mounts. Compose is also the final deliverable, so using it from day one means it is tested every day.
- Rejected: native Windows services; Celery just to dodge the fork issue.
- Revisit if: Docker Desktop is too heavy for the laptop; then move development fully into WSL2.

## D-003 SDK is built on the OpenTelemetry SDK — 2026-11-25
- Decision: use OpenTelemetry's tracer, context propagation and batch processor. Sentinel adds the decorator API, LLM/tool capture, redaction and a custom exporter to the collector. Attribute names follow the OTel GenAI conventions where they exist.
- Why: context propagation across async code and background batching are solved problems; rewriting them adds bugs, not value. It makes "optional export to any OpenTelemetry backend" nearly free (add a second exporter), and it is the honest version of the interoperability claim.
- Rejected: hand-rolled span model and batching (more code, weaker interop story); accepting raw OTLP in the collector (protobuf handling is a time sink for week 2).
- Revisit if: OTel overhead pushes per-span cost over the 5 ms target, or the GenAI conventions change shape mid-project (they are still evolving; check the current spec in step 2.2).

## D-004 Package name — 2026-11-25
- Decision: not `sentinel-sdk`. Working name `sentinel-llm`, import `sentinel_llm`. Final name confirmed in step 0.2.
- Why: `sentinel-sdk` (import `sentinel_sdk`) already exists on PyPI as an unrelated project (checked 2026-11-25). The working name has not been checked yet.
- Rejected: keeping `sentinel-sdk` and installing only from GitHub (import-name clash on any machine that has the other package).
- Revisit if: the working name is also taken.
- Note: "Sentinel" is also the name of several unrelated products (including Redis Sentinel, which matters since this project uses Redis). Fine for a portfolio project; be ready for the question.
- Final name (2026-11-26, step 0.2): `sentinel-obs`, import `sentinel_obs`, picked by Sahal. `sentinel-llm` is taken on PyPI (0.1.1, an unrelated LLM observability package). `sentinel-reliability` and `sentinel-agents` were the other options. `sentinel-obs` returned 404 on both the PyPI JSON and simple endpoints on 2026-11-26; the name is not reserved until something is published, so re-check in step 8.4.

## D-005 Agent A without a framework, Agent B on LangGraph — 2026-11-25
- Decision: Agent A calls the provider SDK directly; Agent B uses LangGraph.
- Why: this is what makes "framework-agnostic, works with at least two agent setups" true, using the two integration paths the SDK offers (auto-instrumentation and the callback handler).
- Rejected: both on LangGraph (proves nothing about being framework-agnostic).

## D-006 Fictional product docs for the RAG agent — 2026-11-25
- Decision: write a small docs set for an invented product.
- Why: with real public docs the model can answer from training data, so disabling retrieval would not lower correctness and groundedness checks would be untestable. Invented facts make retrieval failures visible.
- Rejected: an open-source project's docs.

## D-007 Agent B uses a local search tool, not live web search — 2026-11-25
- Decision: `search` runs over a fixed local corpus. A real search provider can be switched on later.
- Why: evals need the same question to have the same right answer tomorrow. Live web results change, cost money and need another key.
- Rejected: live web search by default.

## D-008 One LLM provider behind a wrapper — 2026-11-25
- Decision: provider chosen in step 0.3. Agents and judge share it. Models are set only through env vars.
- Why: one bill, one key in CI. The SDK still instruments both OpenAI and Anthropic clients, which is what the spec asks for.
- Rejected: using both providers in the demo agents (double the setup for no demo value).
- Revisit if: judge agreement is poor and a different judge model would help.
- Provider chosen (2026-11-26, step 0.3a, Sahal): local Ollama with `qwen2.5:7b` for agents and judge, through the official `anthropic` Python SDK and Ollama's Anthropic-compatible endpoint. Moving to the Claude API when credits exist (step 0.3b).
  - Why: no API credits yet. Ollama cloud is pay-per-token as of 2026-11-26, so local is the only free option. `qwen2.5:7b` was already installed and fits in 8 GB of VRAM. Using the `anthropic` SDK for both should make the switch an env change (`LLM_BASE_URL`, `LLM_API_KEY`, `AGENT_MODEL`, `JUDGE_MODEL`).
  - Adds: the `anthropic` dependency and the `LLM_BASE_URL` env var (empty means the Claude API).
  - Rejected: `qwen3.5:9b` (6.6 GB download, tight on 8 GB of VRAM); Ollama cloud (paid); the `openai` SDK (the later switch would need code changes).
  - Known limits per Ollama's docs: no forced tool choice, no prompt caching, no token-counting endpoint, approximate token counts. Observed 2026-11-26: the same prompt sent twice reported 36 then 1 input tokens (likely prompt reuse in Ollama), so token totals are unreliable on this setup. Context defaulted to 4096 tokens here. From a container the URL is `http://host.docker.internal:11434`.
  - Consequences: cost metrics mean nothing on a free local model, so they stay `not measured` until Claude. GitHub runners cannot reach the laptop, so 0.3b must be done before the CI gate in week 3. A model change invalidates baselines, the response cache and judge calibration; re-run them and never mix numbers from two models.

## D-009 RQ plus a ticker process — 2026-11-25
- Decision: Redis + RQ for jobs; a small `ticker` process enqueues periodic jobs.
- Why: far less configuration than Celery for a handful of job types.
- Rejected: Celery (heavier than needed); cron inside containers (awkward to test).
- Revisit if: the current RQ release has built-in periodic scheduling that replaces the ticker (check in step 4.1).

## D-010 PostgreSQL + pgvector for everything — 2026-11-25
- Decision: one database for relational data and embeddings.
- Why: one thing to run, back up and deploy. Volumes in this project are small.
- Rejected: a separate vector database; ClickHouse/DuckDB (first item on the cut list).

## D-011 Local embeddings through fastembed — 2026-11-25
- Decision: a small 384-dim model run locally via `fastembed` (ONNX), with `sentence-transformers` as fallback.
- Why: zero API cost, and no PyTorch in the worker image, which matters on small free-tier instances.
- Rejected: provider embedding APIs (cost, another dependency on the network).
- Revisit if: `fastembed` does not support the chosen model or misbehaves in the worker image (verify in step 1.3, where it is first used).

## D-012 Drift tests chosen for explainability — 2026-11-25
- Decision: input drift = centroid cosine distance with a permutation test. Quality drift = Mann–Whitney U with a minimum effect size.
- Why: both can be explained from scratch in an interview in a minute, and neither assumes the data follows a particular distribution.
- Rejected: MMD and classifier two-sample tests (stronger, harder to explain and tune; possible later upgrade).

## D-013 UMAP → sklearn HDBSCAN — 2026-11-25
- Decision: as in the spec, using scikit-learn's built-in HDBSCAN.
- Why: no separate compiled package to install; HDBSCAN does not need the number of clusters up front and labels outliers as noise.
- Rejected: k-means (needs k, forces every failure into a cluster).

## D-014 Next.js dashboard — 2026-11-25
- Decision: Next.js + Tailwind + Recharts.
- Why: frontend is Sahal's strongest skill, so the dashboard is where this project can look better than most portfolio projects in the same space. The trace viewer in particular benefits from custom UI.
- Rejected: Streamlit as the first choice (stays on the cut list as the fallback).

## D-015 Read keys instead of user accounts — 2026-11-25
- Decision: each project has a write key (ingest) and a read key (dashboard).
- Why: auth beyond API keys is out of scope in the spec; a read-only key is what makes a public demo safe.

## D-016 Response cache makes the CI gate cheap — 2026-11-25
- Decision: LLM responses are cached on (model, prompt, input) and the cache is restored in CI.
- Why: unchanged prompts re-run for free; only what a PR actually changed costs money. Also removes most run-to-run noise.
- Risk: a stale cache can hide a provider-side change. The cache key includes the model name; clear it when the model changes.

## D-017 Seed by replaying recorded spans — 2026-11-25
- Decision: record real span batches once, replay with shifted timestamps.
- Why: the demo needs days of history; replay is free, repeatable and uses real data shapes.
- Rejected: generating fake rows directly in SQL (skips the ingest path, drifts from reality).

## D-018 Hosting — open
- Decision: made in step 8.5 from what is free or cheap that week.
- Why open: free tiers change too often to pick 8 weeks ahead.
