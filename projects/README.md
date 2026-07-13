# projects/ — Per-Board Workspaces

Each real board is a folder here, scaffolded from [`_template/`](_template/). This
is the **only** place board-specific work lives — geometry, net names, decisions.
The framework layers (`workflow/`, `agents/`, `automation/`, `knowledge/`,
`templates/`) stay board-agnostic so they can serve every board; the specifics live
here.

## Start a board

```bash
cp -r projects/_template projects/my-board
# seed the source-of-truth docs from the templates:
cp templates/build_sheet.template.md   projects/my-board/04_schematic/build_sheet.md
cp templates/net_connection.template.md projects/my-board/04_schematic/net_connection.md
```
Fill `project.yaml`, then point an AI agent at [`../CLAUDE.md`](../CLAUDE.md):
*"follow the workflow, start phase 1 for projects/my-board."*

## Layout of a project

One folder per phase (`00_brief` … `12_verification`) holding that phase's
deliverables, plus `project.yaml` — the manifest the orchestrator reads to know the
current phase, the verdicts so far, and the key decisions. The phase folders are the
audit trail: a future engineer can see exactly why the board is the way it is.

## Rules

- **Commit geometry the moment it exists** — an uncommitted board is one mistake from
  gone. The build is disposable *only* because the knowledge (docs + manifest) is safe.
- **Board-specific facts stay here**, never in `knowledge/`. A general rule belongs
  in `knowledge/`; the instance belongs in the project. That discipline is what keeps
  the framework reusable.
- **Every lesson learned here** gets written up into
  [`../knowledge/learning-db.md`](../knowledge/learning-db.md) so the next board
  inherits it.

> The origin project (an ESP32 robotics board) is the reference example behind this
> whole framework; its lessons seed [`../knowledge/learning-db.md`](../knowledge/learning-db.md).
