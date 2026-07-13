# templates/ — Source-of-Truth Blanks

The fill-in-the-blank artifacts that **define a board**. Copy them into a project
and fill them; the schematic, placement, and routing are generated from them. These
are *data* — the *engine* that consumes them lives in
[`../automation/`](../automation/).

| Template | Defines | Filled in phase |
|---|---|---|
| [`build_sheet.template.md`](build_sheet.template.md) | every part, pin, net (the tick-sheet) | 3–4 |
| [`net_connection.template.md`](net_connection.template.md) | the net dictionary + membership oracle | 3 |
| [`design_rules.template.json`](design_rules.template.json) | net classes, widths, clearances, diff pairs | 7 |
| [`trace_width_table.template.json`](trace_width_table.template.json) | per-net IPC-2221 current→width | 7 |
| [`route_sequence.template.json`](route_sequence.template.json) | the ordered, DRC-gated routing plan | 7/11 |
| [`placement.template.json`](placement.template.json) | region plan, coordinates, refdes silk | 8–9 |

## The two that matter most

`build_sheet.md` and `net_connection.md` **are the board.** They must agree
net-for-net; on conflict, the net dictionary wins. Get them right and the schematic
generator becomes dumb and deterministic — it just wires each pin to its named net.

Every template marks **SPECIFIC** (replace per board) vs **GENERAL** (keep the
structure) fields so you know exactly what to change.
