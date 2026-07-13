# Phase 2 — BOM Planning

**Owning agent:** bom-planner · **Tool:** web research · **Autonomy:** Tier 1 (execute; human signs cost trades)

Once the project is approved, generate the Bill of Materials. **The BOM is fully
validated before schematic design begins.**

- **Objective:** a BOM where every part is datasheet-verified, sourcable, and
  second-sourced.
- **Inputs:** the approved architecture; target region/distributors; cost target.
- **Outputs:** a BOM with distributor/LCSC IDs, datasheet notes, second-source
  column, lead-time flags.
- **Component-selection rules (all must be satisfied per part):**
  Indian-market availability · LCSC availability · cost optimization · long-term
  availability · preferred manufacturers · package compatibility · electrical
  compatibility · lead time · manufacturing constraints.
- **Validation:** verify each part by **decoding its manufacturer/LCSC ID** against
  the spec — never trust the search string.
- **Deliverables:** `02_bom/bom.md`, `02_bom/datasheets/` notes per critical part.
- **Engineering checklist:**
  - [ ] Module variant correct (e.g. onboard vs external antenna — decisive on a
        compact board).
  - [ ] Every regulator's dropout adequate at minimum battery voltage.
  - [ ] No "cheap clone" trap (genuine part vs a look-alike module).
  - [ ] Packages hand-solderable if that's a project constraint.
- **Automation:** distributor availability search (some sites block automated
  *fetch* → use web *search*); cost roll-up; datasheet Q&A extraction.
- **Human review:** client signs cost/feature trades (a fuel-gauge IC vs an ADC
  divider is a UX/cost call, not an engineering mandate).
- **Exit gate:** every part validated on all nine rules, second sources noted, cost
  target met or the gap justified → **BOM approved.**

> Knowledge: [`../knowledge/learning-db.md`](../knowledge/learning-db.md) (sourcing
> gotchas), [`../knowledge/knowledge-graph.md`](../knowledge/knowledge-graph.md) (component-choice heuristics).
