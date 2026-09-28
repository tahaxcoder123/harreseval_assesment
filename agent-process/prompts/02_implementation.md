# Implementation Prompt

## Goal
Implement the end-to-end Python engine for `harness-eval` based on Pydantic v2 schemas and the abstract runner interface.

## Requirements
1. `src/harness_eval/models.py`: Versioned data models (`RunResult`, `HarnessConfig`, `ComparisonReport`, `TaskOutcome`, `DecisionOutcome`).
2. `src/harness_eval/harness/`: Loader and diff engine calculating structural deltas between baseline and candidate harnesses (models, skills, tools, hooks, system prompt).
3. `src/harness_eval/benchmarks/`: Benchmark YAML loader validating tasks, acceptance criteria, and holdout specifications.
4. `src/harness_eval/runners/`: Deterministic `MockRunner` with seedable variations, realistic unified diffs, and test outputs; plus `RealAgentRunner` for subprocess/API invocation.
5. `src/harness_eval/evaluation/`: Multi-dimensional evaluators, comparator, descriptive statistics across repetitions, and transparent decision logic.
6. `src/harness_eval/reporting/`: Rich terminal output, standalone HTML report with interactive inspection, and structured JSON output with per-task artifact directories (`runs/task-xxx/`).
7. `sample_project/`: A realistic Python application with deliberate bugs and gaps to benchmark.
