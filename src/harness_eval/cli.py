"""Main CLI entrypoint for harness-eval."""
import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import List, Optional

from harness_eval import __version__
from harness_eval.benchmarks.loader import load_benchmark
from harness_eval.config import DEFAULT_POLICY
from harness_eval.evaluation.comparator import (
    compare_task_runs,
    compute_aggregate_metrics,
    compute_metric_deltas,
)
from harness_eval.evaluation.decision import evaluate_decision
from harness_eval.evaluation.statistics import compute_statistical_summary
from harness_eval.harness.diff import compute_harness_diff
from harness_eval.harness.loader import load_harness
from harness_eval.models import (
    ComparisonReport,
    RunResult,
    TaskComparison,
)
from harness_eval.reporting.html_reporter import export_html_report
from harness_eval.reporting.json_reporter import export_json_report
from harness_eval.reporting.terminal import console, print_terminal_summary
from harness_eval.runners.base import AgentRunner
from harness_eval.runners.mock_runner import MockRunner
from harness_eval.runners.real_runner import RealAgentRunner


def run_evaluation(
    baseline_path: str,
    candidate_path: str,
    tasks_path: str,
    output_dir: str,
    task_filter: Optional[str] = None,
    runner_type: str = "mock",
    repetitions: int = 1,
    seed: Optional[int] = 42,
    export_formats: str = "all",
) -> ComparisonReport:
    """Executes the full evaluation comparison workflow."""
    baseline_dir = Path(baseline_path).resolve()
    candidate_dir = Path(candidate_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Harnesses
    baseline_config = load_harness(baseline_dir)
    candidate_config = load_harness(candidate_dir)
    harness_diff = compute_harness_diff(
        baseline_config,
        candidate_config,
        baseline_dir=baseline_dir,
        candidate_dir=candidate_dir,
    )

    # 2. Load Benchmark
    suite = load_benchmark(tasks_path, task_filter=task_filter)
    project_dir = (Path(tasks_path).parent.parent.parent / suite.project_path).resolve()

    # 3. Instantiate Runner
    runner: AgentRunner
    if runner_type.lower() == "real":
        runner = RealAgentRunner()
    else:
        runner = MockRunner()

    all_baseline_runs: List[RunResult] = []
    all_candidate_runs: List[RunResult] = []
    task_comparisons: List[TaskComparison] = []

    # 4. Execute Tasks across Repetitions
    for rep in range(1, repetitions + 1):
        for task in suite.tasks:
            # Baseline execution
            b_run = runner.run(
                task=task,
                harness=baseline_config,
                project_dir=project_dir,
                iteration=rep,
                seed=seed,
            )
            all_baseline_runs.append(b_run)

            # Candidate execution
            c_run = runner.run(
                task=task,
                harness=candidate_config,
                project_dir=project_dir,
                iteration=rep,
                seed=seed,
            )
            all_candidate_runs.append(c_run)

            # Record task-level comparison for the final iteration
            if rep == repetitions:
                comp = compare_task_runs(task, b_run, c_run)
                task_comparisons.append(comp)

    # 5. Compute Aggregate Metrics & Deltas
    baseline_agg = compute_aggregate_metrics(all_baseline_runs)
    candidate_agg = compute_aggregate_metrics(all_candidate_runs)
    metric_deltas = compute_metric_deltas(baseline_agg, candidate_agg)

    # 6. Statistical Reliability
    stats = compute_statistical_summary(
        baseline_runs=all_baseline_runs,
        candidate_runs=all_candidate_runs,
        repetitions=repetitions,
        total_tasks=len(suite.tasks),
    )

    # 7. Evaluate Decision
    decision_report = evaluate_decision(
        baseline=baseline_agg,
        candidate=candidate_agg,
        deltas=metric_deltas,
        comparisons=task_comparisons,
        statistics=stats,
        policy=DEFAULT_POLICY,
    )

    # 8. Assemble Full Report
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report = ComparisonReport(
        timestamp=now_str,
        tool_version=__version__,
        runner_type=runner_type,
        random_seed=seed,
        repetitions=repetitions,
        benchmark=suite,
        harness_diff=harness_diff,
        baseline_aggregate=baseline_agg,
        candidate_aggregate=candidate_agg,
        metric_deltas=metric_deltas,
        task_comparisons=task_comparisons,
        decision=decision_report,
        statistics=stats,
        artifacts_path=str(out_dir),
    )

    # 9. Export Artifacts
    if export_formats in ("all", "json"):
        export_json_report(report, out_dir)
    if export_formats in ("all", "html"):
        export_html_report(report, out_dir)

    return report


def cmd_evaluate(args: argparse.Namespace) -> None:
    try:
        report = run_evaluation(
            baseline_path=args.baseline,
            candidate_path=args.candidate,
            tasks_path=args.tasks,
            output_dir=args.output,
            task_filter=args.task,
            runner_type=args.runner,
            repetitions=args.repetitions,
            seed=args.seed,
            export_formats=args.format,
        )
        print_terminal_summary(report)
    except Exception as e:
        console.print(f"[bold red]Evaluation Error:[/bold red] {e}")
        sys.exit(1)


def cmd_inspect(args: argparse.Namespace) -> None:
    """Inspects raw evaluation artifacts for a specific task."""
    reports_dir = Path(args.output).resolve()
    runs_dir = reports_dir / "runs" / args.task_id
    if not runs_dir.exists():
        console.print(f"[bold red]No saved artifacts found for task '{args.task_id}' in {reports_dir}[/bold red]")
        sys.exit(1)

    comp_file = runs_dir / "comparison.json"
    if comp_file.exists():
        with open(comp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        console.rule(f"[bold cyan]TASK INSPECTION: {args.task_id}[/bold cyan]")
        console.print(f"[bold]Title:[/bold] {data.get('title')}")
        console.print(f"[bold]Outcome:[/bold] {data.get('outcome')}")
        console.print(f"[bold]Explanation:[/bold] {data.get('explanation')}\n")
        
        console.print("[bold]Evidence Points:[/bold]")
        for ep in data.get("evidence_points", []):
            console.print(f" - {ep}")

        console.print("\n[bold]Baseline Run Summary:[/bold]")
        b = data.get("baseline_run", {})
        console.print(f" Status: {b.get('status')} | Cost: ${b.get('estimated_cost')} | Time: {b.get('runtime_seconds')}s")
        if b.get("generated_changes"):
            console.print("[dim]Baseline Patch:[/dim]")
            console.print(b.get("generated_changes"))

        console.print("\n[bold]Candidate Run Summary:[/bold]")
        c = data.get("candidate_run", {})
        console.print(f" Status: {c.get('status')} | Cost: ${c.get('estimated_cost')} | Time: {c.get('runtime_seconds')}s")
        if c.get("generated_changes"):
            console.print("[green]Candidate Patch:[/green]")
            console.print(c.get("generated_changes"))


def cmd_diff(args: argparse.Namespace) -> None:
    """Shows configuration differences between baseline and candidate harnesses."""
    try:
        baseline_dir = Path(args.baseline).resolve()
        candidate_dir = Path(args.candidate).resolve()
        baseline = load_harness(baseline_dir)
        candidate = load_harness(candidate_dir)
        diff = compute_harness_diff(baseline, candidate, baseline_dir, candidate_dir)
        console.print(diff.summary_text)
    except Exception as e:
        console.print(f"[bold red]Diff Error:[/bold red] {e}")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="harness-eval",
        description="A focused evaluation and comparison tool for coding-agent harnesses.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Compare baseline vs candidate harnesses")
    eval_parser.add_argument("--baseline", default="harnesses/baseline", help="Path to baseline harness directory")
    eval_parser.add_argument("--candidate", default="harnesses/candidate", help="Path to candidate harness directory")
    eval_parser.add_argument("--tasks", default="benchmarks/sample/tasks.yaml", help="Path to benchmark tasks YAML")
    eval_parser.add_argument("--output", default="reports/sample", help="Directory to export report artifacts")
    eval_parser.add_argument("--task", default=None, help="Filter to a specific task ID")
    eval_parser.add_argument("--runner", choices=["mock", "real"], default="mock", help="Runner execution engine")
    eval_parser.add_argument("--repetitions", type=int, default=1, help="Repetitions per task for variance estimation")
    eval_parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible mock runs")
    eval_parser.add_argument("--format", choices=["all", "terminal", "html", "json"], default="all", help="Output format")
    eval_parser.set_defaults(func=cmd_evaluate)

    # inspect command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect raw task evidence and diffs from an evaluation run")
    inspect_parser.add_argument("task_id", help="Task ID to inspect (e.g. task-01)")
    inspect_parser.add_argument("--output", default="reports/sample", help="Directory containing evaluation reports")
    inspect_parser.set_defaults(func=cmd_inspect)

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Display configuration differences between harnesses")
    diff_parser.add_argument("--baseline", default="harnesses/baseline", help="Path to baseline harness directory")
    diff_parser.add_argument("--candidate", default="harnesses/candidate", help="Path to candidate harness directory")
    diff_parser.set_defaults(func=cmd_diff)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
