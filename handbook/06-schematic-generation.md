# 06 — Schematic Generation

**Workflow steps:** [Phase 3](../workflow/03-easyeda-initialization.md) + [Phase 4](../workflow/04-schematic-generation.md) + [Phase 5](../workflow/05-schematic-audit.md) · **For:** electronics engineers.

- **Purpose:** turn the approved BOM into a correct, checked schematic in EasyEDA.
- **What you need:** the approved BOM; EasyEDA Pro open and signed in.
- **What you get:** a complete schematic with **zero wiring errors**, ready for
  placement.

## How it works (three stages)

1. **Set up the EasyEDA project** — the AI creates the project, the sheets, and picks
   the board stack-up (2 / 4 / 6-layer) from the feasibility verdict.
2. **Draw the schematic, block by block** — power, MCU, each sensor, connectors, etc.
   The AI places the symbols and wires every connection by net name. It does one
   functional block at a time so mistakes stay small and easy to see.
3. **Audit the schematic** — before any PCB work, the AI reads the finished schematic
   back and checks it for: missing nets, floating pins, short circuits, rule
   violations, naming problems, interface correctness, and datasheet compliance.

## What you do

- Run the drawing scripts the AI hands you inside EasyEDA (it tells you exactly
  where: *Settings → Extensions → Standalone Script*), and run **Annotate** when it
  asks (this numbers the parts).
- Review the audit report. Approve, or point at anything wrong.
- Make the engineering calls the AI flags (e.g. "should this pull-up be 4.7 k or
  10 k?").

## What the AI does

- Finds the correct symbols, places them, and wires by net name.
- Organizes the schematic into readable blocks across sheets.
- Runs the full audit and gives a verdict: PASS / CONDITIONAL / FAIL.

## What good looks like

- Every block placed and wired, with no unconnected pins.
- The audit reports **0 shorts, 0 floating pins**, and the net list exactly matches
  the plan.
- Analog ground connects to ground at exactly one point.

## Common mistakes

- Skipping the audit and going straight to layout. **This is the cheapest, most
  valuable check in the whole flow** — a schematic error caught here saves hours of
  layout rework.
- Forgetting to run **Annotate** in EasyEDA — the part numbers won't be set otherwise.

## Validation checklist

- [ ] Board stack-up chosen and set.
- [ ] Every block drawn and wired; 0 unconnected pins.
- [ ] Audit: 0 shorts, 0 floating pins, net list matches the plan.
- [ ] Parts annotated in EasyEDA.
- [ ] I approved the audit.

## Next step

With a clean schematic, plan the physical layout.

---
◀ [05 — BOM planning](05-bom-planning.md) · Next ▶ [07 — PCB placement](07-pcb-placement.md)
