# automation/kicad/ — Routing & Verification Engine

**Routing happens here, not in EasyEDA.** KiCad's `pcbnew` + `kicad-cli` API can
script pours, zones, stitching vias, and DRC — the things EasyEDA's API refuses.
Used in phases 10 (export/import), 11 (routing), 12 (verification).

## The DRC ground truth — the most important rule

DRC is only trustworthy when run in the board's own tool with the board's own
ruleset. `kicad-cli pcb drc` reads the ruleset from the **sibling `.kicad_pro`** — a
bare `.kicad_pcb` reports the weak defaults as "clean" (the phantom-DRC trap that
turned a real 1091 violations into a false "0"). Always wrap it:

- [`drc.sh`](drc.sh) — copies the ruleset beside the board, then runs `kicad-cli`.
  **This is the ground truth.** Never run bare `kicad-cli pcb drc` on a naked board.

## The pipeline this engine supports

- **Phase 10 — import:** PADS export from EasyEDA → `kicad-cli pcb import --format
  pads` (carries nets + placement; the Altium export is unusable ASCII). Verify
  fidelity: 0 dropped footprints, sub-µm residual. Restore mounting holes (they
  don't survive the export).
- **Phase 11 — route:** planes → criticals → constrained auto-route → power pours →
  **GND pour + λ/20 stitch LAST**. Stitching vias are **collision-checked** against
  all copper on all layers before insertion (a blind via-per-pad gave 250–815
  shorts). The analog-ground island is single-tied and excluded from the stitch grid.
- **Phase 12 — verify/export:** DRC (via `drc.sh`), gerbers/drill/CPL/BOM export,
  DFM.

## Engineering rules baked in

- >~5 A ⇒ plane/pour, never a trace; via farms sized to IPC ampacity.
- On an asymmetric-plane stackup, a cross-plane via needs a GND↔plane bypass cap,
  not a ground stitch.
- Treat every `pcbnew` session as one-shot (handles go stale after mutation).

Deep reference: [`../../docs/11_REUSABLE_SYSTEMS.md`](../../docs/11_REUSABLE_SYSTEMS.md)
(S7 migration/stitcher, S8 audit), [`../../docs/09_VALIDATION.md`](../../docs/09_VALIDATION.md).
