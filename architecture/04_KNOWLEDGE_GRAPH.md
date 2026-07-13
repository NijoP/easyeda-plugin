# 04 · Architecture Knowledge Graph

A navigable graph of the concepts, relationships, and flows behind the platform. Nodes are
**concepts / subsystems / artifacts**; edges are `→ produces`, `⊳ verifies`, `⊣ blocks`,
`≈ generalizes`, `⇄ adapts`. This complements the *engineering-heuristics* graph in
[`../docs/03_KNOWLEDGE_GRAPH.md`](../docs/03_KNOWLEDGE_GRAPH.md) (that one is board-design
wisdom; this one is platform architecture).

---

## A. Concept nodes

- **KNOWLEDGE** (docs, rules, memory) — the source.
- **IR**: `Enet`(netlist) · `BoardModel`(geometry) · `RuleSet`(DRC/DFM) — tool-neutral L2.
- **CAD ADAPTER** — the L1 seam; `⇄` translates IR ↔ tool.
- **BACKEND**: EasyEDA(Bridge/CDP) · KiCad(cli/kipy) · Altium(future).
- **ENGINEERING CORE** — IPC-2221 · geometry · routing-math · congestion · DFM.
- **AGENTS** — reasoning functions (requirement…doc).
- **ORCHESTRATOR** — 12 phases + gates + state.
- **VERIFIER** — ERC · DRC(kicad-cli) · geometry-audit · `.enet`-diff.
- **INTERFACES** — CLI · MCP · Skill.

## B. Core relationships (the spine)

```
KNOWLEDGE ──→ AGENTS ──→ (Ops/plan) ──→ ORCHESTRATOR ──→ CAD ADAPTER ⇄ BACKEND
    ▲                                        │                 │
    │                                        ▼                 ▼
 MEMORY ←── VERIFIER ⊳ (PASS/FAIL) ←──── IR (Enet/Board/RuleSet) ←── readback
```
- `AGENTS → IR` (never AGENTS → BACKEND directly).
- `ORCHESTRATOR` gates each phase on `VERIFIER ⊳ PASS`.
- `BACKEND → readback → IR → VERIFIER` (truth flows up from coordinates, not screenshots).
- `VERIFIER → MEMORY → KNOWLEDGE` (lessons compound).

## C. Data flow (design → manufacture)

`requirements → BOM/datasheet → build_sheet → .enet(netlist) → schematic(backend) →`
`placement directive → BoardModel(geometry) → route plan → tracks/vias → DRC(RuleSet) →`
`export(gerber/step/bom) → handoff docs`. Each `→` crosses a **phase gate**.

## D. Decision flow (the big calls, from the design KG)

`density → layer count?` · `peak current → plane vs trace (IPC-2221)?` ·
`module RF variant → keep-out?` · `size vs routability (constrained-opt)?` ·
`safety fn → IC-bundled (mandate)` vs `UX fn → client call`. Each decision is a node with a
recorded rationale (ADR-style) in the knowledge plane.

## E. Validation flow

`ERC (schematic) ⊳ → .enet diff ⊳ → geometry/spacing audit ⊳ → DRC vs RuleSet ⊳ (kicad-cli =`
`ground truth) → DFM (manufacturer profile) ⊳`. **No gate skipped; ruleset always paired with
the board** (phantom-DRC guard).

## F. Automation flow

`Agent op → Orchestrator → CAD Adapter → {EasyEDA: EdaSession.run(js) via Bridge/CDP |`
`KiCad: kicad-cli subprocess / kipy socket} → {ok,v}/{ok,err} → reliability wrap`
`(diagnose→recover→heal) → readback → IR`. **Out-of-process at every backend.**

## G. Learning-source edges (provenance)

| Node | EasyEDA taught | KiCad taught | Our project taught |
|---|---|---|---|
| IR/netlist | `.enet` v2.0.0 + verifier | derived connectivity | net_connection ↔ recon drift |
| RuleSet | data-driven DFM (18+7) | DRC constraint engine | phantom-DRC; ruleset-with-board |
| CAD Adapter | out-of-proc Bridge | kicad-cli + kipy altitudes | CDP profile-hack fragility |
| Routing | external-engine bridges | freerouting import | "$300 wall"; no custom router |
| Libraries | LCSC link | KLC-check + wizards | wrong-value fuzzy-search parts |
| Geometry | primitive math (rotated pad) | typed object graph | coords-are-truth, stale getAll |
| Reliability | login-cache, console-capture | — | envelope-never-swallow, heal |

## H. Extensibility edges (future CAD)

`CadBackend(Protocol)` is the extension point: a new tool (`Altium`) implements
`capabilities/run/read_netlist/read_board/drc/export` and plugs into L1 with **zero change**
above it. `≈` this is EasyEDA's plugin runtime + KiCad's cli/kipy contracts, generalized.

## I. Failure-mode edges (what ⊣ blocks what)

- `wrong eda.* signature ⊣ renderer` → mitigate: typed/probed wrapper, one guarded probe.
- `bare board (no ruleset) ⊣ real DRC` → mitigate: RuleSet always travels with BoardModel.
- `artifact-path state ⊣ recoverability` → mitigate: decision-based state + recovery baseline.
- `in-process binding ⊣ tool upgrades` → mitigate: out-of-process adapters only.
- `blind stitch via ⊣ copper (shorts)` → mitigate: collision-checked geometry (core).

> Read this graph as the platform's contract: **knowledge generates the IR, adapters build it
> on any backend, verifiers gate every phase, and every lesson flows back into knowledge.**
