# Contributing to MARS

**Machine Assets Reporting Standard — Contribution Guide**

Thank you for your interest in contributing to MARS. This standard improves through challenge, not consensus. If you see an error, a gap, or a better approach — we want to hear from you.

---

## Ways to Contribute

### 1. Report an Error
Found a mistake in the schema, a formula error, or an incorrect benchmark value?

→ Open a [GitHub Issue](https://github.com/machineassets/mars/issues) with the label `bug`

Include:
- What the current value or definition says
- What you believe it should say
- Evidence or reasoning supporting the correction

---

### 2. Propose a Change — MARS Enhancement Proposal (MEP)
Any change to the schema, formula, or methodology requires a MEP.

→ Open a [GitHub Discussion](https://github.com/machineassets/mars/discussions) under **MEP Proposals**

Use the MEP template in [GOVERNANCE.md](./GOVERNANCE.md#mep-template).

MEPs require a 14-day community review before a maintainer decision. See [GOVERNANCE.md](./GOVERNANCE.md) for the full process.

---

### 3. Contribute an Example Payload
Real-world or synthetic MARS records help engineers understand the standard in practice.

→ Submit a pull request adding a `.json` file to the `examples/` folder

Requirements:
- Must be a valid MARS v0.9 record (passes schema validation)
- Must include a comment block explaining the deployment scenario
- Must not contain real proprietary data
- Synthetic data clearly labelled as such

---

### 4. Contribute to the SDK
Python, TypeScript, or ROS2 integration code welcome.

→ Submit a pull request to the relevant folder under `sdk/`

Requirements:
- Includes a README explaining usage
- Includes at least one working example
- Code released under MIT License (see [GOVERNANCE.md](./GOVERNANCE.md#intellectual-property))

---

### 5. Share Deployment Data
Have real robot deployment data that could validate or challenge MARS benchmark values?

This is the most valuable contribution possible. Anonymised data is welcome.

→ Email [standards@machineassets.ai](mailto:standards@machineassets.ai)

We will work with you to incorporate validated data into v1.0 benchmark ranges with full attribution.

---

## Pull Request Process

1. Fork the repository
2. Create a branch: `git checkout -b mep/your-proposal-name`
3. Make your changes
4. Validate any schema changes: `python -m jsonschema -i examples/sample.json schema/MARS_v0.9.json`
5. Submit a pull request with a clear description of what changed and why
6. Reference the related MEP Discussion or Issue number

Pull requests without a corresponding Issue or MEP Discussion will be asked to open one first.

---

## What We Are Looking For

**Most needed right now:**

- Robotics engineers — validate schema fields against real ROS2 implementations
- Insurance actuaries — challenge MRS formula weights and premium tier logic
- Fleet operators — validate TSR, MTBI, and AS benchmark ranges against real data
- Standards professionals — alignment with ISO 10218, ISO/TS 15066, ISO 13482

**Please do not submit:**

- Changes that create manufacturer dependencies
- Changes that restrict the schema's openness
- Benchmark updates without supporting evidence

---

## First Contribution?

Not sure where to start? Look for issues labelled:

- `good first issue` — small, well-defined tasks
- `help wanted` — areas where we actively need input
- `benchmark-review` — benchmark values needing empirical validation

---

## Questions?

Open a [GitHub Discussion](https://github.com/machineassets/mars/discussions) or email [standards@machineassets.ai](mailto:standards@machineassets.ai).

---

*By contributing to MARS you agree your contributions may be incorporated under the applicable license. See [GOVERNANCE.md](./GOVERNANCE.md#intellectual-property) for details.*
