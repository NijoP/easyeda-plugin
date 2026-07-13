# Phase 11 — AI-Assisted Routing (in KiCad)

**Owning agent:** router · **Tool:** KiCad (`pcbnew` + `kicad-cli`) · **Autonomy:** Tier 3 (go-ahead before drawing copper)

KiCad is the routing engine. Routing is AI-assisted automation, iterated until all
design rules are satisfied.

- **Objective:** a fully routed board, DRC-clean against its own ruleset.
- **Inputs:** the verified KiCad board + its `.kicad_pro` ruleset; the design-rules
  + trace-width tables.
- **The AI considers:** IPC standards · trace-width / current capacity · differential
  pairs · high-speed signals · ground returns · EMI reduction · thermal
  performance · manufacturability · layer optimization.
- **Order (the sequence that works):** define planes → route the hardest criticals
  first (diff pairs 0-via over a solid plane; fast signals with correct return
  handling) → constrained auto-route the bulk → power pours with via farms → **GND
  pour + λ/20 stitching LAST** (pouring early strands opens; stitch freq = edge-rate
  knee `0.35/t_rise`, collision-checked, excluding any analog island).
- **Validation:** iterate until **0 unrouted** and **DRC-clean** via
  `kicad-cli pcb drc` with the `.kicad_pro` sibling present — **never a bare
  `.kicad_pcb`** (that reports phantom-clean).
- **Deliverables:** `11_routing/board_routed.kicad_pcb` (committed) + a routing
  report + the applied `design_rules.json` / `route_sequence.json`.
- **Engineering checklist:**
  - [ ] Every high-current path is a plane/pour (>~5 A can't be a trace); via farms
        sized to IPC ampacity.
  - [ ] Return paths correct — on an asymmetric-plane stackup, a cross-plane via
        needs a bypass cap, not a ground stitch.
  - [ ] Diff pairs: width/gap/Z per the rules, 0 vias, solid reference.
  - [ ] Stitching collision-checked; analog island single-tied and excluded.
  - [ ] Never a blind via-per-pad (collision-check every via).
- **Automation:** the router + stitcher + `drc.sh` ground truth
  ([`../automation/kicad/`](../automation/kicad/)); the fine-pitch tail may need an
  interactive finish.
- **Human review:** **go-ahead before routing begins**; signs the DRC-clean verdict.
- **Exit gate:** 0 unrouted + DRC 0 errors vs the ruleset + board committed →
  final verification.
