"""Transparent decision logic for evaluating harness comparisons."""
from typing import List
from harness_eval.config import DecisionPolicy, DEFAULT_POLICY
from harness_eval.models import (
    AggregateMetrics,
    DecisionOutcome,
    DecisionReport,
    MetricDelta,
    StatisticalSummary,
    TaskComparison,
    TaskOutcome,
)


def evaluate_decision(
    baseline: AggregateMetrics,
    candidate: AggregateMetrics,
    deltas: List[MetricDelta],
    comparisons: List[TaskComparison],
    statistics: StatisticalSummary,
    policy: DecisionPolicy = DEFAULT_POLICY,
) -> DecisionReport:
    """Computes a defensible POSITIVE, NEGATIVE, or INCONCLUSIVE verdict based on evidence."""
    rules_triggered: List[str] = []
    trade_offs: List[str] = []

    # 1. Count task-level regressions and improvements
    regressions = sum(1 for c in comparisons if c.outcome == TaskOutcome.REGRESSED)
    improvements = sum(1 for c in comparisons if c.outcome == TaskOutcome.IMPROVED)
    both_passed = sum(1 for c in comparisons if c.outcome == TaskOutcome.BOTH_PASSED)
    both_failed = sum(1 for c in comparisons if c.outcome == TaskOutcome.BOTH_FAILED)

    correctness_delta = candidate.correctness_rate - baseline.correctness_rate
    req_delta = candidate.requirement_satisfaction_rate - baseline.requirement_satisfaction_rate
    
    cost_increase_pct = 0.0
    if baseline.average_cost > 0:
        cost_increase_pct = ((candidate.average_cost - baseline.average_cost) / baseline.average_cost) * 100.0

    runtime_increase_pct = 0.0
    if baseline.average_runtime > 0:
        runtime_increase_pct = ((candidate.average_runtime - baseline.average_runtime) / baseline.average_runtime) * 100.0

    # Rule checks
    # Check A: Absolute degradation
    if correctness_delta < -0.02:
        rules_triggered.append("RULE_CORRECTNESS_DEGRADATION")
        justification = (
            f"Candidate reduced overall correctness by {abs(correctness_delta)*100:.1f} percentage points "
            f"({baseline.correctness_rate*100:.1f}% -> {candidate.correctness_rate*100:.1f}%)."
        )
        return DecisionReport(
            outcome=DecisionOutcome.NEGATIVE,
            summary_verdict="Candidate harness degrades overall agent correctness.",
            justification=justification,
            trade_offs=[f"Correctness dropped by {abs(correctness_delta)*100:.1f}pp"],
            rules_triggered=rules_triggered,
        )

    # Check B: Task regressions present
    if regressions > policy.max_tolerated_regressions:
        rules_triggered.append("RULE_REGRESSION_DETECTED")
        trade_offs.append(f"{regressions} task(s) regressed under candidate harness.")
        if correctness_delta <= 0:
            return DecisionReport(
                outcome=DecisionOutcome.NEGATIVE,
                summary_verdict="Candidate caused task regressions with no net correctness gain.",
                justification=f"Found {regressions} task regression(s) without offsetting correctness improvements.",
                trade_offs=trade_offs,
                rules_triggered=rules_triggered,
            )
        else:
            # Improvement on some tasks but regression on others -> classic INCONCLUSIVE
            rules_triggered.append("RULE_UNRESOLVED_REGRESSION_RISK")
            return DecisionReport(
                outcome=DecisionOutcome.INCONCLUSIVE,
                summary_verdict="Candidate shows improvement on some tasks but introduces regressions.",
                justification=(
                    f"Candidate improved {improvements} task(s) (+{correctness_delta*100:.1f}pp correctness), "
                    f"but introduced {regressions} regression(s). Cannot recommend deployment without addressing regressions."
                ),
                trade_offs=trade_offs,
                rules_triggered=rules_triggered,
            )

    # Check C: Cost and Runtime trade-offs
    has_large_cost_increase = cost_increase_pct > policy.max_cost_increase_pct
    if has_large_cost_increase:
        rules_triggered.append("RULE_HIGH_COST_INCREASE")
        trade_offs.append(f"Cost increased by +{cost_increase_pct:.1f}% (${baseline.average_cost:.4f} -> ${candidate.average_cost:.4f}/task).")

    if runtime_increase_pct > 40.0:
        rules_triggered.append("RULE_HIGH_RUNTIME_INCREASE")
        trade_offs.append(f"Runtime increased by +{runtime_increase_pct:.1f}% ({baseline.average_runtime:.1f}s -> {candidate.average_runtime:.1f}s).")

    # Check D: Sample size uncertainty
    is_small_sample = statistics.sample_size < policy.min_sample_size_for_certainty
    if is_small_sample:
        rules_triggered.append("RULE_SMALL_SAMPLE_SIZE")
        trade_offs.append(
            f"Sample size (N={statistics.sample_size}) is below threshold of {policy.min_sample_size_for_certainty} tasks for statistical certainty."
        )

    # Evaluate positive threshold
    has_significant_improvement = correctness_delta >= policy.min_correctness_delta

    if has_significant_improvement:
        if has_large_cost_increase or is_small_sample:
            # Trade-off or uncertainty triggers INCONCLUSIVE
            rules_triggered.append("RULE_INCONCLUSIVE_DUE_TO_TRADEOFFS")
            reasons = []
            if has_large_cost_increase:
                reasons.append(f"higher operational cost (+{cost_increase_pct:.1f}%)")
            if is_small_sample:
                reasons.append(f"limited sample size (N={statistics.sample_size})")

            justification = (
                f"Candidate improved correctness by +{correctness_delta*100:.1f} percentage points "
                f"({baseline.correctness_rate*100:.1f}% -> {candidate.correctness_rate*100:.1f}%) and had 0 regressions. "
                f"However, the verdict is INCONCLUSIVE due to {', and '.join(reasons)}. "
                "Engineering teams should verify whether the accuracy gain justifies the added resource cost."
            )
            return DecisionReport(
                outcome=DecisionOutcome.INCONCLUSIVE,
                summary_verdict="Promising correctness gain, but inconclusive due to resource trade-offs or sample size.",
                justification=justification,
                trade_offs=trade_offs,
                rules_triggered=rules_triggered,
            )
        else:
            # Clean positive!
            rules_triggered.append("RULE_CLEAR_POSITIVE")
            justification = (
                f"Candidate demonstrated robust correctness gains (+{correctness_delta*100:.1f}pp) "
                f"with zero regressions, acceptable resource utilization, and sufficient benchmark coverage."
            )
            return DecisionReport(
                outcome=DecisionOutcome.POSITIVE,
                summary_verdict="Candidate harness demonstrably improves agent performance.",
                justification=justification,
                trade_offs=trade_offs,
                rules_triggered=rules_triggered,
            )

    # Neither improved nor regressed significantly
    rules_triggered.append("RULE_NEGLIGIBLE_DIFFERENCE")
    return DecisionReport(
        outcome=DecisionOutcome.INCONCLUSIVE,
        summary_verdict="No meaningful performance difference observed between harnesses.",
        justification=(
            f"Net correctness difference is negligible ({correctness_delta*100:+.1f}pp). "
            "Neither harness demonstrated a clear advantage on this benchmark."
        ),
        trade_offs=trade_offs,
        rules_triggered=rules_triggered,
    )
