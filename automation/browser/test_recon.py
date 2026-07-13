#!/usr/bin/env python3
"""Test the board-agnostic netlist reconstructor (pure geometry, no live board).
Run: python3 automation/browser/test_recon.py"""
import recon


def test_reconstruct():
    comps = [
        {"des": "R1", "name": "10k",
         "pins": [{"num": "1", "name": "A", "x": 10, "y": 10},
                  {"num": "2", "name": "B", "x": 20, "y": 10}]},
        {"des": "U1", "name": "IC",
         "pins": [{"num": "1", "name": "VCC", "x": 30, "y": 10}]},
    ]
    # a wire on net VCC with vertices at (10,10) and (30,10) touches R1.1 and U1.1
    wires = [{"net": "VCC", "line": [10, 10, 30, 10]}]
    r = recon.reconstruct(comps, wires)

    assert r["counts"]["nets"] == 1
    assert "R1.1(A)" in r["nets"]["VCC"] and "U1.1(VCC)" in r["nets"]["VCC"]
    assert r["counts"]["connected_pins"] == 2
    assert r["counts"]["unconnected_pins"] == 1                     # R1.2 sits between vertices
    assert r["unconnected"][0]["des"] == "R1" and r["unconnected"][0]["pin"] == "2"
    assert r["components"]["U1"]["1"] == "VCC"

    # a suspicious merge: two nets meeting at one pin coordinate -> flagged *MULTI
    r2 = recon.reconstruct(
        [{"des": "R9", "pins": [{"num": "1", "name": "P", "x": 5, "y": 5}]}],
        [{"net": "A", "line": [5, 5, 9, 5]}, {"net": "B", "line": [5, 5, 5, 9]}])
    assert r2["components"]["R9"]["1"].endswith("*MULTI")


if __name__ == "__main__":
    test_reconstruct()
    print("PASS — recon: pin->net coordinate matching, unconnected + *MULTI detection.")
