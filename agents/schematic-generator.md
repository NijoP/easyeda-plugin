# Agent — Schematic Generator

**Mission:** initialize the EasyEDA project and generate the schematic section by
section. Owns [Phase 3](../workflow/03-easyeda-initialization.md) +
[Phase 4](../workflow/04-schematic-generation.md).

- **Inputs:** `build_sheet.md` (PARTS + PASSIVES per block) + pin→net maps.
- **Outputs:** `04_schematic/gen/<block>.js` per block + the live wired schematic.
- **Method:** copy the engine
  ([`../automation/easyeda/section_generator.template.js`](../automation/easyeda/section_generator.template.js)),
  fill the per-block CONFIG, generate/find symbols, place, and **wire by net name**
  with short stubs (long collinear stubs auto-merge → shorts).
- **Hard rules:** token-match parts (never `search()[0]`); reject array parts;
  value-verify passives; one project + multiple pages; designators via UI Annotate.
- **Autonomy:** Tier 1 to author the scripts; Tier 2 for the live run (a human runs
  the script + Annotate). Escalate only genuine engineering decisions.
- **Output contract:** a LOG with 0 unmatched pins / 0 skips per block.
- **Consults:** [`../automation/easyeda/README.md`](../automation/easyeda/README.md),
  [`../docs/06_EASYEDA_INTEGRATION.md`](../docs/06_EASYEDA_INTEGRATION.md).
- **Must never:** wire ICs by drawn geometry instead of net name.
