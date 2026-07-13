# Phase 8 — Visual Placement Planning

**Owning agent:** placement-planner · **Tool:** none (visual planning) · **Autonomy:** Tier 2 (AI proposes; approved before scripting)

Generate a **visual placement map before writing any automation scripts.** Prove
the layout on paper before touching the board.

- **Objective:** an approved zone map that satisfies the client's requirements.
- **Inputs:** the placement knowledge graph (Phase 7); the client constraints
  (Phase 6).
- **The AI determines:** functional zones · power zones · signal flow · connector
  locations · sensor locations · high-speed routing regions · thermal regions ·
  ground strategy · future routing channels.
- **Validation:** evaluate the map against the client's requirements; **iterate
  until it satisfies them** (edge parts open outward, sensors share axis,
  noisy/quiet partition, room for the routing channels Phase 11 will need).
- **Deliverables:** `08_visual_placement/placement_map.(png|svg)` + a zone
  definition ([`../templates/placement.template.json`](../templates/placement.template.json)
  `zones` + `anchors` blocks), with a written rationale.
- **Engineering checklist:**
  - [ ] Every functional zone placed with a reason.
  - [ ] Ground strategy defined (plane(s), analog island, return paths).
  - [ ] Routing channels reserved between zones.
  - [ ] Thermal actors spread; high-current kept short and wide.
- **Automation:** zone map render; congestion overlay to spot channels that will
  saturate.
- **Human review:** **client/engineer approves the map** before any script is
  written. If it fails, refine and re-present.
- **Exit gate:** placement plan approved → proceed to automated placement.

> Rule: never write placement automation before the plan is approved. A rejected
> plan is cheap on paper and expensive as executed geometry.
