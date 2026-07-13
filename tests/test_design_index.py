import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow.design_index import DesignIndex

NETLIST = {
    "nets": {
        "VSYS": ["U1.1(VDD)", "C1.1(P)", "R1.1(A)"],
        "GND":  ["U1.2(GND)", "C1.2(N)", "R1.2(B)"],
        "SDA":  ["U1.3(SDA)"],          # single-pin net
        "3V3":  ["U2.1(VDD)"],          # U2 on a power net with NO cap
    },
    "components": {
        "U1": {"1": "VSYS", "2": "GND", "3": "SDA"},
        "C1": {"1": "VSYS", "2": "GND"},
        "R1": {"1": "VSYS", "2": "GND"},
        "U2": {"1": "3V3"},
    },
    "inventory": [{"des": "U1", "name": "MCU", "lcsc": "C100"}, {"des": "C1", "name": "100n"},
                  {"des": "R1", "name": "10k"}, {"des": "U2", "name": "IC2"}],
    "unconnected": [{"des": "U2", "pin": "2", "name": "NC"}],
}
RULES = {"VSYS": "POWER_HC", "GND": "GND_PLANE", "SDA": "SIGNAL"}   # 3V3 unclassed
CUR = {"VSYS": 10}


def test_queries():
    ix = DesignIndex(NETLIST, RULES, CUR)
    n = ix.net("VSYS")
    assert n["class"] == "POWER_HC" and n["npins"] == 3
    assert n["components"] == ["C1", "R1", "U1"]
    assert n["method"] == "plane/pour" and n["width_mm"] > 5     # 10 A
    c = ix.component("U1")
    assert set(c["nets"]) == {"VSYS", "GND", "SDA"} and c["neighbors"] == ["C1", "R1"]
    assert ix.decaps_of("U1") == ["C1"]
    assert any(r["net"] == "VSYS" for r in ix.power_rails())


def test_blast_radius():
    ix = DesignIndex(NETLIST, RULES, CUR)
    br = ix.net_blast_radius("VSYS")
    assert br["components"] == ["C1", "R1", "U1"] and "GND" in br["also_touches_nets"]
    cb = ix.component_blast_radius("U1")
    assert set(cb["nets"]) == {"VSYS", "GND", "SDA"} and cb["adjacent_components"] == ["C1", "R1"]


def test_health():
    h = DesignIndex(NETLIST, RULES, CUR).health()
    assert "SDA" in h["single_pin_nets"] and "3V3" in h["single_pin_nets"]
    assert h["unconnected_pins"] == 1
    assert h["unclassed_nets"] == ["3V3"]
    assert h["nets_needing_plane"] == ["VSYS"]
    assert "U2 on 3V3" in h["ic_power_nets_without_a_cap"]
    assert h["ok"] is False


if __name__ == "__main__":
    test_queries(); test_blast_radius(); test_health()
    print("PASS — design_index: net/component queries, blast radius, power rails, health.")
