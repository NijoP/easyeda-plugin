# Design Standards — The Hard Engineering Rules

The quantifiable limits every project must respect. Unlike the heuristics in
[`knowledge-graph.md`](knowledge-graph.md), these are enforceable numbers — an agent
that violates one has produced a defect, not a judgment call. Reusable for any board.

---

## Board size vs layer count

- **Density = component courtyard area ÷ board area × 2.** ≤25% routes comfortably
  on 2-layer; ~35% is tight; **>45% ⇒ 4-layer or an interactive finish.**
- **Current → layers:** any rail whose peak current can't be a manufacturable trace
  must ride a **plane** ⇒ ≥4 layers. Add layers for *amps*, then use them for routing.

## IPC-2221 trace width

`I = k · ΔT^0.44 · A^0.725` — external 1 oz `k = 0.048`; internal 0.5 oz `k = 0.024`.
1 oz external @ΔT10 °C: **1 A = 0.25 mm · 2 A = 0.76 mm · 5 A = 2.79 mm · 10 A =
7.62 mm.** Rules:
- **>~5 mm ⇒ use a plane/pour; a trace is absurd.**
- Treat an at-limit width as **zero margin** — add ≥10%.
- A **0.5 oz inner plane ≈ half the ampacity** of 1 oz outer for the same width;
  never the sole conductor for a path above ~5 A (add an outer 1 oz bridge + via farm).

## Via ampacity (20 µm plating, ΔT10 °C)

0.2 mm drill ≈ 0.5 A · 0.3 mm ≈ 0.9 A · 0.5 mm ≈ 1.7 A · 0.8 mm ≈ 2.8 A.
- **10 A ⇒ 15–18× 0.3 mm or 5–7× 0.5 mm vias.** The via nearest the source hogs
  current → **symmetric farms.**

## Decoupling

- ≤2 mm from the pin (≤3 mm and via-at-pad above 100 MHz). "A 100 nF cap 5 cm away is
  useless at 100 MHz" — loop inductance dominates.
- Thick inner-core stackups give too little interplane capacitance (~10 pF) to help;
  all bulk decoupling is discrete and close.

## Ground & stitching

- Main GND plane **100% solid** — no slots to isolate an analog island (a slot is a
  return-path discontinuity; the pour boundary does the isolation).
- Analog-ground island: **single star-tie**, proven by deleting the tie and asserting
  the island's connected-node count == its own pin count. Exclude it from the stitch grid.
- **λ/20 stitch frequency = edge-rate knee `0.35 / t_rise`, not the clock.** Stitch
  last, collision-checked.

## Return paths

- On an `F=GND / B=power` stackup, a signal that vias F↔B changes its reference plane.
  Fix with a **GND↔power bypass cap ≤2–3 mm** at each transition — a ground stitch
  does nothing.

## Differential pairs (e.g. USB)

- Target Zdiff per spec (~90 Ω for USB). **0 vias on the pair; solid reference plane;
  no foreign via/plane-cut under the corridor.** At full-speed the run is electrically
  short — matching is best-practice; the 0-via + solid-ref rules are the hard ones.

## Fine-pitch mask bridging (geometry, not a rule)

- At ≤0.5 mm pad pitch: `web ≈ pitch − pad_width − 2×mask_expansion`. If
  `web < ~0.15 mm` it **bridges** — no clearance rule fixes it. Mitigate with an
  explicit F.Cu + solder-mask **keepout zone** at the connector mouth.

## DFM floor (JLCPCB 4-layer reference — adjust per fab)

Copper-edge clearance 0.25 mm · track/space 0.15 mm (capable 0.09) · hole-to-copper
0.20 mm · via drill ≥0.20 (prefer 0.30 signal / 0.40 power) · via pad 0.50 signal /
0.60 power · annular ring ≥0.10 mm.

## The one meta-rule

**DRC ground truth = the board's own tool + its own ruleset.** KiCad: `kicad-cli`
with the sibling `.kicad_pro`. Never a bare board file; never cross tools.
