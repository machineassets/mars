"""
mars-core — Canonical formula implementation for MARS v0.9.
Single source of truth for all MARS calculations.
"""

from mars.core.formulas import (
    compute_am_roi,
    compute_mrs,
    compute_safety_score,
    compute_rsv,
    check_sla_status,
)
from mars.core.validation import validate_record
from mars.core.schema_loader import load_schema

__version__ = "0.9.0"
__all__ = [
    "compute_am_roi",
    "compute_mrs",
    "compute_safety_score",
    "compute_rsv",
    "check_sla_status",
    "validate_record",
    "load_schema",
]
