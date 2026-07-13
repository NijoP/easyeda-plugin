# Phase 4 — Autonomous Schematic Generation

**Owning agent:** schematic-generator · **Tool:** EasyEDA (Standalone-Script) · **Autonomy:** Tier 1/2 (AI generates; human runs the script + Annotate)

Using the approved BOM, the EasyEDA API, browser automation, and Node.js scripts,
generate the schematic **one functional block at a time.**

- **Objective:** realize the schematic, section by section, re-runnably.
- **Inputs:** `build_sheet.md` (PARTS + PASSIVES per block), the block's pin→net map.
- **Outputs:** one generator script per block; parts placed & wired by net name.
- **The AI:** creates/finds symbols, places components, wires connections
  **by net name** (short stubs — long collinear stubs auto-merge into shorts),
  organizes blocks into pages, verifies interfaces, follows best practices.
- **Validation:** script LOG shows 0 unmatched pins, 0 skipped parts; parts
  token-matched (never `search()[0]`); array parts rejected; passives value-verified.
- **Deliverables:** `04_schematic/gen/<block>.js` per block; the live schematic.
- **Engineering checklist:**
  - [ ] Every IC decoupled; boot-strap/enable pins strapped; open-drain buses pulled.
  - [ ] Analog ground is a separate net with exactly one tie point.
  - [ ] Interfaces (USB, SPI, I²C) wired per datasheet.
- **Automation:** the board-agnostic engine
  ([`../automation/easyeda/section_generator.template.js`](../automation/easyeda/section_generator.template.js));
  batch execution via [`../automation/browser/`](../automation/browser/).
- **Human intervention:** **only when an engineering decision needs approval** — the
  human runs each script and runs project-wide **Annotate** (designators aren't
  scriptable).
- **Exit gate:** every block placed & wired, 0 unmatched pins, Annotate done →
  ready for audit.
