#!/usr/bin/env python3
"""Generate the ``example-usb-c-3v3`` reference KiCad PCB from its netlist.

WHY THIS EXISTS
---------------
This project's philosophy is "knowledge is the source, geometry is a build artifact".
The board ``.kicad_pcb`` is therefore *generated* by this script from the 8-component /
6-net contract below, rather than hand-authored. Emitting the S-expression geometry
programmatically is far more reliable than typing raw Lisp by hand, and it keeps this
generator as the single source of truth: re-running it reproduces the board exactly.

WHAT IT PRODUCES
----------------
A fully valid, fully routed, DRC-clean KiCad 10 board plus a sibling project file:

    projects/example-usb-c-3v3/10_kicad_export/board.kicad_pcb
    projects/example-usb-c-3v3/10_kicad_export/board.kicad_pro

The board matches ``projects/example-usb-c-3v3/04_schematic/netlist.enet`` pad-for-net
(verify with ``python3 -m pcbflow.cli import-check``), and passes KiCad DRC against the
JLCPCB 2-layer 1oz ruleset with 0 violations and 0 unconnected items.

THE NETLIST (source of truth — do NOT edit here; mirror of netlist.enet)
------------------------------------------------------------------------
    J1  USB-C   pad1=VBUS pad2=GND pad3=CC1 pad4=CC2
    R1  0402    pad1=CC1  pad2=GND
    R2  0402    pad1=CC2  pad2=GND
    U1  SOT-23-5 pad1=VBUS pad2=GND pad3=VBUS pad5=+3V3   (no pad 4)
    C1  0603    pad1=VBUS pad2=GND
    C2  0603    pad1=+3V3 pad2=GND
    R3  0402    pad1=+3V3 pad2=LED_A
    D1  0603    pad1=LED_A pad2=GND
    Nets: VBUS, +3V3, GND, CC1, CC2, LED_A

RULESET (JLCPCB 2-layer 1oz) enforced by the emitted (setup) + net classes
--------------------------------------------------------------------------
    min track 0.15  min clearance 0.15  copper-to-edge 0.25
    via drill >=0.20  via pad >=0.50  annular ring >=0.10  hole-to-hole >=0.50
    net class POWER (VBUS,+3V3) track 0.4mm ; DEFAULT track 0.25mm

FOOTPRINTS ARE SIMPLIFIED
-------------------------
Footprints are simplified reference SMD footprints (rectangular F.Cu pads at realistic
sizes / pitches). Real vendor library footprints are NOT required: the board only needs
to be electrically valid and DRC-clean, which these are. See ``PADSPECS`` below.

ROUTING
-------
Every net is routed with EXPLICIT track segments (NO copper zones/pours — ``kicad-cli``
cannot fill zones offline, so an unfilled GND zone would leave pads unconnected and fail
the connectivity check). GND is routed with real tracks like every other net. Routing is
primarily on F.Cu; B.Cu + a through-via is used only where a crossing forces it.

USAGE
-----
    python3 tools/gen_example_board.py            # write board + project
    python3 tools/gen_example_board.py --help
    python3 tools/gen_example_board.py --stdout    # print board to stdout, write nothing
"""
from __future__ import annotations

import argparse
import math
import os
import sys

# ── output paths (fixed by the task) ────────────────────────────────────────
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(REPO, "projects", "example-usb-c-3v3", "10_kicad_export")
BOARD_PATH = os.path.join(EXPORT_DIR, "board.kicad_pcb")
PROJECT_PATH = os.path.join(EXPORT_DIR, "board.kicad_pro")

# ── design rules (JLCPCB 2-layer 1oz) ───────────────────────────────────────
CLEARANCE = 0.15          # min copper-to-copper clearance (mm)
TRACK_MIN = 0.15          # min track width (mm)
EDGE_CLEAR = 0.25         # copper-to-edge (informational; placement keeps >=this)
VIA_DRILL = 0.30          # via drill (>= 0.20 floor; 0.30 is comfortable)
VIA_PAD = 0.60            # via pad / diameter (>= 0.50 floor)
W_POWER = 0.40            # POWER net-class track width
W_DEFAULT = 0.25          # DEFAULT net-class track width

BOARD_W = 35.0            # board outline width (mm)
BOARD_H = 22.0            # board outline height (mm)

# ── net table: name -> id. id 0 is the mandatory "no-net". ──────────────────
NETS = ["VBUS", "GND", "+3V3", "CC1", "CC2", "LED_A"]
NET_ID = {name: i + 1 for i, name in enumerate(NETS)}   # 1-based; 0 reserved for ""
POWER_NETS = {"VBUS", "+3V3"}


def net_width(net: str) -> float:
    """Track width for a net, per net class."""
    return W_POWER if net in POWER_NETS else W_DEFAULT


# ── footprint pad geometry (simplified reference footprints) ────────────────
# Each entry: list of (pad_name, dx, dy, w, h) relative to the component origin.
# 0402: 0.6 x 0.5 mm pads at +-0.5 mm.  0603: 0.8 x 0.9 mm pads at +-0.75 mm.
# SOT-23-5: 0.6 x 0.9 mm pads, 0.95 mm pitch (pins 1/2/3 on one side, 5 opposite).
def _passive_0402():
    return [("1", -0.50, 0.0, 0.60, 0.50), ("2", 0.50, 0.0, 0.60, 0.50)]


def _passive_0603():
    return [("1", -0.75, 0.0, 0.80, 0.90), ("2", 0.75, 0.0, 0.80, 0.90)]


def _sot235():
    # Bottom row pins 1,2,3 at y=+1.0; top row pin 5 at y=-1.0 (pin 4 absent per netlist).
    p = 0.95
    return [
        ("1", -p, 1.00, 0.60, 0.90),
        ("2", 0.0, 1.00, 0.60, 0.90),
        ("3", p, 1.00, 0.60, 0.90),
        ("5", -p, -1.00, 0.60, 0.90),
    ]


def _usbc():
    # 4 simple pads on a 1.2 mm vertical pitch (reference USB-C; real 24-pin not needed).
    return [
        ("1", 0.0, -1.80, 0.90, 0.80),   # VBUS
        ("2", 0.0, -0.60, 0.90, 0.80),   # GND
        ("3", 0.0, 0.60, 0.90, 0.80),   # CC1
        ("4", 0.0, 1.80, 0.90, 0.80),   # CC2
    ]


# ── component instances ─────────────────────────────────────────────────────
# ref -> (footprint_lib_name, origin_x, origin_y, pads, pad_net_map)
# pad_net_map: pad_name -> net_name  (mirrors the netlist exactly).
COMPONENTS = {
    "J1": ("USB-C_Ref", 4.5, 11.0, _usbc(),
           {"1": "VBUS", "2": "GND", "3": "CC1", "4": "CC2"}),
    "R1": ("R_0402_Ref", 8.5, 13.4, _passive_0402(),
           {"1": "CC1", "2": "GND"}),
    "R2": ("R_0402_Ref", 8.5, 15.4, _passive_0402(),
           {"1": "CC2", "2": "GND"}),
    "C1": ("C_0603_Ref", 12.5, 7.0, _passive_0603(),
           {"1": "VBUS", "2": "GND"}),
    "U1": ("SOT-23-5_Ref", 17.0, 11.0, _sot235(),
           {"1": "VBUS", "2": "GND", "3": "VBUS", "5": "+3V3"}),
    "C2": ("C_0603_Ref", 22.0, 7.0, _passive_0603(),
           {"1": "+3V3", "2": "GND"}),
    "R3": ("R_0402_Ref", 25.5, 11.0, _passive_0402(),
           {"1": "+3V3", "2": "LED_A"}),
    "D1": ("LED_0603_Ref", 29.5, 11.0, _passive_0603(),
           {"1": "LED_A", "2": "GND"}),
}


def pad_abs(ref: str) -> dict:
    """Absolute (x, y) pad-center of every pad of a component. -> {pad_name: (x, y)}."""
    _, ox, oy, pads, _ = COMPONENTS[ref]
    return {name: (ox + dx, oy + dy) for (name, dx, dy, w, h) in pads}


def pad_net(ref: str, pad: str) -> str:
    return COMPONENTS[ref][4][pad]


# ── explicit routing ────────────────────────────────────────────────────────
# A track = (net_name, (x1,y1), (x2,y2), layer).  A via = (net_name, (x,y)).
# Endpoints are given as ("REF", "pad") pad references or literal (x, y) waypoints.
# All tracks are hand-planned so different nets keep >= CLEARANCE apart; the only
# crossing (GND daisy-chain passing the CC/VBUS band) hops to B.Cu via one via pair.

def _p(ref: str, pad: str):
    return pad_abs(ref)[pad]


def routes():
    """Return (tracks, vias) — explicit hand-planned routing for every net."""
    tracks = []
    vias = []

    def T(net, a, b, layer="F.Cu"):
        pa = _p(*a) if isinstance(a[0], str) else a
        pb = _p(*b) if isinstance(b[0], str) else b
        tracks.append((net, pa, pb, layer))

    def V(net, xy):
        vias.append((net, xy))

    # Pad coordinates for reference (computed):
    #   J1: 1(4.5,9.2)VBUS 2(4.5,10.4)GND 3(4.5,11.6)CC1 4(4.5,12.8)CC2
    #   R1: 1(8.0,13.4)CC1 2(9.0,13.4)GND
    #   R2: 1(8.0,15.4)CC2 2(9.0,15.4)GND
    #   C1: 1(11.75,7.0)VBUS 2(13.25,7.0)GND
    #   U1: 1(16.05,12.0)VBUS 2(17.0,12.0)GND 3(17.95,12.0)VBUS 5(16.05,10.0)+3V3
    #   C2: 1(21.25,7.0)+3V3 2(22.75,7.0)GND
    #   R3: 1(25.0,11.0)+3V3 2(26.0,11.0)LED_A
    #   D1: 1(28.75,11.0)LED_A 2(30.25,11.0)GND

    # ---- VBUS (POWER 0.4) : J1.1 -> C1.1 -> U1.1 -> U1.3 ----------------------
    # J1.1 (4.5,9.2) right along y=9.2 (clear of the CC band below), up into C1.1.
    T("VBUS", ("J1", "1"), (11.75, 9.2))     # J1.1 right along y=9.2
    T("VBUS", (11.75, 9.2), ("C1", "1"))     # up into C1.1 (11.75,7.0)
    # C1.1 -> U1.1. Leave C1.1 going LEFT/down (away from C1.2 GND at 13.25,7) then
    # run along y=9.2 to x=15.2 and approach U1.1 (16.05,12) from the LEFT at y=12
    # (never crossing x=16.05 where U1.5 +3V3 sits at y=10).
    T("VBUS", ("C1", "1"), (11.75, 9.2))     # C1.1 down to the y=9.2 lane (same x, clear of C1.2)
    T("VBUS", (11.75, 9.2), (15.2, 9.2))     # right along y=9.2 to a left-of-U1 lane
    T("VBUS", (15.2, 9.2), (15.2, 12.0))     # down at x=15.2 (left of U1.1)
    T("VBUS", (15.2, 12.0), ("U1", "1"))     # into U1.1 (16.05,12) from the left
    # Bridge U1.1 (16.05,12) <-> U1.3 (17.95,12) BELOW U1.2 (GND,17.0,12), at y=14.2.
    # (U1.2's GND stub leaves down-RIGHT and clears the right end of this bridge.)
    T("VBUS", ("U1", "1"), (16.05, 14.2))    # U1.1 down below the pad row
    T("VBUS", (16.05, 14.2), (17.95, 14.2))  # across under U1.2
    T("VBUS", (17.95, 14.2), ("U1", "3"))    # up into U1.3

    # ---- +3V3 (POWER 0.4) : U1.5 -> C2.1 -> R3.1 ------------------------------
    # U1.5 (16.05,10) UP (never toward U1.1 at y=12), across the top into C2.1.
    T("+3V3", ("U1", "5"), (16.05, 8.6))     # U1.5 up
    T("+3V3", (16.05, 8.6), (21.25, 8.6))    # across the top to the C2 column
    T("+3V3", (21.25, 8.6), ("C2", "1"))     # down into C2.1 (21.25,7.0)
    # C2.1 down to R3.1 (25.0,11), keeping LEFT of the GND drop at x=24.2 / 22.75.
    T("+3V3", ("C2", "1"), (21.25, 11.0))    # C2.1 down at x=21.25 (left of GND vias)
    T("+3V3", (21.25, 11.0), ("R3", "1"))    # across at y=11 into R3.1 (25.0,11)

    # ---- LED_A (DEFAULT 0.25) : R3.2 -> D1.1 ---------------------------------
    T("LED_A", ("R3", "2"), ("D1", "1"))     # R3.2 (26.0,11.0) -> D1.1 (28.75,11.0)

    # ---- CC1 (DEFAULT 0.25) : J1.3 -> R1.1 -----------------------------------
    # Lanes: CC1 turns down at x=7.3, CC2 turns down at x=6.5 (CC2's pad is BELOW CC1's,
    # so CC2 takes the inner/left lane and CC1 the outer/right lane -> no crossing).
    T("CC1", ("J1", "3"), (7.3, 11.6))       # J1.3 (4.5,11.6) right along y=11.6
    T("CC1", (7.3, 11.6), (7.3, 13.4))       # down at x=7.3
    T("CC1", (7.3, 13.4), ("R1", "1"))       # across into R1.1 (8.0,13.4)

    # ---- CC2 (DEFAULT 0.25) : J1.4 -> R2.1 -----------------------------------
    T("CC2", ("J1", "4"), (6.5, 12.8))       # J1.4 (4.5,12.8) right along y=12.8
    T("CC2", (6.5, 12.8), (6.5, 15.4))       # down at x=6.5 (left of CC1's lane)
    T("CC2", (6.5, 15.4), ("R2", "1"))       # across into R2.1 (8.0,15.4)

    # ---- GND (DEFAULT 0.25) : J1.2 R1.2 R2.2 C1.2 U1.2 C2.2 D1.2 -------------
    # GND runs on B.Cu (which is otherwise empty) as one spine; each GND pad drops
    # to the spine through its own via on a short F.Cu stub. This keeps GND entirely
    # clear of the busy F.Cu signal band — no F.Cu crossings at all.
    gnd_pads = [("J1", "2"), ("R1", "2"), ("R2", "2"),
                ("C1", "2"), ("U1", "2"), ("C2", "2"), ("D1", "2")]
    # via point next to each GND pad (offset so the drill clears the SMD pad copper).
    via_pt = {
        ("J1", "2"): (6.0, 10.4),
        ("R1", "2"): (9.0, 12.2),
        ("R2", "2"): (9.0, 16.6),
        ("C1", "2"): (13.25, 5.6),
        ("U1", "2"): (17.0, 12.9),   # short straight stub down (stops ABOVE the y=14.2 VBUS bridge)
        ("C2", "2"): (24.2, 7.0),
        ("D1", "2"): (30.25, 13.0),
    }
    for ref, pad in gnd_pads:
        vp = via_pt[(ref, pad)]
        T("GND", (ref, pad), vp)            # short F.Cu stub pad -> via
        V("GND", vp)                        # via to B.Cu
    # B.Cu spine tying every GND via together (straight runs; B.Cu is otherwise empty).
    order = [(6.0, 10.4), (9.0, 12.2), (9.0, 16.6), (13.25, 5.6),
             (17.0, 12.9), (24.2, 7.0), (30.25, 13.0)]
    for a, b in zip(order, order[1:]):
        T("GND", a, b, "B.Cu")

    return tracks, vias


# ── S-expression emission ───────────────────────────────────────────────────
def _fmt(v: float) -> str:
    return f"{v:.4f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def _pad_sexp(name, shape, dx, dy, w, h, net_name):
    nid = NET_ID[net_name]
    return (f'    (pad "{name}" smd {shape} (at {_fmt(dx)} {_fmt(dy)}) '
            f'(size {_fmt(w)} {_fmt(h)}) (layers "F.Cu" "F.Paste" "F.Mask") '
            f'(net {nid} "{net_name}"))')


def _footprint_sexp(ref):
    libname, ox, oy, pads, netmap = COMPONENTS[ref]
    lines = [f'  (footprint "ref:{libname}" (layer "F.Cu")',
             f'    (at {_fmt(ox)} {_fmt(oy)})',
             f'    (property "Reference" "{ref}" (at 0 -2.2 0) (layer "F.SilkS") '
             f'(effects (font (size 1 1) (thickness 0.15))))',
             f'    (property "Value" "{ref}" (at 0 2.2 0) (layer "F.Fab") '
             f'(effects (font (size 1 1) (thickness 0.15))))']
    for (name, dx, dy, w, h) in pads:
        lines.append(_pad_sexp(name, "rect", dx, dy, w, h, netmap[name]))
    lines.append("  )")
    return "\n".join(lines)


def _seg_sexp(net, a, b, layer):
    nid = NET_ID[net]
    w = net_width(net)
    return (f'  (segment (start {_fmt(a[0])} {_fmt(a[1])}) (end {_fmt(b[0])} {_fmt(b[1])}) '
            f'(width {_fmt(w)}) (layer "{layer}") (net {nid}))')


def _via_sexp(net, xy):
    nid = NET_ID[net]
    return (f'  (via (at {_fmt(xy[0])} {_fmt(xy[1])}) (size {_fmt(VIA_PAD)}) '
            f'(drill {_fmt(VIA_DRILL)}) (layers "F.Cu" "B.Cu") (net {nid}))')


def _outline_sexp():
    """Edge.Cuts rectangle 0,0 -> BOARD_W,BOARD_H."""
    m = 0.0
    corners = [(m, m), (BOARD_W - m, m), (BOARD_W - m, BOARD_H - m), (m, BOARD_H - m), (m, m)]
    out = []
    for (x1, y1), (x2, y2) in zip(corners, corners[1:]):
        out.append(f'  (gr_line (start {_fmt(x1)} {_fmt(y1)}) (end {_fmt(x2)} {_fmt(y2)}) '
                   f'(stroke (width 0.1) (type solid)) (layer "Edge.Cuts"))')
    return "\n".join(out)


def _net_table_sexp():
    lines = ['  (net 0 "")']
    for name in NETS:
        lines.append(f'  (net {NET_ID[name]} "{name}")')
    return "\n".join(lines)


def _setup_sexp():
    """(setup) — minimal valid block. DRC constraints (min clearance/track/hole) live in
    the sibling .kicad_pro (net_settings + design_settings), which kicad-cli reads for rules."""
    return (
        "  (setup\n"
        "    (pad_to_mask_clearance 0)\n"
        "  )"
    )


LAYERS = """  (layers
    (0 "F.Cu" signal)
    (2 "B.Cu" signal)
    (9 "F.Adhes" user "F.Adhesive")
    (11 "B.Adhes" user "B.Adhesive")
    (13 "F.Paste" user)
    (15 "B.Paste" user)
    (17 "F.SilkS" user "F.Silkscreen")
    (19 "B.SilkS" user "B.Silkscreen")
    (21 "F.Mask" user)
    (23 "B.Mask" user)
    (25 "Dwgs.User" user "User.Drawings")
    (27 "Cmts.User" user "User.Comments")
    (29 "Eco1.User" user "User.Eco1")
    (31 "Eco2.User" user "User.Eco2")
    (33 "Edge.Cuts" user)
    (35 "Margin" user)
    (37 "F.CrtYd" user "F.Courtyard")
    (39 "B.CrtYd" user "B.Courtyard")
    (41 "F.Fab" user)
    (43 "B.Fab" user)
  )"""


def emit_board() -> str:
    tracks, vias = routes()
    parts = [
        "(kicad_pcb",
        "  (version 20240108)",
        '  (generator "gen_example_board.py")',
        '  (generator_version "10.0")',
        "  (general (thickness 1.6))",
        '  (paper "A4")',
        LAYERS,
        _setup_sexp(),
        _net_table_sexp(),
    ]
    for ref in COMPONENTS:
        parts.append(_footprint_sexp(ref))
    parts.append(_outline_sexp())
    for (net, a, b, layer) in tracks:
        parts.append(_seg_sexp(net, a, b, layer))
    for (net, xy) in vias:
        parts.append(_via_sexp(net, xy))
    parts.append(")")
    return "\n".join(parts) + "\n"


PROJECT_JSON = None  # built in emit_project()


def emit_project() -> str:
    """A .kicad_pro carrying the same DRC constraints + net classes so the sibling
    project (which kicad-cli reads for rules) enforces the ruleset."""
    import json

    doc = {
        "board": {"design_settings": {
            "rules": {
                "min_clearance": CLEARANCE,
                "min_track_width": TRACK_MIN,
                "min_through_hole_diameter": VIA_DRILL,
                "min_via_diameter": VIA_PAD,
                "min_hole_to_hole": 0.50,
                "min_hole_clearance": 0.20,
                "min_copper_edge_clearance": EDGE_CLEAR,
                "min_annular_width": 0.10,
                "allow_blind_buried_vias": False,
                "allow_microvias": False,
            },
        }},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": CLEARANCE, "track_width": W_DEFAULT,
                 "via_diameter": VIA_PAD, "via_drill": VIA_DRILL,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1,
                 "diff_pair_gap": 0.25, "diff_pair_width": 0.2,
                 "line_style": 0, "pcb_color": "rgba(0,0,0,0.000)",
                 "schematic_color": "rgba(0,0,0,0.000)", "wire_width": 6, "bus_width": 12},
                {"name": "POWER", "clearance": CLEARANCE, "track_width": W_POWER,
                 "via_diameter": VIA_PAD, "via_drill": VIA_DRILL,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1,
                 "diff_pair_gap": 0.25, "diff_pair_width": 0.2,
                 "line_style": 0, "pcb_color": "rgba(0,0,0,0.000)",
                 "schematic_color": "rgba(0,0,0,0.000)", "wire_width": 6, "bus_width": 12,
                 "nets": ["VBUS", "+3V3"]},
            ],
            "meta": {"version": 3},
            "net_colors": None,
            "netclass_assignments": None,
            "netclass_patterns": [
                {"netclass": "POWER", "pattern": "VBUS"},
                {"netclass": "POWER", "pattern": "+3V3"},
            ],
        },
        "meta": {"filename": "board.kicad_pro", "version": 1},
        "pcbnew": {"last_paths": {}, "page_layout_descr_file": ""},
    }
    return json.dumps(doc, indent=2) + "\n"


def _self_check():
    """Assert every pad-net in COMPONENTS matches the netlist contract (defensive)."""
    expected = {
        "J1": {"1": "VBUS", "2": "GND", "3": "CC1", "4": "CC2"},
        "R1": {"1": "CC1", "2": "GND"},
        "R2": {"1": "CC2", "2": "GND"},
        "U1": {"1": "VBUS", "2": "GND", "3": "VBUS", "5": "+3V3"},
        "C1": {"1": "VBUS", "2": "GND"},
        "C2": {"1": "+3V3", "2": "GND"},
        "R3": {"1": "+3V3", "2": "LED_A"},
        "D1": {"1": "LED_A", "2": "GND"},
    }
    for ref, m in expected.items():
        assert COMPONENTS[ref][4] == m, f"pad-net mismatch on {ref}: {COMPONENTS[ref][4]} != {m}"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Generate the example-usb-c-3v3 reference KiCad PCB from its netlist.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Outputs:\n  " + BOARD_PATH + "\n  " + PROJECT_PATH,
    )
    ap.add_argument("--stdout", action="store_true",
                    help="print the board to stdout and write no files")
    args = ap.parse_args(argv)

    _self_check()
    board_text = emit_board()

    if args.stdout:
        sys.stdout.write(board_text)
        return 0

    os.makedirs(EXPORT_DIR, exist_ok=True)
    with open(BOARD_PATH, "w", encoding="utf-8") as f:
        f.write(board_text)
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(emit_project())
    print(f"wrote {BOARD_PATH}")
    print(f"wrote {PROJECT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
