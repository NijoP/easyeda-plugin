# 09 — Verification

**Workflow step:** [Phase 12](../workflow/12-final-verification.md) · **For:** electronics engineers.

- **Purpose:** confirm the board is truly ready to manufacture.
- **What you need:** a routed, DRC-clean board.
- **What you get:** a signed-off design and a green light to produce the files.

## What the AI checks

A complete engineering review, the same list you'd run in a design review:

- **DRC** (design-rule check) and **ERC** (electrical-rule check),
- **manufacturing** review (can the fab actually build it?),
- **silkscreen** review (labels legible, not under parts),
- **assembly** review (polarity marks, pin-1 indicators, room to solder),
- **mechanical** review (mounting holes, clearances),
- **BOM** validation (the parts list matches what's on the board).

## What you do

- Review the verification report.
- **Sign off** the design — this is your professional judgment, and it stays yours.
  The AI verifies and recommends; you approve.

## What good looks like

- Every check passes.
- Nothing is starved or borderline without being called out and understood.
- You'd stake your name on this going to a fab.

## Common mistakes

- Treating verification as a formality — read each section.
- Passing "manufacturable but borderline" items silently. If something is at a limit,
  the report should name it so *you* decide.

## Validation checklist

- [ ] DRC and ERC clean.
- [ ] Manufacturing, silkscreen, assembly, mechanical reviews pass.
- [ ] BOM matches the placed parts.
- [ ] I signed off the design.

## Next step

Produce the manufacturing package.

---
◀ [08 — Routing](08-routing.md) · Next ▶ [10 — Manufacturing](10-manufacturing.md)
