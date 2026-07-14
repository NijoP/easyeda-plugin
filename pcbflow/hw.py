"""Hardware checks — the electrical-correctness + integrity detectors, folded into harmonized
findings behind one entry point.

- Tier 1 (electrical correctness): pin-type ERC, power-tree integrity, component ratings.
- Tier 2 (integrity): thermal always; signal-integrity (impedance + length match) and
  power-distribution (IR drop + via ampacity) when a routed board is supplied.

All checks need the optional parts spec (`pcbflow.parts`); board checks need a `.kicad_pcb`.
With missing data a check reports nothing (never guesses). Tiers 3–4 are scoped in
docs/HW_IMPLEMENTATION_PLAN.md. Pure Python 3 standard library.
"""
from . import erc_pins, kicad_sexp, pdn, power_tree, ratings, si, thermal
from .enet import Enet
from .parts import Parts
from .stackup import Stackup


def run(netlist, parts=None, board=None, stack=None):
    """Run the hardware checks. `netlist` is a path (parts.json auto-loaded beside it) or an Enet.
    Pass `board` (a `.kicad_pcb` path) to add the routed-geometry checks (SI + PDN)."""
    if isinstance(netlist, Enet):
        enet, parts = netlist, (parts or Parts())
    else:
        enet = Enet.load(netlist)
        parts = parts or Parts.beside(netlist)

    fs = []
    fs += erc_pins.run(enet, parts)                       # T1
    pt_findings, rails = power_tree.run(enet, parts)
    fs += pt_findings
    fs += ratings.run(enet, parts, rails)
    fs += thermal.run(enet, parts, rails)                 # T2 (no board needed)

    if board:                                             # T2 (routed geometry)
        geometry = kicad_sexp.read_pcb_geometry(board)
        stack = stack or Stackup.two_layer()              # caller overrides with stack= for 4-layer
        fs += si.run(enet, geometry, stack)
        fs += pdn.run(enet, geometry, stack, rails)
    return fs
