# 01 · EasyEDA Pro — Architecture Teardown

Reverse-engineered from the public [`easyeda`/JLCEDA org](https://github.com/orgs/easyeda/repositories)
(76 repos: `pro-api-sdk`, `easyeda-api-skill`, `eext-run-api-gateway`,
`extension-dev-mcp-tools`, `easyeda-pro-netlist-format`, `eext-jlc-order-dfm-checker`,
`eext-netlist-explorer`, `eext-*-integration`, the `format/**` specs). We did not read
proprietary editor source; we reverse-engineered the **public contracts** — the API
surface, the file/netlist formats, the transport, and the extension model — which is
exactly the boundary an AI harness binds to.

> **Thesis of EasyEDA's design:** a monolithic web/desktop editor with a **stable,
> class-based scripting API** (`eda.*`) and a **plugin (extension) runtime**, wrapped in
> late-2025 by an **out-of-process AI-automation stack** (typed API package + WebSocket
> bridge + MCP). The editor is the kernel; everything reusable is a plugin or a document.

---

## A. Subsystem-by-subsystem

### A1 · Extension / plugin runtime — *the extensibility spine*
- **Purpose:** third-party features without forking the editor.
- **Model:** each extension gets its **own isolated `eda` object** (not shared across
  extensions), a manifest (`extension.json`: name/displayName/publisher/entry), and an
  iframe/inline UI surface. Two execution contexts: compiled **extension package**
  (`.eext`) and a **Standalone Script** paste-box for quick logic.
- **Interface:** the `eda` root aggregates class instances named
  `<lowercased-3-letter-prefix>_<Class>` — e.g. `SYS_ToastMessage → eda.sys_ToastMessage`,
  `PCB_* → eda.pcb_*`, `SCH_* → eda.sch_*`, `DMT_* → eda.dmt_*` (document/project mgmt).
- **Extensibility:** an official **marketplace** (jlc-ext.com); 60+ first-party `eext-*`
  extensions (DFM, netlist explorer, routers, MCAD bridges, simulation).
- **Trade-off:** one API for UI plugins *and* automation ⇒ the same surface a human clicks
  is the surface an AI scripts. Simplicity over separation. **Failure mode:** an unknown
  `*.create` signature can hard-hang the renderer (no schema enforcement at the boundary).

### A2 · Data model & file format — *documents as typed trees*
- **Purpose:** persist project/schematic/PCB as structured source.
- **Model (from `format/**`):** three trees — **project** (meta, groups, instances,
  variants, blobs), **schematic** (component, pin, wire, obj, shape, text, table),
  **pcb** (component, pad_via, primitive, shape, text, rule, partition, panel, 3d,
  dimension). Everything is an addressable **primitive with an ID + attributes**.
- **Interface:** read/write via `eda.*` at runtime, OR parse the saved source directly.
- **Insight:** connectivity is **by net name**, merged globally; geometry is a projection
  of the netlist + placement, not the source of truth. (This is the same "geometry is a
  build artifact" stance our project independently reached.)

### A3 · Netlist — *`.enet` v2.0.0, a real interchange standard*
- **Purpose:** a tool-neutral, versioned schematic-connectivity contract.
- **Model:** JSON with `version, components (attrs + pin→net), designRule, differentialPair,
  netClass, equalLengthNetGroup`. Ships a **conformance verifier** (`enet-format-verify.mjs`)
  and a 496-component reference example.
- **Why it matters:** connectivity, *design intent* (net classes, diff pairs, length
  matching), and *physical rules* travel together in one validated file. This is the
  cleanest artifact in the whole ecosystem to adopt.

### A4 · Rule / DRC architecture — *data-driven, manufacturer-aware*
- **Purpose:** catch un-manufacturable geometry before fabrication.
- **Model (from `eext-jlc-order-dfm-checker`):** **18 PCB + 7 SMT checks** whose thresholds
  are **auto-selected by board material / layer count / copper weight** — the engineer
  never types process parameters. Checks carry **coordinates + reason**, are clickable, and
  export to report. Notable correctness details: **rotated-rect pad true-distance** and
  **same-net skip (including copper cross-connect)** — the exact geometry a naive checker
  gets wrong.
- **Interface:** DFM is itself an extension over the PCB data model (not a hidden core).
- **Trade-off:** DFM lives *outside* the editor kernel as a plugin ⇒ rules are inspectable,
  swappable, and vendor-specific (JLCPCB) without editor changes.

### A5 · Automation / IPC — *the out-of-process AI bridge*
- **Purpose:** let external AI tools drive the editor safely.
- **Architecture (from `scripts/bridge-server.mjs`):**
  ```
  AI Agent ⇄ HTTP/WS ⇄ Bridge Server (Node) ⇄ WebSocket ⇄ EasyEDA editor
                        ports 49620–49629        via run-api-gateway ext.
  ```
  - **Discovery + handshake:** scan port range, `GET /health → {service:"easyeda-bridge"}`.
  - **Execution:** `POST /execute {code}` → editor runs it, result correlated by **UUID**
    (`type:execute|result|error`, `id`), 30 s timeout, errors returned as data.
  - **Multiplexing:** multiple EDA windows registered by `windowId`, one **active**,
    selectable via `/eda-windows/select`. Heartbeat ping/pong, auto-reconnect.
- **Why this shape:** decouples the AI (any Agent-Skills tool) from the editor lifecycle;
  no in-process coupling, no profile hacks. **Failure modes handled:** window disconnect
  rejects its pending requests; port collision → singleton exit; timeout → reject-not-hang.
- **Sibling:** `extension-dev-mcp-tools` (MCP: `import_plugin`/`dev_plugin`/`get_console_logs`
  via Playwright + Chrome remote-debug 9222-9231, **login cached in `.browser-data/`**).

### A6 · Routing — *never built in-house; two external engines bridged*
- **Purpose:** autoroute without owning a router.
- **Model:** `eext-freerouting-intergration` (Java freerouting) and
  `eext-kirouting-integration` (**Rust A\*** via `drandyhaas/KiCadRoutingTools`) each run
  behind a **Python/FastAPI bridge that converts EasyEDA↔KiCad** and writes results back.
- **Lesson:** even a mature ECAD vendor treats routing as a **pluggable external service**,
  and reuses **KiCad as a format hub**. Validates our "no custom autorouter" rule.

### A7 · Design intelligence — *`eext-netlist-explorer`*
- Views: full netlist, **connection-reference net**, **connector pin-mapping (SVG)**,
  **device topology graph** (GND-filtered, click-to-highlight same net), **BOM aggregation**,
  JSON, multi-format export. This is a complete "ask the board" surface — and it is *exactly*
  the feature set of our `pcbmunch` intelligence server.

---

## B. Engineering principles EasyEDA demonstrates

| Principle | Evidence | Take for us |
|---|---|---|
| **Kernel + plugins** | editor core + 60 `eext-*` | keep our core thin; features are adapters/tools |
| **One stable scripting API for humans *and* AI** | `eda.*` drives UI and the bridge | our `EdaSession` is that seam |
| **Out-of-process automation** | Bridge Server, MCP | never couple the AI to the editor process |
| **Versioned interchange with a verifier** | `.enet` v2.0.0 + verify | adopt `.enet`; gate on the verifier |
| **Data-driven, vendor-aware DRC as a plugin** | DFM checker | DFM = swappable ruleset, not hardcoded |
| **Reuse external engines + KiCad as a format hub** | router bridges | adapters over freerouting/KiCadRoutingTools |
| **Correctness in geometry primitives** | rotated-pad, same-net skip | copy the *math*, not the code |

---

## C. What to ADOPT · REDESIGN · AVOID

**ADOPT (conceptually):** the Bridge transport contract; `.enet` as our netlist interchange
+ verifier gate; the DFM ruleset (thresholds + pad math); the netlist-explorer view taxonomy
for pcbmunch; the kernel+plugin decomposition; login-cache + console-capture reliability.

**REDESIGN:** the *scripting API ergonomics* — EasyEDA's `eda.*` has no schema at the call
boundary (wrong signature → renderer hang). Our harness must add a **typed, probed,
fail-fast wrapper** (align to `@jlceda/pro-api-types`, one guarded probe, never a signature
loop).

**SIMPLIFY:** we don't need the editor, marketplace, iframe UI, or 60 feature plugins — only
the automation seam + the document/netlist/rule contracts.

**NEVER COPY:** editor UI source, proprietary rendering, the marketplace, or any bundled
extension code (license + scope). We bind to *contracts*, not code.
