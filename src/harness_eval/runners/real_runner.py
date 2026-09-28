"""Real runner executing agent code modifications against sandbox or subprocesses."""
import os
import subprocess
import time
from pathlib import Path
from typing import Optional
from harness_eval.models import (
    BenchmarkTask,
    HarnessConfig,
    LintResult,
    RunResult,
    RunStatus,
    TestSuiteResult,
)
from harness_eval.runners.base import AgentRunner


class RealAgentRunner(AgentRunner):
    """Executes a real agent workflow via environment commands or LLM APIs.
    
    If no API key or agent executable is found in the environment,
    it fails safely with actionable configuration instructions.
    """

    def __init__(self, agent_command: Optional[str] = None) -> None:
        self.agent_command = agent_command or os.getenv("AGENT_RUNNER_CMD")

    def run(
        self,
        task: BenchmarkTask,
        harness: HarnessConfig,
        project_dir: Path,
        iteration: int = 1,
        seed: Optional[int] = None,
    ) -> RunResult:
        start_time = time.time()

        if not self.agent_command and not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            # Informative error rather than crash
            return RunResult(
                task_id=task.id,
                harness_id=harness.name,
                status=RunStatus.ERROR,
                runtime_seconds=round(time.time() - start_time, 2),
                error=(
                    "Real runner requires AGENT_RUNNER_CMD, OPENAI_API_KEY, or ANTHROPIC_API_KEY "
                    "in environment. To run locally without API keys, use --runner mock (default)."
                ),
                is_mock=False,
                seed=seed,
                iteration=iteration,
            )

        # In real execution mode, run the configured command in the target directory
        try:
            cmd = f"{self.agent_command} --task {task.id} --harness {harness.name}"
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=task.evaluation.timeout_seconds,
            )
            elapsed = round(time.time() - start_time, 2)
            is_success = proc.returncode == 0

            return RunResult(
                task_id=task.id,
                harness_id=harness.name,
                status=RunStatus.SUCCESS if is_success else RunStatus.FAILED,
                runtime_seconds=elapsed,
                stdout=proc.stdout,
                stderr=proc.stderr,
                error=None if is_success else f"Process exited with code {proc.returncode}",
                is_mock=False,
                seed=seed,
                iteration=iteration,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                task_id=task.id,
                harness_id=harness.name,
                status=RunStatus.TIMEOUT,
                runtime_seconds=float(task.evaluation.timeout_seconds),
                error=f"Task timed out after {task.evaluation.timeout_seconds}s",
                is_mock=False,
                seed=seed,
                iteration=iteration,
            )
        except Exception as e:
            return RunResult(
                task_id=task.id,
                harness_id=harness.name,
                status=RunStatus.ERROR,
                runtime_seconds=round(time.time() - start_time, 2),
                error=str(e),
                is_mock=False,
                seed=seed,
                iteration=iteration,
            )
