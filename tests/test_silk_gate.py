"""Tests for G1 — silkscreen-over-pad check and the routing quality gate (folds DRC + silk +
rulebook). Standalone or pytest:  python3 tests/test_silk_gate.py"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow import gates, silk_check  # noqa: E402


def _board(ref_dx, ref_dy):
    """A footprint at (10,10) with a pad at its origin; the reference silk text is offset by
    (ref_dx, ref_dy). Offset (0,0) puts the text on the pad."""
    return (f'(kicad_pcb (version 1) (net 0 "") (net 1 "A")'
            f'  (footprint "R_0402" (at 10 10)'
            f'    (property "Reference" "R1")'
            f'    (pad "1" smd (at 0 0) (size 0.6 0.6) (net 1 "A"))'
            f'    (fp_text reference "R1" (at {ref_dx} {ref_dy}) (layer "F.SilkS"))))')


def _rules(fs):
    return {f["rule_id"] for f in fs}


def test_silk_over_pad_fires():
    assert "silk_over_pad" in _rules(silk_check.run(_board(0, 0)))       # text sits on the pad


def test_silk_clear_is_clean():
    assert silk_check.run(_board(0, 2)) == []                           # text 2 mm above the pad


def test_routing_gate_folds_silk_failure():
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "04_schematic"))
        with open(os.path.join(t, "04_schematic", "netlist.enet"), "w") as f:
            json.dump({"version": "2.0.0", "components": {
                "r": {"props": {"Designator": "R1"}, "pinInfoMap": {
                    "1": {"number": "1", "name": "1", "net": "A"}}}}}, f)
        with open(os.path.join(t, "board.kicad_pcb"), "w") as f:
            f.write(_board(0, 0))                                        # silk-over-pad board
        # a passing DRC runner isolates the silk failure; routing gate must still FAIL
        out = gates.compute_phase_gate(t, 11, drc_runner=lambda b: {"ok": True, "report": "r"})
        assert out.status == "FAIL", out.status
        assert "silk" in out.summary


def test_routing_gate_empty_without_board():
    with tempfile.TemporaryDirectory() as t:
        assert gates.compute_phase_gate(t, 11).status == "EMPTY"


def _run():
    for nm, fn in sorted(globals().items()):
        if nm.startswith("test_") and callable(fn):
            fn()
    print("PASS — G1: silk-over-pad fires/clears, routing gate folds silk failure, empty w/o board.")


if __name__ == "__main__":
    _run()
