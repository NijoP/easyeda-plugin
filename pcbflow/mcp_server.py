"""PCB Flow MCP server — exposes the harness as tools any AI agent can call.

Optional component (keeps the core dependency-free). Install the extra and run:

    pip install -e ".[mcp]"
    python3 -m pcbflow.mcp_server        # stdio transport

Then register it with an AI host (Claude Code / Cursor / Codex) — see pcbflow/MCP.md.
Every tool is thin glue over the already-tested pcbflow modules.
"""
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import ipc, phases
from . import geometry as _geom
from . import routing as _rout
from . import congestion as _cong
from .project import Project

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"

mcp = FastMCP("pcbflow")


# --- engineering ---------------------------------------------------------------
@mcp.tool()
def ipc_trace_width(current_a: float, delta_t_c: float = 10.0,
                    copper_oz: float = 1.0, internal: bool = False) -> dict:
    """IPC-2221 minimum trace width (mm) for a current; recommends trace vs plane/pour,
    and the 0.3 mm via-farm count when a plane is needed."""
    r = ipc.recommend(current_a, delta_t_c=delta_t_c, copper_oz=copper_oz, internal=internal)
    if r["method"] == "plane/pour":
        r["via_farm_0p3mm"] = ipc.via_count(current_a, 0.3)
    return r


@mcp.tool()
def trace_width_table(nets: list, delta_t_c: float = 10.0) -> list:
    """Per-net IPC-2221 width + trace/plane call.
    nets: [{"net", "i_peak_a", optional "oz", "internal"}]."""
    return _rout.trace_width_table(nets, delta_t_c=delta_t_c)


@mcp.tool()
def stitch_pitch(t_rise_ns: float, er: float = 4.3) -> dict:
    """λ/20 ground-stitch pitch (mm) from an edge rise time (ns) — from the edge rate,
    not the clock — plus the edge-rate knee in MHz."""
    return {"edge_knee_mhz": _rout.edge_knee_mhz(t_rise_ns),
            "stitch_pitch_mm": _rout.stitch_pitch_mm(t_rise_ns, er)}


@mcp.tool()
def spacing_audit(parts: list, min_gap: float = 0.5, whitelist: Optional[list] = None) -> dict:
    """Same-layer pad-spacing audit on real geometry.
    parts: [{"ref", "layer": "TOP"|"BOTTOM", "bbox": [x0,y0,x1,y1]}]."""
    v = _geom.spacing_audit(parts, min_gap=min_gap, whitelist=whitelist or [])
    return {"violations": v, "clean": not v}


@mcp.tool()
def predict_congestion(nets: list, w_mm: float, h_mm: float, bin_mm: float = 2.0) -> dict:
    """Routing-congestion prediction — which 2 mm bins need a via-fan to the other layer.
    nets: [{"drc_class", "bbox": [x0,y0,x1,y1]}]."""
    g = _cong.grid(nets, w_mm, h_mm, bin_mm=bin_mm)
    hot = _cong.saturated(g)
    return {"bins": f"{g['nx']}x{g['ny']}", "bin_mm": g["bin_mm"],
            "saturated": hot, "saturated_count": len(hot)}


# --- project orchestration -----------------------------------------------------
@mcp.tool()
def list_phases() -> list:
    """The 12-phase PCB Flow pipeline (number, name, owning agent)."""
    return [{"phase": n, "name": name, "agent": agent} for (n, name, agent) in phases.PHASES]


@mcp.tool()
def project_init(name: str, description: str = "") -> dict:
    """Create a project workspace (starts at phase 1)."""
    p = Project.init(PROJECTS, name, description)
    return {"name": name, "current_phase": p.current_phase()}


@mcp.tool()
def project_status(name: str) -> dict:
    """A project's current phase, owning agent, and latest verdict."""
    return Project(PROJECTS / name).status()


@mcp.tool()
def record_verdict(name: str, phase: int, verdict: str, note: str = "") -> dict:
    """Record a phase verdict (PASS / CONDITIONAL / FAIL)."""
    Project(PROJECTS / name).record_verdict(phase, verdict, note)
    return {"ok": True, "name": name, "phase": phase, "verdict": verdict.upper()}


@mcp.tool()
def advance_phase(name: str) -> dict:
    """Advance a project to the next phase — refuses without a PASS ('place nothing over wrong')."""
    p = Project(PROJECTS / name)
    try:
        nxt = p.advance()
        return {"ok": True, "advanced_to": nxt, "phase_name": phases.phase_name(nxt)}
    except RuntimeError as e:
        return {"ok": False, "error": str(e)}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
