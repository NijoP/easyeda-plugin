# 17 · Upstream-Tooling Verdict — engineering the harness on KiCad + EasyEDA

We inspected the two upstream GitHub orgs that own the tools PCB Flow drives —
[KiCad](https://github.com/orgs/KiCad/repositories) (100 repos) and
[EasyEDA / JLCEDA](https://github.com/orgs/easyeda/repositories) (76 repos) — to
answer one question: **what already exists upstream that we should adopt, align to,
or learn from, instead of hand-rolling.**

**Headline finding.** EasyEDA has, in the last year, shipped an *official* AI-automation
stack that is a superset of the one we reverse-engineered on the Light Dome project:
a typed API package, a WebSocket code-execution bridge, an editor-side gateway
extension, a debug MCP, machine-readable file/netlist format specs, and reference
extensions that mirror our `pcbmunch` and DFM work. KiCad's GitHub is a read-only
mirror + libraries; its automation story is `kicad-cli` (which we already use) plus
the KiCad 9 **IPC API** (`kipy`). The verdict: **stop treating these as black boxes,
bind to the official contracts, and keep our thin Python core as the orchestrator.**

This does not change the thesis (*knowledge is source, geometry is a build artifact*).
It replaces the most fragile, hand-rolled parts of the **build backend** with
maintained upstream contracts.

---

## 0 · TL;DR verdict table

| Upstream asset | What it is | Verdict for PCB Flow | Pri |
|---|---|---|---|
| `easyeda/easyeda-api-skill` → `references/classes/DMT_*.md` + `@jlceda/pro-api-types` | Full `eda.*` API class reference + npm types | **ALIGN-TO** — source of truth for the API surface our generators/probes target | P0 |
| `easyeda/easyeda-api-skill` (Bridge) + `eext-run-api-gateway` | Node WebSocket Bridge with HTTP `/execute` + editor gateway extension (ports 49620-49629, handshake `easyeda-bridge`) | **ADOPT** as primary EasyEDA transport; keep our raw-CDP driver as fallback | P0 |
| `easyeda/easyeda-pro-netlist-format` (`.enet` v2.0.0 + `enet-format-verify.mjs`) | Official JSON netlist: components, designRule, differentialPair, netClass, equalLengthNetGroup | **ADOPT** as canonical netlist interchange + a phase-5 validation gate | P0 |
| `easyeda/easyeda-api-skill/format/**` (+ `easyeda-pro-file-format`) | Machine-readable project/schematic/PCB source-format specs | **LEARN-FROM / parse directly** — read-only analysis without live CDP | P1 |
| `easyeda/eext-jlc-order-dfm-checker` | 18 PCB + 7 SMT JLCPCB DFM checks, thresholds auto-matched to material/layers/copper; rotated-rect pad true-distance, same-net skip | **ADOPT the ruleset** into `pcbflow/geometry.py` + a new `dfm.py` | P1 |
| `easyeda/eext-netlist-explorer` | Netlist views: connection-ref, connector pin-mapping, device topology, BOM, multi-format export | **LEARN-FROM** — it *is* `pcbmunch`'s feature set → adopt its view taxonomy as the roadmap | P1 |
| `easyeda/eext-freerouting-intergration` + `eext-kirouting-integration` (Rust A* via `drandyhaas/KiCadRoutingTools`) | Two proven external autorouters + an EasyEDA↔KiCad format-conversion bridge | **ADOPT as adapters** (keeps our "no custom autorouter" rule) | P1 |
| `KiCad` `kicad-cli` (in `kicad-source-mirror`) | Headless DRC / gerber / netlist export | **KEEP** — already our DRC ground truth (`tools/drc.py`, `automation/kicad/drc.sh`) | — |
| KiCad 9 **IPC API** (`kipy`, dev on GitLab) | Stable out-of-process Python board API, supersedes SWIG `pcbnew` | **LEARN-FROM / forward path** for interactive KiCad manipulation | P1 |
| `KiCad/kicad-library-utils`, `kicad-symbols`, `kicad-footprints`, `kicad-footprint-wizards` | Official libs + KLC checkers + parametric footprint generators | **CONSUME** for library validation + part generation | P2 |
| `easyeda/extension-dev-mcp-tools` | MCP: `import_plugin` / `dev_plugin` / `get_console_logs` (Playwright + Chrome 9222-9231, login cache) | **LEARN-FROM** — fold login-cache + console-capture into our reliability layer | P2 |
| `KiCad/kicad-python` (GitHub) | Old SWIG-era scripting API | **IGNORE** — repo is deprecated (→ `atait/kicad-python`); use `kicad-cli`/`kipy` | — |

---

## 1 · KiCad verdict — we are already on the right interface

- **`kicad-cli` is the correct headless contract and we already use it.** DRC with a
  ruleset sidecar (`.kicad_pro`) is our ground truth — that stays. Nothing upstream
  beats it for gerber/DRC/netlist export in CI.
- **The SWIG `pcbnew` Python module is legacy.** The reference project drove placement
  through `/usr/bin/python3` + `pcbnew`; that still works but is the past. The
  GitHub `KiCad/kicad-python` repo is **explicitly deprecated** (moved to
  `atait/kicad-python`).
- **Forward path = the KiCad 9 IPC API (`kipy`).** An out-of-process, versioned Python
  API (developed on GitLab, published as `kicad-python`/module `kipy`) that talks to a
  running KiCad over a socket — no in-process SWIG, no ABI coupling. *We do not
  rewrite anything now*, but new KiCad-side interactive automation should target `kipy`
  behind a thin adapter, with `kicad-cli` remaining the verification gate. **Mark as
  unit-designed / needs validation against the installed KiCad version.**
- **Libraries are free leverage.** `kicad-symbols` / `kicad-footprints` /
  `kicad-packages3D` + `kicad-library-utils` (KLC compliance checkers) +
  `kicad-footprint-wizards` (parametric generators) let PCB Flow *validate* and
  *generate* library parts instead of trusting fuzzy vendor search (the exact failure
  mode of KG-T6 / F9 in [`13_LESSONS_LEARNED.md`](13_LESSONS_LEARNED.md)).

**Net:** KiCad needs no re-architecture. Add a `kipy` adapter as an option, wire the
KLC checkers into library validation. `kicad-cli` stays the source of DRC truth.

---

## 2 · EasyEDA verdict — bind to the official automation stack

Today PCB Flow drives EasyEDA two ways (see [`06`](06_EASYEDA_INTEGRATION.md)):
standalone-script paste, and **raw CDP into a logged-in Chrome profile**
(`window._EXTAPI_ROOT_`, port 9222 — with the Google-OAuth-blocked, clone-the-profile,
kill-`Singleton*` workarounds). That was necessary in 2026-H1. It no longer is.

**2.1 Transport — adopt the official Bridge (`/execute`).**
`easyeda-api-skill` ships a Node **Bridge Server** that opens a port in `49620-49629`
and exposes:

```
GET  /health          → connection status
POST /execute {code}  → runs `return await eda.<...>` inside the editor, returns JSON
```

paired with the editor-side **`run-api-gateway`** extension (handshake `easyeda-bridge`,
auto-scan, auto-reconnect, heartbeat). This is *exactly* our `cdp.eval()` envelope
(`{ok,v}`/`{ok,err}`) but maintained upstream, handshake-verified, and it does **not**
require cloning a Chrome profile or defeating OAuth — the user logs into their normal
EasyEDA, ticks "allow external interaction", and the gateway connects out.

→ **Action:** add `automation/easyeda/bridge.py` — a stdlib HTTP client for
`/health` + `/execute` — and make it the *primary* `run(js)->{ok,...}` transport, with
`automation/browser/cdp.py` kept as the fallback for screenshots and when the gateway
isn't installed. One `EdaSession` interface, two backends. Our reliability layer
(`tools/recover.py`, `tools/heal.py`) wraps it unchanged (same envelope).

**2.2 API surface — align to the reference, stop guessing.**
`references/classes/DMT_*.md` (DMT_Pcb, DMT_Schematic, DMT_Board, DMT_Project, …) +
the `@jlceda/pro-api-types` npm package are the authoritative `eda.*` signatures. Our
`section_generator.template.js` and `api_probe.js` should be *checked against* them,
and the "tested-signatures table" in [`06`](06_EASYEDA_INTEGRATION.md) becomes a
*diff against upstream* instead of a hand-maintained list. This kills a whole class of
"wrong-signature hard-hangs the renderer" bugs (see memory + `05` §B).

**2.3 Netlist — adopt `.enet` v2.0.0 as the interchange.**
`.enet` is JSON with `version / components / designRule / differentialPair / netClass /
equalLengthNetGroup`, with a real conformance verifier (`enet-format-verify.mjs`) and
a 496-component reference example. This is the missing standard under our
`net_connection.md` ↔ recon pipeline.
→ **Action:** `pcbflow` recon/dump emits `.enet`; phase-5 verification runs the
official verifier as a gate (fail-closed). `net_connection.md` becomes a human view
*generated from* `.enet`, not a parallel source that can drift.

**2.4 File formats — parse directly for read-only analysis.**
`format/pcb/*.md` (`rule.md`, `pad_via.md`, `primitive.md`, `component.md`),
`format/schematic/*.md`, `format/project/*.md` fully specify the source files. For
*read-only* work (design intelligence, DFM, audits) we can parse the saved project
instead of round-tripping through a live CDP session — faster, offline, CI-able. Live
CDP stays for *writes* and for reading unsaved state.

**2.5 DFM — adopt the JLCPCB ruleset.**
`eext-jlc-order-dfm-checker` encodes **18 PCB + 7 SMT** checks with thresholds
auto-selected by board material / layer count / copper weight, and — critically — it
does **rotated-rect pad true-distance** and **same-net skip (incl. copper cross-connect)**.
That is precisely the geometry our reference project had to discover the hard way.
→ **Action:** encode these thresholds + the pad-distance logic into `pcbflow/geometry.py`
and a new `pcbflow/dfm.py`; expose as `pcbflow dfm` and a `pcbmunch` tool. This is the
authoritative source — do not invent our own numbers.

**2.6 Design intelligence — `eext-netlist-explorer` validates `pcbmunch`.**
Its views (full netlist, connection-reference net, connector pin-mapping SVG, device
topology graph with GND filtering, BOM aggregation, multi-format export) are the exact
surface `pcbmunch` should expose. Treat it as the **feature spec** for pcbmunch:
`get_net` / `blast_radius` / `power_rails` already exist; add `connection_ref`,
`connector_pairs`, `topology`, `bom_health`, and CSV/SVG/JSON export.

**2.7 Routing — two proven external routers, zero custom code.**
Our rule is *no custom autorouter*. Upstream officially integrates two:
**freerouting** (`eext-freerouting-intergration`) and a **Rust-accelerated A\* router**
(`eext-kirouting-integration` → `drandyhaas/KiCadRoutingTools`) via a **Python/FastAPI
bridge that converts EasyEDA↔KiCad**. That conversion bridge is the reusable pattern
(and it doubles as our EasyEDA→KiCad handoff for the DRC gate). → **Action:** add
`automation/routing/` adapters that shell out to freerouting and KiCadRoutingTools;
never write our own maze router (F8, `13_LESSONS_LEARNED.md`).

---

## 3 · What to vendor vs reference (licensing-aware)

The responsible way to "fetch suitable things" is a **curated pointer catalog**, not
a blind copy of 351 upstream files (bloat + attribution risk). See
[`knowledge/upstream/README.md`](../knowledge/upstream/README.md) for the pinned list.

- **Reference (link, don't copy):** the full `references/classes/**` API docs and
  `format/**` specs — large, versioned upstream, better fetched on demand.
- **Vendor (small, permissive, high-value):** the `.enet` format spec + its verifier
  invocation, and the DFM threshold table — small, stable, and we build tooling on
  them. `pro-api-sdk` is **Apache-2.0** (attribution-friendly). Verify each repo's
  license before copying any file; record it in the catalog.
- **Depend, don't fork:** `@jlceda/pro-api-types` (npm), freerouting, KiCadRoutingTools —
  invoke as external tools / dev-deps.

---

## 4 · What we deliberately ignore

Peripheral to a *schematic→PCB→manufacturing* harness (leave to EasyEDA's marketplace):
simulation (`easyeda-simulation-engine`, `eext-simulation-with-*`), MCAD bridges
(SolidWorks / Fusion360 / FreeCAD), Blender render, art-PCB / coil / graffiti-silk /
QR generators, and the old KiCad `.pretty` footprint repos beyond the ones we consume.
None of these change the harness.

---

## 5 · Net effect on the architecture

The build backend gains **maintained upstream contracts**; the Python core stays the
orchestrator and stays the same size.

```
knowledge (source)                      ← unchanged: build_sheet / net_connection / rules
        │  pcbflow (Python stdlib orchestrator)   ← unchanged core, +dfm.py, +bridge client
        ▼
   EDA build backend
   ├─ EasyEDA ── Bridge /execute (primary) ─┐   ← NEW official transport
   │            └ raw CDP (fallback/shots) ─┤
   │            binds to @jlceda/pro-api-types + format specs  ← NEW: align, don't guess
   ├─ netlist ── .enet v2.0.0 (+ verifier gate)                ← NEW canonical interchange
   ├─ DFM ────── JLCPCB 18+7 ruleset                           ← NEW authoritative rules
   ├─ routing ── freerouting / KiCadRoutingTools adapters      ← external, no custom router
   └─ KiCad ──── kicad-cli (DRC truth) + kipy adapter (fwd)    ← keep + forward path
```

**Prioritized build order:** P0 = Bridge `/execute` client + `.enet` adopt + API-surface
alignment. P1 = `dfm.py` from the JLCPCB checker, pcbmunch views from netlist-explorer,
routing adapters, `kipy` adapter. P2 = library-utils validation, console-capture
reliability, ship an Agent-Skills-compatible `SKILL.md`.

> Everything above the P0/P1 line is **unit-designable now**; the transport, DFM, and
> routing adapters need a **live EasyEDA/KiCad session to validate** — mark them
> "needs real-world validation" until then, per our honesty rule.
