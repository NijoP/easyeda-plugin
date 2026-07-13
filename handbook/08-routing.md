# 08 — Routing

**Workflow steps:** [Phase 10](../workflow/10-export-to-kicad.md) + [Phase 11](../workflow/11-ai-routing.md) · **For:** electronics engineers.

- **Purpose:** connect every net with copper, correctly and manufacturably.
- **What you need:** an approved placement.
- **What you get:** a fully routed board that passes the design-rule check (DRC).

## Why routing happens in KiCad

Routing and rule-checking can be automated far better in KiCad than in EasyEDA. So
the AI **moves your placed board from EasyEDA to KiCad** (and checks the move is
faithful — same parts, same positions) before routing. You don't manage this
handoff; you just approve the go-ahead to route.

## What the AI does

Routing is done to professional standards. The AI works through, in order:

1. the **ground and power planes**,
2. the **hardest, most sensitive nets first** (differential pairs, high-speed
   signals) while there's room,
3. the **bulk of the signals**,
4. the **power pours**,
5. and the **ground pour with stitching last**.

Throughout, it respects: IPC trace-width and current rules, ground return paths,
EMI, thermal spread, and manufacturability. It repeats until the design-rule check is
clean.

## What you do

- Give the **go-ahead to route** (this is a checkpoint — routing changes the board).
- Review the routing report and the DRC result.
- If a few tricky spots need a human hand (very fine-pitch escapes), the AI tells you
  exactly which and gives you a precise plan.

## What good looks like

- **Zero unrouted nets.**
- **DRC reports zero errors** against the board's own rule set.
- High-current paths are wide copper or planes (never thin traces); grounds return
  cleanly.

## Common mistakes

- Starting routing before the placement is truly final — re-placing after routing
  wastes the routing.
- Trusting a "0 unrouted" number from a router without a real DRC — the AI always
  confirms with the proper design-rule check.

## Validation checklist

- [ ] Board exported to KiCad and verified to match EasyEDA.
- [ ] 0 unrouted nets.
- [ ] DRC: 0 errors against the correct rule set.
- [ ] High-current paths sized correctly; grounds clean.
- [ ] The routed board is saved.

## Next step

With routing clean, run the final verification.

---
◀ [07 — PCB placement](07-pcb-placement.md) · Next ▶ [09 — Verification](09-verification.md)
