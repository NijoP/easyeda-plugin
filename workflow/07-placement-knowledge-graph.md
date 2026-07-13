# Phase 7 — Placement Knowledge Graph

**Owning agent:** placement-planner · **Tool:** none (analysis) · **Autonomy:** Tier 1 (execute)

Before placing any component, build the placement knowledge graph — the reasoning
that will drive every placement decision. **No component is placed until this is
complete.**

- **Objective:** a structured model of what must sit near what, and why.
- **Inputs:** the verified schematic (net list + currents); the client constraints
  from Phase 6.
- **The graph describes:** functional blocks · component relationships · placement
  priorities · thermal considerations · high-current paths · analog/digital
  separation · EMI-sensitive regions · mechanical constraints · routing complexity ·
  manufacturing considerations.
- **Validation:** every net has a class + current; every IC has its decap-adjacency
  edges; every high-current path is identified; every EMI/analog region is marked.
- **Deliverables:** `07_placement_kg/placement_graph.json` (nodes = blocks/parts,
  edges = adjacency requirements with weights), a per-net current + class table.
- **Engineering checklist:**
  - [ ] Decoupling caps edged to their IC (highest adjacency weight).
  - [ ] High-current (motor/power) paths flagged for wide copper / plane.
  - [ ] Analog and digital domains separated; EMI sources isolated.
  - [ ] Thermal actors (FETs, regulators) noted for spread + copper.
- **Automation:** graph builder + IPC-2221 per-net current/width
  ([`../automation/shared/`](../automation/shared/)); congestion prediction grid.
- **Human review:** engineer confirms the priorities and separations.
- **Exit gate:** graph complete and consistent with the schematic + constraints →
  ready for the visual plan.

> This is the "think before you place" gate — see the placement heuristics in
> [`../knowledge/knowledge-graph.md`](../knowledge/knowledge-graph.md).
