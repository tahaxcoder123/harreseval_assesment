# DESIGN.md — Harness Comparison & Evaluation Engine

## 1. Concepts Defined & Rationale
- **Harness**: The operational perimeter surrounding an LLM agent—prompts, `AGENTS.md`, skill libraries, tool access, hooks, and model selection.
- **Holdout Verification**: Split test evaluation (visible unit tests vs. private holdout tests). Guardrails against benchmark gaming where models patch known tests without solving core requirements.
- **Multi-Dimensional Quality**: Separates correctness, business requirement fulfillment, convention compliance, token efficiency, and runtime. Avoids collapsing multidimensional trade-offs into an arbitrary single score.
- **Transparent Inconclusiveness**: First-class evaluation outcome (`POSITIVE`, `NEGATIVE`, `INCONCLUSIVE`) triggered whenever regressions occur, costs increase disproportionately, or sample size is insufficient.

## 2. The Five Hardest Decisions
1. **Refusing Single-Score Aggregation**: Rejected a weighted composite score (e.g., "78.4/100") because aggregate scores conceal critical edge-case regressions behind high average scores.
2. **Prioritizing Holdout Tests Over Unit Tests**: Weighted holdout tests at 60% and unit tests at 40%. Visible tests reward models that overfit to assertion messages; holdout tests test generalized invariant preservation.
3. **Strict Zero-Regression Policy for Positive Verdicts**: Any task that passes under baseline but fails under candidate immediately revokes a `POSITIVE` verdict, forcing `INCONCLUSIVE` or `NEGATIVE`.
4. **Deterministic Mock vs. Real Runner Isolation**: Built a deterministic, seedable mock runner producing realistic AST diffs, pytest logs, and token counts. Allows offline, reproducible evaluation without external API credentials.
5. **Enforcing Small-Sample Guardrails**: Benchmark suites with $N < 10$ tasks or non-replicated runs are explicitly flagged with `RULE_SMALL_SAMPLE_SIZE`, preventing premature certainty on anecdotal runs.

## 3. What Was Cut & Why
- **Real-Time Web Dashboard**: A CLI and standalone HTML report provide complete reproducibility and git-trackable artifacts without server overhead or security vulnerabilities.
- **Complex Statistical Significance Models (p-values / t-tests)**: Standard t-tests assume normal distributions. For small task counts ($N \le 20$), p-values provide an illusion of rigor. Instead, we use transparent sample size thresholds and descriptive bounds (mean, median, min/max).
- **Automated Code Mutation**: Dynamically generating synthetic mutations introduced flaky AST compilation failures, distracting from evaluating actual harness changes.

## 4. When I Did Not Trust My Own Tool's Result
During early testing of Task 01 (pagination), the candidate harness scored a 100% pass rate because `tests/test_users.py` passed cleanly. Yet upon manual code inspection (`harness-eval inspect task-01`), the candidate had returned a dictionary payload unconditionally, breaking existing callers that expected a flat list when `page_size=None`. The tool declared success because existing tests only exercised the paginated path.

## 5. What Was Done in Response
1. Introduced **Acceptance Criteria Verification** separate from test status, explicitly verifying backward compatibility contracts.
2. Added **Holdout Verification Tests** executed independently of repository test suites.
3. Added the `harness-eval inspect <task_id>` command, ensuring engineers can quickly audit diffs and individual criterion scores before accepting a decision.
