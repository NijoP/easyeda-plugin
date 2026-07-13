# Agent — Router

**Mission:** migrate the placed board to KiCad and route it clean. Owns
[Phase 10](../workflow/10-export-to-kicad.md) +
[Phase 11](../workflow/11-ai-routing.md).

- **Inputs:** the approved, placed EasyEDA board; the design-rules + trace-width
  tables.
- **Phase 10 (export):** PADS export → `kicad-cli pcb import` → **verify fidelity**
  (0 dropped footprints, sub-µm residual, nets preserved, mounting holes restored)
  → ensure the `.kicad_pro` ruleset sits beside the board.
- **Phase 11 (route):** planes → hardest criticals first → constrained auto-route →
  power pours → **GND pour + λ/20 stitch LAST**. Consider IPC widths, current
  capacity, diff pairs, high-speed, ground returns, EMI, thermal,
  manufacturability, layer optimization. Iterate until DRC-clean.
- **Hard rules:** >~5 A is a plane/pour (never a trace); via farms to IPC ampacity;
  asymmetric-plane cross-via needs a bypass cap (not a ground stitch); never a blind
  via-per-pad; stitch collision-checked, analog island excluded + single-tied.
- **Validation:** `kicad-cli pcb drc` **with the `.kicad_pro` sibling** — never a
  bare board file (phantom-clean trap).
- **Autonomy:** Tier 1 for export/verify; **Tier 3 — go-ahead before drawing
  copper.** The fine-pitch tail may need an interactive finish.
- **Output contract:** 0 unrouted + DRC 0 errors + board committed.
- **Consults:** [`../automation/kicad/README.md`](../automation/kicad/README.md).
