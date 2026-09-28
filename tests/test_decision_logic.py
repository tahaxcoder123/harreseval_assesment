"""Tests for transparent decision logic and trade-off detection."""
from harness_eval.config import DecisionPolicy
from harness_eval.evaluation.decision import evaluate_decision
from harness_eval.models import (
    AggregateMetrics,
    DecisionOutcome,
    RunResult,
    RunStatus,
    StatisticalSummary,
    TaskComparison,
    TaskOutcome,
)


def make_task_comp(task_id: str, outcome: TaskOutcome) -> TaskComparison:
    dummy_run = RunResult(task_id=task_id, harness_id="dummy", status=RunStatus.SUCCESS)
    return TaskComparison(
        task_id=task_id,
        title=f"Task {task_id}",
        baseline_run=dummy_run,
        candidate_run=dummy_run,
        outcome=outcome,
        correctness_delta=0.2 if outcome == TaskOutcome.IMPROVED else (-0.2 if outcome == TaskOutcome.REGRESSED else 0.0),
        requirement_delta=0.0,
        lint_delta=0,
        cost_delta=0.01,
        runtime_delta=1.0,
        explanation="test",
    )


def test_decision_positive():
    policy = DecisionPolicy(min_sample_size_for_certainty=5, max_cost_increase_pct=50.0)
    baseline = AggregateMetrics(correctness_rate=0.60, average_cost=0.05, average_runtime=10.0)
    candidate = AggregateMetrics(correctness_rate=0.85, average_cost=0.06, average_runtime=11.0)
    stats = StatisticalSummary(sample_size=10, repetitions=2)
    comparisons = [make_task_comp(f"t{i}", TaskOutcome.IMPROVED) for i in range(5)]

    dec = evaluate_decision(baseline, candidate, [], comparisons, stats, policy)
    assert dec.outcome == DecisionOutcome.POSITIVE
    assert "RULE_CLEAR_POSITIVE" in dec.rules_triggered


def test_decision_inconclusive_due_to_cost_tradeoff():
    policy = DecisionPolicy(min_sample_size_for_certainty=5, max_cost_increase_pct=50.0)
    baseline = AggregateMetrics(correctness_rate=0.60, average_cost=0.01, average_runtime=10.0)
    candidate = AggregateMetrics(correctness_rate=0.85, average_cost=0.04, average_runtime=11.0)  # +300% cost
    stats = StatisticalSummary(sample_size=10, repetitions=2)
    comparisons = [make_task_comp(f"t{i}", TaskOutcome.IMPROVED) for i in range(5)]

    dec = evaluate_decision(baseline, candidate, [], comparisons, stats, policy)
    assert dec.outcome == DecisionOutcome.INCONCLUSIVE
    assert "RULE_HIGH_COST_INCREASE" in dec.rules_triggered
    assert any("Cost increased" in t for t in dec.trade_offs)


def test_decision_inconclusive_due_to_small_sample():
    policy = DecisionPolicy(min_sample_size_for_certainty=10)
    baseline = AggregateMetrics(correctness_rate=0.60, average_cost=0.05, average_runtime=10.0)
    candidate = AggregateMetrics(correctness_rate=0.85, average_cost=0.06, average_runtime=11.0)
    stats = StatisticalSummary(sample_size=3, repetitions=1)  # Only 3 tasks
    comparisons = [make_task_comp(f"t{i}", TaskOutcome.IMPROVED) for i in range(3)]

    dec = evaluate_decision(baseline, candidate, [], comparisons, stats, policy)
    assert dec.outcome == DecisionOutcome.INCONCLUSIVE
    assert "RULE_SMALL_SAMPLE_SIZE" in dec.rules_triggered


def test_decision_inconclusive_due_to_regressions():
    policy = DecisionPolicy(max_tolerated_regressions=0)
    baseline = AggregateMetrics(correctness_rate=0.70, average_cost=0.05, average_runtime=10.0)
    candidate = AggregateMetrics(correctness_rate=0.80, average_cost=0.05, average_runtime=10.0)
    stats = StatisticalSummary(sample_size=12, repetitions=1)
    comparisons = [
        make_task_comp("t1", TaskOutcome.IMPROVED),
        make_task_comp("t2", TaskOutcome.IMPROVED),
        make_task_comp("t3", TaskOutcome.REGRESSED),  # 1 regression!
    ]

    dec = evaluate_decision(baseline, candidate, [], comparisons, stats, policy)
    assert dec.outcome == DecisionOutcome.INCONCLUSIVE
    assert "RULE_REGRESSION_DETECTED" in dec.rules_triggered


def test_decision_negative_on_degradation():
    policy = DecisionPolicy()
    baseline = AggregateMetrics(correctness_rate=0.80, average_cost=0.05, average_runtime=10.0)
    candidate = AggregateMetrics(correctness_rate=0.60, average_cost=0.05, average_runtime=10.0)
    stats = StatisticalSummary(sample_size=10, repetitions=1)
    comparisons = [make_task_comp(f"t{i}", TaskOutcome.REGRESSED) for i in range(5)]

    dec = evaluate_decision(baseline, candidate, [], comparisons, stats, policy)
    assert dec.outcome == DecisionOutcome.NEGATIVE
    assert "RULE_CORRECTNESS_DEGRADATION" in dec.rules_triggered
