# Changelog

All notable changes to PCB Flow are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-beta] — 2026-07-13

First public **Beta**. An AI-assisted electronics engineering workspace that takes a board
from requirements to manufacturing-ready files, with EasyEDA (schematic + placement) and
KiCad (routing + verification) and the engineer in the loop.

### Added
- **12-phase engineering workflow** (`workflow/`) with per-phase gates and AI agent roster
  (`agents/`), plus the engineering knowledge base (`knowledge/`) and templates.
- **`pcbflow` package + CLI** — project phase-gating, IPC-2221 solver, placement geometry,
  routing width/stitch math, congestion analysis.
- **`.enet` v2.0.0 netlist IR** (`pcbflow/enet.py`) — parse/emit/verify EasyEDA's official
  netlist, engineering views (nets, BOM, floating pins, net classes), and a bridge into the
  design-intelligence index.
- **Data-driven DRC/DFM RuleSet** (`pcbflow/dfm.py`) — JLCPCB capability profile with the
  phantom-DRC guard and true hole-to-hole / same-net-skip geometry.
- **MCP servers** — `pcbflow-mcp` (compute/orchestration) and `pcbmunch` (design intelligence).
- **EasyEDA automation** — official Bridge transport (`automation/easyeda/bridge.py`) with a
  unified `EdaSession` (Bridge primary, raw-CDP fallback), plus recon/dump.
- **KiCad integration** — `kicad-cli` DRC runner as the verification ground truth.
- **Reliability layer** (`tools/`) — environment `doctor`, structured logging, diagnosis,
  retry/recovery, and self-healing; all unit-tested and cross-platform.
- **Architecture audit** (`architecture/`) — EasyEDA/KiCad teardown, target architecture,
  and knowledge graph; upstream-tooling verdict (`docs/17`) + catalog (`knowledge/upstream/`).
- **Worked example** — `projects/example-usb-c-3v3/` (a real, machine-checkable board).
- **Handbook** for engineers, incl. Windows and macOS setup guides.

### Known limitations (Beta)
- The EasyEDA Bridge/CDP transport, KiCad routing, and placement automation are unit-tested
  against mocks; **end-to-end paths need validation on a live EDA session**, and the
  cross-platform tooling is validated on Linux (Windows/macOS built + unit-tested, not yet
  host-validated).
- The `enet`/`dfm`/`bridge` modules are library-complete but not yet wired as first-class CLI
  subcommands.

[Unreleased]: https://github.com/NijoP/pcbflow/compare/v0.1.0-beta...HEAD
[0.1.0-beta]: https://github.com/NijoP/pcbflow/releases/tag/v0.1.0-beta
