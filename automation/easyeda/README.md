# automation/easyeda/ — Schematic + Placement Engine

The board-agnostic engine that drives EasyEDA Pro's Standalone-Script API. Used in
phases 3 (init), 4 (schematic generation), and 9 (placement).

## Files

- [`section_generator.template.js`](section_generator.template.js) — the reusable
  engine (part search, passive picking, wire-by-net-name, stub direction) plus a
  per-block CONFIG. Copy it, fill the CONFIG from `build_sheet.md`, run it in
  *EasyEDA ▸ Settings ▸ Extensions ▸ Standalone Script*.
- [`api_probe.js`](api_probe.js) — **run this first.** Discovers the real library-search
  method, the `create()` return shape, and the pin field names on *your* EasyEDA build
  (the Pro API varies by build), so the other scripts use the right names.
- [`dump_schematic.js`](dump_schematic.js) — dumps the live schematic to JSON
  (`{components, wires}`) for headless verification; feed it to
  [`../browser/recon.py`](../browser/recon.py) via the CDP driver.

## The API contracts (that work)

| Call | Purpose |
|---|---|
| `sch_PrimitiveWire.create([x1,y1,x2,y2], net)` | wire a pin — **net is arg 2**; connect by name |
| `pcb_PrimitiveLine.create('', 11, x1,y1,x2,y2)` | board outline (layer 11) |
| `pcb_PrimitiveVia.create(net, x, y)` | via (collision-check first) |
| `setState_X/Y/Rotation/Layer + done()` | place a component (NOT `modify({x,y})`) |

## Hard rules & limits

- **Connect by net name**, short stubs (long collinear stubs auto-merge → shorts).
- **Never `search()[0]`** — token-match, reject array parts, verify by
  `manufacturerId`. Passives: `"<value> 0603 resistor|capacitor"` + EIA-code match.
- **One project, multiple pages.** Designators via UI **Annotate** (not scriptable).
- **Units:** 1 mm = 39.3700787 internal units; Y increases downward (negate).
- **Cannot do (UI-only):** copper pours, auto-route, Annotate, Check-Nets. Probe an
  unknown `*.create` with **one guarded call**, never a loop (a loop of wrong
  signatures hard-hangs the renderer).
- **Re-read after every mutation** (`getAll()` is stale in the same eval).

Full API reference + the tested-signatures table:
[`../../docs/06_EASYEDA_INTEGRATION.md`](../../docs/06_EASYEDA_INTEGRATION.md).
