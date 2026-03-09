"""MARSBridge — maps ROS2 topic payloads to MARS v0.9 record fields.

No live ROS2 runtime is required.  The bridge uses a lightweight mock
subscriber interface so the module can be imported and tested anywhere.
"""

from __future__ import annotations

import copy
import datetime
import functools
from typing import Any, Callable

from .config_loader import ConfigLoader


# ---------------------------------------------------------------------------
# Mock ROS2 subscriber interface
# ---------------------------------------------------------------------------

class MockSubscription:
    """Holds a callback registered for a topic (no ROS2 runtime needed)."""

    def __init__(self, topic: str, callback: Callable[[dict], None]) -> None:
        self.topic = topic
        self.callback = callback

    def inject(self, message: dict) -> None:
        """Simulate receiving a ROS2 message on this topic."""
        self.callback(message)


class MockNode:
    """Minimal stand-in for a rclpy Node that collects subscriptions."""

    def __init__(self, node_name: str = "mars_bridge_node") -> None:
        self.node_name = node_name
        self._subscriptions: dict[str, MockSubscription] = {}

    def create_subscription(
        self,
        topic: str,
        callback: Callable[[dict], None],
        *_args,
        **_kwargs,
    ) -> MockSubscription:
        sub = MockSubscription(topic, callback)
        self._subscriptions[topic] = sub
        return sub

    def inject(self, topic: str, message: dict) -> None:
        """Push a test message into any registered subscriber for *topic*."""
        if topic not in self._subscriptions:
            raise KeyError(f"No subscription registered for topic '{topic}'")
        self._subscriptions[topic].inject(message)

    @property
    def subscriptions(self) -> dict[str, MockSubscription]:
        return self._subscriptions


# ---------------------------------------------------------------------------
# MARS v0.9 record skeleton
# ---------------------------------------------------------------------------

def _empty_mars_record(robot_id: str, mars_version: str = "0.9") -> dict[str, Any]:
    return {
        "schema_version": mars_version,
        "robot_id": robot_id,
        "timestamp_utc": None,
        "operational_metrics": {
            "autonomy_score": None,
            "uptime_hours": None,
        },
        "task_metrics": {
            "tasks_completed": None,
            "tasks_attempted": None,
            "task_success_ratio": None,
        },
        "energy_metrics": {
            "battery_health_pct": None,
        },
        "stability_safety": {
            "collision_events": None,
        },
    }


# ---------------------------------------------------------------------------
# Nested-key helpers
# ---------------------------------------------------------------------------

def _set_nested(record: dict, dotted_key: str, value: Any) -> None:
    """Set *value* at a dotted path inside *record*, creating dicts as needed."""
    parts = dotted_key.split(".")
    node = record
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def _get_nested(record: dict, dotted_key: str, default: Any = None) -> Any:
    parts = dotted_key.split(".")
    node = record
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


# ---------------------------------------------------------------------------
# Extractor registry
# ---------------------------------------------------------------------------

# Maps topic → callable(message) → {mars_field: value, ...}
_EXTRACTORS: dict[str, Callable[[dict], dict[str, Any]]] = {}


def _register(topic: str):
    def decorator(fn):
        _EXTRACTORS[topic] = fn
        return fn
    return decorator


@_register("/mir/robot_state")
def _extract_robot_state(msg: dict) -> dict[str, Any]:
    # autonomy_score expressed as 0-100; source field: 'autonomy_level' (0.0–1.0)
    raw = msg.get("autonomy_level", None)
    score = round(float(raw) * 100, 2) if raw is not None else None
    return {"operational_metrics.autonomy_score": score}


@_register("/mir/mission_results")
def _extract_mission_results(msg: dict) -> dict[str, Any]:
    completed = msg.get("missions_completed", None)
    attempted = msg.get("missions_attempted", None)
    ratio: float | None = None
    if attempted and attempted > 0 and completed is not None:
        ratio = round(completed / attempted, 4)
    return {
        "task_metrics.tasks_completed": completed,
        "task_metrics.tasks_attempted": attempted,
        "task_metrics.task_success_ratio": ratio,
    }


@_register("/mir/battery_state")
def _extract_battery_state(msg: dict) -> dict[str, Any]:
    pct = msg.get("percentage", None)
    if pct is not None:
        pct = round(float(pct) * 100, 1) if pct <= 1.0 else round(float(pct), 1)
    return {"energy_metrics.battery_health_pct": pct}


@_register("/mir/safety_state")
def _extract_safety_state(msg: dict) -> dict[str, Any]:
    return {"stability_safety.collision_events": msg.get("collision_count", None)}


@_register("/diagnostics")
def _extract_diagnostics(msg: dict) -> dict[str, Any]:
    return {"operational_metrics.uptime_hours": msg.get("uptime_hours", None)}


# ---------------------------------------------------------------------------
# MARSBridge
# ---------------------------------------------------------------------------

class MARSBridge:
    """Subscribes to ROS2 topics and maps payloads to MARS v0.9 record fields.

    Parameters
    ----------
    config_path:
        Path to a YAML mapping config (e.g. ``config/mir200_mapping.yaml``).
    node:
        Optional ``MockNode`` (or real rclpy Node) to register subscriptions on.
        If omitted a fresh ``MockNode`` is created automatically.
    """

    def __init__(
        self,
        config_path: str,
        node: MockNode | None = None,
    ) -> None:
        loader = ConfigLoader(config_path)
        self._cfg = loader.load()

        self._robot_id: str = self._cfg["robot_id"]
        self._mars_version: str = str(self._cfg.get("mars_version", "0.9"))
        self._mappings: list[dict] = self._cfg["mappings"]

        self._record: dict[str, Any] = _empty_mars_record(
            self._robot_id, self._mars_version
        )

        self._node: MockNode = node or MockNode()
        self._subscriptions: list[MockSubscription] = []

        self._register_subscriptions()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _register_subscriptions(self) -> None:
        seen: set[str] = set()
        for entry in self._mappings:
            topic: str = entry["topic"]
            if topic in seen:
                continue
            seen.add(topic)
            callback = functools.partial(self._on_message, topic=topic)
            sub = self._node.create_subscription(topic, callback)
            self._subscriptions.append(sub)

    # ------------------------------------------------------------------
    # Message handler
    # ------------------------------------------------------------------

    def _on_message(self, message: dict, *, topic: str) -> None:
        """Called whenever a message arrives on *topic*."""
        extractor = _EXTRACTORS.get(topic)
        if extractor:
            updates = extractor(message)
            for field, value in updates.items():
                _set_nested(self._record, field, value)
        else:
            # Fallback: use the raw mapping entries for this topic
            for entry in self._mappings:
                if entry["topic"] != topic:
                    continue
                source_field: str = entry.get("source_field", "")
                mars_field: str = entry["mars_field"]
                value = message.get(source_field, None) if source_field else None
                _set_nested(self._record, mars_field, value)

        self._record["timestamp_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

    # ------------------------------------------------------------------
    # Injection helper (testing / simulation)
    # ------------------------------------------------------------------

    def inject(self, topic: str, message: dict) -> None:
        """Simulate a ROS2 message arriving on *topic* (for tests/simulation)."""
        self._node.inject(topic, message)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------

    def get_record(self) -> dict[str, Any]:
        """Return a deep copy of the current MARS record."""
        return copy.deepcopy(self._record)

    @property
    def node(self) -> MockNode:
        return self._node
