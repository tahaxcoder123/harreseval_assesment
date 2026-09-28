"""Tests for runner abstractions."""
from pathlib import Path
from harness_eval.benchmarks.loader import load_benchmark
from harness_eval.harness.loader import load_harness
from harness_eval.models import RunStatus
from harness_eval.runners.mock_runner import MockRunner
from harness_eval.runners.real_runner import RealAgentRunner


def test_mock_runner_deterministic_run():
    suite = load_benchmark("benchmarks/sample/tasks.yaml", task_filter="task-01")
    baseline = load_harness("harnesses/baseline")
    candidate = load_harness("harnesses/candidate")
    runner = MockRunner()

    res_b1 = runner.run(suite.tasks[0], baseline, Path("sample_project"), iteration=1, seed=42)
    res_b2 = runner.run(suite.tasks[0], baseline, Path("sample_project"), iteration=1, seed=42)

    # Identical seed produces identical results
    assert res_b1.input_tokens == res_b2.input_tokens
    assert res_b1.output_tokens == res_b2.output_tokens
    assert res_b1.estimated_cost == res_b2.estimated_cost
    assert res_b1.status == res_b2.status

    # Candidate run produces candidate characteristics
    res_c = runner.run(suite.tasks[0], candidate, Path("sample_project"), iteration=1, seed=42)
    assert res_c.status == RunStatus.SUCCESS
    assert res_c.holdout_test_result.passed == 1
    assert res_c.lint_result.passed is True


def test_real_runner_missing_environment_fails_safely():
    suite = load_benchmark("benchmarks/sample/tasks.yaml", task_filter="task-01")
    baseline = load_harness("harnesses/baseline")
    runner = RealAgentRunner(agent_command=None)

    result = runner.run(suite.tasks[0], baseline, Path("sample_project"))
    assert result.status == RunStatus.ERROR
    assert "Real runner requires AGENT_RUNNER_CMD" in (result.error or "")
