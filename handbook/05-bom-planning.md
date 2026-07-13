# 05 — BOM Planning

**Workflow step:** [Phase 2](../workflow/02-bom-planning.md) · **For:** electronics engineers.

- **Purpose:** produce a Bill of Materials where every part is real, available, and
  the right choice.
- **What you need:** the approved feasibility study.
- **What you get:** a validated BOM you can hand to purchasing and to the schematic step.

## What the AI does

For each part it checks the engineering essentials you'd check yourself, just faster
and across more sources:

- availability (Indian market **and** LCSC), lead time, long-term availability,
- cost, and cheaper equivalents,
- package suitability (including hand-soldering if that matters to you),
- electrical fit,
- preferred manufacturers.

It also **confirms each part is really the right one** by checking its manufacturer
part number against the specification — this catches the classic mix-up of a
wrong-value capacitor or a look-alike part slipping into the list.

## What you do

- Tell the AI your constraints: budget, region, quantity, any preferred vendors, any
  "must-use" parts.
- Review the proposed BOM. Approve, or swap parts you don't like.
- Sign off cost/feature trade-offs — those are yours to make (e.g. a fuel-gauge chip
  vs. a simpler battery-voltage reading).

## What good looks like

- Every line has a real part number, a source, a second source, and a price.
- No "TBD" parts.
- Costs add up to your target, or the gap is explained.

## Common mistakes

- Approving a BOM with a single source for a critical part — ask for a backup.
- Ignoring package choice — a part that's cheaper but impossible to hand-solder can
  wreck a prototype.
- Trusting a part by its description alone — the AI verifies by part number for a
  reason; you should too.

## Validation checklist

- [ ] Every part available (India + LCSC) with a lead time noted.
- [ ] Every critical part has a second source.
- [ ] Packages suit your assembly method.
- [ ] Cost target met or the gap justified.
- [ ] I approved the BOM.

## Next step

With the BOM approved, the AI sets up the EasyEDA project and draws the schematic.

---
◀ [04 — Creating your first project](04-your-first-project.md) · Next ▶ [06 — Schematic generation](06-schematic-generation.md)
