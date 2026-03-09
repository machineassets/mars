"""Tests for MARSBridge topic-to-field mapping and MARSPublisher."""

import io
import json
import os

import pytest

from mars_bridge.bridge import MARSBridge, MockNode, _set_nested, _get_nested
from mars_bridge.publisher import MARSPublisher


MIR200_CONFIG = os.path.join(
    os.path.dirname(__file__), "..", "config", "mir200_mapping.yaml"
)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

class TestNestedHelpers:
    def test_set_and_get_nested_single_level(self):
        d = {}
        _set_nested(d, "foo", 42)
        assert _get_nested(d, "foo") == 42

    def test_set_and_get_nested_deep(self):
        d = {}
        _set_nested(d, "a.b.c", "hello")
        assert _get_nested(d, "a.b.c") == "hello"
        assert _get_nested(d, "a.b") == {"c": "hello"}

    def test_get_nested_missing_returns_default(self):
        d = {"x": 1}
        assert _get_nested(d, "x.y.z", default="N/A") == "N/A"


# ---------------------------------------------------------------------------
# MockNode
# ---------------------------------------------------------------------------

class TestMockNode:
    def test_inject_triggers_callback(self):
        node = MockNode()
        received = []
        node.create_subscription("/test", lambda msg: received.append(msg))
        node.inject("/test", {"value": 7})
        assert received == [{"value": 7}]

    def test_inject_unknown_topic_raises(self):
        node = MockNode()
        with pytest.raises(KeyError):
            node.inject("/no_such_topic", {})

    def test_multiple_subscriptions(self):
        node = MockNode()
        results = {}
        node.create_subscription("/a", lambda m: results.update({"a": m["v"]}))
        node.create_subscription("/b", lambda m: results.update({"b": m["v"]}))
        node.inject("/a", {"v": 1})
        node.inject("/b", {"v": 2})
        assert results == {"a": 1, "b": 2}


# ---------------------------------------------------------------------------
# MARSBridge — topic injection tests
# ---------------------------------------------------------------------------

class TestMARSBridgeMapping:
    @pytest.fixture
    def bridge(self):
        return MARSBridge(MIR200_CONFIG)

    def test_robot_state_autonomy_score(self, bridge):
        bridge.inject("/mir/robot_state", {"autonomy_level": 0.85})
        record = bridge.get_record()
        assert record["operational_metrics"]["autonomy_score"] == pytest.approx(85.0)

    def test_robot_state_full_autonomy(self, bridge):
        bridge.inject("/mir/robot_state", {"autonomy_level": 1.0})
        assert bridge.get_record()["operational_metrics"]["autonomy_score"] == 100.0

    def test_robot_state_zero_autonomy(self, bridge):
        bridge.inject("/mir/robot_state", {"autonomy_level": 0.0})
        assert bridge.get_record()["operational_metrics"]["autonomy_score"] == 0.0

    def test_mission_results_all_fields(self, bridge):
        bridge.inject("/mir/mission_results", {
            "missions_completed": 18,
            "missions_attempted": 20,
        })
        tm = bridge.get_record()["task_metrics"]
        assert tm["tasks_completed"] == 18
        assert tm["tasks_attempted"] == 20
        assert tm["task_success_ratio"] == pytest.approx(0.9)

    def test_mission_results_perfect_score(self, bridge):
        bridge.inject("/mir/mission_results", {
            "missions_completed": 5,
            "missions_attempted": 5,
        })
        assert bridge.get_record()["task_metrics"]["task_success_ratio"] == 1.0

    def test_mission_results_zero_attempted_ratio_is_none(self, bridge):
        bridge.inject("/mir/mission_results", {
            "missions_completed": 0,
            "missions_attempted": 0,
        })
        assert bridge.get_record()["task_metrics"]["task_success_ratio"] is None

    def test_battery_state_fractional(self, bridge):
        bridge.inject("/mir/battery_state", {"percentage": 0.74})
        assert bridge.get_record()["energy_metrics"]["battery_health_pct"] == pytest.approx(74.0)

    def test_battery_state_percent_already(self, bridge):
        # Values > 1.0 are treated as already-percentage
        bridge.inject("/mir/battery_state", {"percentage": 80.0})
        assert bridge.get_record()["energy_metrics"]["battery_health_pct"] == pytest.approx(80.0)

    def test_safety_state_collision_events(self, bridge):
        bridge.inject("/mir/safety_state", {"collision_count": 3})
        assert bridge.get_record()["stability_safety"]["collision_events"] == 3

    def test_diagnostics_uptime(self, bridge):
        bridge.inject("/diagnostics", {"uptime_hours": 47.5})
        assert bridge.get_record()["operational_metrics"]["uptime_hours"] == 47.5

    def test_record_has_timestamp_after_injection(self, bridge):
        bridge.inject("/diagnostics", {"uptime_hours": 1.0})
        record = bridge.get_record()
        assert record["timestamp_utc"] is not None
        assert record["timestamp_utc"].endswith("Z")

    def test_record_schema_version(self, bridge):
        assert bridge.get_record()["schema_version"] == "0.9"

    def test_record_robot_id(self, bridge):
        assert bridge.get_record()["robot_id"] == "mir200-001"

    def test_get_record_returns_deep_copy(self, bridge):
        r1 = bridge.get_record()
        r1["robot_id"] = "tampered"
        r2 = bridge.get_record()
        assert r2["robot_id"] == "mir200-001"

    def test_sequential_injections_accumulate(self, bridge):
        bridge.inject("/mir/robot_state", {"autonomy_level": 0.9})
        bridge.inject("/mir/battery_state", {"percentage": 0.6})
        record = bridge.get_record()
        assert record["operational_metrics"]["autonomy_score"] == pytest.approx(90.0)
        assert record["energy_metrics"]["battery_health_pct"] == pytest.approx(60.0)


# ---------------------------------------------------------------------------
# MARSPublisher tests
# ---------------------------------------------------------------------------

class TestMARSPublisher:
    def _make_record(self, robot_id="test-bot"):
        return {
            "schema_version": "0.9",
            "robot_id": robot_id,
            "timestamp_utc": "2025-01-01T00:00:00Z",
            "operational_metrics": {"autonomy_score": 95.0, "uptime_hours": 10.0},
            "task_metrics": {
                "tasks_completed": 10,
                "tasks_attempted": 10,
                "task_success_ratio": 1.0,
            },
            "energy_metrics": {"battery_health_pct": 88.0},
            "stability_safety": {"collision_events": 0},
        }

    def test_publish_returns_valid_json(self):
        buf = io.StringIO()
        pub = MARSPublisher(stream=buf)
        record = self._make_record()
        result = pub.publish(record)
        parsed = json.loads(result)
        assert parsed["robot_id"] == "test-bot"

    def test_publish_writes_to_stream(self):
        buf = io.StringIO()
        pub = MARSPublisher(stream=buf)
        pub.publish(self._make_record())
        assert len(buf.getvalue()) > 0

    def test_to_json_no_stream_write(self):
        buf = io.StringIO()
        pub = MARSPublisher(stream=buf)
        record = self._make_record()
        result = pub.to_json(record)
        # to_json should NOT write to stream
        assert buf.getvalue() == ""
        assert json.loads(result)["schema_version"] == "0.9"

    def test_publish_raises_on_missing_robot_id(self):
        buf = io.StringIO()
        pub = MARSPublisher(stream=buf)
        bad_record = {"schema_version": "0.9"}
        with pytest.raises(ValueError, match="robot_id"):
            pub.publish(bad_record)

    def test_publish_raises_on_empty_robot_id(self):
        buf = io.StringIO()
        pub = MARSPublisher(stream=buf)
        bad_record = {"schema_version": "0.9", "robot_id": ""}
        with pytest.raises(ValueError):
            pub.publish(bad_record)

    def test_full_pipeline_bridge_to_publisher(self):
        """End-to-end: inject messages → get_record → publish → valid JSON."""
        bridge = MARSBridge(MIR200_CONFIG)
        bridge.inject("/mir/robot_state", {"autonomy_level": 0.95})
        bridge.inject("/mir/mission_results", {"missions_completed": 9, "missions_attempted": 10})
        bridge.inject("/mir/battery_state", {"percentage": 0.82})
        bridge.inject("/mir/safety_state", {"collision_count": 0})
        bridge.inject("/diagnostics", {"uptime_hours": 24.0})

        record = bridge.get_record()
        buf = io.StringIO()
        pub = MARSPublisher(stream=buf)
        json_str = pub.publish(record)

        out = json.loads(json_str)
        assert out["operational_metrics"]["autonomy_score"] == pytest.approx(95.0)
        assert out["task_metrics"]["task_success_ratio"] == pytest.approx(0.9)
        assert out["energy_metrics"]["battery_health_pct"] == pytest.approx(82.0)
        assert out["stability_safety"]["collision_events"] == 0
        assert out["operational_metrics"]["uptime_hours"] == 24.0
