# Sentinel

Production reliability platform for LLM agents: tracing SDK → collector → evals, health, drift, failure clustering → dashboard + alerts. Solo 8-week portfolio project (owner: Sahal). Target roles: AI Engineer, Forward Deployed Engineer.

## Read before doing anything

1. `plan/rules.md` — how to work in this repo. Non-negotiable.
2. `plan/completed.md` — where the project is right now and what step is next.
3. `plan/steps.md` — the step you are about to do (read that step only, plus its phase header).
4. `plan/architecture.md` — locked decisions and contracts. Read the sections the step touches.

`plan/spec.md` is the original project spec. It is the source of truth for scope; `architecture.md` is the source of truth for how.

## Session protocol

1. Read the four files above. State the next step ID and its "Done when" in ≤5 lines.
2. Do that one step. Nothing from later steps.
3. Run the step's "Done when" check and show the real output.
4. Update `plan/completed.md` (always), `plan/results.md` (if a number was measured), `plan/decisions.md` (if a decision was made or changed).
5. Commit. Stop. Do not start the next step unless asked.

## Hard rules (full list in plan/rules.md)

- Never invent, estimate or round up a metric. Unmeasured stays `not measured`.
- Never commit secrets. Keys live in `.env` (gitignored) and GitHub Actions secrets.
- All services run in Docker Compose. RQ workers do not run natively on Windows.
- Ask before adding a dependency that is not in `plan/architecture.md`.
- Ask before any batch of more than 100 paid LLM calls, with a cost estimate.
- Human-only work (hand labels, golden-set review, friend test, demo video) is never done or simulated by an AI.

## Commands

Run from the repo root. `test` and `lint` work now; `up`/`down` need step 0.4, `simulate` step 1.6, `eval` step 3.4.

```
make up        # start postgres, redis, collector, worker, ticker, dashboard
make down
make test      # pytest across sdk/, collector/, workers/, evals/
make lint      # ruff check + ruff format --check
make simulate  # run the traffic simulator against the local collector
make eval      # run offline evals for both agents and compare to baseline
```

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
