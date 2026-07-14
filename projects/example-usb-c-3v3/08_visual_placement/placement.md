# Phase 8 — Visual placement

The placement realised by `tools/gen_example_board.py` (the generator is the source of truth
for exact coordinates; regenerate with `make example`):

- **J1** at the left edge, pads opening outward.
- **R1/R2** just inboard of J1's CC pins.
- **U1** centred, with **C1** at its input and **C2** at its output, both within ~2 mm.
- **R3 → D1** to the right, LED at the edge.

Verified by the real-geometry spacing audit in phase 9.
