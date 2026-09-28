"""Tests for harness configuration diff calculation."""
from harness_eval.harness.diff import compute_harness_diff
from harness_eval.harness.loader import load_harness


def test_harness_diff_detection():
    baseline = load_harness("harnesses/baseline")
    candidate = load_harness("harnesses/candidate")

    diff = compute_harness_diff(
        baseline,
        candidate,
        baseline_dir="harnesses/baseline",
        candidate_dir="harnesses/candidate",
    )

    assert diff.model_changed is True
    assert diff.baseline_model == "claude-3-5-haiku-20241022"
    assert diff.candidate_model == "claude-3-5-sonnet-20241022"
    assert "skills/python-testing.md" in diff.skills_added
    assert "skills/basic-python.md" in diff.skills_removed
    assert "hooks/pre_commit_lint.sh" in diff.hooks_added
    assert diff.agents_file_changed is True
    assert diff.system_prompt_changed is True
    assert "HARNESS COMPARISON SUMMARY" in diff.summary_text
