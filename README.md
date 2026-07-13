# AXON — An AI-Native Electronics Engineering Workspace

> A modular, open framework that takes a hardware product from **client
> requirements to manufacturing-ready outputs** — with AI agents doing the
> engineering, browser automation + EasyEDA + KiCad as the tooling, and a human
> supervising every irreversible step.
>
> Not a prompt-engineering repo. An **engineering framework** that is reusable for
> any electronics project: IoT, robotics, motor control, audio, sensors, power,
> wearables.

**→ New here? Read [`DESIGN_WORKFLOW.md`](DESIGN_WORKFLOW.md) — the 12-phase design
method, written for electronics engineers who've never seen this flow.**
**→ Want the structure? Read [`ARCHITECTURE.md`](ARCHITECTURE.md).**

---

## The core idea

Most PCB projects treat the *schematic* as the design. AXON doesn't. It treats a
small set of authored documents — the **build sheet**, the **net dictionary**, and
the **design rules** — as the real source, and treats the schematic, placement,
and routed copper as **build output generated from them.**

> **Knowledge is the source. Geometry is the build artifact.**

Protect and version the knowledge; regenerate the geometry. A cheap verification
gate follows every stage, so nothing is ever built on top of something wrong.

---

## The 12-phase workflow

EasyEDA hosts the schematic + placement; **KiCad is the routing and verification
engine** (its API can script pours, zones, and DRC — EasyEDA's cannot). Each phase
has a hard exit gate; you never start a phase until the previous one passes.

| # | Phase | Tool | Exit gate |
|---|---|---|---|
| 1 | Requirement analysis & feasibility | — | feasibility study complete, no unquantified requirement |
| 2 | BOM planning | — | every part validated (India + LCSC + lifecycle + package/electrical) |
| 3 | EasyEDA project initialization | EasyEDA | sheets + board params + stackup set |
| 4 | Autonomous schematic generation | EasyEDA | every block placed & wired, 0 unmatched pins |
| 5 | Schematic audit | browser | netlist == source docs; 0 shorts/floating/ERC |
| 6 | Placement planning (client constraints) | — | board dims/shape/connector/keep-out defined |
| 7 | Placement knowledge graph | — | functional/thermal/EMI/current graph complete |
| 8 | Visual placement planning | — | placement map approved against client needs |
| 9 | Automated component placement | EasyEDA | 0 spacing violations (real geometry), constraints met |
| 10 | Export to KiCad | EasyEDA→KiCad | imported board verified == EasyEDA, placement preserved |
| 11 | AI-assisted routing | KiCad | 0 unrouted, DRC-clean, IPC widths, return paths |
| 12 | Final verification | KiCad | DRC+ERC+DFM+assembly+BOM all pass → manufacturing-ready |

Full detail per phase → [`workflow/`](workflow/). Deep dive → [`DESIGN_WORKFLOW.md`](DESIGN_WORKFLOW.md).

---

## Repository structure

```
axon/
├── DESIGN_WORKFLOW.md   START HERE — the 12-phase method for engineers
├── ARCHITECTURE.md      why the repo is shaped this way (read this second)
├── CLAUDE.md / AGENTS.md  AI operating manuals
├── CONTRIBUTING.md      for humans and AI agents
│
├── workflow/     THE 12-PHASE PIPELINE — one gated file per phase
├── agents/       AI worker roles (feasibility, BOM, schematic, placement, router, …)
├── automation/   the tools that touch the EDA world
│   ├── easyeda/    schematic + placement (Standalone-Script engine)
│   ├── browser/    headless CDP driver + netlist reconstruction
│   ├── kicad/      routing + verification engine (pours, DRC, stitching)
│   └── shared/     IPC-2221 solver, units, congestion grid
├── knowledge/    the engineering brain that COMPOUNDS across projects
│   ├── principles.md · knowledge-graph.md · design-standards.md
│   ├── learning-db.md  (append-only failure→lesson log)
│   └── knowledge-inheritance.md
├── templates/    source-of-truth blanks (build_sheet, net_connection, rules, …)
├── projects/     per-board workspaces that INHERIT the framework
│   └── _template/  scaffold: one folder per phase + project.yaml manifest
└── docs/         the reference library (philosophy, patterns, lessons, V2)
```

Every directory's purpose, contributor use, AI-agent interaction, and the
cross-project inheritance model are explained in [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## Start a new board

```bash
cp -r projects/_template projects/my-board
cp templates/build_sheet.template.md   projects/my-board/04_schematic/build_sheet.md
cp templates/net_connection.template.md projects/my-board/04_schematic/net_connection.md
```
Then point an AI agent at [`CLAUDE.md`](CLAUDE.md): *"follow the workflow, start
phase 1 for projects/my-board."* The agent walks the 12 phases, running the
replayable work autonomously and stopping for your sign-off on the irreversible
steps (placement approval, go-ahead to route, DRC sign-off, fab order). Every
lesson it learns flows back into `knowledge/` — so your **next** board starts
smarter.

---

## Provenance & honesty

Extracted from a real ESP32 robotics board (EasyEDA Pro + KiCad, AI-driven, ~30
sessions), **including the record of what went wrong** — see
[`docs/13_LESSONS_LEARNED.md`](docs/13_LESSONS_LEARNED.md) and
[`knowledge/learning-db.md`](knowledge/learning-db.md). You inherit the solutions
without paying the tuition.

## License

[MIT](LICENSE).
