"""Tests for P1 — codified placement via visual mapping (intent, HPWL optimizer, SVG, gate).
Every check has a known-bad case that makes it fire. Standalone or pytest:
    python3 tests/test_placement.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow import findings, placement_check, placer, render_svg  # noqa: E402
from pcbflow.enet import Enet  # noqa: E402
from pcbflow.placement_intent import PlacementIntent  # noqa: E402


def _enet(comps):
    return Enet.from_dict({"version": "2.0.0", "components": {
        cid: {"props": {"Designator": des},
              "pinInfoMap": {p: {"number": p, "name": p, "net": n} for p, n in pins.items()}}
        for cid, (des, pins) in comps.items()}})


def _rules(fs):
    return {f["rule_id"] for f in fs}


# a small board: U1 talks to U2, U3; each has a decap; J1 is a left-edge connector
E = _enet({"u1": ("U1", {"1": "A", "2": "B", "3": "GND"}),
           "u2": ("U2", {"1": "A", "2": "GND"}),
           "u3": ("U3", {"1": "B", "2": "GND"}),
           "c1": ("C1", {"1": "A", "2": "GND"}),
           "j1": ("J1", {"1": "A", "2": "GND"})})
INTENT = PlacementIntent.from_dict({
    "board": {"outline_mm": [40, 25]}, "connectors": {"J1": "left"},
    "decoupling": {"C1": "U1"},
    "sizes_mm": {"U1": [3, 3], "U2": [3, 3], "U3": [3, 3], "C1": [1, 0.5], "J1": [3, 5]}})


# ── intent + optimizer ─────────────────────────────────────────────
def test_intent_accessors():
    assert INTENT.outline() == (40, 25)
    assert INTENT.connector_edge("J1") == "left"
    assert INTENT.decouples_ic("C1") == "U1"


def test_optimize_reduces_hpwl():
    plan, m = placer.optimize(E, INTENT)
    assert m["hpwl_final"] <= m["hpwl_initial"]              # optimization never worsens trace length
    assert set(plan) == {"U1", "U2", "U3", "C1", "J1"}


def test_decap_ends_up_near_its_ic():
    plan, _ = placer.optimize(E, INTENT)
    d = ((plan["C1"]["x"] - plan["U1"]["x"]) ** 2 + (plan["C1"]["y"] - plan["U1"]["y"]) ** 2) ** 0.5
    assert d < 4.0, d                                        # the decap snapped toward its IC
    assert "decoupling_too_far" not in _rules(placement_check.run(plan, INTENT, E))


def test_connector_slides_to_its_edge():
    plan, _ = placer.optimize(E, INTENT)
    assert plan["J1"]["x"] <= 2.0                            # J1 stayed on the left edge


# ── gate: known-bad per check ──────────────────────────────────────
def _plan(**pos):
    return {r: {"x": xy[0], "y": xy[1], "rot": 0, "layer": "TOP"} for r, xy in pos.items()}


def test_decoupling_too_far_fails():
    p = _plan(U1=(5, 5), C1=(15, 15))                        # ~14 mm apart
    assert "decoupling_too_far" in _rules(placement_check.run(p, INTENT, E))


def test_decoupling_far_warns():
    p = _plan(U1=(5, 5), C1=(8, 5))                          # 3 mm -> WARN band (2–4 mm)
    r = placement_check.run(p, INTENT, E)
    assert "decoupling_far" in _rules(r) and "decoupling_too_far" not in _rules(r)


def test_connector_off_edge_fails():
    p = _plan(J1=(20, 12), U1=(5, 5), C1=(6, 5))            # J1 in the middle, not left edge
    assert "connector_off_edge" in _rules(placement_check.run(p, INTENT, E))


def test_courtyard_overlap_fails():
    p = _plan(U1=(10, 10), U2=(10.5, 10), C1=(10.2, 10))    # 3x3 courtyards on top of each other
    assert "courtyard_overlap" in _rules(placement_check.run(p, INTENT, E))


def test_keepout_intrusion_fails():
    intent = PlacementIntent.from_dict({**INTENT.spec, "keepouts": [{"x": 8, "y": 8, "w": 4, "h": 4, "name": "mount"}]})
    p = _plan(U1=(9, 9), C1=(9.5, 9), J1=(1, 12))          # U1 sits in the keep-out
    assert "keepout_intrusion" in _rules(placement_check.run(p, intent, E))


# ── SVG render ─────────────────────────────────────────────────────
def test_render_svg_is_valid():
    plan, _ = placer.optimize(E, INTENT)
    svg = render_svg.render(plan, INTENT, E)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert "<rect" in svg and ">U1<" in svg                 # outline + a component label


def test_placement_findings_harmonized():
    p = _plan(U1=(5, 5), C1=(15, 15), J1=(1, 12))
    for f in placement_check.run(p, INTENT, E):
        assert findings.validate(f) == [] and f["detector"] == "placement"


def _run():
    for nm, fn in sorted(globals().items()):
        if nm.startswith("test_") and callable(fn):
            fn()
    print("PASS — placement: intent, HPWL optimize, decap-snap, connector-edge, decap far/too-far, "
          "courtyard overlap, keep-out, SVG render.")


if __name__ == "__main__":
    _run()
