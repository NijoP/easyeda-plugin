# HW_GAP_ANALYSIS.md — hardware-engineering coverage gaps + roadmap

A senior hardware/PCB engineer's review of pcbflow **as a design harness that should catch what
a skilled engineer would.** It inventories what the harness verifies today, then scopes the
missing checks as workstreams — each with the check to add, the data it needs, the failure mode
it prevents, where it plugs into the existing architecture, and effort (S/M/L).

Framing: every new check is a **detector** that emits the harmonized finding schema
(`pcbflow/findings.py`) and feeds a **phase gate** (`pcbflow/gates.py`) — the same architecture
the software checks already use. These are **advisory gates**: they inform the engineer and can
block advance/export, but the human still owns every risk decision (no auto-sign-off).

---

## What the harness already covers (baseline — so we're honest)

| Layer | Covered by | Notes |
|---|---|---|
| Geometric manufacturing DRC | **`kicad-cli` DRC** | clearance, shorts, unconnected, annular ring, hole-to-hole, courtyard, silk-over-pad, edge clearance — the real geometry check |
| Netlist parity | `pcbflow import-check` | board pads match the schematic `.enet` at ref-per-net level |
| Trace sizing | `pcbflow/ipc.py` (IPC-2221) | per-trace width / plane call for a current |
| DFM pre-check | `pcbflow/dfm.py` | track width, via drill/pad/annular, hole-to-hole, silk, board size vs a JLCPCB profile |
| Topology ERC | `pcbflow/erc.py` | floating pins, dangling nets, missing ground, power-rail-without-any-cap |
| Placement | `pcbflow/geometry.py` | pad spacing, keep-out intrusion, out-of-board |
| Congestion / stitch pitch | `pcbflow/congestion.py`, `routing.py` | routing demand grid; λ/20 stitch pitch calc |

**The gap in one sentence:** this is a rigorous *manufacturing-geometry + netlist-parity*
harness, but not yet an *electrical-correctness or integrity* harness — the checks that separate
"the gerbers are clean" from "the board works and survives."

---

## Tier 1 — Electrical correctness (the "doesn't work / smokes on power-up" class) — ✅ SHIPPED

> **Status:** implemented as `pcbflow hw` (`erc_pins.py` · `power_tree.py` · `ratings.py`), enabled
> by the `parts.json` data model. HW1–HW3 below are live and tested; HW4 is a rule-table follow-up.

### HW1 · Pin-type & driver-conflict ERC  *(M)*
- **Check:** two outputs driving one net, output tied to a power rail, input left unconnected,
  bidirectional/power-pin conflicts, no-connect honored.
- **Data it needs:** electrical **pin types** (in/out/power/bidir/passive/NC). The `.enet`
  `pinInfoMap` drops these today — extend the schema (or read them from the EasyEDA symbol) so
  `pcbflow/erc.py` can reason about drive direction.
- **Prevents:** contention shorts, unpowered ICs, damaged outputs. This is the core of real ERC
  that the current topology-only ERC explicitly punts on.
- **Plugs in:** new detectors in `erc.py` → schematic gate (phase 5).

### HW2 · Component rating & value sanity  *(M)*
- **Check:** cap V-rating > rail voltage (with margin), LED current-limit resistor present and
  in range, MOSFET Vgs/Vds margin, LDO/regulator dropout at load, inductor saturation current,
  resistor power dissipation.
- **Data it needs:** part parameters (voltage/current/power ratings) — from the BOM MPN, a small
  parametric table, or datasheet lookup; rail voltages from the power tree (HW3).
- **Prevents:** exactly the failures in `knowledge/learning-db.md` — **LDO brownout** and **FET
  under-margin** — which today have no automated guard.
- **Plugs in:** new `pcbflow/ratings.py` detector → schematic/BOM gate.

### HW3 · Power-tree integrity  *(M)*
- **Check:** every IC power pin reaches a **sourced** rail; each rail traces back to a
  regulator/connector; voltage-domain consistency (a 3V3 part's VDD isn't on a 5V net); rail
  current budget ≤ its regulator rating.
- **Data it needs:** pin types (HW1) + a rail→source→voltage model derived from the netlist +
  per-part current estimates.
- **Prevents:** unpowered/mis-powered parts, over-drawn regulators, reverse-fed rails.
- **Plugs in:** new `pcbflow/power_tree.py` → schematic gate; also feeds HW2 and HW6.

### HW4 · Required-termination check  *(S)*
- **Check:** bus/reset/enable/boot-strap terminations present — I²C SDA/SCL pull-ups, reset
  pull-ups, unused-input tie-off, series termination where declared.
- **Data it needs:** net-class / interface tags (the `.enet` `netClass` already exists) + a rule
  table of "interface X requires termination Y."
- **Prevents:** dead buses, floating resets, indeterminate strap states.
- **Plugs in:** `erc.py` rule table → schematic gate.

## Tier 2 — Integrity (works at DC, fails at speed/current) — **highest ROI**

### HW0 · Stack-up model  *(S, prerequisite for HW5/HW6)*
- **Add:** a formal stack-up (layer count, copper weight per layer, dielectric thickness + Er)
  as a first-class object the integrity calcs consume. Today `dfm` only knows layers + copper-oz.
- **Plugs in:** `pcbflow/stackup.py`; consumed by HW5 (impedance) and HW6 (current/IR).

### HW5 · Signal-integrity gate — diff-pair length-match + impedance  *(M) — do this first*
- **Check:** differential-pair intra-pair skew and length-match tolerance; equal-length group
  matching; controlled-impedance targets (USB 90Ω diff, 50Ω single-ended) against the stack-up.
- **Data it needs:** **already in the `.enet`** — `differentialPair`, `equalLengthNetGroup`,
  `netClass` — plus HW0's stack-up. **Nothing consumes these fields today; the model is already
  built.** This is mostly data-plumbing.
- **Prevents:** failed USB/high-speed links, timing skew, reflections.
- **Plugs in:** new `pcbflow/si.py` detector → routing/verification gate (phases 11–12).

### HW6 · Power integrity — per-net current, via ampacity, IR drop  *(M)*
- **Check:** sum current per net (not just per trace), enforce **via ampacity** vs the actual via
  count on a high-current net, estimate IR drop across planes/traces.
- **Data it needs:** per-net current budget + HW0 stack-up + via geometry from `kicad_sexp`.
- **Prevents:** over-fused vias, browned-out rails under load, hot copper. `knowledge/` documents
  via ampacity but never enforces it.
- **Plugs in:** extend `pcbflow/ipc.py`/new `pdn.py` → routing gate.

### HW7 · Thermal  *(M)*
- **Check:** junction-temp estimate for dissipative parts, copper-area-for-dissipation, thermal
  relief adequacy on high-current pads.
- **Data it needs:** part power dissipation (from HW2/HW6) + copper area from `kicad_sexp` + θJA.
- **Prevents:** thermal shutdown, derating failures (the other half of the LDO-brownout class).
- **Plugs in:** new `pcbflow/thermal.py` → verification gate.

### HW8 · Ground/return-path & stitching enforcement  *(M)*
- **Check:** stitching vias actually present at the computed λ/20 pitch; inner planes solid;
  analog/digital ground partitioned as declared; no high-speed net crossing a plane split.
- **Data it needs:** board copper + zones from `kicad_sexp` + the stitch pitch from `routing.py`.
- **Prevents:** EMI, ground bounce, broken return paths. `routing.py` computes the pitch but
  nothing verifies the vias exist.
- **Plugs in:** new detector reading the board → verification gate.

## Tier 3 — Manufacturing & assembly reality (geometry DRC ≠ DFM/DFA) — ✅ SHIPPED

### HW9 · Footprint audit (IPC-7351)  *(M)*
- **Check:** pad geometry vs datasheet/IPC density level, courtyard, pin-1/polarity marking,
  3D model presence. The example uses admittedly **simplified** footprints — the harness has no
  footprint-correctness check.
- **Prevents:** unsolderable/misaligned parts, reversed polarity.

### HW10 · DFA / DFT  *(M)*
- **Check:** fiducials present, test-point coverage/access, tombstoning risk (asymmetric pad
  thermal), paste/stencil ratio, pick-and-place clearance, polarity marks on silk.
- **Prevents:** assembly yield loss, untestable boards.

### HW11 · BOM / sourcing verification  *(M)*
- **Check:** MPN presence, DNP handling, second-source, lifecycle/availability, package↔footprint
  match, JLCPCB/assembly compatibility.
- **Data it needs:** `enet.bom()` (exists) + a distributor/parametric lookup.
- **Prevents:** unbuildable BOMs, EOL parts, wrong packages. Today `bom()` only aggregates.
- **Plugs in:** new `pcbflow/bom_audit.py` → BOM gate (phase 2).

### HW12 · Safety creepage/clearance + panelization  *(M)*
- **Check:** creepage/clearance by **voltage class** (matters >50 V / mains / isolation), and
  panelization rules (V-score/mousebites, depanel edge clearance).
- **Prevents:** arc-over / safety-cert failure; panel/depanel damage.

## Tier 4 — Requirements ↔ design traceability — ✅ SHIPPED (HW14 mechanical deferred)

### HW13 · Requirements-to-design gate  *(S)*
- **Check:** the stated **power budget, board size, layer count, and cost target** in
  `01_feasibility` are machine-verified against the actual BOM/board — not just documented.
- **Data it needs:** structured feasibility fields + `bom()` cost + board size from `kicad_sexp`.
- **Prevents:** silent scope drift (a board that quietly blew its cost/size/power target).
- **Plugs in:** new `pcbflow/feasibility_check.py` → feasibility gate (phase 1) + export gate.

### HW14 · Mechanical / 3D  *(L)*
- **Check:** enclosure/connector collision, mounting-hole vs standoff, board-outline vs
  mechanical drawing.
- **Prevents:** boards that don't fit their enclosure.

---

## Priority sequence (by leverage × failure-cost)

1. **HW5 (SI gate)** — the `.enet` already carries diff-pair/equal-length/net-class intent that
   nothing reads; a real length-match + impedance gate is mostly plumbing on a model you built.
   Pair with **HW0 (stack-up)**.
2. **HW2 (ratings) + HW3 (power tree)** — these map directly onto failures the project's own
   `learning-db` already paid for (LDO brownout, FET margin). Highest "we've been burned by this."
3. **HW1 (pin-type ERC)** — unblocks HW3/HW2 and closes the biggest hole in schematic correctness.
4. **HW6 (PDN) + HW8 (return path)** — the reason 4-layer/routing rigor exists in the first place.
5. **HW11 (BOM audit) + HW9 (footprints)** — buildability.
6. The rest (HW4, HW7, HW10, HW12, HW13, HW14) as the domain demands (e.g. HW12 only when a board
   is high-voltage).

**Method, when we execute:** same loop as the software hardening — one workstream per phase, each
a detector emitting harmonized findings behind a gate, with a known-good + known-bad fixture that
proves it blocks the failure it targets. See [`../IMPROVEMENT_PLAN.md`](../IMPROVEMENT_PLAN.md)
for the format and [`../VALIDATION.md`](../VALIDATION.md) for the proof discipline.
