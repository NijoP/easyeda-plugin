# PCB Flow — Product Roadmap

Where the project is and where it's going. (This is the *product* roadmap; the
internal reliability build plan lives in
[`reliability/ROADMAP.md`](reliability/ROADMAP.md).)

## ✅ Current capabilities

- **The 12-phase engineering workflow** — client requirement → feasibility → BOM →
  EasyEDA project → AI schematic generation → schematic audit → placement planning →
  placement knowledge graph → automated placement → KiCad export → AI-assisted routing
  → verification → manufacturing, each with a hard checkpoint.
- **AI agent roster** — one defined role per phase, coordinated by an orchestrator.
- **Automation** — EasyEDA schematic + placement (Standalone-Script engine), headless
  browser readback (CDP), KiCad routing + DRC, and a shared IPC-2221 / congestion layer.
- **Engineering knowledge base** — first principles, a heuristics graph, hard design
  standards (IPC widths, via ampacity, DFM floor), and an append-only learning log that
  compounds across projects.
- **Reliability layer (built + unit-tested)** — a preflight environment `doctor`, automatic
  fault diagnosis, safe retry, a phantom-DRC guard, checkpoint/resume, and cross-platform
  tooling. Structured logging and the self-healing recovery engine are implemented and
  unit-tested but **opt-in** — not yet wired into every phase, and the live browser/KiCad
  recovery strategies still need real-session validation (see below).
- **Engineer handbook** — a 12-step onboarding path plus a glossary, written for
  electronics engineers with no software background.

## 🚧 In progress / needs real-world validation

- **Live-session validation** of the recovery strategies (renderer-hang reset, session
  re-auth, Chrome/CDP recovery) against a real EasyEDA session.
- **Non-Linux validation** of the cross-platform launcher and DRC runner on macOS and
  Windows (logic is written and unit-tested; the live launch needs a real host).
- **A worked reference project** end-to-end in `projects/` as a public example.

## 🔭 Planned

- Fold the `tools/` reliability verbs (`doctor`, `recover`, `heal`, `state`, …) into the
  unified `pcbflow` CLI as first-class subcommands.
- A source-of-truth linter (auto-check `build_sheet.md` ↔ `net_connection.md`).
- Deeper KiCad-native routing automation (pours/zones/stitching scripted end-to-end).
- More AI-agent adapters and an explicit adapter interface.

## 🧪 Future research

- **Board recompile** — regenerate schematic → placement → routing from the knowledge
  layer with one command (making "geometry is a build artifact" literally executable).
- A **cross-project knowledge graph** that promotes board-specific lessons into general
  engineering rules automatically.
- Additional EDA backends behind a common adapter.

## 🌟 Long-term vision

Every electronics engineer has a disciplined AI collaborator that carries a design from
brief to manufacturing, gets smarter with every board, and never takes an irreversible
decision out of human hands.

> Status legend: ✅ built & tested · 🚧 in progress / needs validation · 🔭 planned ·
> 🧪 research · 🌟 vision.
