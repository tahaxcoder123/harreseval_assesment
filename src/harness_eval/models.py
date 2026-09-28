"""Structured, versioned data models for harness evaluation."""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


SCHEMA_VERSION = "1.0.0"


class RunStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class TaskOutcome(str, Enum):
    IMPROVED = "IMPROVED"
    REGRESSED = "REGRESSED"
    UNCHANGED = "UNCHANGED"
    BOTH_FAILED = "BOTH_FAILED"
    BOTH_PASSED = "BOTH_PASSED"


class DecisionOutcome(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    INCONCLUSIVE = "INCONCLUSIVE"


class HarnessConfig(BaseModel):
    name: str
    version: str = "1.0.0"
    description: str = ""
    model: str = "default-model"
    temperature: float = 0.0
    max_iterations: int = 5
    system_prompt: str = ""
    agents_file: str = "AGENTS.md"
    skills: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    cost_per_1k_input: float = 0.0015
    cost_per_1k_output: float = 0.0075
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HarnessDiff(BaseModel):
    baseline_name: str
    candidate_name: str
    model_changed: bool = False
    baseline_model: str = ""
    candidate_model: str = ""
    skills_added: List[str] = Field(default_factory=list)
    skills_removed: List[str] = Field(default_factory=list)
    tools_added: List[str] = Field(default_factory=list)
    tools_removed: List[str] = Field(default_factory=list)
    hooks_added: List[str] = Field(default_factory=list)
    hooks_removed: List[str] = Field(default_factory=list)
    agents_file_changed: bool = False
    system_prompt_changed: bool = False
    summary_text: str = ""


class AcceptanceCriterion(BaseModel):
    id: str
    description: str
    weight: float = 1.0


class TaskEvaluationSpec(BaseModel):
    unit_tests: List[str] = Field(default_factory=list)
    holdout_tests: List[str] = Field(default_factory=list)
    lint_checks: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = 60


class BenchmarkTask(BaseModel):
    id: str
    title: str
    description: str
    target_files: List[str] = Field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriterion] = Field(default_factory=list)
    evaluation: TaskEvaluationSpec = Field(default_factory=TaskEvaluationSpec)


class BenchmarkSuite(BaseModel):
    benchmark_name: str
    version: str = "1.0.0"
    project_path: str = "sample_project"
    tasks: List[BenchmarkTask] = Field(default_factory=list)


class CriterionResult(BaseModel):
    criterion_id: str
    description: str
    passed: bool
    score: float
    max_score: float
    reason: str = ""


class TestSuiteResult(BaseModel):
    __test__ = False
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    pass_rate: float = 0.0
    failures: List[str] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""


class LintResult(BaseModel):
    passed: bool = True
    issues: List[str] = Field(default_factory=list)
    violations_count: int = 0


class RunResult(BaseModel):
    task_id: str
    harness_id: str
    status: RunStatus
    generated_changes: str = ""
    files_modified: List[str] = Field(default_factory=list)
    unit_test_result: TestSuiteResult = Field(default_factory=TestSuiteResult)
    holdout_test_result: TestSuiteResult = Field(default_factory=TestSuiteResult)
    criteria_results: List[CriterionResult] = Field(default_factory=list)
    lint_result: LintResult = Field(default_factory=LintResult)
    runtime_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    error: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    is_mock: bool = True
    seed: Optional[int] = None
    iteration: int = 1


class TaskComparison(BaseModel):
    task_id: str
    title: str
    baseline_run: RunResult
    candidate_run: RunResult
    outcome: TaskOutcome
    correctness_delta: float
    requirement_delta: float
    lint_delta: int
    cost_delta: float
    runtime_delta: float
    explanation: str
    evidence_points: List[str] = Field(default_factory=list)


class AggregateMetrics(BaseModel):
    total_tasks: int = 0
    correctness_rate: float = 0.0
    requirement_satisfaction_rate: float = 0.0
    convention_compliance_rate: float = 0.0
    average_cost: float = 0.0
    total_cost: float = 0.0
    average_runtime: float = 0.0
    total_runtime: float = 0.0
    pass_rate: float = 0.0
    failure_rate: float = 0.0
    total_tokens: int = 0


class MetricDelta(BaseModel):
    metric: str
    baseline: float
    candidate: float
    absolute_delta: float
    relative_delta_pct: float
    is_favorable: Optional[bool] = None


class DecisionReport(BaseModel):
    outcome: DecisionOutcome
    summary_verdict: str
    justification: str
    trade_offs: List[str] = Field(default_factory=list)
    rules_triggered: List[str] = Field(default_factory=list)


class StatisticalSummary(BaseModel):
    repetitions: int = 1
    sample_size: int = 0
    is_statistically_significant: bool = False
    significance_note: str = ""
    correctness_mean_diff: float = 0.0
    cost_mean_diff: float = 0.0
    runtime_mean_diff: float = 0.0


class ComparisonReport(BaseModel):
    schema_version: str = SCHEMA_VERSION
    timestamp: str
    tool_version: str = "0.1.0"
    runner_type: str = "mock"
    random_seed: Optional[int] = None
    repetitions: int = 1
    benchmark: BenchmarkSuite
    harness_diff: HarnessDiff
    baseline_aggregate: AggregateMetrics
    candidate_aggregate: AggregateMetrics
    metric_deltas: List[MetricDelta] = Field(default_factory=list)
    task_comparisons: List[TaskComparison] = Field(default_factory=list)
    decision: DecisionReport
    statistics: StatisticalSummary
    artifacts_path: str = ""
