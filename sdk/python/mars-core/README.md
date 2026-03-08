# mars-core

Canonical formula implementation for MARS v0.9

The single source of truth for all Machine Assets Reporting Standard calculations.
Browser validator, Python SDK, ROS2 bridge, and dashboard all depend on this library.

## Installation

```bash
pip install -e .
```

## Run tests

```bash
pytest
```

## Quick start

```python
import json
from mars import compute_am_roi, compute_mrs, check_sla_status

with open("examples/humanoid_factory_example.json") as f:
    record = json.load(f)

print(f"AM-ROI:     {compute_am_roi(record):.4f}")   # → 0.7499
print(f"MRS:        {compute_mrs(record):.4f}")       # → 0.8752
print(f"SLA status: {check_sla_status(record)['sla_status']}")  # → compliant
```

## Reference output

| Example                    | AM-ROI | MRS   | SLA Status |
|----------------------------|--------|-------|------------|
| humanoid_factory_example   | 0.750  | 0.875 | compliant  |
| warehouse_robot_example    | 0.844  | 0.787 | compliant  |
| amr_logistics_example      | 2.40   | 0.930 | compliant  |

## Formulas

| Function              | Formula |
|-----------------------|---------|
| `compute_am_roi`      | `[(R + HLE×DF) × TSR × AS] / TCO_annual` |
| `compute_mrs`         | `(TSR×0.30) + (AS×0.25) + (MTBI_norm×0.20) + (Safety_norm×0.25)` |
| `compute_safety_score`| `100 × [(1−fall_rate)×0.35 + (1−collision_rate)×0.35 + (1−near_miss_rate)×0.20 + iso_factor×0.10]` |
| `compute_rsv`         | `purchase_price × (1−cumulative_depreciation) × condition_factor × model_factor` |
| `check_sla_status`    | Six-threshold RaaS SLA check (TSR, uptime, AS, MTBI, vision, collision rate) |
