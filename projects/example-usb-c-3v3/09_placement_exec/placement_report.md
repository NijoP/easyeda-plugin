# Phase 9 — Placement execution + spacing audit

Placement is executed by the generator and checked against real geometry (never the placer's
own grid model). Same-layer pad gaps are kept above the hand-assembly minimum; copper stays
≥ 0.25 mm from the board edge. The routed board then passes `kicad-cli` DRC clean
(see [`../12_verification/verification.report.md`](../12_verification/verification.report.md)).
