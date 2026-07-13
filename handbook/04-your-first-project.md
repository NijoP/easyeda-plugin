# 04 — Creating Your First Project

**For:** electronics engineers · **Software knowledge needed:** none — the AI does the setup.

- **Purpose:** start a new board and give the AI its requirements.
- **What you need:** a clear idea of what the product must do.
- **What you get:** a project folder and a completed **feasibility study** (Step 1 of
  the workflow).

## What you do

1. Tell the AI to create the project:
   > *"Create a new project called `my-board`. It's a [describe the product: what it
   > does, power source, key sensors, size limits, budget, quantity]. Do the
   > feasibility study."*
2. The AI sets up a project folder from the template and starts Phase 1.
3. Answer any questions it asks (e.g. "battery type?", "target unit cost?").
4. Read the feasibility study it produces and approve or adjust.

## What the AI does

- Creates `projects/my-board/` with one folder per design step (you'll see
  `01_feasibility`, `02_bom`, … `12_verification`) and a `project.yaml` record.
- Produces the **feasibility study**: what the product needs, whether it's
  technically feasible, a rough cost, a power budget, the hardware architecture, the
  risks, and how complex it is.
- Does the key sizing math for you: is the board big enough for the parts? does any
  power rail need a heavier copper plane (which decides 2 vs 4 layers)?

## What good looks like

- A feasibility study you'd be comfortable showing a client.
- Every requirement is written down with a number and a source.
- A clear verdict: feasible as-is, feasible with changes, or not feasible.

## Where things end up

Everything for this board lives under `projects/my-board/`. The `project.yaml` file
is the "cover sheet" — it records which step you're on and every decision made. You
don't edit it by hand; the AI keeps it current.

## Common mistakes

- Giving a one-line brief. The more the AI knows up front (power, size, cost,
  environment, quantity), the better the study.
- Skipping the study to "get to the schematic." **No schematic work starts until the
  feasibility study is approved** — this is the checkpoint that prevents wasted work.

## Checklist

- [ ] Project folder created under `projects/`.
- [ ] Feasibility study produced and read.
- [ ] Every requirement quantified; no unanswered conflict.
- [ ] I approved the study (the project is a "go").

## Next step

With the study approved, plan the parts list.

---
◀ [03 — VS Code & your AI assistant](03-vscode-and-ai.md) · Next ▶ [05 — BOM planning](05-bom-planning.md)
