"""Tests for JSON, HTML, and raw artifact reporting."""
import json
from pathlib import Path
from harness_eval.cli import run_evaluation
from harness_eval.reporting.html_reporter import export_html_report
from harness_eval.reporting.json_reporter import export_json_report


def test_export_reports(tmp_path: Path):
    report = run_evaluation(
        baseline_path="harnesses/baseline",
        candidate_path="harnesses/candidate",
        tasks_path="benchmarks/sample/tasks.yaml",
        output_dir=str(tmp_path),
        task_filter="task-01",
        runner_type="mock",
    )

    # Check report.json
    json_path = tmp_path / "report.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["schema_version"] == "1.0.0"
    assert "baseline_aggregate" in data
    assert "candidate_aggregate" in data

    # Check summary.json
    summary_path = tmp_path / "summary.json"
    assert summary_path.exists()
    with open(summary_path, "r", encoding="utf-8") as sf:
        sdata = json.load(sf)
    assert "decision" in sdata

    # Check report.html
    html_path = tmp_path / "report.html"
    assert html_path.exists()
    html_content = html_path.read_text(encoding="utf-8")
    assert "<title>Coding Agent Harness Evaluation Report</title>" in html_content
    assert "task-01" in html_content

    # Check raw artifacts
    task_dir = tmp_path / "runs" / "task-01"
    assert (task_dir / "baseline_run.json").exists()
    assert (task_dir / "candidate_run.json").exists()
    assert (task_dir / "comparison.json").exists()
    assert (task_dir / "baseline.patch").exists()
    assert (task_dir / "candidate.patch").exists()
