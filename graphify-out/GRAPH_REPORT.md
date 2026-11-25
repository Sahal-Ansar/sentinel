# Graph Report - sentinel  (2026-11-26)

## Corpus Check
- 19 files · ~14,402 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 22 file(s) not represented in the graph (top: (none) 20, .example 1, .lock 1)

## Summary
- 196 nodes · 353 edges · 16 communities (9 shown, 7 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 74 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Rules
- Offline Eval + CI Regression Gate
- Results
- Sentinel Platform
- Failure-Mode Detection
- Ticker Service
- Agent B: Tool-Using Research Agent
- Root-Cause Failure Clustering
- Collector API Endpoints
- test_import.py
- __init__.py
- sentinel-collector
- sentinel-demo-agents
- sentinel-evals
- sentinel-obs
- sentinel-workers

## God Nodes (most connected - your core abstractions)
1. `Rules` - 14 edges
2. `Results` - 12 edges
3. `Offline Eval + CI Regression Gate` - 11 edges
4. `Fault-Injection Agent Versions` - 11 edges
5. `Weekly Close` - 11 edges
6. `Sentinel Platform` - 10 edges
7. `Plan Folder README` - 9 edges
8. `Failure-Mode Detection` - 9 edges
9. `Completed Log` - 8 edges
10. `Decision Log` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Make Commands` --calls--> `3.4 Eval runner CLI (sentinel-eval)`  [INFERRED]
  CLAUDE.md → plan/steps.md
- `Session Protocol` --references--> `Results`  [EXTRACTED]
  CLAUDE.md → plan/results.md
- `Project Spec` --references--> `Sentinel Platform`  [EXTRACTED]
  plan/spec.md → CLAUDE.md
- `Hard Rules` --references--> `Dependency Rules`  [EXTRACTED]
  CLAUDE.md → plan/rules.md
- `Hard Rules` --references--> `Honesty About Numbers`  [EXTRACTED]
  CLAUDE.md → plan/rules.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Run Completion Job Fan-Out** — plan_architecture_run_lifecycle, plan_architecture_on_run_complete, plan_architecture_detect_failure_modes, plan_architecture_embed_run_input, plan_architecture_online_eval [EXTRACTED 1.00]
- **Fault-Injection Validation Loop** — plan_architecture_fault_injection_set, plan_spec_traffic_simulator, plan_architecture_ground_truth_metadata, plan_steps_5_2_detector_validation, plan_steps_6_6_clustering_validation, plan_results_fault_injection_matrix [INFERRED 0.95]
- **Metrics to Health Score to Alert Pipeline** — plan_architecture_compute_metrics, plan_architecture_metric_snapshots, plan_spec_composite_health_score, plan_architecture_evaluate_alerts, plan_spec_alerting [INFERRED 0.95]

## Communities (16 total, 7 thin omitted)

### Community 0 - "Rules"
Cohesion: 0.12
Nodes (27): Hard Rules, Make Commands, Session Protocol, Architecture and Locked Decisions, Environment Variables, Monorepo Layout, Completed Log, Current Position (+19 more)

### Community 1 - "Offline Eval + CI Regression Gate"
Cohesion: 0.08
Nodes (33): a-bad-prompt, a-wrong-model, detect_drift Job, embed_run_input Job, online_eval Job, D-008 One LLM provider behind a wrapper, D-010 PostgreSQL + pgvector for everything, D-011 Local embeddings through fastembed (+25 more)

### Community 2 - "Results"
Cohesion: 0.10
Nodes (34): Fault-Injection Agent Versions, Journal, Interview Answers to Rehearse, Weekly Notes, Results, Engineering Metrics, Evaluation Quality Metrics, Fault-Injection Matrix (+26 more)

### Community 3 - "Sentinel Platform"
Cohesion: 0.17
Nodes (16): Sentinel Platform, SDK Guarantees (never raise, never block, bounded memory), SDK Public Surface, Span Wire Format, D-003 SDK built on OpenTelemetry SDK, SDK Code Rules, Alerting, Collector API (spec) (+8 more)

### Community 4 - "Failure-Mode Detection"
Cohesion: 0.15
Nodes (17): b-broken-tool, b-loop, detect_failure_modes Job, Execution Status vs Correctness, Health Score Missing-Data Rules, run_flags Table, Abandonment Detector, Composite Health Score (+9 more)

### Community 5 - "Ticker Service"
Cohesion: 0.15
Nodes (21): Collector Service (FastAPI), compute_metrics Job, Data Model Changes, evaluate_alerts Job, metric_snapshots Table, on_run_complete Job, PostgreSQL + pgvector, Redis Queue (+13 more)

### Community 6 - "Agent B: Tool-Using Research Agent"
Cohesion: 0.20
Nodes (14): a-no-retrieval, a-v1 (baseline), b-v1 (baseline), Ground-Truth Run Metadata (fault_label), D-005 Agent A without framework, Agent B on LangGraph, D-006 Fictional product docs for RAG agent, D-007 Local search tool, not live web search, Agent A: RAG Support Bot (+6 more)

### Community 7 - "Root-Cause Failure Clustering"
Cohesion: 0.17
Nodes (13): cluster_failures Job, Dashboard Service (Next.js), D-014 Next.js dashboard, Dashboard (spec), Root-Cause Failure Clustering, Trace Viewer, 6.4 Clustering pipeline, 6.5 Cluster summaries (+5 more)

### Community 8 - "Collector API Endpoints"
Cohesion: 0.28
Nodes (9): Collector API Endpoints, D-015 Read keys instead of user accounts, D-017 Seed by replaying recorded spans, D-018 Hosting (open), Project-Scoped Query Isolation, Security and Privacy Rules, 7.1 Read API, 8.2 Seed data (+1 more)

## Knowledge Gaps
- **20 isolated node(s):** `sentinel-collector`, `sentinel-demo-agents`, `sentinel-evals`, `sentinel-obs`, `sentinel-workers` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 25 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Sentinel Platform` connect `Sentinel Platform` to `Rules`, `Offline Eval + CI Regression Gate`, `Failure-Mode Detection`, `Root-Cause Failure Clustering`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `Rules` connect `Rules` to `Collector API Endpoints`, `Offline Eval + CI Regression Gate`, `Results`, `Sentinel Platform`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `Results` connect `Results` to `Rules`, `Offline Eval + CI Regression Gate`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Offline Eval + CI Regression Gate` (e.g. with `Git Rules` and `3.4 Eval runner CLI (sentinel-eval)`) actually correct?**
  _`Offline Eval + CI Regression Gate` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `sentinel-collector`, `sentinel-demo-agents`, `sentinel-evals` to the rest of the system?**
  _20 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Rules` be split into smaller, more focused modules?**
  _Cohesion score 0.12315270935960591 - nodes in this community are weakly interconnected._
- **Should `Offline Eval + CI Regression Gate` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._