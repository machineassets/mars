# MARS Governance

**Machine Assets Reporting Standard — Governance Framework**

Version 0.9 | March 2026 | MachineAssets Technical Standards Group

---

## Overview

MARS is an open standard governed by the **MachineAssets Technical Standards Group**. This document defines how the standard evolves, how contributions are made, how decisions are taken, and how versions are released.

Governance exists for one reason: so that any company, engineer, or insurer can depend on MARS without fear that it will change arbitrarily, become proprietary, or disappear. The standard must be bigger than any single contributor.

---

## Principles

**Open** — The schema, methodology, and all governance processes are public. Nothing happens behind closed doors.

**Neutral** — MARS belongs to the community, not to any manufacturer, insurer, or operator. No single commercial interest controls the standard.

**Conservative** — Breaking changes to the schema are rare and deliberate. Implementations must be able to depend on stability.

**Evidence-based** — Changes to benchmark values, formula weights, and methodology require supporting data or community consensus. Opinion alone is insufficient.

**Honest** — Every version clearly labels what is empirically validated versus what is an informed estimate. This transparency is not a weakness — it is what makes MARS trustworthy.

---

## Structure

### MachineAssets Technical Standards Group

The maintainer of MARS. Responsible for:

- Reviewing and merging MARS Enhancement Proposals (MEPs)
- Publishing versioned releases
- Maintaining the schema, methodology, and governance documents
- Communicating with the community via GitHub Discussions

Current maintainer contact: [emmanuel@machineassets.com](mailto:emmanuel@machineassets.com)

### Contributors

Anyone who submits a MEP, opens a validated issue, or contributes code to the reference implementation. Contributors are listed in [CONTRIBUTORS.md](./CONTRIBUTORS.md).

### Design Partners

Organisations that have agreed to validate MARS against real or simulated deployment data. Design partners receive early access to draft versions and are acknowledged in release notes.

---

## MARS Enhancement Proposals (MEPs)

All changes to the standard — schema fields, formula modifications, benchmark updates, new deployment type modules — must go through the MEP process.

### When a MEP is required

- Adding or removing a schema field
- Changing a field name, type, or constraint
- Modifying a formula or calculation methodology
- Updating benchmark values or MRS weighting factors
- Adding a new deployment type module
- Any change that could break existing implementations

### When a MEP is not required

- Fixing a typo or documentation error
- Clarifying an existing field description without changing its meaning
- Adding an example or worked calculation

### MEP Process

**Step 1 — Open a GitHub Discussion**
Post in the [Discussions](https://github.com/machineassets/mars/discussions) tab under the category "MEP Proposals". Use the template below.

**Step 2 — Community Review (minimum 14 days)**
Any contributor may comment, question, or object. The proposer is expected to respond to technical objections with evidence or reasoning.

**Step 3 — Maintainer Decision**
After the review period, the MachineAssets Technical Standards Group either:
- Accepts the MEP → merged into the next minor or major release
- Requests revision → proposer updates and review restarts
- Rejects the MEP → documented with reasoning in the Discussion thread

**Step 4 — Implementation**
Accepted MEPs are implemented in the schema and methodology document before the next versioned release.

### MEP Template

```
## MEP Title

**Type:** Schema change / Formula change / Benchmark update / New module / Other

**Problem being solved:**
What gap or error does this address?

**Proposed change:**
Exact field names, formula modifications, or benchmark values.

**Evidence or reasoning:**
Data, citations, or logical argument supporting the change.

**Impact on existing implementations:**
Does this break backward compatibility? How should existing records be migrated?

**Proposer:**
Name / organisation / contact
```

---

## Versioning

MARS follows semantic versioning adapted for a data standard:

| Version Type | When Used | Example |
|---|---|---|
| Patch (x.x.N) | Typo fixes, clarifications, non-breaking documentation updates | v0.9.1 |
| Minor (x.N.0) | New optional fields, new deployment modules, benchmark updates | v0.10.0 |
| Major (N.0.0) | Breaking schema changes, formula modifications, field removals | v1.0.0 |

**Breaking change policy:** Major version bumps require a minimum 90-day deprecation notice. Existing v0.9 implementations will always be able to validate against the v0.9 schema regardless of future versions.

### Release Schedule

| Version | Target | Notes |
|---|---|---|
| v0.9 | March 2026 | Current public draft — community review open |
| v1.0 | Q2 2026 | First stable release — requires live pilot data and community validation |
| v1.5 | Q3 2026 | Fleet aggregation module, cross-manufacturer benchmarking |
| v2.0 | Q1 2027 | Agricultural, healthcare, construction modules |
| v3.0 | 2028 | Standards body submission (ISO, IFR) |

---

## Benchmark Values and Formula Weights

Benchmark values (TSR ranges, MTBI thresholds, MRS weighting factors) are explicitly versioned estimates in v0.9. They are not fixed.

**How benchmarks are updated:**

Benchmark updates require a MEP with supporting evidence — ideally real deployment data from one or more MARS design partners. Community consensus alone is insufficient for benchmark changes. Data is required.

**Current v0.9 estimates requiring empirical validation:**

- TSR and AS benchmark ranges by deployment type
- MRS formula weights (0.30 / 0.25 / 0.20 / 0.25)
- Insurance premium rate tiers (% of purchase price)
- Depreciation phase rates

Any organisation with deployment data that could validate or challenge these estimates is actively encouraged to submit a MEP or contact the maintainer directly.

---

## Intellectual Property

| Asset | License |
|---|---|
| MARS schema (MARS_v0.9.json) | CC0 1.0 Universal — public domain |
| MARS methodology (MARS_v0.9_Methodology.pdf) | CC BY 4.0 — attribution required |
| Reference implementations (sdk/, examples/) | MIT License |
| This governance document | CC0 1.0 Universal |

**Contributor agreement:** By submitting a MEP or pull request, contributors agree that their contributions may be incorporated into the standard under the applicable license above.

No contributor assignment agreement (CLA) is required for documentation contributions. Code contributions to the SDK and examples are accepted under MIT License.

---

## Conflict of Interest

Contributors with a direct commercial interest in a proposed change must declare that interest at the start of a MEP Discussion. Declaration does not disqualify a contributor — it ensures the community can weigh the proposal with full context.

The MachineAssets Technical Standards Group will not accept MEPs that would restrict the standard's openness, create manufacturer dependencies, or advantage a single commercial actor.

---

## Code of Conduct

MARS discussions are technical. Critique the schema, not the person.

Expected behaviour:
- Engage with evidence and reasoning
- Accept that you may be wrong — the standard improves through disagreement
- Respond to objections rather than ignoring them
- Credit prior work when building on it

Unacceptable behaviour:
- Personal attacks or dismissiveness
- Submitting MEPs designed to advantage a specific manufacturer or operator
- Misrepresenting data or citations

Violations should be reported to [emmanuel@machineassets.com](mailto:emmanuel@machineassets.com).

---

## Amendments to This Document

Changes to the governance framework itself follow the same MEP process as schema changes, with one addition: governance amendments require a 30-day community review period (vs. 14 days for schema changes).

---

*MARS Governance v0.9 | MachineAssets Technical Standards Group | machineassets.ai*
