# pcbmunch — PCB Design-Intelligence MCP Server

In the spirit of `jcodemunch` / `jdocmunch` (code/doc knowledge servers), **reframed
for PCB design**. It indexes a board's connectivity into a queryable model and exposes
it as MCP tools, so an AI **reasons over grounded design facts** — nets, components,
impact, health — instead of guessing. This is what produces better PCB-design output.

## Why it helps

An AI asked to "move VSYS to a plane" or "remove the fuel gauge" normally guesses at the
consequences. With pcbmunch it can *ask the board*: which components are on VSYS, what
its current/width is, what breaks if the part is removed, whether an IC is missing a
decoupling cap. Grounded facts → fewer mistakes.

## Install & run

```bash
pip install -e ".[mcp]"
python3 -m pcbflow.munch_server        # stdio transport
```

Register with an AI host (Claude Code `.mcp.json` shown; Cursor/Codex similar):
```json
{ "mcpServers": { "pcbmunch": {
  "command": "python3", "args": ["-m", "pcbflow.munch_server"],
  "cwd": "/absolute/path/to/pcbflow" } } }
```

## What it indexes

Per project, from `projects/<project>/`:
- `netlist.json` — the reconstructed netlist (`pcbflow dump` → `pcbflow recon`).
- `design_rules.json` *(optional)* — net classes.
- `currents.json` *(optional)* — `{net: peak_amps}` for width/plane calls.

## Tools

| Tool | Answers |
|---|---|
| `index_board(project)` | (re)index; component/net counts |
| `get_net(project, net)` | class, members, components, IPC width + trace/plane |
| `get_component(project, ref)` | value, LCSC, pins→nets, neighbours |
| `search_nets(project, pattern)` | nets matching a regex, with class + pin count |
| `power_rails(project)` | the rails, ranked by consumers |
| `decaps_of(project, ref)` | an IC's likely decoupling caps |
| `net_blast_radius(project, net)` | what a net change affects |
| `component_blast_radius(project, ref)` | what a part change/removal affects |
| `design_health(project)` | single-pin nets, unconnected pins, unclassed nets, high-current nets needing a plane, ICs missing a decoupling cap |

The intelligence core (`pcbflow/design_index.py`) is pure Python and unit-tested; the
server is thin glue. Optional — the core package/CLI have no MCP dependency.
