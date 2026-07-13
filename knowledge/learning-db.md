# Learning Database — Append-Only Failure→Lesson Log

Every failure any project hits lands here in a fixed format, immediately available
to every future project. **Append only. Never delete** (a lesson that stops being
relevant is marked superseded, not removed). Agents write here; the next board reads
here before it acts.

## Entry format

```
### L<N> — <reusable heuristic title>
- Heuristic:   <the rule, stated generically — no project-specific names>
- Why:         <the physics or engineering reason>
- Instance:    <the specific project evidence>
- Validation:  <an auto-checkable assertion>
- Prevention:  <how to stop it being re-walked>
```

---

## Seed lessons (from the origin project)

### L1 — An autorouter's "0 unrouted" is not DRC
- Heuristic: validate the *imported* board with the real DRC, not the router's self-report.
- Why: the router's internal check is weaker than the real rule set.
- Instance: a board reported "0 unrouted" while `kicad-cli` found 1091 violations.
- Validation: `drc.sh <board>` returns 0 errors.
- Prevention: gate every route on `automation/kicad/drc.sh`, never the router UI count.

### L2 — Route thin first, pour last
- Heuristic: connect every pad with a thin trace, then pour planes; GND pour is the final pass.
- Why: a pour is capacity/return reinforcement, not the primary connection; pouring early strands opens.
- Instance: pour-first fragmented the GND pour and left channels unusable.
- Validation: 0 unrouted before the first pour pass.
- Prevention: enforce the Phase-11 order (planes → criticals → autoroute → power pours → GND+stitch last).

### L3 — Never a blind via-per-pad
- Heuristic: collision-check every stitch/plane-tie via against all copper on all layers before insertion.
- Why: a via landing in adjacent copper of a different net is a short.
- Instance: a via at every power pad → 250–815 net-to-net shorts.
- Validation: post-stitch shorts == 0.
- Prevention: the stitcher takes an exclusion set and checks pad/track/hole clearance per via.

### L4 — DRC needs the sibling ruleset
- Heuristic: run DRC in the board's own tool with its own ruleset; a bare board file lies.
- Why: `kicad-cli` reads rules from the sibling `.kicad_pro`; without it, defaults report phantom-clean.
- Instance: bare `.kicad_pcb` DRC said "0"; with the ruleset it was 1091.
- Validation: `drc.sh` refuses/ warns without a `.kicad_pro`.
- Prevention: always route DRC through `automation/kicad/drc.sh`.

### L5 — Asymmetric-plane cross-via needs a cap, not a stitch
- Heuristic: on an `F=GND / B=power` stackup, a fast signal that vias F↔B needs a GND↔power bypass cap ≤3 mm both ends.
- Why: the via changes the signal's reference plane; a GND stitch (GND↔GND) does nothing for the return.
- Instance: fast SPI on the power-referenced layer.
- Validation: every cross-plane fast-signal via has a bypass cap within 3 mm.
- Prevention: the router flags cross-plane fast-signal vias and requires the cap.

### L6 — Verify a part by its manufacturer ID
- Heuristic: confirm a placed part by decoding its manufacturer/LCSC ID against the spec, not the search string.
- Why: a fuzzy library search returns close-but-wrong parts that pass visually.
- Instance: a 12 pF cap and a 2.2 µH inductor landed in µF slots via a bad LCSC ID.
- Validation: every placed part's decoded ID matches the BOM value/type.
- Prevention: the schematic generator logs and checks `manufacturerId` per part.

### L7 — Commit geometry immediately; never couple status to paths
- Heuristic: commit every board artifact the moment it exists; status references decisions, not file paths.
- Why: uncommitted geometry is one pivot from gone; a status pointing at a deleted file lies.
- Instance: three "delivered" boards, two lost; a "SHIP" status pointing at an uncommitted, deleted file.
- Validation: the manufacturing package is committed before "manufacturing-ready".
- Prevention: Phase-12 exit gate = package committed; the project manifest holds decisions, not paths.

### L8 — Re-read the board after every mutation
- Heuristic: never trust the tool's in-memory model after a write; re-read in a fresh call.
- Why: `getAll()` is stale in the same eval; pad rotation goes stale; the net resolver lags after bulk create.
- Instance: audits showed phantom 2 mm overlaps from a pre-move snapshot; pins read FLOAT right after a bulk wire create.
- Validation: placement audits run on a fresh readback, using component (not pad) rotation.
- Prevention: the placer/auditor always re-`getAll()` after mutations.
