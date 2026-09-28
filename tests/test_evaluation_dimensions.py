"""Tests for individual evaluation dimensions."""
from harness_eval.evaluation.dimensions import (
    compute_task_convention_compliance,
    compute_task_correctness,
    compute_task_requirement_satisfaction,
)
from harness_eval.models import (
    CriterionResult,
    LintResult,
    RunResult,
    RunStatus,
    TestSuiteResult,
)


def test_correctness_with_holdout():
    run = RunResult(
        task_id="t1",
        harness_id="test",
        status=RunStatus.SUCCESS,
        unit_test_result=TestSuiteResult(total=10, passed=10, failed=0, pass_rate=1.0),
        holdout_test_result=TestSuiteResult(total=2, passed=1, failed=1, pass_rate=0.5),
    )
    # 1.0 * 0.40 + 0.5 * 0.60 = 0.70
    score = compute_task_correctness(run)
    assert score == 0.70


def test_correctness_without_holdout():
    run = RunResult(
        task_id="t1",
        harness_id="test",
        status=RunStatus.SUCCESS,
        unit_test_result=TestSuiteResult(total=5, passed=4, failed=1, pass_rate=0.8),
        holdout_test_result=TestSuiteResult(total=0, passed=0, failed=0, pass_rate=0.0),
    )
    score = compute_task_correctness(run)
    assert score == 0.80


def test_requirement_satisfaction():
    run = RunResult(
        task_id="t1",
        harness_id="test",
        status=RunStatus.SUCCESS,
        criteria_results=[
            CriterionResult(criterion_id="c1", description="desc", passed=True, score=1.5, max_score=1.5),
            CriterionResult(criterion_id="c2", description="desc", passed=False, score=0.0, max_score=1.0),
        ],
    )
    # 1.5 / 2.5 = 0.60
    score = compute_task_requirement_satisfaction(run)
    assert score == 0.60


def test_convention_compliance_deductions():
    clean_run = RunResult(
        task_id="t1",
        harness_id="test",
        status=RunStatus.SUCCESS,
        lint_result=LintResult(passed=True, violations_count=0),
    )
    assert compute_task_convention_compliance(clean_run) == 1.0

    dirty_run = RunResult(
        task_id="t1",
        harness_id="test",
        status=RunStatus.SUCCESS,
        lint_result=LintResult(passed=False, violations_count=2, issues=["err1", "err2"]),
    )
    # 1.0 - (2 * 0.25) = 0.50
    assert compute_task_convention_compliance(dirty_run) == 0.50


def test_empty_metrics_edge_case():
    empty_run = RunResult(
        task_id="empty",
        harness_id="test",
        status=RunStatus.FAILED,
    )
    assert compute_task_correctness(empty_run) == 0.0
    assert compute_task_requirement_satisfaction(empty_run) == 0.0
    assert compute_task_convention_compliance(empty_run) == 1.0
