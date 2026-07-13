# 00 · Architecture Audit Report — PCB Flow

**Role:** Harness-Level Engineering Architect. **Scope:** learn from mature ECAD ecosystems
(EasyEDA/JLCEDA, KiCad) and design the architecture of an **AI-native Electronics Engineering
Workspace**. **Method:** reverse-engineer *contracts and engineering decisions*, never copy
code. **Status:** audit — *no implementation until approved* (the P0 Bridge client already
merged stands on its own; nothing here is built yet).

Detail annexes: [`01 EasyEDA teardown`](01_EASYEDA_TEARDOWN.md) ·
[`02 KiCad teardown`](02_KICAD_TEARDOWN.md) · [`03 Target architecture`](03_TARGET_ARCHITECTURE.md) ·
[`04 Knowledge graph`](04_KNOWLEDGE_GRAPH.md).

---

## Executive summary

Two mature ECAD tools, studied independently, **converge on the same architecture**:
*structured source + derived geometry + data-driven rules + out-of-process automation +
external routing + convention-checked libraries.* Our project reached the same thesis by
different means (*knowledge is source, geometry is a build artifact*). The audit's conclusion
is therefore high-confidence: **build a thin, tool-agnostic, pure-Python core over a
CAD-adapter seam; treat EasyEDA and KiCad as backends; keep rules and netlists as versioned,
verifiable data; keep AI provider-neutral and out-of-process.** The largest architectural gap
today is that our code still assumes a single tool (EasyEDA-via-CDP); the fix is the
**`CadBackend` interface** + a **tool-neutral IR**.

---

## 1 · What we learned from EasyEDA

1. **Kernel + plugin runtime.** One editor core; ~60 `eext-*` features as plugins over a
   stable class-based API (`eda.*`). Extensibility without forking.
2. **One scripting API serves humans *and* AI** — the same surface a user clicks is what the
   AI scripts. Powerful, but **no schema at the call boundary** (wrong signature → renderer
   hang) → we must add a typed/probed wrapper.
3. **Out-of-process AI bridge** (`bridge-server.mjs`): HTTP/WS gateway, port discovery +
   `service` handshake, UUID-correlated `/execute`, window multiplexing, timeouts, errors as
   data. The right way to drive an editor.
4. **`.enet` v2.0.0** — a versioned netlist that carries connectivity **+ design intent**
   (net classes, diff pairs, length groups) **+ physical rules**, with a conformance verifier.
5. **Data-driven, manufacturer-aware DFM** (18 PCB + 7 SMT), thresholds auto-selected by
   material/layers/copper, with correct primitive math (rotated-pad distance, same-net skip).
6. **Routing is external + KiCad-as-format-hub** (freerouting, Rust-A* KiCadRoutingTools).
7. **Design intelligence as a view layer** (`eext-netlist-explorer`) = our `pcbmunch`.

Full analysis + subsystem I/O/failure-modes: [`01`](01_EASYEDA_TEARDOWN.md).

## 2 · What we learned from KiCad

1. **Explicit typed object model** (BOARD→FOOTPRINT→PAD/TRACK/VIA/ZONE) with **derived
   connectivity** — rigor that makes real DRC possible.
2. **Text-first s-expression source** (diffable, versionable) + **JSON project file holding
   rules/net-classes** — geometry is reviewable, rules live *with* the project.
3. **Data-driven DRC/ERC rule engine** (constraint + condition + severity) — *rules are data*,
   the same shape as EasyEDA's DFM. Strong cross-tool convergence.
4. **Two automation altitudes:** `kicad-cli` (stable headless verifier — our DRC ground truth)
   and the **IPC API `kipy`** (out-of-process, versioned; supersedes in-process SWIG `pcbnew`).
5. **Convention-checked + generatable libraries** (KLC checkers, footprint wizards) — validate
   and generate parts instead of trusting fuzzy vendor search.
6. **Rendering is a projection** of the model (plotter abstraction) — screenshots ≠ truth.

Full analysis: [`02`](02_KICAD_TEARDOWN.md). The convergence table is [`02 §D`](02_KICAD_TEARDOWN.md).

## 3 · What we learned from our own project

From [`../docs/13_LESSONS_LEARNED.md`](../docs/13_LESSONS_LEARNED.md) and memory:
- **Geometry is a build artifact** — validated by both tools' derived connectivity.
- **Phantom DRC** — a board without its ruleset sidecar DRC's against garbage → *ruleset must
  travel with the board*.
- **Decision-based state, not artifact paths** — status coupled to files that get deleted
  drifts and lies (the recovery-baseline case study).
- **CDP profile-cloning is fragile** — the official Bridge is the robust replacement.
- **No custom autorouter** ("$300 wall") — adapt external engines.
- **Coordinates are truth, `getAll()` is stale, wrong signatures hang** — the automation
  boundary needs typed, probed, envelope'd, fail-fast wrapping.
- **Envelope-never-swallow + self-healing** reliability is already a strength to preserve.

## 4 · Ideas to ADOPT

| # | Idea | Source | Where it lands |
|---|---|---|---|
| A1 | `CadBackend` adapter seam + tool-neutral IR | both | L1/L2 (§ Target 03) |
| A2 | Official Bridge transport (`/execute`) | EasyEDA | **done** (`automation/easyeda/bridge.py`) |
| A3 | `.enet` v2.0.0 as netlist IR + verifier gate | EasyEDA | L2 + phase-5 |
| A4 | Data-driven RuleSet (DRC+DFM unified schema) | both | L2/L3 (`pcbflow/dfm.py`) |
| A5 | `kicad-cli` = verification ground truth | KiCad | **done** (`tools/drc.py`) |
| A6 | `kipy` out-of-process interactive adapter | KiCad | L1 KiCadBackend |
| A7 | KLC-checked + parametric libraries | KiCad | component/library agents |
| A8 | netlist-explorer views → `pcbmunch` | EasyEDA | intelligence server |
| A9 | External-router adapters (freerouting/Rust-A*) | both | L1 routing |
| A10 | login-cache + console-capture reliability | EasyEDA | `tools/` |
| A11 | Rules live with project; ADR decision records | KiCad | knowledge plane |
| A12 | Ship an Agent-Skills `SKILL.md` | EasyEDA | L6 |

## 5 · Ideas to AVOID / never copy

- **Any editor/GUI/rendering source, marketplace, or bundled extension code** (license + scope).
- **In-process bindings** (SWIG `pcbnew`, coupling to a browser profile) — always out-of-process.
- **A hand-rolled DRC/DFM ruleset or netlist format** — adopt `.enet` + the DFM thresholds.
- **A custom autorouter** — adapt external engines.
- **A tool-specific core** — no EasyEDA/KiCad names above L1.
- **Provider lock-in** for AI — keep every agent behind a provider-neutral adapter.
- **Screenshots as truth**, **artifact-path state**, **blind stitch vias** — known failure modes.

## 6 · Proposed architecture (summary; full in [`03`](03_TARGET_ARCHITECTURE.md))

Seven layers: **L0 backends → L1 CAD adapters (the seam) → L2 tool-neutral IR
(`Enet`/`BoardModel`/`RuleSet`) → L3 pure engineering core → L4 orchestration + gates →
L5 provider-neutral agents (each with an independent verifier) → L6 CLI/MCP/Skill**, with a
cross-cutting **knowledge plane** (docs + KG + memory + rules). One universal `{ok,v}/{ok,err}`
envelope; data flows down, truth flows up; no gate skipped.

---

## 7 · Gap analysis — current repo vs ideal

| Area | Strength (keep) | Gap / debt | Risk |
|---|---|---|---|
| Core | pure-Python, tested `ipc/geometry/routing/congestion` | no typed **BoardModel** IR yet (dicts) | maintainability |
| Netlist | recon/dump exist | not `.enet`; can drift from `net_connection.md` | correctness |
| Rules | design-standards documented | **no RuleSet schema / `dfm.py`**; phantom-DRC risk | manufacturability |
| Transport | Bridge + CDP + envelope (done) | KiCad side has no `kipy` adapter | extensibility |
| Multi-tool | — | **no `CadBackend` seam** — core assumes EasyEDA | scalability (blocks Altium/others) |
| Agents | 12-phase workflow, gates | agents not yet provider-neutral adapters; verifiers ad hoc | provider lock, quality |
| Intelligence | `pcbmunch` (net/blast/rails/health) | missing explorer views (topology, connector-map, BOM) | feature parity |
| Libraries | — | no KLC-check / parametric generation | wrong-part regressions |
| Reliability | doctor/log/diagnose/recover/heal + tests | no login-cache/console-capture | robustness |
| Docs/memory | strong (docs 00-17, KG, memory) | KG split needs upkeep | drift |

**Top-3 architecture problems:** (1) single-tool coupling — no adapter seam; (2) untyped IR +
non-`.enet` netlist; (3) rules not a portable data document. All three are addressed by L1/L2.

---

## 8 · Implementation roadmap (phased; build only after approval)

Priorities: **P0 = unblocks multi-tool + correctness; P1 = capability; P2 = polish.**
Complexity: S/M/L. Every phase's exit criterion is *tests green + honest live-validation flag*.

| Ph | Objective | Key deliverables | Depends | Risks | Validation / Exit | Cx | Pri |
|----|-----------|------------------|---------|-------|-------------------|----|-----|
| **0** | Transport (started) | `bridge.py`+`EdaSession` ✅ | — | live bridge unverified | mock test ✅; **live EasyEDA smoke** | S | P0 |
| **1** | Tool-neutral IR | `pcbflow/enet.py` (parse/emit/verify), typed `BoardModel`, `RuleSet` schema | 0 | `.enet` version drift | round-trip + official verifier gate | M | P0 |
| **2** | CAD adapter seam | `CadBackend` Protocol; `EasyEDABackend`, `KiCadBackend` (cli); core stops naming tools | 1 | leaky abstraction | core imports no tool; both backends pass a shared conformance test | M | P0 |
| **3** | Rules unified | `pcbflow/dfm.py` from JLCPCB 18+7; per-mfr RuleSet profiles; ruleset-with-board guard | 1 | threshold accuracy | match reference numbers; no phantom-DRC | M | P1 |
| **4** | KiCad interactive | `kipy` adapter behind KiCadBackend; kicad-cli stays verifier | 2 | KiCad-version API skew | validate vs installed KiCad; cli remains truth | L | P1 |
| **5** | Routing adapters | freerouting + KiCadRoutingTools behind L1; EasyEDA↔KiCad convert | 2 | external tool setup | route a sample to 0-unrouted; DRC clean | L | P1 |
| **6** | Intelligence parity | `pcbmunch` gains topology/connector-map/BOM/export views | 1 | — | parity with netlist-explorer view set | M | P1 |
| **7** | Libraries | KLC-style validator + parametric footprint gen | 2 | KLC scope | reject a known-bad part; generate a footprint | M | P2 |
| **8** | Agents provider-neutral | LLM adapter interface; each agent + its verifier formalized | 2 | — | swap provider with no core change | M | P2 |
| **9** | Reliability + Skill | login-cache/console-capture; Agent-Skills `SKILL.md` | 0 | — | resume without re-login; skill loads in a compliant tool | S | P2 |

**Critical path:** 0 → 1 → 2 unlocks everything (multi-tool + correct IR). Do those first.

---

## 9 · Recommendation

Approve **Phases 1–2** (IR + CAD-adapter seam) as the next build — they convert PCB Flow from
an EasyEDA script harness into a genuine **tool-agnostic AI-native workspace**, and every later
capability (KiCad, routing, DFM, Altium) plugs into the seam. Phase 0 is already merged and
just needs a live smoke test. **No code beyond Phase 0 until this audit is approved.**
