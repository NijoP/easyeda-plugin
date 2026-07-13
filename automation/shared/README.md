# automation/shared/ — Backend-Agnostic Engineering Math

Pure computation, no EDA tool. Used across phases (feasibility, KG, routing).

## What lives here

- **IPC-2221 trace-width solver.** `I = k·ΔT^0.44·A^0.725` (k=0.048 external 1 oz,
  0.024 internal 0.5 oz) → the minimum width for a net's peak current. Any net whose
  minimum exceeds ~5 mm must be a **plane/pour**, not a trace. Emits
  [`../../templates/trace_width_table.template.json`](../../templates/trace_width_table.template.json)
  from a netlist + current budget.
- **Via ampacity.** 0.3 mm drill ≈ 0.9 A, 0.5 mm ≈ 1.7 A (20 µm plating, ΔT10) →
  via-farm sizing (10 A ⇒ 15–18× 0.3 mm). The via nearest the source hogs current →
  symmetric farms.
- **Unit conversion.** mm ↔ EasyEDA internal (×39.3700787), mil, KiCad nm.
- **Congestion grid.** 2 mm-bin routing-demand model per layer;
  `demand > capacity` ⇒ a via-fan is required. Emits
  [`../../templates/placement.template.json`](../../templates/placement.template.json)-adjacent
  congestion data and predicts IC-edge saturation before it happens.

## Why it's separate

These are engineering facts, not tool behaviours — they don't change when the EDA
backend changes. Keeping them backend-agnostic means the feasibility analyst, the
placement planner, and the router all use the *same* numbers. The hard rules behind
them live in [`../../knowledge/design-standards.md`](../../knowledge/design-standards.md).
