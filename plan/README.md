# Plan folder

Everything needed to build Sentinel, one step at a time.

| File | What it is | Who updates it |
|---|---|---|
| `spec.md` | The original project spec. Scope source of truth. | Nobody (frozen) |
| `architecture.md` | Locked technical decisions, repo layout, contracts, data-model changes | Only via a `decisions.md` entry |
| `steps.md` | 57 ordered steps, each with a "Done when" check | Only when a step is cut or split |
| `completed.md` | Current position + log of finished steps | After every step |
| `rules.md` | Working rules for any AI agent (and for you) | Rarely |
| `decisions.md` | Decision log: what was chosen, why, what was rejected | When a decision is made or changed |
| `results.md` | Every measured number about Sentinel. Feeds the README and resume | When something is measured |
| `journal.md` | Weekly notes, hardest bugs, "what I'd do differently" | Weekly, by you |

`../CLAUDE.md` at the repo root is read by Claude Code at the start of every session and points here.

## How a session goes

Open the repo in Claude Code and paste one of these.

**Normal session**
```
Do the next step.
```
(CLAUDE.md tells it to read rules → completed → steps, do exactly one step, verify, log, commit, stop.)

**Specific step**
```
Do step 2.3. Before writing code, tell me your plan in 5 lines and wait for my OK.
```

**When you want to understand what was built**
```
Walk me through what step 2.3 added, file by file, as if I have to explain it in an interview. One concept at a time.
```

**End of week**
```
Run the weekly close from plan/steps.md for week 2.
```

**When behind schedule**
```
I'm behind. Read plan/completed.md and the cut list in plan/steps.md and tell me what to cut and what that does to the remaining steps. Don't change any files yet.
```

## Before step 0.1

1. This folder currently sits inside OneDrive. Move the project out before `git init` (step 0.1 covers where to).
2. `sentinel-sdk` is already taken on PyPI by an unrelated project. Step 0.2 picks the final package name.
