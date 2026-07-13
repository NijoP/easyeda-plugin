# Upstream tooling catalog

Curated, pinned pointers to the KiCad + EasyEDA upstream assets PCB Flow binds to.
This is the "fetch suitable things" list from
[`docs/17_UPSTREAM_TOOLING_VERDICT.md`](../../docs/17_UPSTREAM_TOOLING_VERDICT.md) —
kept as **references**, not vendored copies, so upstream stays the source of truth and
we don't inherit bloat or attribution risk. Verify each license before copying any file.

> Inspected 2026-07-13: [KiCad org](https://github.com/orgs/KiCad/repositories) (100 repos)
> + [EasyEDA/JLCEDA org](https://github.com/orgs/easyeda/repositories) (76 repos).

## EasyEDA — the official AI-automation stack (bind to these)

| Repo | Assets we use | Role in PCB Flow | License |
|---|---|---|---|
| [`easyeda/easyeda-api-skill`](https://github.com/easyeda/easyeda-api-skill) | `references/classes/DMT_*.md` (API surface), `format/{pcb,schematic,project}/*.md` (source specs), `SKILL.md`, Node **Bridge Server** | API-surface source of truth; direct file parsing; primary transport | verify |
| [`easyeda/pro-api-sdk`](https://github.com/easyeda/pro-api-sdk) · npm `@jlceda/pro-api-types` | TypeScript API types + extension scaffold | validate `section_generator`/`api_probe` against real signatures | **Apache-2.0** |
| [`easyeda/eext-run-api-gateway`](https://github.com/easyeda/eext-run-api-gateway) | editor-side gateway extension (handshake `easyeda-bridge`, ports 49620-49629) | pairs with the Bridge — the robust replacement for raw-CDP profile cloning | verify |
| [`easyeda/easyeda-pro-netlist-format`](https://github.com/easyeda/easyeda-pro-netlist-format) | `.enet` v2.0.0 spec + `enet-format-verify.mjs` + examples | **canonical netlist interchange** + phase-5 verify gate | verify |
| [`easyeda/easyeda-pro-file-format`](https://github.com/easyeda/easyeda-pro-file-format) · [`easyeda-std-file-format`](https://github.com/easyeda/easyeda-std-file-format) | project/schematic/PCB source-file specs | offline read-only analysis without live CDP | verify |
| [`easyeda/eext-jlc-order-dfm-checker`](https://github.com/easyeda/eext-jlc-order-dfm-checker) | 18 PCB + 7 SMT DFM checks; rotated-rect pad true-distance; same-net skip | authoritative JLCPCB DFM ruleset → `pcbflow/dfm.py` | verify |
| [`easyeda/eext-netlist-explorer`](https://github.com/easyeda/eext-netlist-explorer) | connection-ref, connector pin-map, topology, BOM, export views | feature spec for `pcbmunch` design intelligence | verify |
| [`easyeda/eext-freerouting-intergration`](https://github.com/easyeda/eext-freerouting-intergration) | freerouting autorouter integration | routing adapter (no custom router) | verify |
| [`easyeda/eext-kirouting-integration`](https://github.com/easyeda/eext-kirouting-integration) → [`drandyhaas/KiCadRoutingTools`](https://github.com/drandyhaas/KiCadRoutingTools) | Rust A* router + Python/FastAPI EasyEDA↔KiCad bridge | routing adapter + format-conversion pattern | verify |
| [`easyeda/extension-dev-mcp-tools`](https://github.com/easyeda/extension-dev-mcp-tools) | `import_plugin` / `dev_plugin` / `get_console_logs`; login cache, console capture | reliability patterns to fold into `tools/` | verify |

## KiCad — verification + libraries (already aligned)

| Asset | Role | Status |
|---|---|---|
| `kicad-cli` (in [`KiCad/kicad-source-mirror`](https://github.com/KiCad/kicad-source-mirror), dev on GitLab) | headless DRC / gerber / netlist export | **DRC ground truth — in use** (`tools/drc.py`, `automation/kicad/drc.sh`) |
| KiCad 9 **IPC API** `kipy` (PyPI `kicad-python`, dev on GitLab) | out-of-process board API, supersedes SWIG `pcbnew` | forward path — add adapter, validate vs installed KiCad |
| [`KiCad/kicad-library-utils`](https://github.com/KiCad/kicad-library-utils) | KLC symbol/footprint compliance checkers | library validation (guards fuzzy-search wrong parts) |
| [`KiCad/kicad-symbols`](https://github.com/KiCad/kicad-symbols) · [`kicad-footprints`](https://github.com/KiCad/kicad-footprints) · [`kicad-packages3D`](https://github.com/KiCad/kicad-packages3D) | official libraries | consume for part generation |
| [`KiCad/kicad-footprint-wizards`](https://github.com/KiCad/kicad-footprint-wizards) | parametric footprint generators | generate footprints on demand |
| [`KiCad/kicad-python`](https://github.com/KiCad/kicad-python) (GitHub) | old SWIG scripting API | **DEPRECATED** → `atait/kicad-python`; do not use |

## Ignore (out of harness scope)

Simulation (`easyeda-simulation-engine`, `eext-simulation-with-*`), MCAD bridges
(SolidWorks/Fusion360/FreeCAD), Blender render, art-PCB/coil/graffiti/QR generators —
leave to the EasyEDA marketplace.

## Notes

- Pin to a commit/release before depending on any spec; upstream `.enet` / API versions move.
- `@jlceda/pro-api-types`, freerouting, and KiCadRoutingTools are **dependencies**, not forks.
- Live-session assets (Bridge transport, DFM, routing) need real EasyEDA/KiCad validation
  before we claim they work — per the honesty rule in [`docs/17`](../../docs/17_UPSTREAM_TOOLING_VERDICT.md).
