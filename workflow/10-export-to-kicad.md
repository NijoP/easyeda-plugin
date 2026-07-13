# Phase 10 — Export to KiCad

**Owning agent:** router · **Tool:** EasyEDA → KiCad · **Autonomy:** Tier 1 (execute + verify)

**Routing is not done in EasyEDA.** Move the placed board to KiCad, which is the
routing engine, and verify the migration is lossless.

- **Objective:** the placed board, faithfully in KiCad, ready to route.
- **Inputs:** the approved, placed EasyEDA board.
- **Actions:**
  - Export the PCB in **PADS** format (`pcb_ManufactureData.getPadsFile()`) — PADS
    carries nets + placement; the Altium export is unusable ASCII.
  - Import into KiCad (`kicad-cli pcb import --format pads`).
  - **Verify the imported board matches the EasyEDA design**: 0 dropped footprints,
    sub-µm position residual (unit-agnostic affine fit), all nets present,
    placement preserved.
  - Restore anything the export drops (M2 mounting holes live on EasyEDA's hole
    layer and often don't survive → re-add and re-verify).
- **Validation:** import fidelity report — footprint count in == out, max position
  residual ≈ 0, net count preserved, only expected items unconnected.
- **Deliverables:** `10_kicad_export/board.kicad_pcb` + a sibling `.kicad_pro`
  (carries the DRC ruleset — required for real DRC) + a fidelity report.
- **Engineering checklist:**
  - [ ] Footprints: in-count == out-count, 0 dropped.
  - [ ] Position residual sub-µm; placement visually matches.
  - [ ] Mounting holes / keep-outs restored.
  - [ ] The `.kicad_pro` ruleset is present beside the board.
- **Automation:** PADS export + `kicad-cli` import + fidelity check
  ([`../automation/kicad/`](../automation/kicad/)).
- **Human review:** confirms the import is faithful.
- **Exit gate:** imported board verified == EasyEDA, placement preserved → route.

> Why the split: KiCad's `pcbnew`/`kicad-cli` API can script pours, zones,
> stitching, and DRC; EasyEDA's cannot. The board lives where routing is
> automatable. See [`../automation/kicad/README.md`](../automation/kicad/README.md).
