# 03 · Target Architecture — the AI-native Electronics Engineering Workspace

Synthesized from the EasyEDA ([`01`](01_EASYEDA_TEARDOWN.md)) and KiCad
([`02`](02_KICAD_TEARDOWN.md)) teardowns and our own project's lessons
([`../docs/13_LESSONS_LEARNED.md`](../docs/13_LESSONS_LEARNED.md)). This is the
**tool-agnostic** architecture PCB Flow grows into — EasyEDA and KiCad become *backends*,
Altium/others plug in later.

> **Governing principle (unchanged, now reinforced by both tools):**
> **Knowledge is the source. Geometry is a build artifact.** Rules are data. Automation is
> out-of-process. The AI reasons; deterministic code and the CAD backend build and verify.

---

## A. The layered model

```
┌──────────────────────────────────────────────────────────────────────┐
│ L6  INTERFACES        CLI · MCP servers (pcbflow-mcp, pcbmunch) · Agents │
├──────────────────────────────────────────────────────────────────────┤
│ L5  AGENTS            requirement · feasibility · datasheet · schematic  │
│     (provider-neutral) placement · routing · DRC/DFM · doc — see §D      │
├──────────────────────────────────────────────────────────────────────┤
│ L4  ORCHESTRATION     12-phase workflow · project lifecycle/state ·      │
│                        phase gates ("advance needs a PASS")              │
├──────────────────────────────────────────────────────────────────────┤
│ L3  ENGINEERING CORE  IPC-2221 · geometry/spacing · routing math ·       │
│     (pure Python)      congestion · DFM rules · netlist model (.enet)    │
├──────────────────────────────────────────────────────────────────────┤
│ L2  DESIGN MODEL      typed board/netlist/rules — the tool-neutral IR     │
│                        (knowledge = source; geometry derived)            │
├──────────────────────────────────────────────────────────────────────┤
│ L1  CAD ADAPTERS      EasyEDABackend · KiCadBackend · (AltiumBackend…)   │
│     (the seam)         transport + format + capability per tool          │
├──────────────────────────────────────────────────────────────────────┤
│ L0  CAD BACKENDS      EasyEDA (Bridge/CDP) · KiCad (kicad-cli/kipy) · …   │
└──────────────────────────────────────────────────────────────────────┘
              KNOWLEDGE PLANE (cross-cutting): docs · knowledge graph · memory · rules
```

Data flows **down** (intent → model → adapter → backend geometry); truth flows **up**
(backend readback → model → validation → verdict). No layer reaches around the one below.

---

## B. The keystone: the **CAD Adapter interface** (L1)

The single most important new abstraction — it makes us multi-tool. Every backend implements
one capability-typed interface; the core never names a tool.

```python
class CadBackend(Protocol):
    name: str                      # "easyeda" | "kicad" | "altium"
    def capabilities(self) -> set[str]      # {"schematic","place","route","drc","export"}
    def run(self, op: Op) -> Result         # {ok, v}|{ok, err}  ← the universal envelope
    def read_netlist(self) -> Enet          # → tool-neutral .enet model (L2)
    def read_board(self) -> BoardModel      # → typed board IR (L2)
    def drc(self, ruleset: RuleSet) -> DrcReport
    def export(self, kind, out) -> Result   # gerbers/step/bom/pdf
```

- **EasyEDABackend** → transport = `EdaSession` (Bridge primary, CDP fallback, already built);
  format = `eda.*` API + `.enet` + `format/**` specs; capabilities = schematic, place, (route
  via external), drc(=DFM).
- **KiCadBackend** → transport = `kicad-cli` (verify/export) + `kipy` (interactive);
  format = s-expr; capabilities = place, route(import), drc, export. **The verification
  ground truth.**
- **Envelope everywhere** = the `{ok,v}/{ok,err}` contract from `cdp.py`/`bridge.py`, so the
  reliability layer wraps every backend identically.

**Why this shape (from the teardowns):** both tools already expose *out-of-process,
envelope-able* contracts. An adapter per tool + a neutral IR is the only way "design once,
build on any tool" holds — and the only way DRC/DFM rules stay portable.

---

## C. The Design Model / IR (L2) — tool-neutral

Three typed artifacts, versioned, git-committable (the "commit the artifact" gate):

1. **Netlist** — adopt **`.enet` v2.0.0** verbatim (components, designRule, differentialPair,
   netClass, equalLengthNetGroup). It already carries intent + rules; don't invent our own.
2. **Board IR** — a typed model (`Board → Component → Pad`, `Track/Via/Zone`, `Net`) distilled
   from KiCad's explicit object graph; geometry is **derived + verified**, never authored blind.
3. **RuleSet** — a **data-driven DRC/DFM document** (constraint + condition + severity),
   unifying KiCad's DRC engine and EasyEDA's DFM checker. One schema, per-manufacturer
   profiles (JLCPCB, generic-2L, generic-4L). **Never DRC without the matching ruleset.**

Everything above L2 speaks the IR; only L1 translates IR ↔ tool.

---

## D. Agent architecture (L5) — provider-neutral, one-responsibility-each

Agents are **stateless reasoning functions** over the knowledge plane + IR; they never touch a
backend directly — they emit **Ops/plans** that L4 executes through L1. Provider-independence
is mandatory (any LLM behind an adapter).

| Agent | Input | Output | Verifier (who checks it) |
|---|---|---|---|
| Requirement | brief | requirement model | human gate |
| Feasibility | requirements | feasibility verdict + risks | IPC/geometry core |
| BOM / Datasheet / Component-research | requirements | parts + datasheet facts | library KLC-check |
| Schematic-gen | build_sheet | `eda.*` section plan → schematic | ERC + net diff vs `.enet` |
| Placement-planner + KG | netlist + outline | placement directive | geometry/spacing core |
| Placement-executor | directive | board geometry | DRC + audit (coords, not eye) |
| Routing-planner | placement | route sequence + rules | congestion core |
| Router (adapter) | plan | tracks/vias | DRC |
| DRC/DFM | board + ruleset | pass/fail + coordinates | kicad-cli ground truth |
| Doc | everything | handoff docs | — |

**Pattern (from KiCad ERC + our lessons):** every generative agent has an **independent
verifier** (the layered-authority / "never launder a warrant" rule). Nothing advances a phase
without a machine PASS.

---

## E. Orchestration + lifecycle (L4)

- **12-phase workflow** (existing) with **phase gates**: `project.py` already enforces
  "advance needs a PASS." Keep it; feed gates from L3 verifiers + L1 DRC.
- **Project state** = JSON, crash-safe, decision-based (never artifact-path-based — the
  recovery-baseline lesson). State references *decisions and the IR*, not volatile files.
- **Reliability** (existing `tools/`): doctor → structured `{ok,err}` logging → diagnose →
  recover → heal, wrapping every L1 call. Fold in EasyEDA's login-cache + console-capture.

---

## F. Interfaces (L6)

- **CLI** (`pcbflow`) — the human/automation entry; `sys.executable` for cross-platform.
- **MCP servers** — `pcbflow-mcp` (compute/orchestration) + `pcbmunch` (design intelligence,
  grown to the `eext-netlist-explorer` view set). Provider-neutral, tool-callable by any agent.
- **Agent-Skills SKILL.md** — ship PCB Flow's EDA knowledge as an Agent-Skills-standard skill
  (as EasyEDA does), so any compliant tool can drive it.

---

## G. Knowledge plane (cross-cutting)

Docs (source of truth) + the **knowledge graph** ([`04`](04_KNOWLEDGE_GRAPH.md)) +
file-based memory + the rule documents. This is what makes the platform *AI-native*: the LLM
reasons over durable, structured knowledge, and geometry is regenerated from it — not the
reverse. Both EasyEDA (net-name merge) and KiCad (derived connectivity) validate the stance.

---

## H. Non-negotiable design rules (carried into every module)

1. **Tool-agnostic core** — L2–L5 never import a tool; only L1 adapters do.
2. **One universal envelope** `{ok,v}/{ok,err}` across every backend + agent op.
3. **Rules are data** — DRC/DFM/net-class are documents, per-manufacturer profiles.
4. **Out-of-process automation** — never couple to an editor/binary in-process.
5. **Geometry is derived + verified** — screenshots are sanity, coordinates are truth.
6. **Provider-neutral AI** — no lock to one LLM vendor.
7. **Pure + tested core** — L3 stays stdlib, pure, unit-tested; live paths flagged.
8. **Commit the artifact** — IR + rules are versioned; state is decision-based.
