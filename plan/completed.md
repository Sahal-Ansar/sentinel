# Completed

The single source of truth for where the project is. Updated after every step.

## Pace

Updated every session. On track = steps done / 57 is at least sessions used / 48.

- **Sessions used:** 2 / 48
- **Steps done:** 3 / 57
- **Status:** on track (0.3 is not counted until 0.3b is done)
- **Crunch weeks:** 2, 7, 8

## Current position

- **Next step:** 1.1 LLM wrapper `[short]`
- **Week:** not started
- **Blocked on:** nothing
- **Open (started, not done):** 0.3 (0.3a done; 0.3b waits for Claude API credits, due before the week 3 CI gate)
- **Cut so far:** none

## Progress

| Phase | Steps | Done | Deliverable shown working |
|---|---|---|---|
| 0 Setup | 4 | 3 | — |
| 1 Demo agents + simulator | 6 | 0 | no |
| 2 SDK + collector | 8 | 0 | no |
| 3 Offline eval + CI gate | 6 | 0 | no |
| 4 Online eval + calibration | 5 | 0 | no |
| 5 Health, SLOs, alerts | 6 | 0 | no |
| 6 Drift + clustering | 6 | 0 | no |
| 7 Dashboard | 8 | 0 | no |
| 8 Package, deploy, docs | 8 | 0 | no |
| **Total** | **57** | **3** | |

## How to log a step

Add an entry at the top of the log (newest first), then update "Current position" and the table. Use this shape:

```
### <step id> <step name> — <YYYY-MM-DD>
- Status: done | in progress | cut
- Commit: <short hash>
- What was built: 2–4 lines
- Done-when check: the command run and what it showed
- Deviations from steps.md / architecture.md: none | what and why (link the decisions.md ID)
- Numbers measured: none | metric = value (also copied to results.md)
- Follow-ups: none | anything deliberately left for a later step
```

Rules: a step is `done` only if its check was actually run and passed. A step that was started and not finished is `in progress` with what is left. Never delete an entry; correct it with a new line.

## Log

### 0.4 Compose skeleton — 2026-11-26
- Status: done
- Commit: the commit that adds this entry, `feat: compose skeleton (0.4)`
- What was built: `docker-compose.yml` with `postgres` (`pgvector/pgvector:0.8.7-pg17`) and `redis` (`redis:8.8.4-alpine`), healthchecks, named volumes, ports bound to 127.0.0.1. Optional `POSTGRES_PASSWORD`, `POSTGRES_HOST_PORT` and `REDIS_HOST_PORT` overrides.
- Done-when check: `rtk proxy make up` exited 0 with both containers `(healthy)`; `psql -c "CREATE EXTENSION vector"` printed `CREATE EXTENSION`, version 0.8.7. Data survived `make down` and `make up`.
- Deviations from steps.md / architecture.md: none. Defaults are 5432 and 6379; the local `.env` uses 5433 because another project's container (`juris-db-1`) holds 5432.
- Numbers measured: none
- Follow-ups: `DATABASE_URL` from this host must use port 5433 here (5432 inside compose). The extension was created by hand; a migration should create it in phase 2. Use `--quiet-pull` or a filtered log for future `make up` output.

### 0.3a Local LLM — 2026-11-26
- Status: done (0.3 as a whole: in progress, 0.3b left)
- Commit: 02076f0
- What was built: `demo_agents/check_llm.py`, the `anthropic` dependency (2.14.0) in `demo_agents`, `LLM_BASE_URL` in `.env.example`, local `.env` (gitignored, placeholder key). Step 0.3 split into 0.3a and 0.3b.
- Done-when check: `rtk proxy uv run --locked --package sentinel-demo-agents --env-file .env python demo_agents/check_llm.py` printed `qwen2.5:7b end_turn 36` and `text='Ready'`, exit 0. A second run also passed.
- Deviations from steps.md / architecture.md: local Ollama instead of a paid provider, `LLM_BASE_URL` added (D-008). No spending cap or GitHub secret yet (0.3b).
- Numbers measured: none (the token counts above are check output, not results)
- Follow-ups: 1.1 should pick a context size above Ollama's 4096 default, or long prompts may be cut off, and should not trust Ollama's input token counts (36, then 1, for the same prompt). Ollama must be running (`ollama serve`) before any agent run. 0.3b before the week 3 CI gate.

### 0.2 Repo scaffold — 2026-11-26
- Status: done
- Commit: 10391ba
- What was built: folder layout from `architecture.md` §2, `uv` workspace (sdk, collector, workers, evals, demo_agents), `.gitignore`, `.gitattributes`, `.env.example`, `Makefile`, ruff, pre-commit, `ci.yml`. Package name `sentinel-obs` (D-004). Knowledge graph in `graphify-out/`. Added `rules.md` §12, §1 items 8–9, the §9 remote and commit rule, and the Pace block.
- Done-when check: first push to `Sahal-Ansar/sentinel`. `rtk proxy gh run view 45697791391` showed `✓ main ci`, `✓ lint-and-test in 9s`. CI ran `make lint` (ruff check, ruff format --check) and `make test` (1 passed).
- Deviations from steps.md / architecture.md: `sentinel-llm` was taken, so the name changed (D-004). Ruff skips `*.md` so it does not reformat the plan. `uv_build` (part of uv) is the SDK build backend.
- Numbers measured: none
- Follow-ups: `make` is not installed locally, so the Makefile has only run in CI; 0.4 needs it. `.claude/` is gitignored because `graphify claude install` writes machine-local paths; rerun it on a new clone. `graphify update .` segfaults here (Microsoft Store Python) unless run as `PYTHONHASHSEED=0 graphify update .`. The graph's plan-doc nodes predate this session's plan edits; refresh with `/graphify . --update` at the week 1 close. Empty folders hold `.gitkeep`; remove each when real files land.
- Correction (2026-11-26): GNU Make 4.4.1 is now installed; `make lint` and `make test` pass locally.

### 0.1 Machine setup — 2026-11-26
- Status: done
- Commit: 10391ba
- What was built: project copied from OneDrive to `C:\dev\sentinel` (10 files, all hashes matched). rtk 0.49.0 and graphify 0.9.67 were already installed; `gh` 2.105.0 installed and signed in.
- Done-when check: through `rtk proxy` from `C:\dev\sentinel`: Docker Compose v5.5.1, git 2.46.1.windows.1, uv 0.12.19, node v22.14.0.
- Deviations from steps.md / architecture.md: `claude` removed from 0.1 at Sahal's request (desktop app already includes it).
- Numbers measured: none
- Follow-ups: the Docker engine was not running during the check; start Docker Desktop before 0.4. Sahal deletes the OneDrive copy.

### Plan created — 2026-11-25
- Status: done
- What was built: `CLAUDE.md` and the `plan/` folder (spec, architecture, steps, rules, decisions, results, journal). No code yet.
- Follow-ups: move the project out of OneDrive before `git init` (step 0.1); final package name (step 0.2); LLM provider choice (step 0.3).
