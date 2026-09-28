"""Tests for benchmark loader and validation."""
import pytest
from harness_eval.benchmarks.loader import load_benchmark


def test_load_sample_benchmark():
    suite = load_benchmark("benchmarks/sample/tasks.yaml")
    assert suite.benchmark_name == "sample_project_benchmark"
    assert len(suite.tasks) == 6
    task_ids = [t.id for t in suite.tasks]
    assert "task-01" in task_ids
    assert "task-06" in task_ids


def test_load_benchmark_with_filter():
    suite = load_benchmark("benchmarks/sample/tasks.yaml", task_filter="task-03")
    assert len(suite.tasks) == 1
    assert suite.tasks[0].id == "task-03"
    assert suite.tasks[0].title == "Add duplicate email validation"


def test_load_benchmark_with_invalid_filter_raises_error():
    with pytest.raises(ValueError, match="not found"):
        load_benchmark("benchmarks/sample/tasks.yaml", task_filter="nonexistent-task")


def test_load_nonexistent_benchmark_file_raises_error():
    with pytest.raises(FileNotFoundError):
        load_benchmark("benchmarks/sample/does_not_exist.yaml")
