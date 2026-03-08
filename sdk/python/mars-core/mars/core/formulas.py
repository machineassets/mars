"""
Pure formula functions for MARS v0.9 canonical calculations.

All functions are pure: no side effects, no global state mutation.
Same input always produces the same output.
"""

from mars.core.benchmarks import MTBI_BENCHMARKS


def compute_am_roi(record: dict) -> float:
    """Compute the Autonomous Machine Return on Investment (AM-ROI).

    Formula:
        AM-ROI = [(R + HLE × DF) × TSR × AS] / TCO_annual

    Variables:
        R        = financial_metrics.revenue_direct_period (default 0 if missing)
        HLE      = financial_metrics.hle_annual
                   (Human Labour Equivalent annual cost)
        DF       = financial_metrics.displacement_factor
                   (fraction of human role displaced by robot)
        TSR      = task_metrics.task_success_ratio
        AS       = operational_metrics.autonomy_score
        TCO      = financial_metrics.tco_annual
                   (Total Cost of Ownership, annual)

    Returns:
        float — dimensionless ROI ratio. Values < 1.0 indicate the robot has
        not yet broken even; values >= 1.0 indicate net positive return.
    """
    fm = record["financial_metrics"]
    tm = record["task_metrics"]
    om = record["operational_metrics"]

    R = fm.get("revenue_direct_period", 0) or 0
    HLE = fm["hle_annual"]
    DF = fm["displacement_factor"]
    TSR = tm["task_success_ratio"]
    AS = om["autonomy_score"]
    TCO = fm["tco_annual"]

    return ((R + HLE * DF) * TSR * AS) / TCO


def compute_mrs(record: dict) -> float:
    """Compute the MARS Risk Score (MRS) for insurance underwriting.

    Formula:
        MRS = (TSR × 0.30) + (AS × 0.25) + (MTBI_norm × 0.20) + (Safety_norm × 0.25)

    Variables:
        TSR         = task_metrics.task_success_ratio
        AS          = operational_metrics.autonomy_score
        MTBI_norm   = min(operational_metrics.mtbi_hours / benchmark, 1.0)
                      where benchmark is from MTBI_BENCHMARKS keyed on
                      environment.deployment_type (default 150.0)
        Safety_norm = stability_safety.safety_score / 100.0

    Weight check: 0.30 + 0.25 + 0.20 + 0.25 = 1.00

    Returns:
        float in [0.0, 1.0] — higher is better (lower insurance risk).
        Risk tiers: excellent ≥ 0.90, good 0.80–0.89, standard 0.70–0.79,
        elevated 0.50–0.69, high < 0.50.
    """
    tm = record["task_metrics"]
    om = record["operational_metrics"]
    ss = record["stability_safety"]
    env = record["environment"]

    TSR = tm["task_success_ratio"]
    AS = om["autonomy_score"]
    mtbi_hours = om["mtbi_hours"]
    safety_score = ss["safety_score"]
    deployment_type = env.get("deployment_type", "")

    benchmark = MTBI_BENCHMARKS.get(deployment_type, MTBI_BENCHMARKS["default"])
    MTBI_norm = min(mtbi_hours / benchmark, 1.0)
    Safety_norm = safety_score / 100.0

    return (TSR * 0.30) + (AS * 0.25) + (MTBI_norm * 0.20) + (Safety_norm * 0.25)


def compute_safety_score(record: dict) -> float:
    """Compute the MARS safety score from raw incident and compliance data.

    Formula:
        safety_score = 100 × [
            (1 − fall_rate)      × 0.35 +
            (1 − collision_rate) × 0.35 +
            (1 − near_miss_rate) × 0.20 +
            iso_factor           × 0.10
        ]

    Variables:
        fall_rate      = falls_detected / uptime_hours × 100, capped at 1.0
        collision_rate = collision_events / uptime_hours × 100, capped at 1.0
        near_miss_rate = near_miss_events / uptime_hours × 100, capped at 1.0
        iso_factor     = 1.0 if any of iso_10218_compliance,
                         iso_ts15066_compliance, iso_13482_compliance is True;
                         else 0.5

    All rates are incidents per 100 uptime hours before capping.

    Returns:
        float in [0.0, 100.0] — higher is safer.
    """
    ss = record["stability_safety"]
    om = record["operational_metrics"]

    uptime_hours = om["uptime_hours"]
    falls = ss["falls_detected"]
    collisions = ss["collision_events"]
    near_misses = ss["near_miss_events"]

    fall_rate = min(falls / uptime_hours * 100, 1.0)
    collision_rate = min(collisions / uptime_hours * 100, 1.0)
    near_miss_rate = min(near_misses / uptime_hours * 100, 1.0)

    iso_factor = (
        1.0
        if any(
            [
                ss.get("iso_10218_compliance", False),
                ss.get("iso_ts15066_compliance", False),
                ss.get("iso_13482_compliance", False),
            ]
        )
        else 0.5
    )

    return 100.0 * (
        (1.0 - fall_rate) * 0.35
        + (1.0 - collision_rate) * 0.35
        + (1.0 - near_miss_rate) * 0.20
        + iso_factor * 0.10
    )


def compute_rsv(record: dict, model_factor: float = 0.75) -> float:
    """Compute the Robot Resale Value (RSV).

    Formula:
        RSV = purchase_price × (1 − cumulative_depreciation) × condition_factor × model_factor

    Variables:
        cumulative_depreciation = depreciation_rate_annual × (robot_age_days / 365)
        condition_factor        = (TSR × 0.6) + (AS × 0.4)
            TSR = task_metrics.task_success_ratio
            AS  = operational_metrics.autonomy_score
        model_factor            = explicit parameter, default 0.75
                                  (market liquidity / OEM support factor)

    Returns:
        float — estimated resale value in the same currency as purchase_price.
    """
    fm = record["financial_metrics"]
    tm = record["task_metrics"]
    om = record["operational_metrics"]

    purchase_price = fm["purchase_price"]
    depreciation_rate_annual = fm["depreciation_rate_annual"]
    robot_age_days = fm["robot_age_days"]
    TSR = tm["task_success_ratio"]
    AS = om["autonomy_score"]

    cumulative_depreciation = depreciation_rate_annual * (robot_age_days / 365.0)
    condition_factor = (TSR * 0.6) + (AS * 0.4)

    return purchase_price * (1.0 - cumulative_depreciation) * condition_factor * model_factor


def check_sla_status(record: dict) -> dict:
    """Check all six RaaS SLA thresholds against contracted minimums.

    Checks:
        1. task_success_ratio   >= contracted_tsr_minimum
        2. uptime_ratio         >= contracted_uptime_minimum
           where uptime_ratio   = uptime_hours / (uptime_hours + downtime_hours)
        3. autonomy_score       >= contracted_as_minimum
        4. mtbi_hours           >= contracted_mtbi_minimum_hours
        5. vision_accuracy      >= contracted_vision_accuracy_minimum
        6. collision_events per 100 uptime hours
                                <= contracted_collision_max_per_100hrs

    Returns:
        dict with keys:
            sla_status (str): "compliant" if all checks pass, "breach" otherwise.
            active_breach_metrics (list[str]): names of breached metrics, empty if compliant.
    """
    sla = record["raas_sla"]
    tm = record["task_metrics"]
    om = record["operational_metrics"]
    ai = record["ai_performance"]
    ss = record["stability_safety"]

    TSR = tm["task_success_ratio"]
    AS = om["autonomy_score"]
    uptime = om["uptime_hours"]
    downtime = om["downtime_hours"]
    mtbi = om["mtbi_hours"]
    vision_accuracy = ai["vision_accuracy"]
    collision_events = ss["collision_events"]

    uptime_ratio = uptime / (uptime + downtime)
    collision_per_100 = collision_events / uptime * 100.0

    breaches = []

    if TSR < sla["contracted_tsr_minimum"]:
        breaches.append("task_success_ratio")

    if uptime_ratio < sla["contracted_uptime_minimum"]:
        breaches.append("uptime_ratio")

    if AS < sla["contracted_as_minimum"]:
        breaches.append("autonomy_score")

    if mtbi < sla["contracted_mtbi_minimum_hours"]:
        breaches.append("mtbi_hours")

    if vision_accuracy < sla["contracted_vision_accuracy_minimum"]:
        breaches.append("vision_accuracy")

    if collision_per_100 > sla["contracted_collision_max_per_100hrs"]:
        breaches.append("collision_events")

    return {
        "sla_status": "compliant" if not breaches else "breach",
        "active_breach_metrics": breaches,
    }
