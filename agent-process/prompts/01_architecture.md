# Architecture Prompt

## Goal
Design an evaluation engine that compares two coding-agent harnesses (baseline vs candidate) across identical benchmark tasks and produces an evidence-based report answering: "Did changing the harness make the agent better, worse, or inconclusive?"

## Key Directives
1. Avoid single-number aggregate scores that conceal trade-offs.
2. Formulate explicit dimensions:
   - Correctness (visible unit tests + private holdout tests)
   - Requirement / Business alignment (task-specific acceptance criteria)
   - Convention / Code quality (linting, type hints, formatting)
   - Token & Cost efficiency (input/output token accounting and cost formulas)
   - Runtime latency
   - Reliability & Failure modes (timeouts, crashes, regressions)
3. Design an abstract `AgentRunner` allowing deterministic mock runs and pluggable real agent runners.
4. Establish transparent decision criteria with first-class `INCONCLUSIVE` outcomes.
