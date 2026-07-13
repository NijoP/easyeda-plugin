"""pcbmunch — a PCB design-intelligence MCP server (in the spirit of jcodemunch /
jdocmunch, reframed for PCB design).

Index a board's connectivity once, then answer grounded questions — net/component
lookups, blast radius (what breaks if I change this net/part), power rails, and a
design-health radar — so an AI produces better, fact-checked PCB-design output.

Optional component. Install and run:
    pip install -e ".[mcp]"
    python3 -m pcbflow.munch_server        # stdio transport
Register with an AI host — see pcbflow/PCBMUNCH.md.

It indexes  projects/<project>/netlist.json  (the recon.py output), plus optional
design_rules.json (net classes) and currents.json ({net: peak_amps}).
"""
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .design_index import DesignIndex

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"

mcp = FastMCP("pcbmunch")
_CACHE = {}


def _load(project, reindex=False):
    if not reindex and project in _CACHE:
        return _CACHE[project]
    base = PROJECTS / project
    nl = base / "netlist.json"
    if not nl.exists():
        raise FileNotFoundError(
            f"no netlist at {nl} — run `pcbflow dump` then `pcbflow recon` first")
    netlist = json.loads(nl.read_text())
    netlist = netlist.get("v", netlist)                 # tolerate the CDP {ok,v} envelope
    rules = {}
    rp = base / "design_rules.json"
    if rp.exists():
        for nc in json.loads(rp.read_text()).get("net_classes", []):
            for net in nc.get("nets", []):
                rules[net] = nc.get("name")
    cp = base / "currents.json"
    currents = json.loads(cp.read_text()) if cp.exists() else {}
    ix = DesignIndex(netlist, rules, currents)
    _CACHE[project] = ix
    return ix


def _found(x):
    return x if x is not None else {"error": "not found"}


@mcp.tool()
def index_board(project: str) -> dict:
    """(Re)index a board's design and return a summary (component/net counts)."""
    return _load(project, reindex=True).summary()


@mcp.tool()
def get_net(project: str, net: str) -> dict:
    """Everything about a net: class, pin members, connected components, and (if a
    current is known) its IPC-2221 width + trace/plane call."""
    return _found(_load(project).net(net))


@mcp.tool()
def get_component(project: str, ref: str) -> dict:
    """A component: value, LCSC, pins→nets, the nets it touches, and its neighbours."""
    return _found(_load(project).component(ref))


@mcp.tool()
def search_nets(project: str, pattern: str) -> list:
    """Find nets by regex/substring, with their class and pin count."""
    return _load(project).search_nets(pattern)


@mcp.tool()
def power_rails(project: str) -> list:
    """The board's power/ground rails, ranked by number of consumers."""
    return _load(project).power_rails()


@mcp.tool()
def decaps_of(project: str, ref: str) -> list:
    """Capacitors sharing a power net with an IC (its likely decoupling)."""
    return _load(project).decaps_of(ref)


@mcp.tool()
def net_blast_radius(project: str, net: str) -> dict:
    """Impact of changing a net: the components on it and the adjacent nets touched."""
    return _found(_load(project).net_blast_radius(net))


@mcp.tool()
def component_blast_radius(project: str, ref: str) -> dict:
    """Impact of changing/removing a part: the nets and other components affected."""
    return _found(_load(project).component_blast_radius(ref))


@mcp.tool()
def design_health(project: str) -> dict:
    """A design-health radar: single-pin nets, unconnected pins, unclassed nets,
    high-current nets needing a plane, and ICs on a power net with no decoupling cap."""
    return _load(project).health()


def main():
    mcp.run()


if __name__ == "__main__":
    main()
