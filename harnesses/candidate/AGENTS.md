# Candidate Agent Guidelines

## Quality Invariants
1. **Type Annotations**: Always annotate function signatures and return types explicitly.
2. **Backward Compatibility**: Never break existing callers. If adding parameters, make them optional.
3. **Acceptance Criteria**: Verify every acceptance criterion listed in the task description before finalizing.
4. **Edge Cases & Error Handling**: Test boundary conditions (empty inputs, negative values, duplicate keys) and raise appropriate exceptions.
5. **Pre-commit Check**: Run the pre-commit lint hook before concluding.
