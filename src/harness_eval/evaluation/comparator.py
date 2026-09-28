"""Baseline vs Candidate comparator for tasks and aggregate metrics."""
from typing import Dict, List, Tuple
from harness_eval.evaluation.dimensions import (
    compute_task_convention_compliance,
    compute_task_correctness,
    compute_task_requirement_satisfaction,
)
from harness_eval.models import (
    AggregateMetrics,
    BenchmarkTask,
    MetricDelta,
    RunResult,
    RunStatus,
    TaskComparison,
    TaskOutcome,
)


def compare_task_runs(
    task: BenchmarkTask,
    baseline_run: RunResult,
    candidate_run: RunResult,
) -> TaskComparison:
    """Performs an in-depth comparison of a single task between baseline and candidate."""
    b_corr = compute_task_correctness(baseline_run)
    c_corr = compute_task_correctness(candidate_run)
    corr_delta = round(c_corr - b_corr, 4)

    b_req = compute_task_requirement_satisfaction(baseline_run)
    c_req = compute_task_requirement_satisfaction(candidate_run)
    req_delta = round(c_req - b_req, 4)

    b_lint = baseline_run.lint_result.violations_count
    c_lint = candidate_run.lint_result.violations_count
    lint_delta = c_lint - b_lint

    cost_delta = round(candidate_run.estimated_cost - baseline_run.estimated_cost, 4)
    runtime_delta = round(candidate_run.runtime_seconds - baseline_run.runtime_seconds, 2)

    # Determine qualitative outcome
    b_pass = (baseline_run.status == RunStatus.SUCCESS) and (b_corr >= 0.90)
    c_pass = (candidate_run.status == RunStatus.SUCCESS) and (c_corr >= 0.90)

    evidence_points: List[str] = []

    if c_pass and not b_pass:
        outcome = TaskOutcome.IMPROVED
        explanation = f"Candidate resolved task requirements (correctness: {b_corr*100:.1f}% -> {c_corr*100:.1f}%)."
    elif b_pass and not c_pass:
        outcome = TaskOutcome.REGRESSED
        explanation = f"Candidate regressed on this task (correctness: {b_corr*100:.1f}% -> {c_corr*100:.1f}%)."
    elif b_pass and c_pass:
        outcome = TaskOutcome.BOTH_PASSED
        explanation = "Both harnesses satisfied task requirements."
    elif not b_pass and not c_pass:
        outcome = TaskOutcome.BOTH_FAILED
        explanation = "Both harnesses failed to satisfy holdout criteria."
    else:
        outcome = TaskOutcome.UNCHANGED
        explanation = "Performance remained unchanged between harnesses."

    # Evidence points
    if baseline_run.unit_test_result.failed > 0:
        evidence_points.append(f"Baseline unit test failures: {baseline_run.unit_test_result.failures}")
    if candidate_run.unit_test_result.failed > 0:
        evidence_points.append(f"Candidate unit test failures: {candidate_run.unit_test_result.failures}")

    if baseline_run.holdout_test_result.failed > 0:
        evidence_points.append("Baseline failed holdout test verification.")
    if candidate_run.holdout_test_result.failed == 0 and candidate_run.holdout_test_result.total > 0:
        evidence_points.append("Candidate passed all holdout test assertions.")

    if b_lint > c_lint:
        evidence_points.append(f"Candidate reduced lint issues by {b_lint - c_lint}.")
    elif c_lint > b_lint:
        evidence_points.append(f"Candidate introduced {c_lint - b_lint} new lint issues.")

    if abs(cost_delta) > 0.001:
        evidence_points.append(f"Cost delta: ${cost_delta:+.4f} ({baseline_run.estimated_cost:.4f} -> {candidate_run.estimated_cost:.4f})")

    return TaskComparison(
        task_id=task.id,
        title=task.title,
        baseline_run=baseline_run,
        candidate_run=candidate_run,
        outcome=outcome,
        correctness_delta=corr_delta,
        requirement_delta=req_delta,
        lint_delta=lint_delta,
        cost_delta=cost_delta,
        runtime_delta=runtime_delta,
        explanation=explanation,
        evidence_points=evidence_points,
    )


def compute_aggregate_metrics(runs: List[RunResult]) -> AggregateMetrics:
    """Computes overall aggregate metrics across a collection of task runs."""
    total = len(runs)
    if total == 0:
        return AggregateMetrics()

    corr_scores = [compute_task_correctness(r) for r in runs]
    req_scores = [compute_task_requirement_satisfaction(r) for r in runs]
    conv_scores = [compute_task_convention_compliance(r) for r in runs]

    costs = [r.estimated_cost for r in runs]
    runtimes = [r.runtime_seconds for r in runs]
    tokens = [r.total_tokens for r in runs]

    successful = sum(1 for r in runs if r.status == RunStatus.SUCCESS)

    return AggregateMetrics(
        total_tasks=total,
        correctness_rate=round(sum(corr_scores) / total, 4),
        requirement_satisfaction_rate=round(sum(req_scores) / total, 4),
        convention_compliance_rate=round(sum(conv_scores) / total, 4),
        average_cost=round(sum(costs) / total, 4),
        total_cost=round(sum(costs), 4),
        average_runtime=round(sum(runtimes) / total, 2),
        total_runtime=round(sum(runtimes), 2),
        pass_rate=round(successful / total, 4),
        failure_rate=round((total - successful) / total, 4),
        total_tokens=sum(tokens),
    )


def compute_metric_deltas(
    baseline: AggregateMetrics,
    candidate: AggregateMetrics,
) -> List[MetricDelta]:
    """Calculates absolute and relative deltas for each primary evaluation metric."""
    deltas: List[MetricDelta] = []

    metrics = [
        ("Correctness Rate", baseline.correctness_rate, candidate.correctness_rate, True),
        ("Requirement Satisfaction", baseline.requirement_satisfaction_rate, candidate.requirement_satisfaction_rate, True),
        ("Convention Compliance", baseline.convention_compliance_rate, candidate.convention_compliance_rate, True),
        ("Pass Rate", baseline.pass_rate, candidate.pass_rate, True),
        ("Average Cost ($)", baseline.average_cost, candidate.average_cost, False),
        ("Average Runtime (s)", baseline.average_runtime, candidate.average_runtime, False),
        ("Total Tokens", float(baseline.total_tokens), float(candidate.total_tokens), False),
    ]

    for name, b_val, c_val, higher_is_better in metrics:
        abs_delta = round(c_val - b_val, 4)
        if b_val != 0:
            rel_delta_pct = round(((c_val - b_val) / abs(b_val)) * 100.0, 2)
        else:
            rel_delta_pct = 0.0

        if higher_is_better:
            is_favorable = abs_delta > 0
        else:
            is_favorable = abs_delta < 0

        deltas.append(MetricDelta(
            metric=name,
            baseline=round(b_val, 4),
            candidate=round(c_val, 4),
            absolute_delta=abs_delta,
            relative_delta_pct=rel_delta_pct,
            is_favorable=is_favorable,
        ))

    return deltas
