"""Terminal reporting using Rich formatting for evaluation summaries."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from harness_eval.models import ComparisonReport, DecisionOutcome, TaskOutcome


console = Console()


def print_terminal_summary(report: ComparisonReport) -> None:
    """Renders a comprehensive, evidence-based terminal summary."""
    console.print("\n")
    console.rule("[bold cyan]HARNESS EVALUATION REPORT[/bold cyan]")

    # 1. Harness configuration diff
    diff_text = Text()
    diff_text.append(f"Baseline : {report.harness_diff.baseline_name} ({report.harness_diff.baseline_model})\n", style="yellow")
    diff_text.append(f"Candidate: {report.harness_diff.candidate_name} ({report.harness_diff.candidate_model})\n", style="green")
    
    if report.harness_diff.skills_added:
        diff_text.append(f"Skills Added  : {', '.join(report.harness_diff.skills_added)}\n", style="bold green")
    if report.harness_diff.skills_removed:
        diff_text.append(f"Skills Removed: {', '.join(report.harness_diff.skills_removed)}\n", style="bold red")
    if report.harness_diff.hooks_added:
        diff_text.append(f"Hooks Added   : {', '.join(report.harness_diff.hooks_added)}\n", style="bold green")

    console.print(Panel(diff_text, title="Harness Changes", border_style="cyan"))

    # 2. Executive Metrics Summary Table
    table = Table(title=f"Evaluation Overview ({report.benchmark.tasks.__len__()} Tasks, Repetitions={report.repetitions})", show_header=True, header_style="bold magenta")
    table.add_column("Evaluation Dimension", style="dim", width=26)
    table.add_column("Baseline", justify="right", width=14)
    table.add_column("Candidate", justify="right", width=14)
    table.add_column("Delta", justify="right", width=14)
    table.add_column("Relative", justify="right", width=12)

    for delta in report.metric_deltas:
        # Format values
        is_pct = "Rate" in delta.metric or "Compliance" in delta.metric or "Satisfaction" in delta.metric
        if is_pct:
            b_str = f"{delta.baseline * 100:.1f}%"
            c_str = f"{delta.candidate * 100:.1f}%"
            d_str = f"{delta.absolute_delta * 100:+.1f}pp"
        elif "$" in delta.metric:
            b_str = f"${delta.baseline:.4f}"
            c_str = f"${delta.candidate:.4f}"
            d_str = f"${delta.absolute_delta:+.4f}"
        elif "(s)" in delta.metric:
            b_str = f"{delta.baseline:.1f}s"
            c_str = f"{delta.candidate:.1f}s"
            d_str = f"{delta.absolute_delta:+.1f}s"
        else:
            b_str = f"{int(delta.baseline)}"
            c_str = f"{int(delta.candidate)}"
            d_str = f"{int(delta.absolute_delta):+d}"

        rel_str = f"{delta.relative_delta_pct:+.1f}%" if delta.baseline != 0 else "-"

        # Colorize delta
        if delta.is_favorable is True:
            style = "bold green"
        elif delta.is_favorable is False and abs(delta.absolute_delta) > 0.001:
            style = "bold red"
        else:
            style = "white"

        table.add_row(delta.metric, b_str, c_str, Text(d_str, style=style), rel_str)

    console.print(table)

    # 3. Per-Task Comparison Table
    task_table = Table(title="Per-Task Evidence Breakdown", show_header=True, header_style="bold blue")
    task_table.add_column("Task ID", style="bold", no_wrap=True)
    task_table.add_column("Title")
    task_table.add_column("Baseline", justify="center", no_wrap=True)
    task_table.add_column("Candidate", justify="center", no_wrap=True)
    task_table.add_column("Outcome", justify="center", no_wrap=True)
    task_table.add_column("Cost Delta", justify="right", no_wrap=True)

    for t in report.task_comparisons:
        b_status = f"{t.baseline_run.status.value}"
        c_status = f"{t.candidate_run.status.value}"

        if t.outcome == TaskOutcome.IMPROVED:
            outcome_text = Text("IMPROVED (+)", style="bold green")
        elif t.outcome == TaskOutcome.REGRESSED:
            outcome_text = Text("REGRESSED (-)", style="bold red")
        elif t.outcome == TaskOutcome.BOTH_PASSED:
            outcome_text = Text("BOTH PASSED", style="green")
        elif t.outcome == TaskOutcome.BOTH_FAILED:
            outcome_text = Text("BOTH FAILED", style="yellow")
        else:
            outcome_text = Text("UNCHANGED", style="dim")

        cost_str = f"${t.cost_delta:+.4f}"
        task_table.add_row(t.task_id, t.title, b_status, c_status, outcome_text, cost_str)

    console.print(task_table)

    # 4. Decision verdict banner
    dec = report.decision
    if dec.outcome == DecisionOutcome.POSITIVE:
        dec_color = "bold green"
        box_style = "green"
    elif dec.outcome == DecisionOutcome.NEGATIVE:
        dec_color = "bold red"
        box_style = "red"
    else:
        dec_color = "bold yellow"
        box_style = "yellow"

    dec_text = Text()
    dec_text.append(f"DECISION: {dec.outcome.value}\n\n", style=dec_color)
    dec_text.append(f"Verdict: {dec.summary_verdict}\n", style="bold white")
    dec_text.append(f"Reason: {dec.justification}\n\n", style="white")

    if dec.trade_offs:
        dec_text.append("Documented Trade-offs / Limitations:\n", style="bold underline")
        for to in dec.trade_offs:
            dec_text.append(f" - {to}\n", style="yellow")

    if report.statistics.significance_note:
        dec_text.append(f"\nStatistical Reliability: {report.statistics.significance_note}\n", style="dim")

    console.print(Panel(dec_text, title="Evaluator Conclusion", border_style=box_style))

    if report.artifacts_path:
        console.print(f"\n[bold]Report files generated:[/bold]")
        console.print(f"  [cyan]HTML Report :[/cyan] {report.artifacts_path}/report.html")
        console.print(f"  [cyan]JSON Report :[/cyan] {report.artifacts_path}/report.json")
        console.print(f"  [cyan]Summary JSON:[/cyan] {report.artifacts_path}/summary.json\n")
