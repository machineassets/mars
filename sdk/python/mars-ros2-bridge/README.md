# mars-ros2-bridge

**Sprint 3 — MARS v0.9 ROS2 Bridge Skeleton**

A Python bridge that subscribes to ROS2 topics, maps their payloads to MARS v0.9 performance record fields, and publishes valid MARS JSON records. No live ROS2 installation required — a mock subscriber interface lets the bridge run and be tested anywhere.

---

## Project Structure

```
mars-ros2-bridge/
├── mars_bridge/
│   ├── __init__.py
│   ├── bridge.py          # MARSBridge — topic subscription + field mapping
│   ├── config_loader.py   # YAML config loading + validation
│   └── publisher.py       # MARS JSON record output
├── config/
│   ├── mir200_mapping.yaml    # MiR200 AMR field mapping
│   └── generic_mapping.yaml  # Template for any ROS2 robot
├── tests/
│   ├── __init__.py
│   ├── test_config_loader.py
│   └── test_bridge_mapping.py
├── docs/
│   └── MARS_OpenRobOps_Profile.md
└── README.md
```

---

## Quick Start

### Install dependencies

```bash
pip install pyyaml pytest
```

### Run tests

```bash
pytest tests/ -v
```

### Basic usage

```python
from mars_bridge import MARSBridge, MARSPublisher

bridge = MARSBridge("config/mir200_mapping.yaml")

# Simulate a ROS2 message arriving on a topic
bridge.inject("/mir/robot_state", {"autonomy_level": 0.92})
bridge.inject("/mir/mission_results", {"missions_completed": 45, "missions_attempted": 48})
bridge.inject("/mir/battery_state", {"percentage": 0.78})
bridge.inject("/mir/safety_state", {"collision_count": 0})
bridge.inject("/diagnostics", {"uptime_hours": 8.5})

record = bridge.get_record()

publisher = MARSPublisher()
publisher.publish(record)
```

---

## MiR200 Topic Mapping

| ROS2 Topic | MARS Field |
|---|---|
| `/mir/robot_state` → `autonomy_level` | `operational_metrics.autonomy_score` |
| `/mir/mission_results` → `missions_completed` | `task_metrics.tasks_completed` |
| `/mir/mission_results` → `missions_attempted` | `task_metrics.tasks_attempted` |
| `/mir/mission_results` (computed) | `task_metrics.task_success_ratio` |
| `/mir/battery_state` → `percentage` | `energy_metrics.battery_health_pct` |
| `/mir/safety_state` → `collision_count` | `stability_safety.collision_events` |
| `/diagnostics` → `uptime_hours` | `operational_metrics.uptime_hours` |

---

## MARS v0.9 Record Schema

```json
{
  "schema_version": "0.9",
  "robot_id": "mir200-001",
  "timestamp_utc": "2025-01-01T10:00:00Z",
  "operational_metrics": {
    "autonomy_score": 92.0,
    "uptime_hours": 8.5
  },
  "task_metrics": {
    "tasks_completed": 45,
    "tasks_attempted": 48,
    "task_success_ratio": 0.9375
  },
  "energy_metrics": {
    "battery_health_pct": 78.0
  },
  "stability_safety": {
    "collision_events": 0
  }
}
```

---

## Adding a New Robot

1. Copy `config/generic_mapping.yaml`
2. Replace `robot_id`, topic names, and `source_field` values
3. Point `MARSBridge` at your new config:

```python
bridge = MARSBridge("config/my_robot_mapping.yaml")
```

If your robot has topics that need custom extraction logic (e.g. unit conversions), add an extractor function in `bridge.py` using the `@_register("/your/topic")` decorator.

---

## Architecture

```
ROS2 Topics  ──►  MockNode / rclpy Node
                       │
                  MARSBridge._on_message()
                       │
                  Extractor functions    ◄── @_register decorators
                       │
                  MARS record dict       ◄── config/mir200_mapping.yaml
                       │
                  MARSPublisher.publish()
                       │
                  JSON output (stdout / file / API)
```

## Related Documents

- [`docs/MARS_OpenRobOps_Profile.md`](docs/MARS_OpenRobOps_Profile.md) — MARS positioning relative to OpenRobOps/ORO
