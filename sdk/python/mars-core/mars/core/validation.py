"""
Three-layer MARS record validation.

Layer 1 — JSON Schema (Draft 7) structural validation.
Layer 2 — Internal consistency constraints derived from the schema.
Layer 3 — Non-negative field checks.
"""

import calendar
import json
from datetime import datetime
from typing import Any

import jsonschema

from mars.core.schema_loader import load_schema


def _strip_comment_keys(obj: Any) -> Any:
    """Recursively remove _comment_* documentation keys before schema validation.

    The MARS example files intentionally include _comment_* fields as inline
    documentation. These are not part of the data model and must be removed
    before JSON Schema validation so that additionalProperties checks
    (if any) do not flag them.
    """
    if isinstance(obj, dict):
        return {
            k: _strip_comment_keys(v)
            for k, v in obj.items()
            if not k.startswith("_comment")
        }
    if isinstance(obj, list):
        return [_strip_comment_keys(item) for item in obj]
    return obj


def _field_path(path) -> str:
    """Convert a jsonschema error path deque to a dot-separated string."""
    parts = list(path)
    if not parts:
        return "(root)"
    return ".".join(str(p) for p in parts)


def _layer1_schema(record: dict) -> list[str]:
    """Run JSON Schema Draft 7 validation; return human-readable error strings."""
    schema = load_schema()
    instance = _strip_comment_keys(record)
    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for err in validator.iter_errors(instance):
        path = _field_path(err.absolute_path)
        errors.append(f"[schema] {path}: {err.message}")
    return errors


def _layer2_constraints(record: dict) -> list[str]:
    """Check internal consistency constraints. Return human-readable error strings."""
    errors = []

    # --- Task sum constraint ---
    tm = record.get("task_metrics", {})
    attempted = tm.get("tasks_attempted")
    completed = tm.get("tasks_completed", 0)
    failed = tm.get("tasks_failed", 0)
    partial = tm.get("tasks_partial", 0)
    if attempted is not None:
        expected_sum = completed + failed + partial
        if attempted != expected_sum:
            errors.append(
                f"[constraint] task_metrics.tasks_attempted ({attempted}) must equal "
                f"tasks_completed + tasks_failed + tasks_partial "
                f"({completed} + {failed} + {partial} = {expected_sum})"
            )

    # --- Autonomy score + intervention rate == 1.0 ---
    om = record.get("operational_metrics", {})
    autonomy = om.get("autonomy_score")
    intervention = om.get("intervention_rate")
    if autonomy is not None and intervention is not None:
        deviation = abs(autonomy + intervention - 1.0)
        if deviation > 0.001:
            errors.append(
                f"[constraint] operational_metrics: autonomy_score ({autonomy}) + "
                f"intervention_rate ({intervention}) = {autonomy + intervention:.4f}, "
                f"must be 1.000 ± 0.001 (deviation = {deviation:.4f})"
            )

    # --- Monthly period uptime + downtime == days_in_month × 24 ---
    rp = record.get("record_period", {})
    if rp.get("period_type") == "monthly":
        period_start_str = rp.get("period_start", "")
        uptime = om.get("uptime_hours")
        downtime = om.get("downtime_hours")
        if period_start_str and uptime is not None and downtime is not None:
            try:
                dt = datetime.fromisoformat(period_start_str.replace("Z", "+00:00"))
                days_in_month = calendar.monthrange(dt.year, dt.month)[1]
                expected_hours = days_in_month * 24.0
                actual_hours = uptime + downtime
                if abs(actual_hours - expected_hours) > 0.01:
                    errors.append(
                        f"[constraint] operational_metrics: uptime_hours ({uptime}) + "
                        f"downtime_hours ({downtime}) = {actual_hours}, but period "
                        f"{dt.year}-{dt.month:02d} has {days_in_month} days "
                        f"= {expected_hours:.1f} expected hours"
                    )
            except (ValueError, AttributeError):
                pass  # Malformed date; will be caught by schema validation

    # --- Hallucination rate consistency ---
    ai = record.get("ai_performance", {})
    hallucination_rate = ai.get("hallucination_rate")
    hallucination_events = ai.get("hallucination_events")
    tasks_attempted = tm.get("tasks_attempted")
    if (
        hallucination_rate is not None
        and hallucination_events is not None
        and tasks_attempted
    ):
        expected_rate = hallucination_events / tasks_attempted
        if abs(hallucination_rate - expected_rate) > 0.0001:
            errors.append(
                f"[constraint] ai_performance.hallucination_rate ({hallucination_rate}) "
                f"must equal hallucination_events / tasks_attempted "
                f"({hallucination_events} / {tasks_attempted} = {expected_rate:.6f}), "
                f"tolerance 0.0001"
            )

    return errors


_NON_NEGATIVE_FIELDS: list[tuple[str, str]] = [
    ("operational_metrics", "uptime_hours"),
    ("operational_metrics", "downtime_hours"),
    ("task_metrics", "tasks_attempted"),
    ("task_metrics", "tasks_completed"),
    ("task_metrics", "tasks_failed"),
    ("task_metrics", "tasks_partial"),
    ("operational_metrics", "incident_count"),
    ("stability_safety", "falls_detected"),
    ("stability_safety", "collision_events"),
    ("stability_safety", "near_miss_events"),
    ("financial_metrics", "purchase_price"),
    ("financial_metrics", "tco_annual"),
    ("financial_metrics", "hle_annual"),
]


def _layer3_non_negative(record: dict) -> list[str]:
    """Flag any field that contains a negative value. Return error strings."""
    errors = []
    for section, field in _NON_NEGATIVE_FIELDS:
        value = record.get(section, {}).get(field)
        if value is not None and value < 0:
            errors.append(
                f"[non-negative] {section}.{field} = {value}: must be ≥ 0"
            )
    return errors


def validate_record(record: dict) -> list[str]:
    """Validate a MARS record through three layers of checks.

    Layer 1 — JSON Schema Draft 7 structural validation.
    Layer 2 — Internal consistency constraints:
               task sum, autonomy/intervention sum, monthly period hours,
               hallucination rate derivation.
    Layer 3 — Non-negative field checks for counts, hours, and monetary values.

    Args:
        record: A parsed MARS v0.9 record as a Python dict.

    Returns:
        list[str] — Human-readable error messages. Empty list means the record
        passed all validation layers.
    """
    errors: list[str] = []
    errors.extend(_layer1_schema(record))
    errors.extend(_layer2_constraints(record))
    errors.extend(_layer3_non_negative(record))
    return errors
