# Sample Project (`sample_project`)

`sample_project` is a standalone, lightweight Python e-commerce and user management service used as the evaluation target codebase for `harness-eval` benchmarks.

---

## 1. Directory Structure

```text
sample_project/
├── pyproject.toml              # Build & pytest configuration for the target service
├── app/                        # Application source code under evaluation
│   ├── __init__.py
│   ├── auth.py                 # Authentication, password hashing, and JWT tokens
│   ├── database.py             # In-memory database with transaction support
│   ├── orders.py               # Order service with subtotal, discount, and tax calculations
│   └── users.py                # User service with pagination, search, and validation
├── tests/                      # Visible unit tests (accessible to agents during dev)
│   ├── test_orders.py
│   └── test_users.py
└── eval_tests/                 # Private holdout verification tests (NEVER exposed to prompts)
    ├── test_auth_coverage_holdout.py
    ├── test_database_refactor_holdout.py
    ├── test_duplicate_email_holdout.py
    ├── test_orders_holdout.py
    ├── test_pagination_holdout.py
    └── test_phone_field_holdout.py
```

---

## 2. Core Modules

| Module | Primary Class / Component | Responsibilities & Baseline Gaps |
| :--- | :--- | :--- |
| [`app/users.py`](file:///d:/Task/chat/sample_project/app/users.py) | `UserService` | User records, email validation, phone attributes, and pagination. Baseline code lacks pagination and duplicate email checks. |
| [`app/orders.py`](file:///d:/Task/chat/sample_project/app/orders.py) | `OrderService` | Order lifecycle and pricing. Baseline code contains an intentional calculation bug where discounts are added instead of subtracted. |
| [`app/database.py`](file:///d:/Task/chat/sample_project/app/database.py) | `Database` | Key-value data persistence with transactions. Baseline code lacks atomic rollback behavior on unhandled exceptions. |
| [`app/auth.py`](file:///d:/Task/chat/sample_project/app/auth.py) | `AuthService` | SHA-256 password hashing and JWT token handling. Baseline code lacks comprehensive test coverage. |

---

## 3. The Role of Private Holdout Tests (`eval_tests/`)

> [!IMPORTANT]
> **Holdout Test Isolation Rule**: Never expose holdout test files (`eval_tests/`) to the visible prompt context of a candidate agent harness.

Standard unit tests in `tests/` are visible to agents (or can be run by agents using pre-commit hooks or terminal tools). When an agent attempts a task, it might modify code until visible assertions pass, inadvertently breaking contracts or introducing regressions.

Holdout tests in `eval_tests/` are executed strictly during the evaluation phase to verify:
1. **Edge Case Invariants**: Invariants not asserted in standard unit tests.
2. **Backward Compatibility**: Contracts like returning a flat list when `page_size=None` (Task 01).
3. **True Robustness**: Resistance to test gaming or minimal-effort patching.

In `harness-eval`, correctness is calculated with **60% weight on holdout tests** and **40% on unit tests**:

$$\text{Correctness Score} = (0.40 \times \text{Unit Pass Rate}) + (0.60 \times \text{Holdout Pass Rate})$$

---

## 4. Benchmark Tasks Alignment

The sample project serves as the subject for the 6 benchmark tasks defined in [`benchmarks/sample/tasks.yaml`](file:///d:/Task/chat/benchmarks/sample/tasks.yaml):

1. **`task-01`**: Add pagination to `UserService.list_users` in `app/users.py`.
2. **`task-02`**: Fix discount addition bug in `OrderService.calculate_total` in `app/orders.py`.
3. **`task-03`**: Add duplicate email validation in `UserService.create_user` in `app/users.py`.
4. **`task-04`**: Add unit tests for `AuthService` in `tests/test_auth.py`.
5. **`task-05`**: Refactor atomic transaction rollback context manager in `app/database.py`.
6. **`task-06`**: Add optional `phone_number` field support in `app/users.py`.

---

## 5. Running Tests Locally

To run the unit tests directly within `sample_project`:

```bash
cd sample_project
pytest -v tests
```

To run both unit tests and holdout verification tests:

```bash
cd sample_project
pytest -v tests eval_tests
```

For more details on evaluation scoring and harness comparisons, refer to the [Main Documentation](file:///d:/Task/chat/docs/Project_Documentation.md).
