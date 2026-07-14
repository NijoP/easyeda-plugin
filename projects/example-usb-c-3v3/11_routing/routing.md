# Phase 11 — Routing

2-layer, explicit tracks (no unfilled pours). Widths from the net classes in
[`design_rules.json`](design_rules.json): **POWER** (VBUS, +3V3) at 0.4 mm, everything else at
0.25 mm — all ≥ the 0.15 mm fab floor. GND is routed with real tracks (not a zone) so the board
is DRC-connected without an interactive fill. DRC ground truth = `kicad-cli` against this ruleset.
