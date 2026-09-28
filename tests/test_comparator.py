"""Tests for baseline vs candidate comparator."""
from harness_eval.benchmarks.loader import load_benchmark
from harness_eval.evaluation.comparator import (
    compare_task_runs,
    compute_aggregate_metrics,
    compute_metric_deltas,
)
from harness_eval.models import (
    RunResult,
    RunStatus,
    TaskOutcome,
    TestSuiteResult,
)


def test_compare_task_outcome_improved():
    suite = load_benchmark("benchmarks/sample/tasks.yaml", task_filter="task-01")
    task = suite.tasks[0]

    b_run = RunResult(
        task_id=task.id,
        harness_id="baseline",
        status=RunStatus.FAILED,
        unit_test_result=TestSuiteResult(total=2, passed=2, pass_rate=1.0),
        holdout_test_result=TestSuiteResult(total=1, passed=0, failed=1, pass_rate=0.0),
    )
    c_run = RunResult(
        task_id=task.id,
        harness_id="candidate",
        status=RunStatus.SUCCESS,
        unit_test_result=TestSuiteResult(total=2, passed=2, pass_rate=1.0),
        holdout_test_result=TestSuiteResult(total=1, passed=1, pass_rate=1.0),
    )

    comparison = compare_task_runs(task, b_run, c_run)
    assert comparison.outcome == TaskOutcome.IMPROVED
    assert comparison.correctness_delta > 0
    assert len(comparison.evidence_points) > 0


def test_compare_task_outcome_regressed():
    suite = load_benchmark("benchmarks/sample/tasks.yaml", task_filter="task-01")
    task = suite.tasks[0]

    b_run = RunResult(
        task_id=task.id,
        harness_id="baseline",
        status=RunStatus.SUCCESS,
        unit_test_result=TestSuiteResult(total=2, passed=2, pass_rate=1.0),
        holdout_test_result=TestSuiteResult(total=1, passed=1, pass_rate=1.0),
    )
    c_run = RunResult(
        task_id=task.id,
        harness_id="candidate",
        status=RunStatus.FAILED,
        unit_test_result=TestSuiteResult(total=2, passed=1, failed=1, pass_rate=0.5),
        holdout_test_result=TestSuiteResult(total=1, passed=0, failed=1, pass_rate=0.0),
    )

    comparison = compare_task_runs(task, b_run, c_run)
    assert comparison.outcome == TaskOutcome.REGRESSED
    assert comparison.correctness_delta < 0


def test_aggregate_metrics_calculation():
    runs = [
        RunResult(
            task_id="t1",
            harness_id="test",
            status=RunStatus.SUCCESS,
            runtime_seconds=10.0,
            estimated_cost=0.05,
            total_tokens=1000,
            unit_test_result=TestSuiteResult(total=2, passed=2, pass_rate=1.0),
        ),
        RunResult(
            task_id="t2",
            harness_id="test",
            status=RunStatus.FAILED,
            runtime_seconds=20.0,
            estimated_cost=0.07,
            total_tokens=1500,
            unit_test_result=TestSuiteResult(total=2, passed=0, failed=2, pass_rate=0.0),
        ),
    ]

    agg = compute_aggregate_metrics(runs)
    assert agg.total_tasks == 2
    assert agg.pass_rate == 0.5
    assert agg.average_runtime == 15.0
    assert agg.average_cost == 0.06
    assert agg.total_tokens == 2500


def test_empty_runs_aggregate():
    agg = compute_aggregate_metrics([])
    assert agg.total_tasks == 0
    assert agg.pass_rate == 0.0
