# Agent — BOM Planner

**Mission:** produce a fully validated Bill of Materials. Owns
[Phase 2](../workflow/02-bom-planning.md).

- **Inputs:** approved architecture; target region/distributors; cost target.
- **Outputs:** `02_bom/bom.md` + `02_bom/datasheets/` — every part with
  distributor/LCSC ID, datasheet note, second source, lead-time flag.
- **Selection rules (all must hold per part):** Indian-market availability · LCSC
  availability · cost optimization · long-term availability · preferred
  manufacturers · package compatibility · electrical compatibility · lead time ·
  manufacturing constraints.
- **Validation:** verify each part by **decoding its manufacturer/LCSC ID** vs the
  spec — never the search string (a fuzzy match dropped a 12 pF cap and a 2.2 µH
  inductor into µF slots once).
- **Autonomy:** Tier 1 — research and validate; human signs cost/feature trades.
- **Output contract:** BOM table + a `PASS/CONDITIONAL/FAIL` on the nine rules.
- **Tooling note:** some distributor sites block automated *fetch* → use web
  *search* to confirm availability, ground prices on cross-distributor twins.
- **Consults:** [`../knowledge/learning-db.md`](../knowledge/learning-db.md),
  [`../knowledge/knowledge-graph.md`](../knowledge/knowledge-graph.md).
