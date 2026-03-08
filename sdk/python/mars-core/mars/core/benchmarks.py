"""
MTBI benchmark table by deployment_type for MARS Risk Score computation.

Benchmarks represent the mean-time-between-incidents (hours) expected for
a well-operated robot in each deployment sector, used to normalise MTBI_norm
in the MRS formula.
"""

MTBI_BENCHMARKS: dict[str, float] = {
    "automotive_manufacturing": 200.0,
    "logistics_warehouse": 150.0,
    "healthcare": 500.0,
    "retail": 100.0,
    "agricultural": 80.0,
    "last_mile_delivery": 120.0,
    "default": 150.0,
}
