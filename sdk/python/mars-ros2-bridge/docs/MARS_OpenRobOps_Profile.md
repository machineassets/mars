# MARS v0.9 and OpenRobOps: Measurement Above the Ontology Layer

**For:** Florian Pestoni
**From:** MARS Engineering
**Date:** 2025

---

## What OpenRobOps Gives Us (and What It Doesn't)

OpenRobOps / ORO is the right foundation. It provides a shared vocabulary for robot capabilities, action types, and operational state — the semantic backbone that lets heterogeneous fleets talk to each other without custom translation for every pairing. If you want to reason about *what a robot can do*, ORO is the layer to use.

What ORO deliberately does not address is *how well* a robot is doing it, and what that performance is worth. That's not a gap in ORO's design — it's a clear separation of concerns. ORO describes capability; MARS measures execution.

---

## Where MARS Sits

MARS (Mobile Autonomy Rating System, v0.9) operates one layer above ORO. It ingests structured operational data — sourced from ROS2 topics, fleet management APIs, or ORO-annotated task logs — and produces normalized performance records against a fixed schema:

| MARS Section | What It Captures |
|---|---|
| `operational_metrics` | Autonomy score, uptime hours, intervention rate |
| `task_metrics` | Tasks completed, attempted, success ratio |
| `energy_metrics` | Battery health, charge cycle efficiency |
| `stability_safety` | Collision events, E-stop frequency |

These aren't raw sensor values. They're derived KPIs — clean, comparable across vendors, and directly usable in financial models (TCO, ROI, lease/SLA pricing).

---

## The Relationship in Practice

Think of the stack as:

```
[ Financial Valuation / SLA Pricing ]
          ↑
    [ MARS v0.9 ]         ← performance measurement + normalization
          ↑
  [ OpenRobOps / ORO ]   ← capability ontology + task semantics
          ↑
    [ ROS2 / Robot ]      ← raw execution
```

ORO tells you a robot completed a `PickAndPlace` action. MARS tells you it completed 94% of them successfully, ran for 11.2 hours on a charge, and had zero collision events this shift. Finance then prices that against the SLA floor.

---

## Concrete Proposal: MARS Export Adapter for ORO

We should build a lightweight export adapter that reads ORO task completion logs and maps them directly into MARS `task_metrics` fields. The adapter would:

1. Parse ORO `ActionStatus` records for completed/failed task counts
2. Map ORO capability identifiers to MARS task categories
3. Emit a valid MARS v0.9 JSON record, ready for scoring or SLA evaluation

This keeps ORO as the authoritative task log and MARS as the performance lens on top of it — no duplication, clean separation. Implementation is a single Python module, roughly the same shape as the ROS2 bridge we've already built for MiR200.

I'd suggest a 2-week spike: one week to define the ORO→MARS field mapping schema, one week to implement and validate against a sample ORO task log. Happy to scope it in more detail — let me know if a call makes sense.
