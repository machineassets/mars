"""
Regression tests for mars.core.formulas against the three canonical MARS examples.

Ground truth values are taken from the _comment fields in each example JSON.
All expected values must match without adjusting them to fit a wrong implementation.
"""

import json
from pathlib import Path

import pytest

from mars.core.formulas import (
    check_sla_status,
    compute_am_roi,
    compute_mrs,
    compute_rsv,
    compute_safety_score,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def load_example(filename: str) -> dict:
    with open(EXAMPLES_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# humanoid_factory_example.json — Figure 02 @ BMW Spartanburg
# _comment_am_roi: "0.7499"  → expected 0.750 ±0.001
# _comment_mrs:    "0.8752"  → expected 0.875 ±0.001
# ---------------------------------------------------------------------------

class TestHumanoidFactory:
    @pytest.fixture(scope="class")
    def record(self):
        return load_example("humanoid_factory_example.json")

    def test_am_roi(self, record):
        result = compute_am_roi(record)
        assert abs(result - 0.750) <= 0.001, (
            f"compute_am_roi(humanoid_factory) = {result:.6f}, expected 0.750 ±0.001"
        )

    def test_mrs(self, record):
        result = compute_mrs(record)
        assert abs(result - 0.875) <= 0.001, (
            f"compute_mrs(humanoid_factory) = {result:.6f}, expected 0.875 ±0.001"
        )

    def test_sla_status_compliant(self, record):
        result = check_sla_status(record)
        assert result["sla_status"] == "compliant", (
            f"SLA status = {result['sla_status']!r}, expected 'compliant'"
        )

    def test_sla_no_breaches(self, record):
        result = check_sla_status(record)
        assert result["active_breach_metrics"] == [], (
            f"active_breach_metrics = {result['active_breach_metrics']}, expected []"
        )


# ---------------------------------------------------------------------------
# warehouse_robot_example.json — Digit @ TMMC (Toyota Manufacturing Canada)
# _comment_am_roi: "0.8445 → stored 0.844"  → expected 0.844 ±0.001
# _comment_mrs:    "0.78660 → stored 0.787"  → expected 0.787 ±0.001
# ---------------------------------------------------------------------------

class TestWarehouseRobot:
    @pytest.fixture(scope="class")
    def record(self):
        return load_example("warehouse_robot_example.json")

    def test_am_roi(self, record):
        result = compute_am_roi(record)
        assert abs(result - 0.844) <= 0.001, (
            f"compute_am_roi(warehouse_robot) = {result:.6f}, expected 0.844 ±0.001"
        )

    def test_mrs(self, record):
        result = compute_mrs(record)
        assert abs(result - 0.787) <= 0.001, (
            f"compute_mrs(warehouse_robot) = {result:.6f}, expected 0.787 ±0.001"
        )

    def test_sla_status_compliant(self, record):
        result = check_sla_status(record)
        assert result["sla_status"] == "compliant", (
            f"SLA status = {result['sla_status']!r}, expected 'compliant'"
        )


# ---------------------------------------------------------------------------
# amr_logistics_example.json — MiR200 @ Rotterdam
# _comment_am_roi: "2.4024 → stored 2.40"   → expected 2.40 ±0.01
# _comment_mrs:    "0.92983 → stored 0.930"  → expected 0.930 ±0.001
# ---------------------------------------------------------------------------

class TestAMRLogistics:
    @pytest.fixture(scope="class")
    def record(self):
        return load_example("amr_logistics_example.json")

    def test_am_roi(self, record):
        result = compute_am_roi(record)
        assert abs(result - 2.40) <= 0.01, (
            f"compute_am_roi(amr_logistics) = {result:.6f}, expected 2.40 ±0.01"
        )

    def test_mrs(self, record):
        result = compute_mrs(record)
        assert abs(result - 0.930) <= 0.001, (
            f"compute_mrs(amr_logistics) = {result:.6f}, expected 0.930 ±0.001"
        )

    def test_sla_status_compliant(self, record):
        result = check_sla_status(record)
        assert result["sla_status"] == "compliant", (
            f"SLA status = {result['sla_status']!r}, expected 'compliant'"
        )


# ---------------------------------------------------------------------------
# compute_safety_score spot-checks against _comment_safety_score ground truth
# ---------------------------------------------------------------------------

class TestSafetyScore:
    def test_humanoid_factory_safety_score(self):
        """
        _comment: fall_rate=0, collision_rate=0.16447, near_miss_rate=0.32895,
                  iso_factor=1.0. Result=87.66
        """
        record = load_example("humanoid_factory_example.json")
        result = compute_safety_score(record)
        assert abs(result - 87.66) <= 0.05, (
            f"compute_safety_score(humanoid_factory) = {result:.4f}, expected 87.66 ±0.05"
        )

    def test_warehouse_robot_safety_score(self):
        """
        _comment: fall_rate=0.14793, collision_rate=0.44379, near_miss_rate=0.29586,
                  iso_factor=1.0. Result=73.37
        """
        record = load_example("warehouse_robot_example.json")
        result = compute_safety_score(record)
        assert abs(result - 73.37) <= 0.05, (
            f"compute_safety_score(warehouse_robot) = {result:.4f}, expected 73.37 ±0.05"
        )

    def test_amr_logistics_safety_score(self):
        """
        _comment: fall_rate=0, collision_rate=0.28090, near_miss_rate=0.56180,
                  iso_factor=1.0. Result=78.93
        """
        record = load_example("amr_logistics_example.json")
        result = compute_safety_score(record)
        assert abs(result - 78.93) <= 0.05, (
            f"compute_safety_score(amr_logistics) = {result:.4f}, expected 78.93 ±0.05"
        )


# ---------------------------------------------------------------------------
# compute_rsv spot-check — humanoid_factory uses default model_factor=0.75
# _comment_rsv: "RSV=250000×0.84449×0.918×0.75=145,350"
# ---------------------------------------------------------------------------

class TestRSV:
    def test_humanoid_factory_rsv(self):
        record = load_example("humanoid_factory_example.json")
        result = compute_rsv(record, model_factor=0.75)
        assert abs(result - 145350) <= 200, (
            f"compute_rsv(humanoid_factory, model_factor=0.75) = {result:.2f}, "
            f"expected 145350 ±200"
        )
