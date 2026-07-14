"""Tests for Tier-3 (creepage, DFA, BOM audit) and Tier-4 (feasibility) hardware checks.
Standalone or pytest:  python3 tests/test_hw_t3_t4.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow import bom_audit, creepage, dfa, feasibility_check  # noqa: E402
from pcbflow.enet import Enet  # noqa: E402
from pcbflow.parts import Parts  # noqa: E402


def _enet(comps):
    return Enet.from_dict({"version": "2.0.0", "components": {
        cid: {"props": {"Designator": des, **props},
              "pinInfoMap": {p: {"number": p, "name": p, "net": n} for p, n in pins.items()}}
        for cid, (des, pins, props) in comps.items()}})


def _rules(fs):
    return {f["rule_id"] for f in fs}


# ── creepage (HW12) ────────────────────────────────────────────────
def test_creepage_table_and_check():
    assert creepage.required_spacing_mm(5) == 0.13
    assert creepage.required_spacing_mm(120) == 0.40
    assert creepage.required_spacing_mm(600) > 0.80          # linear above 500 V
    # a 400 V rail needs 0.40 mm > 0.15 mm board clearance -> error
    rails = {"HV": {"voltage": 400.0}}
    assert "insufficient_creepage" in _rules(creepage.run(_enet({}), rails, min_clearance_mm=0.15))
    # a 5 V rail is fine
    assert creepage.run(_enet({}), {"V5": {"voltage": 5.0}}, 0.15) == []


# ── DFA (HW10) ─────────────────────────────────────────────────────
def test_dfa_fiducials_and_test_points():
    e = _enet({"r": ("R1", {"1": "A", "2": "GND"}, {})})
    p = Parts.from_dict({})
    rules = _rules(dfa.run(e, p))
    assert "fiducials" in rules and "no_test_points" in rules


def test_dfa_tombstoning_risk():
    # a cap between a busy GND net (>=8 pins) and a sparse net -> tombstoning risk
    comps = {"c": ("C1", {"1": "SIG", "2": "GND"}, {})}
    for i in range(8):
        comps[f"u{i}"] = (f"U{i}", {"1": "GND"}, {})
    e = _enet(comps)
    p = Parts.from_dict({"C1": {"role": "cap"}})
    assert "tombstoning_risk" in _rules(dfa.run(e, p))


# ── BOM audit (HW11) ───────────────────────────────────────────────
def test_bom_audit_missing_and_present_mpn():
    e = _enet({"r": ("R1", {"1": "A", "2": "GND"}, {})})
    assert "missing_mpn" in _rules(bom_audit.run(e, Parts.from_dict({})))
    assert bom_audit.run(e, Parts.from_dict({"R1": {"mpn": "0402WGF1001TCE"}})) == []


# ── feasibility (HW13) ─────────────────────────────────────────────
def test_feasibility_budgets():
    fs = feasibility_check.run(
        {"power_budget_w": 1.0, "size_mm": [40, 30], "layers": 2, "cost_target": 5.0, "max_components": 20},
        {"power_w": 1.5, "size_mm": [45, 30], "layers": 4, "cost": 7.0, "components": 25})
    assert _rules(fs) == {"power_over_budget", "size_over_budget", "layers_over_budget",
                          "cost_over_budget", "component_count_over"}
    assert feasibility_check.run({"power_budget_w": 2.0}, {"power_w": 1.0}) == []


def _run():
    for nm, fn in sorted(globals().items()):
        if nm.startswith("test_") and callable(fn):
            fn()
    print("PASS — hw T3/T4: creepage table + check, DFA fiducials/test-points/tombstoning, "
          "BOM MPN audit, feasibility budgets.")


if __name__ == "__main__":
    _run()
