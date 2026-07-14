# Phase 3 — EasyEDA project init

*Live front-end step (EasyEDA Pro). For this text reference the geometry is produced directly
as the KiCad board in phase 10; on a real board you capture the schematic here first.*

- Create the project, one schematic sheet, 2-layer stack-up (1 oz).
- Add the parts from [`../02_bom/bom.md`](../02_bom/bom.md): J1 USB-C, U1 ME6211C33, R1/R2 5.1 kΩ,
  R3 1 kΩ, C1/C2, D1.
- The AI drives EasyEDA via the Bridge (`automation/easyeda/`). This capture is the one
  manual/live step (**NEEDS-LIVE-VALIDATION**); everything downstream runs offline via
  [`make example`](../README.md#reproduce-it-end-to-end).
