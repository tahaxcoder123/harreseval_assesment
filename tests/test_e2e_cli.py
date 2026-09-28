"""End-to-end integration tests for CLI commands."""
import subprocess
import sys


def test_cli_diff_command():
    cmd = [
        sys.executable,
        "-m",
        "harness_eval",
        "diff",
        "--baseline",
        "harnesses/baseline",
        "--candidate",
        "harnesses/candidate",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "HARNESS COMPARISON SUMMARY" in res.stdout
    assert "claude-3-5-sonnet-20241022" in res.stdout


def test_cli_evaluate_and_inspect_command(tmp_path):
    # 1. Run evaluate
    eval_cmd = [
        sys.executable,
        "-m",
        "harness_eval",
        "evaluate",
        "--baseline",
        "harnesses/baseline",
        "--candidate",
        "harnesses/candidate",
        "--tasks",
        "benchmarks/sample/tasks.yaml",
        "--output",
        str(tmp_path),
        "--task",
        "task-01",
    ]
    eval_res = subprocess.run(eval_cmd, capture_output=True, text=True)
    assert eval_res.returncode == 0
    assert "HARNESS EVALUATION REPORT" in eval_res.stdout
    assert "DECISION: INCONCLUSIVE" in eval_res.stdout

    # 2. Run inspect
    inspect_cmd = [
        sys.executable,
        "-m",
        "harness_eval",
        "inspect",
        "task-01",
        "--output",
        str(tmp_path),
    ]
    inspect_res = subprocess.run(inspect_cmd, capture_output=True, text=True)
    assert inspect_res.returncode == 0
    assert "TASK INSPECTION: task-01" in inspect_res.stdout
    assert "Candidate Patch:" in inspect_res.stdout


def test_cli_invalid_task_filter():
    cmd = [
        sys.executable,
        "-m",
        "harness_eval",
        "evaluate",
        "--task",
        "nonexistent-task",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0
    assert "Evaluation Error" in res.stdout
