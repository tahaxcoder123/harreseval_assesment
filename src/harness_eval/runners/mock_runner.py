"""Realistic, deterministic mock runner for evaluating harness changes without external LLM APIs."""
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Optional
from harness_eval.models import (
    BenchmarkTask,
    CriterionResult,
    HarnessConfig,
    LintResult,
    RunResult,
    RunStatus,
    TestSuiteResult,
)
from harness_eval.runners.base import AgentRunner


# Curated realistic diffs and test logs per task and harness
DIFF_TEMPLATES: Dict[str, Dict[str, str]] = {
    "task-01": {
        "baseline": (
            "--- a/app/users.py\n"
            "+++ b/app/users.py\n"
            "@@ -18,2 +18,6 @@\n"
            "-    def list_users(self) -> List[Dict[str, Any]]:\n"
            "-        return self.db.find_all('users')\n"
            "+    def list_users(self, page=1, page_size=None):\n"
            "+        users = self.db.find_all('users')\n"
            "+        # Partial pagination: fails when page_size is None or out of bounds\n"
            "+        start = (page - 1) * page_size if page_size else 0\n"
            "+        return users[start:start + page_size] if page_size else users\n"
        ),
        "candidate": (
            "--- a/app/users.py\n"
            "+++ b/app/users.py\n"
            "@@ -18,2 +18,17 @@\n"
            "-    def list_users(self) -> List[Dict[str, Any]]:\n"
            "-        return self.db.find_all('users')\n"
            "+    def list_users(self, page: int = 1, page_size: Optional[int] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:\n"
            "+        all_users = self.db.find_all('users')\n"
            "+        if page_size is None:\n"
            "+            return all_users\n"
            "+        total = len(all_users)\n"
            "+        total_pages = max(1, (total + page_size - 1) // page_size)\n"
            "+        start = max(0, (page - 1) * page_size)\n"
            "+        items = all_users[start:start + page_size]\n"
            "+        return {\n"
            "+            'items': items,\n"
            "+            'total': total,\n"
            "+            'page': page,\n"
            "+            'page_size': page_size,\n"
            "+            'total_pages': total_pages,\n"
            "+        }\n"
        ),
    },
    "task-02": {
        "baseline": (
            "--- a/app/orders.py\n"
            "+++ b/app/orders.py\n"
            "@@ -25,2 +25,3 @@\n"
            "-        total = round(subtotal + discount_amount + tax_amount, 2)\n"
            "+        # Attempted fix, but still applied tax before discount deduction\n"
            "+        total = round(subtotal - discount_amount + (subtotal * tax_rate), 2)\n"
        ),
        "candidate": (
            "--- a/app/orders.py\n"
            "+++ b/app/orders.py\n"
            "@@ -21,5 +21,4 @@\n"
            "         discount_amount = subtotal * discount_rate\n"
            "         taxable_amount = max(0.0, subtotal - discount_amount)\n"
            "         tax_amount = round(taxable_amount * tax_rate, 2)\n"
            "-        total = round(subtotal + discount_amount + tax_amount, 2)\n"
            "+        total = round(taxable_amount + tax_amount, 2)\n"
        ),
    },
    "task-03": {
        "baseline": (
            "--- a/app/users.py\n"
            "+++ b/app/users.py\n"
            "@@ -10,2 +10,5 @@\n"
            "+        # Case-sensitive check only (misses uppercase duplicate)\n"
            "+        for u in self.db.find_all('users'):\n"
            "+            if u.get('email') == email:\n"
            "+                raise ValueError('Email already registered')\n"
        ),
        "candidate": (
            "--- a/app/users.py\n"
            "+++ b/app/users.py\n"
            "@@ -10,2 +10,6 @@\n"
            "+        normalized_email = email.strip().lower()\n"
            "+        for u in self.db.find_all('users'):\n"
            "+            if str(u.get('email', '')).lower() == normalized_email:\n"
            "+                raise ValueError('Email already registered')\n"
        ),
    },
    "task-04": {
        "baseline": (
            "--- /dev/null\n"
            "+++ b/tests/test_auth.py\n"
            "@@ -0,0 +1,12 @@\n"
            "+import pytest\n"
            "+from app.auth import AuthService\n"
            "+\n"
            "+def test_hash_password():\n"
            "+    svc = AuthService()\n"
            "+    h = svc.hash_password('secret')\n"
            "+    assert len(h) == 64\n"
        ),
        "candidate": (
            "--- /dev/null\n"
            "+++ b/tests/test_auth.py\n"
            "@@ -0,0 +1,32 @@\n"
            "+import pytest\n"
            "+from app.auth import AuthService\n"
            "+\n"
            "+def test_hash_password():\n"
            "+    svc = AuthService()\n"
            "+    h1 = svc.hash_password('secret', 'salt1')\n"
            "+    h2 = svc.hash_password('secret', 'salt2')\n"
            "+    assert h1 != h2\n"
            "+\n"
            "+def test_generate_and_validate_token():\n"
            "+    svc = AuthService()\n"
            "+    tok = svc.generate_token('usr-123')\n"
            "+    assert svc.validate_token(tok) == 'usr-123'\n"
            "+\n"
            "+def test_token_expiration_and_revocation():\n"
            "+    svc = AuthService(token_ttl_seconds=0)\n"
            "+    tok = svc.generate_token('usr-999')\n"
            "+    assert svc.validate_token(tok) is None\n"
            "+    svc.revoke_token(tok)\n"
        ),
    },
    "task-05": {
        "baseline": (
            "--- a/app/database.py\n"
            "+++ b/app/database.py\n"
            "@@ -40,2 +40,7 @@\n"
            "+    from contextlib import contextmanager\n"
            "+    @contextmanager\n"
            "+    def transaction(self):\n"
            "+        self.begin()\n"
            "+        yield self\n"
            "+        self.commit()\n"
        ),
        "candidate": (
            "--- a/app/database.py\n"
            "+++ b/app/database.py\n"
            "@@ -40,2 +40,13 @@\n"
            "+    from contextlib import contextmanager\n"
            "+    @contextmanager\n"
            "+    def transaction(self):\n"
            "+        self.begin()\n"
            "+        try:\n"
            "+            yield self\n"
            "+            self.commit()\n"
            "+        except Exception:\n"
            "+            self.rollback()\n"
            "+            raise\n"
        ),
    },
    "task-06": {
        "baseline": (
            "--- a/app/users.py\n"
            "+++ b/app/users.py\n"
            "@@ -10,2 +10,4 @@\n"
            "+        # Missing length check validation\n"
            "+        if 'phone_number' in extra:\n"
            "+            payload['phone_number'] = str(extra['phone_number'])\n"
        ),
        "candidate": (
            "--- a/app/users.py\n"
            "+++ b/app/users.py\n"
            "@@ -8,2 +8,9 @@\n"
            "+    def create_user(self, user_id: str, email: str, name: str, phone_number: Optional[str] = None, **extra: Any) -> Dict[str, Any]:\n"
            "+        if phone_number is not None:\n"
            "+            cleaned = phone_number.strip()\n"
            "+            if len(cleaned) < 7 or len(cleaned) > 15:\n"
            "+                raise ValueError('Invalid phone number format')\n"
            "+            extra['phone_number'] = cleaned\n"
        ),
    },
}


class MockRunner(AgentRunner):
    """Generates realistic, reproducible evaluation outcomes for harness comparison."""

    def __init__(self, variance: float = 0.05) -> None:
        self.variance = variance

    def run(
        self,
        task: BenchmarkTask,
        harness: HarnessConfig,
        project_dir: Path,
        iteration: int = 1,
        seed: Optional[int] = None,
    ) -> RunResult:
        # Deterministic seed per task, harness, seed, and repetition
        effective_seed = seed if seed is not None else 42
        seed_hash = int(hashlib.md5(f"{task.id}:{harness.name}:{iteration}:{effective_seed}".encode()).hexdigest(), 16) % (2**31)
        rng = random.Random(seed_hash)

        is_candidate = "candidate" in harness.name.lower()

        # Token usage and runtime simulation
        base_input_tokens = 2200 + (len(task.description) * 3) + (len(harness.skills) * 450)
        base_output_tokens = 600 + (len(task.acceptance_criteria) * 180)
        
        # Candidate uses slightly more tokens due to skills and multi-turn verification, but produces more accurate code
        if is_candidate:
            input_tokens = int(base_input_tokens * (1.25 + rng.uniform(-0.05, 0.05)))
            output_tokens = int(base_output_tokens * (1.10 + rng.uniform(-0.05, 0.05)))
            runtime_seconds = round(14.0 + (task.evaluation.timeout_seconds * 0.2) + rng.uniform(-1.5, 2.0), 2)
        else:
            input_tokens = int(base_input_tokens * (1.0 + rng.uniform(-0.05, 0.05)))
            output_tokens = int(base_output_tokens * (1.0 + rng.uniform(-0.05, 0.05)))
            runtime_seconds = round(11.0 + (task.evaluation.timeout_seconds * 0.15) + rng.uniform(-1.0, 1.5), 2)

        total_tokens = input_tokens + output_tokens
        cost = (input_tokens / 1000.0) * harness.cost_per_1k_input + (output_tokens / 1000.0) * harness.cost_per_1k_output
        estimated_cost = round(cost, 5)

        # Retrieve diff template
        task_diffs = DIFF_TEMPLATES.get(task.id, {})
        diff_key = "candidate" if is_candidate else "baseline"
        generated_changes = task_diffs.get(diff_key, f"# Changes for {task.id} under {harness.name}")

        # Determine task results based on benchmark scenario
        # In this realistic scenario:
        # - task-01: Baseline passes basic unit test (2/2) but fails holdout (returns list instead of dict when paginated)
        #            Candidate passes unit (2/2) and holdout (1/1)
        # - task-02: Baseline fixes order total incorrectly (subtotal - discount + tax on subtotal). Fails holdout.
        #            Candidate correctly fixes calculation. Passes unit & holdout.
        # - task-03: Baseline fails case-insensitive duplicate check in holdout. Candidate passes.
        # - task-04: Baseline creates only 1 test, missing token expiration. Candidate creates 3 full tests.
        # - task-05: Baseline implements context manager without exception rollback (fails holdout). Candidate passes.
        # - task-06: Baseline adds field but misses length validator. Candidate validates properly.

        # Let's add slight variance for repetitions if variance enabled
        fail_prob_candidate = 0.05 if iteration > 1 else 0.0
        fail_prob_baseline = 0.50

        # Criteria results
        criteria_results: List[CriterionResult] = []
        for i, crit in enumerate(task.acceptance_criteria):
            if is_candidate:
                passed = rng.random() > fail_prob_candidate
                reason = "Criterion satisfied by candidate implementation" if passed else "Simulated edge-case failure on repetition"
            else:
                # Baseline passes first criterion, often fails subsequent complex criteria
                passed = (i == 0) and (rng.random() > 0.20)
                reason = "Verified baseline functionality" if passed else "Baseline implementation omitted secondary requirement"

            score = crit.weight if passed else 0.0
            criteria_results.append(CriterionResult(
                criterion_id=crit.id,
                description=crit.description,
                passed=passed,
                score=score,
                max_score=crit.weight,
                reason=reason,
            ))

        # Unit test results
        unit_total = len(task.evaluation.unit_tests) * 2
        if is_candidate:
            unit_passed = unit_total
            unit_failed = 0
            unit_failures = []
        else:
            # Baseline passes most basic unit tests
            unit_passed = max(1, unit_total - (1 if task.id == "task-02" else 0))
            unit_failed = unit_total - unit_passed
            unit_failures = ["AssertionError: total mismatch"] if unit_failed > 0 else []

        unit_test_result = TestSuiteResult(
            total=unit_total,
            passed=unit_passed,
            failed=unit_failed,
            errors=0,
            pass_rate=round(unit_passed / max(1, unit_total), 2),
            failures=unit_failures,
            stdout=f"pytest {task.evaluation.unit_tests}: {unit_passed} passed, {unit_failed} failed",
        )

        # Holdout test results
        holdout_total = len(task.evaluation.holdout_tests)
        if is_candidate:
            holdout_passed = holdout_total
            holdout_failed = 0
            holdout_failures = []
        else:
            # Baseline fails holdout tests on tasks 1, 2, 3, 5, 6
            holdout_passed = 0
            holdout_failed = holdout_total
            holdout_failures = [f"AssertionError in {task.evaluation.holdout_tests[0]}"]

        holdout_test_result = TestSuiteResult(
            total=holdout_total,
            passed=holdout_passed,
            failed=holdout_failed,
            errors=0,
            pass_rate=round(holdout_passed / max(1, holdout_total), 2),
            failures=holdout_failures,
            stdout=f"holdout evaluation: {holdout_passed} passed, {holdout_failed} failed",
        )

        # Linting / Code Quality results
        lint_issues: List[str] = []
        if not is_candidate:
            if task.evaluation.lint_checks.get("require_type_hints", False):
                lint_issues.append("Missing explicit type annotations on public function parameters")
            if task.id == "task-01":
                lint_issues.append("Code style: inconsistent return type (Union without annotation)")
        else:
            # Candidate passes linting due to strict-typing and pre-commit hook
            lint_issues = []

        lint_result = LintResult(
            passed=(len(lint_issues) == 0),
            issues=lint_issues,
            violations_count=len(lint_issues),
        )

        # Overall task status
        is_success = (holdout_test_result.failed == 0) and (unit_test_result.failed == 0)
        status = RunStatus.SUCCESS if is_success else RunStatus.FAILED

        return RunResult(
            task_id=task.id,
            harness_id=harness.name,
            status=status,
            generated_changes=generated_changes,
            files_modified=task.target_files,
            unit_test_result=unit_test_result,
            holdout_test_result=holdout_test_result,
            criteria_results=criteria_results,
            lint_result=lint_result,
            runtime_seconds=runtime_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            error=None if is_success else "Holdout verification failed",
            stdout=f"Executed task {task.id} with {harness.name}\nTests: {unit_passed}/{unit_total} unit, {holdout_passed}/{holdout_total} holdout",
            stderr="",
            is_mock=True,
            seed=seed,
            iteration=iteration,
        )
