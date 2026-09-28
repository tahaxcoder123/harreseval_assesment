"""Evaluation metrics across the core evaluation dimensions."""
from typing import List
from harness_eval.models import RunResult


def compute_task_correctness(run: RunResult) -> float:
    """Computes a 0.0 - 1.0 correctness score balancing unit and holdout verification."""
    unit = run.unit_test_result
    holdout = run.holdout_test_result

    unit_rate = unit.pass_rate if unit.total > 0 else (1.0 if run.status.value == "SUCCESS" else 0.0)

    if holdout.total > 0:
        holdout_rate = holdout.pass_rate
        # Holdout tests carry 60% weight to guard against overfitting to visible unit tests
        return round((unit_rate * 0.40) + (holdout_rate * 0.60), 4)
    return round(unit_rate, 4)


def compute_task_requirement_satisfaction(run: RunResult) -> float:
    """Computes requirement satisfaction score based on task acceptance criteria."""
    if not run.criteria_results:
        return 1.0 if run.status.value == "SUCCESS" else 0.0

    total_possible = sum(c.max_score for c in run.criteria_results)
    if total_possible <= 0.0:
        return 1.0 if run.status.value == "SUCCESS" else 0.0

    total_earned = sum(c.score for c in run.criteria_results)
    return round(min(1.0, max(0.0, total_earned / total_possible)), 4)


def compute_task_convention_compliance(run: RunResult) -> float:
    """Computes code quality / convention compliance score (0.0 to 1.0)."""
    if run.lint_result.passed and run.lint_result.violations_count == 0:
        return 1.0
    violations = run.lint_result.violations_count
    # Deduct 0.25 per violation down to 0.0 minimum
    return max(0.0, round(1.0 - (violations * 0.25), 4))
