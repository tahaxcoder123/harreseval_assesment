# Agent Process & Development Audit Trail (`agent-process/`)

The `agent-process/` directory preserves the engineering audit trail, iterative prompt instructions, and full build session transcript that produced `harness-eval`.

---

## 1. Directory Structure

```text
agent-process/
├── prompts/
│   ├── 01_architecture.md            # Initial architecture design directives & requirements
│   ├── 02_implementation.md          # Multi-dimensional engine & test suite implementation
│   └── 03_review_and_evaluation.md   # Final audit, holdout verification, and sample eval run
└── transcript/
    └── build_session.md              # Complete end-to-end build log and tool execution record
```

---

## 2. Iteration Milestones

### Phase 1: Architecture & Data Modeling ([`prompts/01_architecture.md`](file:///d:/Task/chat/agent-process/prompts/01_architecture.md))
- Established the central research question: *"Did changing the coding-agent harness make the agent better, worse, or inconclusive?"*
- Refused single-score composite metrics in favor of native dimensional measurements.
- Designed the pluggable `AgentRunner` abstract interface supporting deterministic `MockRunner` and subprocess `RealAgentRunner`.
- Formulated the 40/60 unit vs. holdout test correctness split.

### Phase 2: Implementation & Multi-Dimensional Logic ([`prompts/02_implementation.md`](file:///d:/Task/chat/agent-process/prompts/02_implementation.md))
- Built Pydantic v2 schemas in [`models.py`](file:///d:/Task/chat/src/harness_eval/models.py) (`SCHEMA_VERSION = "1.0.0"`).
- Implemented multidimensional evaluators in `dimensions.py`, `comparator.py`, and `statistics.py`.
- Enforced defensive decision rules in `decision.py` (zero-regression policy, >60% cost inflation checks, and $N < 10$ small-sample guardrails).
- Built CLI subcommands (`evaluate`, `inspect`, `diff`) in `cli.py`.

### Phase 3: Review, Evaluation & Reporting ([`prompts/03_review_and_evaluation.md`](file:///d:/Task/chat/agent-process/prompts/03_review_and_evaluation.md))
- Validated the 28-test automated pytest suite in `tests/`.
- Executed the full benchmark evaluation against `sample_project/` using `benchmarks/sample/tasks.yaml`.
- Exported standalone dark-mode `report.html`, versioned `report.json`, and compact `summary.json`.
- Documented findings, architectural rationale, and limitations in [`DESIGN.md`](file:///d:/Task/chat/DESIGN.md) and [`docs/Project_Documentation.md`](file:///d:/Task/chat/docs/Project_Documentation.md).

---

## 3. Session Transcript ([`transcript/build_session.md`](file:///d:/Task/chat/agent-process/transcript/build_session.md))

The build session transcript provides a transparent, auditable log of commands executed, files written, tests verified, and decisions made during the creation of this project.

For architectural details, see the [Main Project Documentation](file:///d:/Task/chat/docs/Project_Documentation.md).
