# Agent Development Session Transcript

This transcript documents the step-by-step engineering session in which the `harness-eval` evaluation engine was built, audited, debugged, and verified.

---

## 1. What Was Requested
The engineering goal was to build a production-quality, focused **Harness Comparison and Evaluation Tool for coding agents** answering with verifiable evidence:
> **“Did changing the coding-agent harness make the agent better, worse, or inconclusive?”**

Key constraints and deliverables:
- An `evaluate` command comparing a baseline harness against a candidate harness over benchmark tasks.
- Evaluation across multi-dimensional criteria: Correctness, Requirement satisfaction, Convention compliance, Token/cost efficiency, Runtime, and Failure rates.
- Concrete per-task evidence and holdout verification.
- Transparent decision logic supporting `POSITIVE`, `NEGATIVE`, and `INCONCLUSIVE`.
- Automated test suite covering loaders, metrics, diffing, decision logic, and end-to-end CLI runs.
- `AGENTS.md`, a strictly one-page `DESIGN.md`, and process documentation.

---

## 2. What Was Changed & Implemented
1. **Environment Setup & Dependencies**:
   - Inspected Python 3.14 environment, discovered pre-installed `rich`, `pydantic`, `pytest`.
   - Installed `pyyaml` and `jinja2` via pip for harness configs and standalone HTML reporting.
   - Initialized `pyproject.toml` exposing the `harness-eval` CLI entrypoint.

2. **Sample Benchmark Application (`sample_project/`)**:
   - `app/database.py`: In-memory transactional data store.
   - `app/users.py`: User service.
   - `app/orders.py`: Order calculation service with an intentional calculation bug (discount erroneously added instead of subtracted).
   - `app/auth.py`: Authentication service.
   - `tests/test_users.py`, `tests/test_orders.py`: Baseline test suite.
   - `eval_tests/`: Hidden/holdout evaluation tests for 6 benchmark tasks.

3. **Harness Representations (`harnesses/`)**:
   - `harnesses/baseline/`: `config.yaml`, `AGENTS.md`, general prompt, basic python skill.
   - `harnesses/candidate/`: `config.yaml`, `AGENTS.md`, structured prompt, testing skill, strict typing skill, pre-commit lint hook.

4. **Core Evaluation Engine (`src/harness_eval/`)**:
   - `models.py`: Versioned Pydantic schemas (`SCHEMA_VERSION = "1.0.0"`).
   - `harness/loader.py` & `harness/diff.py`: Structural delta computation.
   - `benchmarks/loader.py`: Benchmark suite loader and task filter.
   - `runners/base.py`: `AgentRunner` ABC.
   - `runners/mock_runner.py`: Deterministic, seeded runner generating realistic diffs, pytest logs, holdout checks, and token calculations.
   - `runners/real_runner.py`: Extension point for external agent subprocesses and LLMs.
   - `evaluation/dimensions.py`: Correctness (unit + holdout), requirement satisfaction, convention compliance scoring.
   - `evaluation/comparator.py`: Task-level and aggregate metric comparators.
   - `evaluation/statistics.py`: Repetition variance, mean/median/min/max, and small-sample detection.
   - `evaluation/decision.py`: Transparent decision framework with rule tracking.
   - `reporting/terminal.py`: Rich terminal output.
   - `reporting/json_reporter.py`: Versioned JSON report and raw task artifact exporter (`runs/task-xxx/`).
   - `reporting/html_reporter.py`: Self-contained, responsive HTML report.
   - `cli.py`: CLI dispatcher (`evaluate`, `inspect`, `diff`).

---

## 3. What Was Checked Manually
1. Ran `sample_project` tests via `pytest sample_project/tests` -> Verified 4 passed.
2. Executed `harness-eval --help` -> Verified command discovery and parameter docs.
3. Executed `harness-eval diff --baseline harnesses/baseline --candidate harnesses/candidate` -> Verified structural diff identified model upgrade, added skills, and added hooks.
4. Executed `harness-eval evaluate --output reports/sample` -> Verified terminal executive summary, per-task breakdown, and `INCONCLUSIVE` verdict.
5. Executed `harness-eval inspect task-01 --output reports/sample` -> Inspected raw patch diffs, evidence points, and test results for Task 01.
6. Executed `harness-eval evaluate --repetitions 3` -> Verified statistical summary across repeated runs ($N=18$).
7. Inspected generated artifacts in `reports/sample/`:
   - `reports/sample/report.html` (30 KB, self-contained HTML).
   - `reports/sample/report.json` and `reports/sample/summary.json`.
   - `reports/sample/runs/task-01/` through `task-06/`.

---

## 4. Mistakes Made by the Agent & Discovery

### Mistake 1: Pytest Test Class Collection Collision
- **What happened**: In `src/harness_eval/models.py`, the model representing test execution results was named `TestSuiteResult`. Because its name begins with `Test`, pytest attempted to collect it as a test class during discovery.
- **How it was discovered**: Running `pytest -v tests` emitted:
  ```text
  PytestCollectionWarning: cannot collect test class 'TestSuiteResult' because it has a __init__ constructor (from: tests/test_comparator.py)
  ```
- **Correction applied**: Added `__test__ = False` inside `TestSuiteResult` in `src/harness_eval/models.py`. Re-running pytest confirmed 28 passed with zero warnings.

### Mistake 2: Unicode Encoding Failure on Windows Console
- **What happened**: In `src/harness_eval/evaluation/statistics.py`, the note string was formatted with a unicode multiplication symbol:
  ```python
  f"Sample size (N={sample_size}, {total_tasks} tasks × {repetitions} reps)..."
  ```
- **How it was discovered**: Upon running `harness-eval evaluate` in Windows PowerShell, the character rendered as a garbled symbol `` (`6 tasks  1 reps`), and column titles on narrower console windows wrapped awkwardly.
- **Correction applied**: Replaced unicode `×` with ASCII `x` in `statistics.py`, ensuring cross-platform terminal compatibility.

### Mistake 3: Table Column Clipping in Terminal Summary
- **What happened**: In `src/harness_eval/reporting/terminal.py`, columns were initially defined with fixed widths (`width=28`, `width=10`), causing truncated text and wrapped lines when task descriptions or outcomes were printed.
- **How it was discovered**: Manual visual inspection of the first terminal summary output revealed awkward line wrapping in the "Per-Task Evidence Breakdown" table.
- **Correction applied**: Updated column definitions in `terminal.py` to use `no_wrap=True` on fixed-content columns (Task ID, Baseline, Candidate, Cost Delta) while allowing the Title column to flex dynamically.

---

## 5. Verification & Test Suite Results
After applying all corrections, the complete automated test suite was executed:
```bash
pytest -v tests
```
Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Task\chat
configfile: pyproject.toml
collected 28 items

tests/test_benchmark_loader.py::test_load_sample_benchmark PASSED        [  3%]
tests/test_benchmark_loader.py::test_load_benchmark_with_filter PASSED   [  7%]
tests/test_benchmark_loader.py::test_load_benchmark_with_invalid_filter_raises_error PASSED [ 10%]
tests/test_benchmark_loader.py::test_load_nonexistent_benchmark_file_raises_error PASSED [ 14%]
tests/test_comparator.py::test_compare_task_outcome_improved PASSED      [ 17%]
tests/test_comparator.py::test_compare_task_outcome_regressed PASSED     [ 21%]
tests/test_comparator.py::test_aggregate_metrics_calculation PASSED      [ 25%]
tests/test_comparator.py::test_empty_runs_aggregate PASSED               [ 28%]
tests/test_decision_logic.py::test_decision_positive PASSED              [ 32%]
tests/test_decision_logic.py::test_decision_inconclusive_due_to_cost_tradeoff PASSED [ 35%]
tests/test_decision_logic.py::test_decision_inconclusive_due_to_small_sample PASSED [ 39%]
tests/test_decision_logic.py::test_decision_inconclusive_due_to_regressions PASSED [ 42%]
tests/test_decision_logic.py::test_decision_negative_on_degradation PASSED [ 46%]
tests/test_e2e_cli.py::test_cli_diff_command PASSED                      [ 50%]
tests/test_e2e_cli.py::test_cli_evaluate_and_inspect_command PASSED      [ 53%]
tests/test_e2e_cli.py::test_cli_invalid_task_filter PASSED               [ 57%]
tests/test_evaluation_dimensions.py::test_correctness_with_holdout PASSED [ 60%]
tests/test_evaluation_dimensions.py::test_correctness_without_holdout PASSED [ 64%]
tests/test_evaluation_dimensions.py::test_requirement_satisfaction PASSED [ 67%]
tests/test_evaluation_dimensions.py::test_convention_compliance_deductions PASSED [ 71%]
tests/test_evaluation_dimensions.py::test_empty_metrics_edge_case PASSED [ 75%]
tests/test_harness_diff.py::test_harness_diff_detection PASSED           [ 78%]
tests/test_harness_loader.py::test_load_baseline_harness PASSED          [ 82%]
tests/test_harness_loader.py::test_load_candidate_harness PASSED         [ 85%]
tests/test_harness_loader.py::test_load_nonexistent_harness_raises_error PASSED [ 89%]
tests/test_reporting.py::test_export_reports PASSED                      [ 92%]
tests/test_runners.py::test_mock_runner_deterministic_run PASSED         [ 96%]
tests/test_runners.py::test_real_runner_missing_environment_fails_safely PASSED [100%]

============================= 28 passed in 4.79s ==============================
```
