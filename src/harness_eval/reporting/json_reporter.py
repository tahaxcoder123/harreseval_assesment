"""JSON report and raw evaluation artifact persistence."""
import json
from pathlib import Path
from typing import Union
from harness_eval.models import ComparisonReport


def export_json_report(
    report: ComparisonReport,
    output_dir: Union[str, Path],
) -> Path:
    """Exports full structured JSON report and per-task raw artifacts."""
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    # 1. Save main report.json
    report_dict = report.model_dump()
    report_file = out / "report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2)

    # 2. Save compact summary.json
    summary_data = {
        "schema_version": report.schema_version,
        "timestamp": report.timestamp,
        "decision": report.decision.outcome.value,
        "verdict": report.decision.summary_verdict,
        "tasks_evaluated": len(report.benchmark.tasks),
        "repetitions": report.repetitions,
        "deltas": {
            d.metric: {
                "baseline": d.baseline,
                "candidate": d.candidate,
                "absolute_delta": d.absolute_delta,
                "relative_delta_pct": d.relative_delta_pct,
            }
            for d in report.metric_deltas
        },
        "trade_offs": report.decision.trade_offs,
    }
    with open(out / "summary.json", "w", encoding="utf-8") as sf:
        json.dump(summary_data, sf, indent=2)

    # 3. Save raw task artifacts in runs/<task_id>/
    runs_dir = out / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    for task_comp in report.task_comparisons:
        task_dir = runs_dir / task_comp.task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # Baseline details
        with open(task_dir / "baseline_run.json", "w", encoding="utf-8") as bf:
            json.dump(task_comp.baseline_run.model_dump(), bf, indent=2)
        if task_comp.baseline_run.generated_changes:
            with open(task_dir / "baseline.patch", "w", encoding="utf-8") as bpf:
                bpf.write(task_comp.baseline_run.generated_changes)

        # Candidate details
        with open(task_dir / "candidate_run.json", "w", encoding="utf-8") as cf:
            json.dump(task_comp.candidate_run.model_dump(), cf, indent=2)
        if task_comp.candidate_run.generated_changes:
            with open(task_dir / "candidate.patch", "w", encoding="utf-8") as cpf:
                cpf.write(task_comp.candidate_run.generated_changes)

        # Task comparison summary
        with open(task_dir / "comparison.json", "w", encoding="utf-8") as tf:
            json.dump(task_comp.model_dump(), tf, indent=2)

    return report_file
