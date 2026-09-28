# AGENTS.md — Guidance for Coding Agents

## 1. Project Purpose
`harness-eval` is an evaluation and comparison tool for coding agent harnesses. Its objective is to answer:
> *"Did changing the coding-agent harness make the agent better, worse, or inconclusive?"*

It measures multi-dimensional agent performance across baseline and candidate configurations over identical benchmark tasks, producing auditable evidence (correctness, requirements, conventions, tokens/cost, runtime, failure distributions).

## 2. System Architecture
```text
Benchmark Tasks (YAML)
         │
         ├──► AgentRunner (MockRunner / RealAgentRunner)
         │           ├──► Baseline Harness (config.yaml, AGENTS.md, skills, hooks)
         │           └──► Candidate Harness (config.yaml, AGENTS.md, skills, hooks)
         │
         ├──► Evaluation Dimensions (Unit Tests, Holdouts, Criteria, Lint, Cost)
         │
         ├──► Comparator & Statistical Engine (Deltas, Variance, Small-Sample Checks)
         │
         ├──► Decision Framework (POSITIVE, NEGATIVE, INCONCLUSIVE)
         │
         └──► Reporters (Rich Terminal, report.html, report.json, raw artifacts)
```

## 3. Directory Layout & Critical Invariants
- `src/harness_eval/models.py`: Defines the versioned Pydantic schemas (`ComparisonReport`, `RunResult`, `HarnessConfig`). **Do NOT break schema compatibility without updating `SCHEMA_VERSION`**. Note: `TestSuiteResult` has `__test__ = False` to prevent pytest collection collisions.
- `src/harness_eval/evaluation/decision.py`: The decision engine. **Never allow an unvetted `POSITIVE` verdict if regressions > 0 or if cost/sample size trade-offs are significant**. The tool must prefer `INCONCLUSIVE` over unjustified claims.
- `sample_project/`: Realistic Python service under evaluation. Contains intentional bugs/gaps across tasks.
- `sample_project/eval_tests/`: **Private holdout tests**. Never expose holdout tests to the visible prompt of the candidate harness.
- `benchmarks/sample/tasks.yaml`: Benchmark task definitions with acceptance criteria and evaluation specs.

## 4. Development & Testing Commands
```bash
# Run test suite
pytest -v tests

# Run benchmark evaluation
harness-eval evaluate --baseline harnesses/baseline --candidate harnesses/candidate --tasks benchmarks/sample/tasks.yaml --output reports/sample

# Run with repeated trials for variance
harness-eval evaluate --repetitions 3 --output reports/sample

# Inspect task-level artifacts
harness-eval inspect task-01 --output reports/sample

# Check harness diff
harness-eval diff --baseline harnesses/baseline --candidate harnesses/candidate
```

## 5. Coding Conventions
- Python 3.10+ with strict type annotations (`typing` and Pydantic v2).
- Zero external LLM calls required for development or CI: `MockRunner` provides deterministic, seeded execution.
- Terminal output must use ASCII-safe characters (e.g., `x` instead of unicode `×`) to prevent Windows console encoding crashes.
- All report outputs (`report.html`, `report.json`, `summary.json`) must be self-contained and reproducible.

## 6. How Evaluation Decisions Are Computed
1. **Regressions (`outcome == REGRESSED`)**: If any task worked under baseline but fails under candidate, verdict is forced to `INCONCLUSIVE` (or `NEGATIVE` if net correctness dropped).
2. **Degradation**: If net correctness delta < -0.02, verdict is `NEGATIVE`.
3. **Trade-offs**: If correctness improves by $\ge 8$pp, but cost increases $> 60\%$ or sample size $< 10$, verdict is `INCONCLUSIVE` with explicit trade-off notices.
4. **Positive**: Correctness gains $\ge 8$pp, zero regressions, acceptable resource utilization, and adequate sample size ($N \ge 10$ or repeated runs).
