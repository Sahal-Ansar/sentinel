# Rules

These apply to every session, whoever is typing. If a rule and a request conflict, stop and say so.

## 1. Workflow

1. Start every session by reading `CLAUDE.md`, this file, `completed.md`, then the next step in `steps.md`.
2. One step per session. Do not start the next step unless asked. Exception: pair a `[short]` step with the next one when time allows.
3. Before writing code, state the step ID, the plan in ≤5 lines, and the "Done when" check.
4. A step is done only when its "Done when" check has been run and the real output shown. "Should work" is not done.
5. If the check fails, the step stays open. Log what happened under the step in `completed.md` as `in progress`, never as done.
6. After a step: update `completed.md`, then `results.md` / `decisions.md` if they apply, then commit.
7. Stuck on the same error after 2 attempts: stop, summarize what was tried, propose 2–3 options, wait.
8. Update the Pace block at the top of `completed.md` every session.
9. At each weekly close, if steps are open, propose cuts from the cut list in `steps.md`, in order, and wait for Sahal's OK. Never skip or cut silently.

## 2. Scope

- Build only what the current step says. No building ahead, no "while I'm here" extras.
- Nothing outside `spec.md`. Stretch goals stay locked until every phase 8 step is done.
- If behind, cut in the order given in `steps.md`. Never cut the never-cut list.
- Changing anything in `architecture.md` needs a `decisions.md` entry first and Sahal's OK.
- A step that turns out too big gets split (2.7a, 2.7b) in `steps.md`, not silently half-done.

## 3. Honesty about numbers

This project's value is that its numbers are real.

- Every number in `results.md`, the README or the resume entry comes from a run that actually happened, recorded with date, commit hash and the exact command.
- Never invent, estimate, extrapolate or round in the flattering direction.
- Unmeasured values stay `not measured`. Unfinished features are written as `in progress`.
- Report misses plainly: if the gate catches 3 of 5 broken versions, write 3 of 5.
- Tuning to hit a target is fine; tuning on the same data you report on is not. Keep a held-out portion (see steps 4.5 and 6.6).

## 4. Human-only work

These are done by Sahal, never by an AI, and never simulated:

- Reviewing every golden-dataset example (3.1)
- Hand-labeling runs for judge calibration (4.4). AI-generated "human" labels make the agreement number meaningless.
- The friend integration test (8.7)
- Recording the demo video (8.8)
- Final say on any decision

An AI may build the tooling, draft candidates and check for mistakes afterwards.

## 5. Explain as you build

Sahal has to defend every part of this in interviews, and the stats are the part interviewers dig into.

- No large unexplained code dumps. After each step, give a short walkthrough: what was added, why it is shaped that way, what to look at first.
- Every statistical or ML concept gets a `docs/learn/<topic>.md` the first time it is used: Cohen's kappa, percentiles (p50/p95/p99), precision and recall, cosine distance, permutation tests, Mann–Whitney U, UMAP, HDBSCAN, Adjusted Rand Index.
- Format for a learn doc: plain English, from first principles, no assumed maths background; one tiny worked example with small real numbers done step by step; a simple diagram or ASCII sketch where it helps; and "how to say this in an interview" in 3 sentences.
- One concept at a time. Do not stack three new ideas into one explanation.

## 6. Cost

- Model names come only from env vars (`AGENT_MODEL`, `JUDGE_MODEL`). Never hardcode a model name in code.
- Default to the cheapest current model tier. Check the provider's current model list and pricing at build time; do not trust memory.
- The LLM response cache is ON in tests, CI and eval runs. Unit tests never make paid calls.
- Before any batch of more than 100 paid LLM calls: estimate the cost, say it, wait for OK.
- Embeddings run locally. No paid embedding APIs.
- A spending cap is set in the provider console (step 0.3). Record actual spend weekly in `journal.md`.

## 7. Dependencies and docs

- Ask before adding any dependency not listed in `architecture.md`.
- LangGraph, the OpenTelemetry GenAI conventions, RQ and the provider SDKs change often. Read the current docs before using an API; do not write it from memory.
- Pin everything through the lockfile. Commit the lockfile.
- Prefer prebuilt wheels. Use `sklearn.cluster.HDBSCAN` rather than the separate `hdbscan` package.

## 8. Code

**Python**
- 3.12, type hints on every function, `ruff` for lint and format, `pytest` for tests.
- Pydantic v2 for all validation. SQLAlchemy 2.0 style, async in the collector.
- Every schema change is an Alembic migration. No manual `ALTER TABLE`.
- Config through env vars loaded by `pydantic-settings`. No config constants scattered in code.
- Structured logs (JSON). No `print` outside CLIs.

**SDK (extra rules, these are the product)**
- Never raise into the host app. Every SDK failure is caught, counted and logged at debug level.
- Never block the host app. Export happens off the request path.
- No work at import time. Nothing happens until `init()` is called.
- Minimal dependencies. The SDK must not import anything from `collector/` or `workers/`.
- Redaction runs before data leaves the process, and is on by default.

**Multi-tenancy**
- Every query that touches tenant data filters by `project_id`. No exceptions.
- Every read endpoint has a test proving project A cannot see project B.

**TypeScript (dashboard)**
- `strict` on, no `any`. Server components by default; client components only where interactivity needs them.
- Every page has loading, empty and error states.

**Tests**
- New logic ships with tests in the same step. Coverage target on `sdk/` and `collector/` is above 70%.
- Tests are deterministic: fixed seeds, stubbed LLM, no network.

## 9. Git

- Small commits, conventional prefixes (`feat:`, `fix:`, `test:`, `docs:`, `chore:`), step ID in the message: `feat(sdk): batching exporter (2.3)`.
- Remote: `https://github.com/Sahal-Ansar/sentinel.git`. Keep commit messages simple. Never add Claude as co-author or any other AI attribution line.
- From phase 3 on, work on a branch per step and merge by PR so the CI gate has real history.
- Never commit `.env`, API keys, database dumps or `node_modules`. Never force-push `main`.
- Tag the end of each week: `week-1` … `week-8`.

## 10. Environment (Windows)

- The repo does not live in OneDrive. See step 0.1.
- Every service runs in Docker Compose. RQ workers need `fork()` and do not run natively on Windows.
- `.gitattributes` forces LF line endings so shell scripts work inside containers.
- Only SDK unit tests and linters need to run natively; everything else goes through `make`.

## 11. Security and privacy

- API keys are stored as SHA-256 hashes, shown once at creation, never logged.
- No real personal data anywhere. The docs corpus, the customers table and the query bank are all fictional.
- The public demo is read-only: ingestion is disabled or rate-limited, and it uses a read-only key.

## 12. Tooling

- Read `graphify-out/GRAPH_REPORT.md` before architecture questions or broad searches. Rebuild the graph at every weekly close and after any step that adds a new module.
- The rtk hook stays on. For a step's "Done when" check, or any number going into `results.md`, run the command through `rtk proxy` so the raw output is what gets shown and recorded.
- At each weekly close, put `rtk gain` output in the journal note.
