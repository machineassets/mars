[README.md](https://github.com/user-attachments/files/25780648/README.md)
# sdk/

Official MARS client libraries.

## Available SDKs

| Language | Package | Status |
|----------|---------|--------|
| Python | `mars-python` | Coming Q2 2026 |
| TypeScript | `mars-ts` | Coming Q2 2026 |
| ROS2 | `mars-ros2` | Coming Q2 2026 |

## Python SDK (Preview)

```python
from mars import MARSRecord, compute_am_roi, compute_mrs

record = MARSRecord(
    machine_id="FIG02-BMW-SPB-001",
    vendor="Figure AI",
    model="Figure 02",
    deployment_environment="automotive_manufacturing"
)

record.operational_metrics.update(
    uptime_hours=1250,
    tasks_completed=89100,
    tasks_attempted=90000,
    incident_count=6
)

print(record.am_roi)   # 1.80
print(record.mrs)      # 0.87
print(record.to_json())
```

## Contributing

SDK contributions welcome. See [GOVERNANCE.md](../GOVERNANCE.md).
All SDK code is released under MIT License.
