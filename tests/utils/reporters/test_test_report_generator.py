import json
import os
from pathlib import Path

import pytest

from utilities.reporters.test_report_generator.test_report_generator import TestReportGenerator


@pytest.fixture
def sol_and_dest(tmp_path):
    test_solution = tmp_path / "test_sol.json"
    dest = Path(os.path.dirname(__file__)) / "test_files"
    test_solution.write_text(json.dumps({
        "username": "mock",
        "test_id": "1234",
        "answers": {
            "question 1": "sol 1",
            "question 2": "sol 2",
            "question 3": "sol 3",
            "question 4": "sol 4",
            "question 5": "sol 5",
            "question 6": {"options_selected": {"op1": False, "op2": True, "op3": True}, "explanation": "exp 6"},
            "question 7": {"options_selected": {"op1": False, "op2": True, "op3": True}, "explanation": "exp 7"},
            "question 8": {"options_selected": {"op1": False, "op2": True, "op3": False}, "explanation": "exp 8"},
            "question 9": {"options_selected": {"op1": False, "op2": False, "op3": True}, "explanation": "exp 9"},
            "question 10": {"options_selected": {"op1": True, "op2": True, "op3": True}, "explanation": "exp 10"},
        }
    }))
    return test_solution, dest


def test_test_report_generator_generate_report(sol_and_dest):
    sol, dest = sol_and_dest
    TestReportGenerator().generate_report(sol, dest / "actual_report.html")

    actual, expected = (dest / "actual_report.html").read_text().split("\n"), \
                       (dest / "expected_report.html").read_text().split("\n")

    actual = [line.strip() for line in actual]
    expected = [line.strip() for line in expected]

    assert actual == expected
