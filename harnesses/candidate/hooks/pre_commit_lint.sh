#!/bin/bash
# Pre-commit hook to verify syntax and absence of forbidden patterns
echo "Running pre-commit check..."
python -m py_compile app/*.py tests/*.py || exit 1
echo "Pre-commit check passed."
