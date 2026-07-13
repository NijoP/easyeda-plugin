# Phase 9 — Automated Component Placement

**Owning agent:** placement-planner · **Tool:** EasyEDA (Node.js automation) · **Autonomy:** Tier 2/3 (AI places; human approves; live write gated)

Once the placement plan is approved, execute it.

- **Objective:** all components placed per the approved plan, spacing-clean and
  practical.
- **Inputs:** the approved zone map + constraints; the schematic parts.
- **Actions:**
  - Generate Node.js automation from the zone map + anchors.
  - Inject the scripts into EasyEDA (via the browser layer).
  - Place all components (region-shelf + demand-sized courtyards + spiral-hug
    decaps + relaxation).
  - **Validate on real pad geometry** (read the board back — never the placer's own
    model, which shows phantom overlaps and misses real ones).
  - If constraints are violated, **surgically re-place the residual violators**
    (don't re-tune the relaxation — it oscillates) and repeat until clean.
  - Generate the refdes silk plan from measured bboxes.
- **Validation:** 0 same-layer pad-gap violations on real geometry; keep-outs +
  board containment respected; connectors open to the edge.
- **Deliverables:** `09_placement_exec/placement.json` +
  `refdes_silk_plan.json` + a real-geometry audit + screenshots.
- **Engineering checklist:**
  - [ ] Origin ≠ centroid handled (component `(x,y)` is the footprint origin).
  - [ ] Audit uses **component** rotation, not stale pad-rotation attrs.
  - [ ] Re-read the board in a fresh eval after every move (stale-getAll bug).
- **Automation:** placer engine ([`../automation/easyeda/`](../automation/easyeda/))
  + real-geometry audit ([`../automation/browser/`](../automation/browser/)).
- **Human review:** **approves the placement** (usability is the criterion).
- **Exit gate:** 0 violations + practical + approved → ready to export to KiCad.
