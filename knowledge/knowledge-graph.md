# Knowledge Graph — Reusable Heuristics

The distilled engineering intelligence: decisions, failures, and quantified rules,
each stated as a reusable rule with the origin instance as evidence. This is a
concise index; the **full graph with all nodes** is in
[`../docs/03_KNOWLEDGE_GRAPH.md`](../docs/03_KNOWLEDGE_GRAPH.md).

## The load-bearing nodes (internalize these first)

**Decisions**
- Density drives board size (≤25% → 2-layer; >45% → 4-layer/interactive).
- Current drives layer count, not routability (add layers for amps, then exploit).
- The module antenna variant is the highest-leverage RF call on a compact board.
- A UX feature is a client call; a safety function is an engineering mandate.

**Layout / routing**
- Route thin first, pour last (GND pour is always the final pass).
- On 2-layer you can't have both a solid bottom GND and zero unrouted.
- Promote a working board to more layers; don't re-route from scratch.
- Never a blind via-per-pad (collision-check every via).
- A dense cluster's opens are a *track* problem — rip-up-reroute, don't re-floorplan.
- Analog-ground island: single star-tie, proven as an invariant.
- Asymmetric-plane cross-via needs a bypass cap, not a ground stitch.

**Electrical (quantified)**
- IPC-2221 widths; >~5 mm ⇒ plane. 0.5 oz inner ≈ half the ampacity of 1 oz outer.
- Decoupling is dominated by loop inductance (≤2 mm from pin).
- λ/20 stitch freq = edge-rate knee `0.35/t_rise`, not the clock.

**Tooling / governance**
- The tool's live state is ground truth; snapshots lie — re-read after every mutation.
- DRC must match the board's authoring tool + correct ruleset.
- Connect by net name; verify a part by decoding its manufacturer ID.
- Never couple status to artifact paths; commit geometry immediately.

The hard, quantifiable subset is enforced in
[`design-standards.md`](design-standards.md); newly-discovered instances land in
[`learning-db.md`](learning-db.md) and graduate here when seen more than once.
