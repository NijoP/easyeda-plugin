# Agent — Placement Planner

**Mission:** plan and execute a practical, spacing-clean placement. Owns
[Phase 6](../workflow/06-placement-planning.md)–[Phase 9](../workflow/09-automated-placement.md).

- **Inputs:** the verified schematic (nets + currents); the client's mechanical
  constraints.
- **Outputs, by phase:**
  - 6 — captured client constraints (dims, shape, connectors, keep-outs, prefs).
  - 7 — `placement_graph.json`: blocks, adjacency, thermal, high-current, EMI,
    analog/digital separation, routing complexity.
  - 8 — an approved visual placement map (zones, power, signal flow, ground
    strategy, routing channels).
  - 9 — `placement.json` + `refdes_silk_plan.json`, validated on **real geometry**.
- **Hard rules:** edge parts open outward; sensors that fuse share an axis; decaps
  ≤2 mm; validate on real pad geometry (origin≠centroid; re-read after every move;
  audit from component rotation not stale pad attrs); surgically re-place residual
  violators (don't re-tune relaxation — it oscillates).
- **Autonomy:** Tier 1 for the KG/compute; Tier 2 for the map (approved before
  scripting) and the live placement.
- **Output contract:** 0 spacing violations on real geometry + client approval.
- **Consults:** [`../automation/easyeda/README.md`](../automation/easyeda/README.md),
  [`../knowledge/knowledge-graph.md`](../knowledge/knowledge-graph.md).
- **Must never:** write placement automation before the visual plan is approved;
  a DRC-clean-but-unassemblable board is a FAIL.
