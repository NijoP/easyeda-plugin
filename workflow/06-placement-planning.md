# Phase 6 — Component Placement Planning

**Owning agent:** placement-planner · **Tool:** none (planning) · **Autonomy:** Tier 5 (client defines constraints)

PCB placement does **not** begin immediately. First capture a logical placement
plan — the physical constraints the client owns.

- **Objective:** capture every mechanical/physical constraint before any component
  is placed.
- **Inputs:** the verified schematic; the client's mechanical intent.
- **The client defines:** board dimensions · board shape · connector locations ·
  USB location · sensor positions · MCU location · mounting holes · keep-out
  regions · mechanical constraints · user-defined placement preferences.
- **Validation:** every constraint is explicit and dimensioned (no "somewhere on
  the left").
- **Deliverables:** `06_placement_plan/constraints.md` (or `.yaml`) — the machine-
  readable constraint set the placer will honor; a dimensioned board outline.
- **Engineering checklist:**
  - [ ] Board outline + shape fixed.
  - [ ] Every edge-critical part assigned an edge + orientation (opens outward).
  - [ ] Mounting holes + keep-outs located.
  - [ ] Sensor axis/orientation requirements noted (sensors that fuse share an axis).
- **Automation:** none — this is an input-gathering phase.
- **Human review:** the **client** provides and confirms the constraints.
- **Exit gate:** all mechanical constraints captured and dimensioned → ready to
  build the placement knowledge graph.

> This phase exists because a DRC-clean board that can't be assembled or plugged in
> is a FAIL. Placement is judged by usability, not wirelength.
