"""Tests for the Tier-2 hardware checks — signal integrity (impedance + length match), power
distribution (IR drop + via ampacity), and thermal. Verifies both the physics functions and the
detectors. Standalone or pytest:  python3 tests/test_hw_t2.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow import findings, hw, pdn, si, thermal  # noqa: E402
from pcbflow.enet import Enet  # noqa: E402
from pcbflow.parts import Parts  # noqa: E402
from pcbflow.stackup import Stackup  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _enet(d):
    base = {"version": "2.0.0", "components": {
        "u": {"props": {"Designator": "U1"}, "pinInfoMap": {"1": {"number": "1", "name": "1", "net": "X"}}}}}
    base.update(d)
    return Enet.from_dict(base)


def _rules(fs):
    return {f["rule_id"] for f in fs}


# ── physics functions ──────────────────────────────────────────────
def test_microstrip_impedance_plausible():
    z = si.microstrip_z0(w_mm=0.30, h_mm=0.20, t_mm=0.035, er=4.3)
    assert 40 < z < 70                                   # ~50 Ω ballpark for FR-4
    assert si.microstrip_z0(0.30, 0.0, 0.035, 4.3) is None   # invalid geometry


def test_trace_resistance_and_via_current():
    r = pdn.trace_resistance(length_mm=25, width_mm=0.4, thickness_mm=0.035)
    assert 0.02 < r < 0.05                               # ~31 mΩ
    iv = pdn.via_current(drill_mm=0.3)
    assert 1.0 < iv < 3.0                                # ~1.8 A per 0.3 mm via at ΔT=10 °C


# ── SI detectors ───────────────────────────────────────────────────
def test_diffpair_skew_flagged():
    e = _enet({"differentialPair": {"USB": {"nets": ["DP", "DN"], "skew_mm": 0.1}}})
    geo = {"tracks": [{"net": "DP", "width": 0.2, "layer": "F.Cu", "length": 10.0},
                      {"net": "DN", "width": 0.2, "layer": "F.Cu", "length": 10.6}], "vias": []}
    assert "diffpair_skew" in _rules(si.run(e, geo, Stackup.two_layer()))


def test_equal_length_flagged():
    e = _enet({"equalLengthNetGroup": {"ADDR": {"nets": ["A0", "A1"], "tol_mm": 0.3}}})
    geo = {"tracks": [{"net": "A0", "width": 0.2, "layer": "F.Cu", "length": 8.0},
                      {"net": "A1", "width": 0.2, "layer": "F.Cu", "length": 9.0}], "vias": []}
    assert "equal_length_violation" in _rules(si.run(e, geo, Stackup.two_layer()))


# ── PDN detectors ──────────────────────────────────────────────────
def test_ir_drop_flagged():
    geo = {"tracks": [{"net": "V1", "width": 0.15, "layer": "F.Cu", "length": 80.0}], "vias": []}
    rails = {"V1": {"voltage": 1.0, "i_load": 3.0}}      # 3 A through a thin long trace
    assert "ir_drop" in _rules(pdn.run(_enet({}), geo, Stackup.two_layer(), rails))


def test_via_ampacity_flagged():
    geo = {"tracks": [{"net": "PWR", "width": 2.0, "layer": "F.Cu", "length": 5.0}],
           "vias": [{"net": "PWR", "drill": 0.3, "x": 0, "y": 0, "size": 0.6}]}
    rails = {"PWR": {"voltage": 5.0, "i_load": 5.0}}      # 5 A through one 0.3 mm via (~1.8 A cap)
    assert "via_ampacity" in _rules(pdn.run(_enet({}), geo, Stackup.two_layer(), rails))


# ── thermal ────────────────────────────────────────────────────────
def test_thermal_overtemp():
    e = _enet({"components": {
        "j": {"props": {"Designator": "J1"}, "pinInfoMap": {"1": {"number": "1", "name": "1", "net": "VIN"}}},
        "u": {"props": {"Designator": "U1"},
              "pinInfoMap": {"1": {"number": "1", "name": "1", "net": "VIN"},
                             "2": {"number": "2", "name": "2", "net": "VOUT"}}}}})
    p = Parts.from_dict({"J1": {"pins": {"1": "pwr_out"}, "ratings": {"v_nominal": 12.0}},
                        "U1": {"role": "ldo", "pins": {"1": "pwr_in", "2": "pwr_out"},
                               "ratings": {"vout": 3.3, "iout": 0.5, "theta_ja": 250, "tj_max": 125}}})
    _, rails = __import__("pcbflow.power_tree", fromlist=["run"]).run(e, p)
    assert "thermal_overtemp" in _rules(thermal.run(e, p, rails))


def test_example_board_hw_with_geometry_is_clean():
    net = os.path.join(REPO, "projects", "example-usb-c-3v3", "04_schematic", "netlist.enet")
    board = os.path.join(REPO, "projects", "example-usb-c-3v3", "10_kicad_export", "board.kicad_pcb")
    if os.path.exists(net) and os.path.exists(board):
        fs = hw.run(net, board=board)
        assert findings.report(fs)["pass"], [f["summary"] for f in fs]


def _run():
    for nm, fn in sorted(globals().items()):
        if nm.startswith("test_") and callable(fn):
            fn()
    print("PASS — hw T2: microstrip Z0, trace R, via current, diff-pair skew, equal-length, "
          "IR drop, via ampacity, thermal, clean example board.")


if __name__ == "__main__":
    _run()
