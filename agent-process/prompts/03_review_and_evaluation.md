# Review & Evaluation Prompt

## Goal
Validate the evaluation engine through comprehensive automated testing, CLI inspection, and edge case audits.

## Focus Areas
1. Test coverage for:
   - Config loading and missing file error handling
   - Harness diffing
   - Benchmark loading and task filtering
   - Dimension scoring edge cases (empty tests, missing holdouts, empty criteria)
   - Comparator task outcomes (IMPROVED, REGRESSED, UNCHANGED)
   - Decision logic triggers (clear positive, high cost trade-off, small sample size, regressions, degradation)
   - End-to-end CLI commands (`evaluate`, `inspect`, `diff`)
2. Audit report outputs:
   - Verify numbers in terminal summary match `report.json` and `report.html` exactly.
   - Verify raw artifacts exist in `runs/task-xxx/`.
3. Check platform compatibility (Windows console character encoding, paths).
