# Phase 6 — Placement plan

Board ≈ 35 × 22 mm, 2-layer. Partition left→right by signal flow:

| Region | Parts | Why |
|---|---|---|
| Left edge | **J1** USB-C | connector must open to the board edge |
| Left-centre | R1, R2 (CC pull-downs) | close to J1's CC pins |
| Centre | **U1** LDO + **C1** (in) + **C2** (out) | decoupling caps within ~2 mm of the LDO pins |
| Right | R3 + **D1** LED | LED visible at the edge |

Keep-outs: 0.25 mm copper-to-edge all around (matches the DRC ruleset).
