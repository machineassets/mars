[README.md](https://github.com/user-attachments/files/25779391/README.md)
# MARS — Machine Assets Reporting Standard

**The open neutral telemetry schema for autonomous machine performance, ROI calculation, and insurance underwriting.**

[![Version](https://img.shields.io/badge/version-0.9.0-blue)](https://github.com/machineassets/MARS)
[![Schema License](https://img.shields.io/badge/schema%20license-CC0%201.0-green)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Methodology License](https://img.shields.io/badge/methodology%20license-CC%20BY%204.0-blue)](https://creativecommons.org/licenses/by/4.0/)
[![Status](https://img.shields.io/badge/status-Public%20Draft-orange)](https://github.com/machineassets/MARS)

---

## The Problem

Every autonomous machine deployment produces performance data. Figure 02 reports it differently than Atlas, differently than Digit, differently than AEON. Insurers pricing autonomous machine risk work from manufacturer spec sheets — not auditable operational records. A CFO approving a 10-robot fleet has no neutral ROI calculation that works across manufacturers.

**No cross-manufacturer standard exists. MARS is that standard.**

---

## What MARS Is

MARS is a JSON Schema (draft-07) telemetry standard defining **19 structured objects** that capture the operational, AI performance, safety, energy, maintenance, and financial data required to compute:

- **AM-ROI** — Autonomous Machine Return on Investment
- **MRS** — MARS Risk Score (direct actuarial input for insurance underwriting)
- **RaaS SLA compliance status** — parametric triggers for Robot-as-a-Service contracts
- **RSV** — Robot Resale Value with 3-phase depreciation model

Any robot. Any manufacturer. One standard.

---

## The Core Formula

```
AM-ROI = [ (R + HLE × DF) × TSR × AS ] / TCO_annual

Where:
  R    = Direct revenue attributable to robot in period
  HLE  = Human Labour Equivalent (fully-loaded annual cost)
  DF   = Displacement Factor (0.0–1.0)
  TSR  = Task Success Ratio (tasks_completed / tasks_attempted)
  AS   = Autonomy Score (1 - intervention_rate)
  TCO  = (P/L) + C_energy + C_maint + C_operator + C_insurance + C_integration
```

AM-ROI < 1.0 = below break-even · AM-ROI ≥ 1.4 = production threshold · AM-ROI ≥ 2.0 = strong return

---

## MARS Risk Score (Insurance Underwriting)

```
MRS = (TSR × 0.30) + (AS × 0.25) + (MTBI_norm × 0.20) + (Safety_norm × 0.25)
```

| MRS Range | Risk Class | Annual Premium |
|-----------|------------|----------------|
| 0.90–1.00 | Excellent  | 0.8–1.2% of P  |
| 0.80–0.89 | Good       | 1.2–2.0% of P  |
| 0.70–0.79 | Standard   | 2.0–3.5% of P  |
| 0.60–0.69 | Elevated   | 3.5–6.0% of P  |
| < 0.60    | Uninsurable | —             |

---

## Schema Structure

19 top-level objects covering the full autonomous machine lifecycle:

| Object | Purpose |
|--------|---------|
| `machine_identity` | Manufacturer, model, serial, firmware, deployment environment |
| `operational_metrics` | Uptime, MTBI, TSR, AS, intervention rate, incident count |
| `financial_metrics` | Purchase price, TCO components, AM-ROI, HLE, DF, payback period |
| `ai_performance` | Vision accuracy, hallucination rate, drift index, model version |
| `stability_safety` | Falls, collisions, near-misses, safety score, ISO compliance |
| `mars_risk_score` | MRS value, risk class, MTBI normalised, safety normalised |
| `raas_sla` | Parametric SLA triggers and breach thresholds |
| `depreciation` | 3-phase model: rapid initial → stable operational → terminal |
| `energy_consumption` | kWh, cost, battery health, charge cycles |
| `maintenance_log` | Cost, components replaced, maintenance type |
| `audit_chain` | SHA-256 hash per record, timestamp, validator signature |
| *(+ 8 additional objects)* | Environmental, fleet, certification, and metadata objects |

---

## Quick Start

### 1. Download the Schema

```bash
curl -O https://raw.githubusercontent.com/machineassets/MARS/main/MARS_v0.9.json
```

### 2. Validate a Record

```python
import json
import jsonschema

with open('MARS_v0.9.json') as f:
    schema = json.load(f)

# Your robot telemetry record
record = {
    "machine_identity": {
        "machine_id": "FIG02-BMW-SPB-001",
        "vendor": "Figure AI",
        "model": "Figure 02",
        "deployment_environment": "automotive_manufacturing"
    },
    "operational_metrics": {
        "uptime_hours": 1250,
        "tasks_completed": 89100,
        "tasks_attempted": 90000,
        "incident_count": 6,
        "H_auto": 1187.5,
        "H_op": 1250
    }
    # ... additional objects
}

jsonschema.validate(instance=record, schema=schema)
print("Valid MARS record.")
```

### 3. Compute AM-ROI

```python
def compute_am_roi(R, HLE, DF, TSR, AS, P, L,
                   C_energy, C_maint, C_operator,
                   C_insurance, C_integration):
    
    tco_annual = (P / L) + C_energy + C_maint + C_operator + C_insurance + C_integration
    net_value  = (R + HLE * DF) * TSR * AS
    am_roi     = net_value / tco_annual
    
    return {
        "am_roi": round(am_roi, 3),
        "tco_annual": tco_annual,
        "net_value": net_value
    }

# Example: Agility Digit at Toyota TMMC (Year 1)
result = compute_am_roi(
    R=0,            # No direct revenue — internal deployment
    HLE=72000,      # CAD — Canadian manufacturing worker, fully loaded
    DF=0.85,        # Partial displacement
    TSR=0.88,       # Task Success Ratio
    AS=0.90,        # Autonomy Score
    P=150000,       # Purchase price CAD
    L=5,            # Expected lifespan years
    C_energy=1200,
    C_maint=15000,
    C_operator=6000,
    C_insurance=3000,
    C_integration=5000
)

print(result)
# {'am_roi': 0.805, 'tco_annual': 60200, 'net_value': 48470}
```

---

## Integration Pathways

| Pathway | Complexity | Time | Best For |
|---------|------------|------|----------|
| ROS2 Topic Bridge | Low–Medium | 1–2 weeks | Any ROS2-compatible machine |
| Vendor Cloud API | Low | 1 week | Figure AI, Boston Dynamics, Agility |
| MARS SDK (Direct) | Medium | 2–4 weeks | Greenfield deployments |
| InOrbit / Viam | Low | Days | Existing RobOps platform users |
| Isaac Sim / Gazebo | Low | Days | Simulation and pilot validation |
| Manual Entry | Minimal | Hours | Proof of concept, historical data |

---

## Worked Examples

Full calculations with trajectory projections in [`MARS_v0.9_Methodology.pdf`](./MARS_v0.9_Methodology.pdf):

**Example A — Agility Digit at Toyota TMMC (Canada)**
Year 1 AM-ROI: **0.80** · Break-even Year 2 · AM-ROI 1.58 by Year 5

**Example B — Figure 02 vs Atlas at BMW Spartanburg**
Figure 02 AM-ROI: **1.80** · Atlas AM-ROI: **1.52** · Figure delivers 18% better return at lower TCO

> Company names and deployment references are used for illustrative purposes only. All figures are estimates based on publicly available information. MARS is not affiliated with or endorsed by any manufacturer or operator referenced herein.

---

## Confidence Levels

MARS is an honest standard. Not everything is equally certain:

| Element | Confidence |
|---------|------------|
| AM-ROI formula structure | High — standard capital investment methodology |
| TCO component categories | High — standard industrial asset management |
| ISO standard references (10218, TS 15066, 13482) | High — verified against ISO catalogue |
| MTBI methodology | High — analogous to IEC 60050-192 MTBF |
| TSR and AS definitions | High — mathematically enforced constraint |
| Depreciation phase model | Medium — analogised from technology equipment data |
| Benchmark TSR/AS ranges | Medium-Low — no large-scale humanoid dataset exists yet |
| MRS weighting factors | Medium-Low — logical construction, not actuarial validation |
| Insurance premium ranges | Low-Medium — emerging market, wide variance |

We explicitly invite challenge on any estimate. That is how v1.0 gets built correctly.

---

## Roadmap

| Version | Target | Milestone |
|---------|--------|-----------|
| **v0.9** (current) | March 2026 | Core schema, AM-ROI, MRS, RaaS SLA, depreciation model |
| v1.0 | Q2 2026 | Community-validated formula, ROS2 SDK, first live pilot data |
| v1.5 | Q3 2026 | Fleet aggregation, cross-manufacturer dashboard |
| v2.0 | Q1 2027 | Agricultural + healthcare modules, parametric insurance templates |
| v3.0 | 2028 | ISO / IFR standards body submission |

---

## Contributing

MARS v0.9 is a public draft actively seeking review from:

- **Robotics engineers** — validate schema fields, integration pathways, ROS2 compatibility
- **Insurance actuaries** — challenge MRS formula weights, premium tier logic
- **Fleet operators** — validate benchmark ranges against real deployment data
- **Standards professionals** — alignment with ISO, IEC, IFR frameworks

**To contribute:**
1. Open an Issue to propose changes or flag errors
2. Submit a Pull Request with schema modifications
3. Email [partnerships@machineassets.com](mailto:partnerships@machineassets.com) for design partner or pilot discussions

---

## Files

| File | Description |
|------|-------------|
| `MARS_v0.9.json` | Complete JSON Schema — 19 objects, all field definitions and constraints |
| `MARS_v0.9_Methodology.pdf` | Full ROI methodology, worked examples, insurance framework, implementation guide. Also available as .docx at [machineassets.ai](https://machineassets.ai) |
| `README.md` | This file |

---

## License

| File | License |
|------|---------|
| `MARS_v0.9.json` | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) — public domain, no conditions, maximum adoption |
| `MARS_v0.9_Methodology.docx` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to use and adapt with attribution to MachineAssets |

The schema is public domain. Standards only work when there is zero friction to adoption.
The methodology is attributed. The intellectual framework carries the MachineAssets name.

---

## Contact

**MachineAssets**  
[machineassets.ai](https://machineassets.ai) · [info@machineassets.ai](mailto:info@machineassets.ai)

*MARS is an independent open standard. Not affiliated with or endorsed by any manufacturer, insurer, or operator referenced in this repository.*
