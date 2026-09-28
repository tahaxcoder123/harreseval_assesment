"""Tests for harness configuration loading."""
from pathlib import Path
import pytest
from harness_eval.harness.loader import load_harness


def test_load_baseline_harness():
    harness = load_harness("harnesses/baseline")
    assert harness.name == "baseline"
    assert harness.model == "claude-3-5-haiku-20241022"
    assert "skills/basic-python.md" in harness.skills
    assert "filesystem" in harness.tools
    assert harness.cost_per_1k_input == 0.001


def test_load_candidate_harness():
    harness = load_harness("harnesses/candidate")
    assert harness.name == "candidate"
    assert harness.model == "claude-3-5-sonnet-20241022"
    assert len(harness.skills) == 2
    assert "hooks/pre_commit_lint.sh" in harness.hooks


def test_load_nonexistent_harness_raises_error():
    with pytest.raises(FileNotFoundError):
        load_harness("harnesses/does_not_exist")
