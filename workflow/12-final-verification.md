# Phase 12 — Final Verification

**Owning agent:** verification-engineer · **Tool:** KiCad + DFM · **Autonomy:** Tier 6 (AI verifies; human signs + orders)

A complete engineering review. **Only after this passes is the project
manufacturing-ready.**

- **Objective:** a fabricatable, committed manufacturing package with a signed
  verdict.
- **Inputs:** the routed, DRC-clean board.
- **The review:** DRC · ERC · manufacturing review · silkscreen review · assembly
  review · mechanical review · BOM validation · final documentation.
- **Validation:** DRC 0 errors (correct ruleset); fab DFM check passes (loginless
  DFM portals can be automated); CPL/BOM cross-check against the placed parts;
  silk legible; mechanical (mounting, clearances) confirmed.
- **Deliverables:** `12_verification/manufacturing/` — gerbers (incl. inner layers),
  drill, CPL, BOM, assembly renders, a DFM report + a zipped package — **all
  committed to git.** Plus `12_verification/final_report.md` with the verdict.
- **Engineering checklist:**
  - [ ] Every layer exported; inner planes present.
  - [ ] Mounting holes + mechanical keep-outs correct.
  - [ ] BOM matches the placed parts; CPL positions correct.
  - [ ] Silkscreen: no refdes under parts, legible size, no pad overlap.
  - [ ] Assembly: polarity marks, pin-1 indicators, hand-solder access if required.
- **Automation:** gerber/drill/CPL export + automated DFM upload + BOM/CPL
  cross-check ([`../automation/kicad/`](../automation/kicad/)).
- **Human review:** signs the DFM report and **places the fab order** — the one
  thing the AI never does (irreversible, external, spends money).
- **Exit gate:** all reviews pass + package **committed** + order placed by a human
  → **manufacturing-ready.**

> Then: write any new lessons to
> [`../knowledge/learning-db.md`](../knowledge/learning-db.md) so the next board
> starts ahead of this one.
