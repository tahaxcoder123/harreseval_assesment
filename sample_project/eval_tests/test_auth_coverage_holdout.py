"""Holdout verification for auth test suite (Task 4)."""
import os
import ast
import pytest


def test_auth_test_file_exists_and_has_tests():
    auth_test_file = os.path.join(os.path.dirname(__file__), "..", "tests", "test_auth.py")
    assert os.path.exists(auth_test_file), "tests/test_auth.py must exist"

    with open(auth_test_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    # Count test functions or test classes
    test_funcs = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert len(test_funcs) >= 3, f"Expected at least 3 test functions, found: {test_funcs}"
