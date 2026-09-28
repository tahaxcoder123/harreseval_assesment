# Test Suite Architecture (`tests/`)

The `tests/` directory contains automated unit, integration, and end-to-end tests for the `harness-eval` evaluation framework.

---

## 1. Directory Structure & Coverage Matrix

The suite consists of **28 automated tests** spanning 9 test modules:

```text
tests/
├── test_benchmark_loader.py         # 4 tests: YAML parsing, filtering, error handling
├── test_comparator.py               # 4 tests: Task comparisons, deltas, aggregate metrics
├── test_decision_logic.py           # 5 tests: POSITIVE, NEGATIVE, trade-offs, regressions
├── test_e2e_cli.py                  # 3 tests: Full CLI execution (evaluate, inspect, diff)
├── test_evaluation_dimensions.py    # 5 tests: 40/60 holdout weighting, criteria, lint
├── test_harness_diff.py             # 1 test : Configuration structural diff detection
├── test_harness_loader.py           # 3 tests: Baseline/candidate YAML loading & validation
├── test_reporting.py                # 1 test : JSON, HTML, and summary artifact export
└── test_runners.py                  # 2 tests: MockRunner determinism & RealRunner error handling
```

### Test Case Breakdown

| Module | Tested Scope | Key Invariants Asserted |
| :--- | :--- | :--- |
| `test_benchmark_loader.py` | Benchmark suite loading & task filtering | Validates tasks YAML parsing, filtering by `--task`, and raises `ValueError` on nonexistent task IDs. |
| `test_comparator.py` | Single-task & aggregate metric comparisons | Verifies `TaskOutcome.IMPROVED`, `TaskOutcome.REGRESSED`, absolute and percentage delta math. |
| `test_decision_logic.py` | Rule-based decision engine | Enforces zero regressions, checks cost increase threshold (>60%), small-sample size guardrail ($N < 10$), and degradation detection. |
| `test_e2e_cli.py` | Subprocess CLI execution | Executes `harness-eval diff`, `evaluate`, and `inspect` end-to-end against sample benchmarks. |
| `test_evaluation_dimensions.py` | Multi-dimensional scoring | Validates the 40% unit + 60% holdout test correctness formula, weighted criteria scoring, and lint deductions. |
| `test_harness_diff.py` | Harness structural comparison | Checks added/removed skills, tools, hooks, and model changes. |
| `test_harness_loader.py` | Harness configuration parsing | Validates YAML parsing into `HarnessConfig` and handles missing directories gracefully. |
| `test_reporting.py` | Artifact generation | Confirms `report.html`, `report.json`, and `summary.json` are generated with valid data. |
| `test_runners.py` | Runner layer execution | Confirms `MockRunner` produces identical results given identical random seeds, and `RealAgentRunner` fails safely when environment variables are missing. |

---

## 2. Running Tests

### Running the Full Test Suite
Ensure the package is installed in editable mode (`pip install -e .`), then run:

```bash
pytest -v tests
```

### Running a Specific Test Module
```bash
pytest -v tests/test_decision_logic.py
```

### Running with Windows PowerShell
If running in PowerShell without an active virtual environment, explicitly set the Python path:

```powershell
$env:PYTHONPATH="src"
python -m pytest -v tests
```

---

## 3. Critical Invariants to Preserve

1. **`TestSuiteResult.__test__ = False`**:
   In `src/harness_eval/models.py`, `TestSuiteResult` has `__test__ = False` set to prevent pytest from attempting to discover and execute it as a test class.
2. **Deterministic Mock Testing**:
   Tests must run completely offline without external LLM API keys or internet access.
3. **Defensive Verdicts**:
   Tests in `test_decision_logic.py` ensure `POSITIVE` verdicts are impossible when regressions are present or when trade-offs are significant.

For further reference, consult the [Technical Documentation](file:///d:/Task/chat/docs/Project_Documentation.md).
