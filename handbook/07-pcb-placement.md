# 07 — PCB Placement

**Workflow steps:** [Phase 6](../workflow/06-placement-planning.md)–[Phase 9](../workflow/09-automated-placement.md) · **For:** electronics engineers.

- **Purpose:** decide where every component sits, then place them — cleanly and
  practically.
- **What you need:** a clean (audited) schematic.
- **What you get:** a placed board that is manufacturable and assemblable, with no
  spacing violations.

## The four stages

1. **Placement planning (you lead).** You define the physical facts: board size and
   shape, where the connectors and USB go, sensor positions, the MCU location,
   mounting holes, keep-out areas, and any preferences. These are *your* mechanical
   decisions.
2. **Placement knowledge graph (the AI thinks first).** Before moving anything, the
   AI works out what must sit near what and why — high-current paths, heat sources,
   analog vs digital separation, EMI-sensitive parts, decoupling caps next to their
   chips.
3. **Visual placement plan (you approve).** The AI shows you a **map** of the zones
   before touching the board. You check it against your requirements and it refines
   until you're happy.
4. **Automated placement (the AI executes).** Once you approve the map, the AI places
   all components and checks the real spacing.

## What you do

- Provide the mechanical constraints (step 1).
- Approve the visual map (step 3) — this is the key checkpoint. A board that passes
  every electrical rule but can't be plugged in or assembled is a failure.
- Approve the final placement.

## What the AI does

- Builds the placement reasoning, proposes the zone map, then places and re-checks on
  the **real** board geometry (not just an estimate).
- Keeps decoupling caps close to their chips, opens connectors to the board edge, and
  keeps sensors that work together aligned to the same axis.

## What good looks like

- Connectors, USB, and button sit on the edge and open outward.
- No two parts too close to hand-solder; nothing over a mounting hole or keep-out.
- The layout leaves room for the routing that comes next.

## Common mistakes

- Letting placement start before you've fixed the board outline and connector
  positions.
- Judging placement only by a screenshot — approve it against real dimensions.
- Optimizing for short wires at the cost of assembly — practicality wins.

## Validation checklist

- [ ] Board outline, connectors, mounting holes, keep-outs defined.
- [ ] Visual placement map approved against requirements.
- [ ] Final placement has 0 spacing violations on real geometry.
- [ ] Edge parts open outward; sensors aligned; decaps close to chips.
- [ ] I approved the placement.

## Next step

The placed board moves to KiCad for routing.

---
◀ [06 — Schematic generation](06-schematic-generation.md) · Next ▶ [08 — Routing](08-routing.md)
