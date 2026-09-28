"""Abstract base class for coding agent runners."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from harness_eval.models import BenchmarkTask, HarnessConfig, RunResult


class AgentRunner(ABC):
    """Abstract interface for executing benchmark tasks against agent harnesses."""

    @abstractmethod
    def run(
        self,
        task: BenchmarkTask,
        harness: HarnessConfig,
        project_dir: Path,
        iteration: int = 1,
        seed: Optional[int] = None,
    ) -> RunResult:
        """Executes a single benchmark task using the specified harness.
        
        Args:
            task: The benchmark task definition.
            harness: The harness configuration under test.
            project_dir: Root directory of the target project to modify/test.
            iteration: Repetition index for variance estimation.
            seed: Optional random seed for reproducible runs.

        Returns:
            A structured RunResult containing execution metrics, test outputs, and diffs.
        """
        pass
