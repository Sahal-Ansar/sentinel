# Completed

The single source of truth for where the project is. Updated after every step.

## Pace

Updated every session. On track = steps done / 57 is at least sessions used / 48.

- **Sessions used:** 1 / 48
- **Steps done:** 2 / 57
- **Status:** on track
- **Crunch weeks:** 2, 7, 8

## Current position

- **Next step:** 0.3 Accounts and keys `[you]` `[short]`
- **Week:** not started
- **Blocked on:** nothing
- **Open (started, not done):** none
- **Cut so far:** none

## Progress

| Phase | Steps | Done | Deliverable shown working |
|---|---|---|---|
| 0 Setup | 4 | 2 | — |
| 1 Demo agents + simulator | 6 | 0 | no |
| 2 SDK + collector | 8 | 0 | no |
| 3 Offline eval + CI gate | 6 | 0 | no |
| 4 Online eval + calibration | 5 | 0 | no |
| 5 Health, SLOs, alerts | 6 | 0 | no |
| 6 Drift + clustering | 6 | 0 | no |
| 7 Dashboard | 8 | 0 | no |
| 8 Package, deploy, docs | 8 | 0 | no |
| **Total** | **57** | **2** | |

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
