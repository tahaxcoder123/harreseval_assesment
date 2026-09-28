"""Loader and validator for benchmark task suites."""
from pathlib import Path
from typing import List, Optional, Union
import yaml
from harness_eval.models import BenchmarkSuite, BenchmarkTask


def load_benchmark(
    benchmark_path: Union[str, Path],
    task_filter: Optional[str] = None,
) -> BenchmarkSuite:
    """Loads a benchmark suite from YAML definition."""
    path = Path(benchmark_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Benchmark file does not exist: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    suite = BenchmarkSuite(**data)

    if task_filter:
        filtered_tasks = [t for t in suite.tasks if t.id == task_filter]
        if not filtered_tasks:
            available_ids = [t.id for t in suite.tasks]
            raise ValueError(
                f"Task ID '{task_filter}' not found in benchmark. Available: {available_ids}"
            )
        suite.tasks = filtered_tasks

    if not suite.tasks:
        raise ValueError(f"No benchmark tasks found in {path}")

    return suite
