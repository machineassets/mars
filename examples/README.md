# MARS v0.9 — Example Payloads

Three fully validated example payloads demonstrating MARS v0.9 schema compliance across different robot classes and deployment environments.

## Examples

### 1. humanoid_factory_example.json
**Robot:** Figure 02 — BMW Spartanburg, automotive manufacturing (US)  
**Currency:** USD | **Period:** February 2026 (28 days)  
**AM-ROI:** 0.750 (Year 1, expected sub-parity) | **MRS:** 0.875 — good tier  
**Key story:** Early humanoid deployment building toward payback. All SLA thresholds met.

### 2. warehouse_robot_example.json
**Robot:** Agility Digit — Toyota TMMC, automotive manufacturing (Canada)  
**Currency:** CAD | **Period:** March 2026 (31 days)  
**AM-ROI:** 0.844 (Year 1) | **MRS:** 0.787 — standard tier  
**Key story:** Lower capital cost delivers better Y1 AM-ROI than premium humanoid despite lower TSR.

### 3. amr_logistics_example.json
**Robot:** MiR200 — Rotterdam logistics centre (Netherlands)  
**Currency:** EUR | **Period:** March 2026 (31 days)  
**AM-ROI:** 2.40 (18 months, stable_operational phase) | **MRS:** 0.930 — excellent tier  
**Key story:** Mature AMR deployment fully paid off, generating EUR 2,044/month net surplus.

## Cross-Example Comparison

| Metric | Figure 02 (BMW) | Digit (TMMC) | MiR200 (Rotterdam) |
|--------|----------------|--------------|-------------------|
| Robot class | Humanoid | Humanoid | AMR |
| Currency | USD | CAD | EUR |
| Purchase price | 250,000 | 150,000 | 35,000 |
| Robot age | 258 days | 212 days | 821 days |
| Depreciation phase | rapid_initial | rapid_initial | stable_operational |
| TSR | 0.930 | 0.910 | 0.975 |
| Autonomy score | 0.90 | 0.87 | 0.96 |
| AM-ROI | 0.750 | 0.844 | 2.40 |
| MRS | 0.875 | 0.787 | 0.930 |
| MRS tier | good | standard | excellent |
| Insurance rate | 1.4% | 2.5% | 1.0% |
| payback_months_remaining | 165.9 | 131.2 | -9.9 (paid off) |

## Validation

Every calculated field includes a `_comment` showing the full formula and inputs. All values are internally consistent — TSR, AS, MTBI, AM-ROI, MRS, RSV, and payback all derive from stored primitives.

To validate against the schema:
```python
import json, jsonschema, urllib.request

schema_url = "https://raw.githubusercontent.com/machineassets/mars/main/schema/MARS_v0.9.json"
with urllib.request.urlopen(schema_url) as r:
    schema = json.load(r)

with open("humanoid_factory_example.json") as f:
    payload = json.load(f)

jsonschema.validate(payload, schema)
print("Validation passed")
```

## Notes

- All company names and deployment references are illustrative only
- Performance figures are based on publicly available information and reasonable estimates
- MARS is not affiliated with any manufacturer, operator, or insurer referenced herein
- Example values are not financial or insurance advice

## License

Schema: CC0 1.0 Universal — public domain  
Methodology: CC BY 4.0 — attribution required  
See [LICENSE](../LICENSE) for full terms.
```

Then scroll down, add commit message:
```
Update examples README with live payload descriptions and comparison table
