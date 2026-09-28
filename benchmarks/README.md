# Benchmarks Directory & Task Specification Guide

The `benchmarks/` directory houses the benchmark suites used by `harness-eval` to evaluate and compare coding-agent harnesses under identical, reproducible conditions.

---

## 1. Overview & Directory Structure

```text
benchmarks/
└── sample/
    └── tasks.yaml        # Standard 6-task benchmark suite for sample_project
```

A benchmark suite defines a collection of realistic software engineering tasks against a target repository (e.g., [`sample_project/`](file:///d:/Task/chat/sample_project)). Each task contains explicit problem descriptions, targeted files, weighted acceptance criteria, visible unit tests, and **private holdout tests**.

---

## 2. Benchmark Task Specification Schema (`tasks.yaml`)

Every benchmark suite is a YAML document containing top-level suite metadata and an array of individual task definitions:

```yaml
benchmark_name: sample_project_benchmark
version: "1.0.0"
project_path: sample_project
tasks:
  - id: task-01
    title: Add pagination to users API
    description: |
      Update UserService.list_users in app/users.py to support optional pagination.
      Accept optional `page: int = 1` and `page_size: Optional[int] = None`.
      When page_size is provided, return a dict with:
      {"items": [...], "total": count, "page": page, "page_size": page_size, "total_pages": pages}.
      When page_size is None or omitted, maintain backward compatibility by returning the plain List[Dict[str, Any]].
    target_files:
      - app/users.py
    acceptance_criteria:
      - id: AC-01-1
        description: "Supports optional page_size and page parameters in list_users"
        weight: 1.0
      - id: AC-01-2
        description: "Returns paginated dictionary payload when page_size is specified"
        weight: 1.0
      - id: AC-01-3
        description: "Preserves backward compatibility: returns list when page_size is None"
        weight: 1.0
    evaluation:
      unit_tests:
        - "tests/test_users.py"
      holdout_tests:
        - "eval_tests/test_pagination_holdout.py"
      lint_checks:
        require_type_hints: true
        forbidden_patterns:
          - "TODO"
          - "pass"
      timeout_seconds: 30
```

### Schema Field Reference

| Field | Type | Description |
| :--- | :--- | :--- |
| `benchmark_name` | `string` | Unique identifier for the benchmark suite. |
| `version` | `string` | Benchmark specification version (e.g., `1.0.0`). |
| `project_path` | `string` | Relative path to the target codebase under evaluation. |
| `tasks` | `list` | List of task definitions executed during the evaluation run. |
| `tasks[].id` | `string` | Unique task ID (e.g., `task-01`, `task-02`). Used in `--task` filtering and `inspect`. |
| `tasks[].title` | `string` | Human-readable title of the task. |
| `tasks[].description` | `string` | Task instructions and constraints presented to the coding agent. |
| `tasks[].target_files` | `list[string]` | Relative paths to files the agent is expected to inspect or modify. |
| `tasks[].acceptance_criteria`| `list[object]` | Structured criteria items with `id`, `description`, and numerical `weight`. |
| `tasks[].evaluation.unit_tests` | `list[string]` | Repository unit tests visible to the agent or run as standard verification. |
| `tasks[].evaluation.holdout_tests` | `list[string]` | Private invariant tests hidden from agent prompt context. |
| `tasks[].evaluation.lint_checks` | `object` | Static compliance constraints (`require_type_hints`, `forbidden_patterns`). |
| `tasks[].evaluation.timeout_seconds` | `int` | Maximum execution time in seconds allowed per run (default: 30s). |

---

## 3. The Holdout Testing Philosophy

Standard coding agent benchmarks are susceptible to **test overfitting and gaming**:
1. An agent can patch code just enough to satisfy the assertions in `tests/test_users.py`.
2. In doing so, it may introduce regressions or break subtle unasserted system contracts (e.g., breaking backward compatibility for existing callers).

To combat this, `harness-eval` enforces **Holdout Verification**:
- **Visible Unit Tests (`tests/`)**: Standard tests that may be inspected or executed during development.
- **Private Holdout Tests (`eval_tests/`)**: Independent test suites kept outside the visible prompt context of the agent.

### Correctness Weighting Formula

Correctness is evaluated using a **40% / 60% split**:

$$\text{Correctness Score} = \begin{cases} (U \times 0.40) + (H \times 0.60) & \text{if } H_{\text{total}} > 0 \\ U & \text{if } H_{\text{total}} = 0 \end{cases}$$

Where $U$ is the unit test pass rate and $H$ is the holdout test pass rate. If an agent passes all visible unit tests but fails the private holdout test, its maximum correctness score is capped at **40.0%**.

---

## 4. Sample Benchmark Tasks (Tasks 01–06)

The standard sample benchmark suite ([`benchmarks/sample/tasks.yaml`](file:///d:/Task/chat/benchmarks/sample/tasks.yaml)) includes 6 diverse software maintenance and feature tasks against [`sample_project`](file:///d:/Task/chat/sample_project):

| Task ID | Task Title | Target Files | Primary Focus & Holdout Assertions |
| :--- | :--- | :--- | :--- |
| `task-01` | Add pagination to users API | `app/users.py` | Validates pagination parameter handling and backward-compatible list returns when `page_size=None`. |
| `task-02` | Fix order total calculation bug | `app/orders.py` | Fixes subtotal discount sign bug (`+` vs `-`) and applies tax on post-discount subtotal. |
| `task-03` | Add duplicate email validation | `app/users.py` | Adds duplicate check on user creation, raising `ValueError` and preserving database integrity. |
| `task-04` | Add auth service unit tests | `tests/test_auth.py` | Exercises password hashing, JWT token generation, and holdout edge cases (token expiry, invalid secret). |
| `task-05` | Refactor db transaction helper | `app/database.py` | Implements an atomic context manager rolling back state on exceptions. |
| `task-06` | Add phone_number field | `app/users.py` | Adds optional phone number validation and storage without breaking existing user serialization. |

---

## 5. Adding a Custom Benchmark Suite

To define your own benchmark suite:

1. Create a subdirectory under `benchmarks/` (e.g., `benchmarks/production_service/`).
2. Add your task definitions YAML file (e.g., `tasks.yaml`).
3. Ensure your target repository contains both visible unit tests (`tests/`) and holdout verification suites (`eval_tests/`).
4. Execute `harness-eval` pointing to your custom benchmark:

```bash
harness-eval evaluate \
  --baseline harnesses/baseline \
  --candidate harnesses/candidate \
  --tasks benchmarks/production_service/tasks.yaml \
  --output reports/production_run
```

You can also filter to run a single task:

```bash
harness-eval evaluate \
  --tasks benchmarks/sample/tasks.yaml \
  --task task-01 \
  --output reports/task01_debug
```

For more details, see the main [Technical Documentation](file:///d:/Task/chat/docs/Project_Documentation.md).
