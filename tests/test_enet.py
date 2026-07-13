"""Tests for pcbflow.enet — the .enet v2.0.0 netlist IR. Standalone or pytest:
    python3 tests/test_enet.py
Fixture mirrors the official lite example (github.com/easyeda/easyeda-pro-netlist-format)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow.enet import Enet  # noqa: E402


def _pin(num, net):
    return {"name": num, "number": num, "net": net, "props": {"Pin Number": num}}


LITE = {
    "version": "2.0.0",
    "components": {
        "gge1": {"props": {"Unique ID": "gge1", "Designator": "R1", "Value": "10K",
                           "DeviceName": "Res_0603", "FootprintName": "R0603",
                           "Add into BOM": "yes", "Convert to PCB": "yes",
                           "Supplier": "LCSC", "Supplier Part": "C1234"},
                 "pinInfoMap": {"1": _pin("1", "$1N2"), "2": _pin("2", "VCC")}},
        "gge2": {"props": {"Unique ID": "gge2", "Designator": "C1", "Value": "10uF",
                           "DeviceName": "C_0603", "FootprintName": "C0603", "Add into BOM": "yes"},
                 "pinInfoMap": {"1": _pin("1", "VCC"), "2": _pin("2", "GND")}},
        "gge3": {"props": {"Unique ID": "gge3", "Designator": "L1", "Value": "10uH",
                           "DeviceName": "L_0603", "FootprintName": "L0603", "Add into BOM": "yes"},
                 "pinInfoMap": {"1": _pin("1", "VCC"), "2": _pin("2", "")}},  # pin2 floating
    },
    "designRule": {"track": {"minWidth": 0.15}},
    "differentialPair": {},
    "netClass": {"POWER": {"nets": ["VCC"]}},
    "equalLengthNetGroup": {},
}


def test_parse_and_props():
    e = Enet.from_dict(LITE)
    assert e.version == "2.0.0" and len(e.components) == 3
    r1 = e.components["gge1"]
    assert r1.designator == "R1" and r1.value == "10K" and r1.in_bom and r1.lcsc == "C1234"
    assert set(r1.pins) == {"1", "2"} and r1.pins["2"].net == "VCC"


def test_views():
    e = Enet.from_dict(LITE)
    nets = e.nets()
    assert nets["VCC"] == ["C1.1(1)", "L1.1(1)", "R1.2(2)"], nets["VCC"]
    assert nets["GND"] == ["C1.2(2)"]
    assert e.unnamed_nets() == ["$1N2"]                       # auto net detected
    assert e.floating_pins() == [{"des": "L1", "pin": "2", "name": "2"}]
    assert e.comp_pin_nets()["R1"] == {"1": "$1N2", "2": "VCC"}
    assert e.net_class_map() == {"VCC": "POWER"}


def test_stats_and_bom():
    e = Enet.from_dict(LITE)
    s = e.stats()
    assert s["components"] == 3 and s["nets"] == 3 and s["unnamed_nets"] == 1
    assert s["floating_pins"] == 1 and s["pins"] == 6
    bom = e.bom()
    assert len(bom) == 3 and all(r["qty"] == 1 for r in bom)


def test_roundtrip():
    e = Enet.from_dict(LITE)
    assert Enet.from_dict(e.to_dict()).to_dict() == e.to_dict()   # stable round-trip
    assert e.to_dict()["version"] == "2.0.0"


def test_verify_clean_and_dirty():
    assert Enet.from_dict(LITE).verify() == []                    # structurally clean
    bad = {"version": "1.0", "components": {
        "x": {"props": {"Designator": "R1"}, "pinInfoMap": {"1": _pin("1", "A")}},
        "y": {"props": {"Designator": "R1"}, "pinInfoMap": {}},   # dup ref + no pins
    }}
    issues = Enet.from_dict(bad).verify()
    assert any("version" in i for i in issues)
    assert any("duplicate designator R1" in i for i in issues)
    assert any("no pins" in i for i in issues)


def test_design_index_bridge():
    """A real .enet becomes queryable pcbmunch intelligence."""
    ix = Enet.from_dict(LITE).design_index(currents={"VCC": 3.0})
    assert ix.summary()["components"] == 3
    vcc = ix.net("VCC")
    assert vcc["class"] == "POWER" and vcc["npins"] == 3
    assert set(vcc["components"]) == {"R1", "C1", "L1"}
    assert vcc["i_peak_a"] == 3.0 and vcc["width_mm"] > 0          # IPC width flows through
    assert ix.component("C1")["nets"] == ["GND", "VCC"]


def _run():
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("PASS — enet: parse, views, stats/bom, round-trip, verify, design_index bridge.")


if __name__ == "__main__":
    _run()
