# PCB Flow MCP Server

Exposes the PCB Flow harness as **MCP tools** so any AI agent that speaks the Model
Context Protocol — Claude Code, Cursor, Codex, and others — can call the engineering
and orchestration functions directly (instead of shelling out). This is what makes the
framework truly **AI-model-agnostic**.

## Install & run

```bash
pip install -e ".[mcp]"          # adds the `mcp` SDK
python3 -m pcbflow.mcp_server     # runs over stdio (how MCP hosts launch it)
```

## Register with an AI host

**Claude Code** — add to `.mcp.json` at your repo root (or `~/.claude.json`):
```json
{
  "mcpServers": {
    "pcbflow": {
      "command": "python3",
      "args": ["-m", "pcbflow.mcp_server"],
      "cwd": "/absolute/path/to/pcbflow"
    }
  }
}
```
(Windows: use `"python"` and the Windows path.)

**Cursor** — Settings → MCP → add a server with the same command/args.
**Any MCP host** — point it at `python3 -m pcbflow.mcp_server` (stdio transport).

## Tools exposed

| Tool | What it returns |
|---|---|
| `ipc_trace_width(current_a, …)` | IPC-2221 width + trace/plane call + via-farm count |
| `trace_width_table(nets, …)` | per-net width + method |
| `stitch_pitch(t_rise_ns, …)` | λ/20 ground-stitch pitch + edge-rate knee |
| `spacing_audit(parts, …)` | same-layer pad-spacing violations |
| `predict_congestion(nets, w, h, …)` | which 2 mm bins need a via-fan |
| `list_phases()` | the 12-phase pipeline |
| `project_init / project_status` | create / inspect a project |
| `record_verdict / advance_phase` | record a verdict / advance (gated on a PASS) |

Each tool is thin glue over the tested `pcbflow` modules (`ipc`, `geometry`, `routing`,
`congestion`, `project`, `phases`), so an agent gets the same verified behaviour as the
CLI — with the phase gates enforced.

## Note

The MCP server is **optional** — the core package and CLI have no MCP dependency. It
also can't be exercised without an MCP host, so validate it once against your agent
after installing (the underlying tool logic is already unit-tested).
