# Phase 1 — Requirement Analysis & Feasibility Study

**Owning agent:** feasibility-analyst · **Tool:** none (analysis) · **Autonomy:** Tier 1 (execute; human approves the project)

The workflow begins when a client provides requirements. **No schematic work
begins until this feasibility study is complete.**

- **Objective:** turn an ambiguous brief into a quantified feasibility verdict.
- **Inputs:** client brief (call, sketch, PDF), hard constraints (size, cost,
  battery, certifications).
- **Outputs (the study):** functional analysis · technical feasibility · cost
  estimate · manufacturing feasibility · power budget · hardware architecture ·
  risk assessment · complexity estimate.
- **Validation:** every requirement has a number and a source; conflicts surfaced,
  not silently reconciled.
- **Deliverables:** `01_feasibility/feasibility_study.md`, a red/amber/green
  constraint table, a power budget, a block diagram.
- **Engineering checklist:**
  - [ ] Density sanity check — component area ÷ board area; is the target size even
        feasible?
  - [ ] Current check — any rail >~5 A ⇒ needs a plane ⇒ ≥4 layers.
  - [ ] Any single requirement that makes the board infeasible flagged.
  - [ ] Certification/mechanical constraints noted.
- **Automation:** transcribe audio → structured requirements; density + IPC-2221
  first-order estimators (`../automation/shared/`).
- **Human review:** client confirms the register; engineer signs the feasibility
  verdict.
- **Exit gate:** feasibility study complete, no unquantified requirement, no
  unaddressed hard conflict → **project approved.**

> Knowledge to consult: [`../knowledge/design-standards.md`](../knowledge/design-standards.md)
> (density thresholds, layer-count trigger), [`../knowledge/learning-db.md`](../knowledge/learning-db.md).
