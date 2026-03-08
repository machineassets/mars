"""
Tests for mars.core.validation — three-layer record validation.
"""

import copy
import json
from pathlib import Path

import pytest

from mars.core.validation import validate_record

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def load_example(filename: str) -> dict:
    with open(EXAMPLES_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# All three canonical examples must pass with zero errors
# ---------------------------------------------------------------------------

class TestExamplesPassValidation:
    def test_humanoid_factory_zero_errors(self):
        record = load_example("humanoid_factory_example.json")
        errors = validate_record(record)
        assert errors == [], f"humanoid_factory_example failed validation:\n" + "\n".join(errors)

    def test_warehouse_robot_zero_errors(self):
        record = load_example("warehouse_robot_example.json")
        errors = validate_record(record)
        assert errors == [], f"warehouse_robot_example failed validation:\n" + "\n".join(errors)

    def test_amr_logistics_zero_errors(self):
        record = load_example("amr_logistics_example.json")
        errors = validate_record(record)
        assert errors == [], f"amr_logistics_example failed validation:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# Layer 2 — constraint: tasks_attempted must equal completed+failed+partial
# ---------------------------------------------------------------------------

class TestTaskSumConstraint:
    def test_wrong_task_sum_returns_constraint_error(self):
        record = load_example("humanoid_factory_example.json")
        # tasks_completed=13671, tasks_failed=588, tasks_partial=441 → sum=14700
        # Deliberately break by changing tasks_attempted to a wrong value
        record["task_metrics"]["tasks_attempted"] = 14800  # wrong: should be 14700
        errors = validate_record(record)
        assert len(errors) > 0, "Expected constraint error for wrong task sum"
        constraint_errors = [e for e in errors if "[constraint]" in e and "task" in e.lower()]
        assert len(constraint_errors) > 0, (
            f"Expected a task-sum constraint error, got:\n" + "\n".join(errors)
        )


# ---------------------------------------------------------------------------
# Layer 2 — constraint: autonomy_score + intervention_rate must equal 1.0 ±0.001
# ---------------------------------------------------------------------------

class TestAutonomyConstraint:
    def test_autonomy_sum_1_05_returns_constraint_error(self):
        record = load_example("humanoid_factory_example.json")
        # Set autonomy_score=0.95, intervention_rate=0.10 → sum=1.05, deviation=0.05
        record["operational_metrics"]["autonomy_score"] = 0.95
        record["operational_metrics"]["intervention_rate"] = 0.10
        errors = validate_record(record)
        assert len(errors) > 0, "Expected constraint error for autonomy sum = 1.05"
        constraint_errors = [e for e in errors if "[constraint]" in e and "autonomy" in e.lower()]
        assert len(constraint_errors) > 0, (
            f"Expected an autonomy-sum constraint error, got:\n" + "\n".join(errors)
        )


# ---------------------------------------------------------------------------
# Layer 3 — non-negative: negative uptime_hours must be flagged
# ---------------------------------------------------------------------------

class TestNonNegativeChecks:
    def test_negative_uptime_hours_returns_error(self):
        record = load_example("humanoid_factory_example.json")
        record["operational_metrics"]["uptime_hours"] = -5.0
        errors = validate_record(record)
        assert len(errors) > 0, "Expected non-negative error for uptime_hours = -5.0"
        non_neg_errors = [e for e in errors if "[non-negative]" in e and "uptime_hours" in e]
        assert len(non_neg_errors) > 0, (
            f"Expected a non-negative error for uptime_hours, got:\n" + "\n".join(errors)
        )

    def test_negative_purchase_price_returns_error(self):
        record = load_example("humanoid_factory_example.json")
        record["financial_metrics"]["purchase_price"] = -1000
        errors = validate_record(record)
        non_neg_errors = [e for e in errors if "[non-negative]" in e and "purchase_price" in e]
        assert len(non_neg_errors) > 0, (
            f"Expected a non-negative error for purchase_price, got:\n" + "\n".join(errors)
        )

    def test_negative_collision_events_returns_error(self):
        record = load_example("humanoid_factory_example.json")
        record["stability_safety"]["collision_events"] = -3
        errors = validate_record(record)
        non_neg_errors = [e for e in errors if "[non-negative]" in e and "collision_events" in e]
        assert len(non_neg_errors) > 0, (
            f"Expected a non-negative error for collision_events, got:\n" + "\n".join(errors)
        )
