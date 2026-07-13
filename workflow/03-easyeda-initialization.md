# Phase 3 — EasyEDA Project Initialization

**Owning agent:** schematic-generator · **Tool:** EasyEDA · **Autonomy:** Tier 2 (AI prepares; human runs the live setup)

After BOM approval, stand up the EasyEDA project.

- **Objective:** an initialized EasyEDA project with the correct structure and
  stackup.
- **Inputs:** approved BOM; feasibility verdict (layer count).
- **Outputs:** a live EasyEDA project with schematic sheets and board parameters.
- **Actions:**
  - Create the EasyEDA project.
  - Create the schematic **sheets** — one project, multiple **pages** (never
    separate schematic files, or nets won't merge and designators collide).
  - Configure board parameters (outline placeholder, units, grid).
  - **Select the stackup** — 2 / 4 / 6-layer — from the feasibility verdict (added
    for current capacity or routability, with the reason recorded).
  - Initialize the source-of-truth docs: copy
    [`../templates/build_sheet.template.md`](../templates/build_sheet.template.md)
    and [`../templates/net_connection.template.md`](../templates/net_connection.template.md)
    into `04_schematic/`.
- **Validation:** sheets exist; board params + stackup set; source docs seeded.
- **Deliverables:** `03_easyeda_init/` (project ID, sheet UUIDs, stackup note);
  seeded `build_sheet.md` + `net_connection.md`.
- **Engineering checklist:**
  - [ ] Stackup matches the current/routability requirement (not defaulted).
  - [ ] Page layout planned (one page per functional block group).
- **Automation:** project/sheet creation via the browser layer
  ([`../automation/browser/`](../automation/browser/)).
- **Human review:** confirms the stackup and project setup.
- **Exit gate:** project + sheets + board params + stackup ready → **initialized.**
