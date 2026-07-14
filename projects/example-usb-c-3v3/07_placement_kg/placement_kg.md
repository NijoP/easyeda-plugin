# Phase 7 — Placement knowledge graph

Proximity constraints the placement must honour (the "why" behind phase 6):

- `C1 → U1.VIN` and `C2 → U1.VOUT`: decoupling caps **≤ 2 mm** from the regulator pins
  (loop area / transient response).
- `R1 → J1.CC1`, `R2 → J1.CC2`: the 5.1 kΩ Rd terminations sit at the connector.
- `J1` and `D1` are **edge-critical** (connector opens out; LED is visible).
- `GND` is the shared return for J1, U1, C1, C2, R1, R2, D1 — kept short and direct.
