# AXON — An AI-Assisted Electronics Engineering Workspace

**Design a professional PCB — from a client's requirements to manufacturing-ready
files — with an AI engineering assistant doing the repetitive work and you making
the engineering calls.**

You bring the electronics knowledge. AXON brings a disciplined, repeatable process
and an AI assistant that runs the tools for you. You never have to learn to program.

> 👉 **New here? Start with the handbook:** [`handbook/`](handbook/README.md) — a
> step-by-step guide from installing the tools to shipping a board. If you read one
> thing, read [`handbook/01-introduction.md`](handbook/01-introduction.md).

---

## What is this?

AXON is a **workspace and a method**, not a program you run. You open it in a code
editor (VS Code), and an **AI assistant** (such as Claude Code) reads the
instructions in this repository and helps you design a PCB by:

- studying the client requirements and doing a feasibility study,
- planning the Bill of Materials,
- drawing the schematic in EasyEDA,
- checking the schematic for errors,
- planning and placing the components,
- routing the board in KiCad,
- and preparing the manufacturing files.

**You stay in control.** The AI does the busywork and the checking; you approve every
important engineering decision.

## Who is it for?

**Electronics engineers** — people who know PCB design, schematics, BOMs, and
manufacturing. You do **not** need to know programming, APIs, or automation. Where a
software idea matters, the handbook explains it in plain language (and the
[glossary](handbook/glossary.md) is always one click away).

## What problem does it solve?

PCB design has a lot of careful, repetitive, error-prone work: wiring every net,
checking every pin, placing every part, sizing every trace, running every check.
AXON hands that work to an AI assistant that is fast, tireless, and follows a fixed
set of engineering rules — while keeping *you*, the engineer, as the decision-maker.
It also remembers what it learned on past boards, so every project starts smarter
than the last.

---

## Who does what

| You (the engineer) decide… | The AI assistant does… |
|---|---|
| What the product must do (requirements) | The feasibility study and the math (density, current, cost) |
| Which parts to use (final BOM approval) | Researching parts, availability, and datasheets |
| The board size, shape, and connector positions | Drawing the schematic and placing the components |
| Whether a placement is practical | Checking the schematic and the placement for errors |
| Go-ahead to start routing | Routing the board and running the design-rule checks |
| **Placing the manufacturing order** (always you) | Preparing the gerbers, BOM, and assembly files |

**The simple rule:** the AI does anything that can be re-done if it's wrong
(analysis, drawing, checking). You approve anything that changes the live design or
that can't be undone — and *you* always place the fab order.

## Which tool does what

- **EasyEDA** — where the **schematic** is drawn and the **components are placed**.
- **KiCad** — where the board is **routed** and the final **design checks** run.
- The AI moves the design from EasyEDA to KiCad for you and keeps them in sync.

(Why the split? KiCad can be automated for routing and rule-checking in ways EasyEDA
cannot. You don't need to worry about this — the AI handles the handoff.)

---

## The workflow, at a glance

```
   Client requirement
        ↓   Feasibility study
   BOM planning
        ↓   Component selection
   EasyEDA project creation
        ↓   Autonomous schematic generation
   Schematic review
        ↓
   Placement planning  →  Placement knowledge graph  →  Automated placement
        ↓   Export to KiCad
   AI routing
        ↓   Design verification
   Manufacturing package
```

Each step has a clear checkpoint. You don't move to the next step until the current
one is confirmed correct. Full walkthrough:
[`handbook/`](handbook/README.md) and [`DESIGN_WORKFLOW.md`](DESIGN_WORKFLOW.md).

---

## What you need

| Thing | What it's for | How to get it |
|---|---|---|
| **VS Code** | the workspace you open this repo in | [handbook step 2](handbook/02-installing-tools.md) |
| **An AI assistant** (Claude Code, Codex, OpenCode, …) | the assistant that reads this repo and helps you | [handbook step 2](handbook/02-installing-tools.md) |
| **EasyEDA Pro** (free account) | schematic + placement | [handbook step 2](handbook/02-installing-tools.md) |
| **KiCad** (free) | routing + verification | [handbook step 2](handbook/02-installing-tools.md) |
| **Git** (installed once, mostly invisible) | saves and publishes your work | [handbook step 2](handbook/02-installing-tools.md) |

**Skills required:** PCB and electronics knowledge. **No programming required.**

---

## Where things live (the repository map)

| Folder | In plain terms |
|---|---|
| [`handbook/`](handbook/) | **Start here.** The step-by-step guide for engineers. |
| [`workflow/`](workflow/) | The 12 design steps, each explained with its checkpoint. |
| [`agents/`](agents/) | The "job descriptions" for the AI helpers (one per step). |
| [`automation/`](automation/) | The tools the AI uses to drive EasyEDA and KiCad. *You don't touch these.* |
| [`knowledge/`](knowledge/) | The engineering rules and lessons the AI follows. |
| [`templates/`](templates/) | Blank forms you fill in for a new board (parts list, net list, rules). |
| [`projects/`](projects/) | **Your boards live here** — one folder per project, with all its files and outputs. |
| [`docs/`](docs/) | Deep reference material. *Optional — for later, or for contributors.* |
| [`reliability/`](reliability/) | How the workspace detects & recovers from problems, plus the [troubleshooting guide](reliability/TROUBLESHOOTING.md). |
| Root files (`CLAUDE.md`, `AGENTS.md`) | Instruction sheets the **AI** reads. You don't need to. |

---

## Where to begin

1. Read [`handbook/01-introduction.md`](handbook/01-introduction.md) (10 minutes).
2. Install the tools: [`handbook/02-installing-tools.md`](handbook/02-installing-tools.md).
3. Create your first project: [`handbook/04-your-first-project.md`](handbook/04-your-first-project.md).

Then just talk to your AI assistant in plain English. It will walk you through the
rest.

## License

[MIT](LICENSE) — free to use, adapt, and share.
