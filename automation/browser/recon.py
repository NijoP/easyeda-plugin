#!/usr/bin/env python3
"""
Netlist reconstructor — rebuild pin->net from a live EasyEDA schematic dump.

The EDA tool's own netlist API hangs headless, so PCB Flow rebuilds connectivity
from geometry: wires carry a `.net`, pins do NOT — so we match each pin to the wire
vertex at its (x, y). Board-agnostic. Pure Python 3 standard library.

Pipeline:
    python3 cdp.py eval ../easyeda/dump_schematic.js > dump.json   # capture the live board
    python3 recon.py dump.json netlist.json                        # rebuild the netlist
Then diff `netlist.json` against your net_connection.md (the phase-5 audit).

Input dump shape (from dump_schematic.js):
    {"components": [{"des","name","lcsc","pins":[{"num","name","x","y"}]}],
     "wires":      [{"net","line":[x1,y1,x2,y2,...]}]}
"""
import json, sys, collections


def reconstruct(components, wires):
    """Return the reconstructed netlist. Pure function — easy to test."""
    vtx = collections.defaultdict(set)                       # (x,y) -> {net}
    for w in wires:
        net = w.get("net")
        if not net:
            continue
        ln = w.get("line") or []
        for i in range(0, len(ln) - 1, 2):
            vtx[(round(ln[i]), round(ln[i + 1]))].add(net)

    nets = collections.defaultdict(list)                     # net -> ["DES.pin(name)"]
    comp_pins = {}                                           # des -> {pin: net}
    unconnected = []
    for c in components:
        des = c.get("des")
        if not des:
            continue
        comp_pins[des] = {}
        for p in c.get("pins", []):
            if "num" not in p:
                continue
            ns = vtx.get((round(p["x"]), round(p["y"])))
            label = f"{des}.{p['num']}({p.get('name')})"
            if ns and len(ns) == 1:
                net = next(iter(ns))
                nets[net].append(label); comp_pins[des][p["num"]] = net
            elif ns:                                          # >1 net at one point = suspect merge
                net = sorted(ns)[0]
                nets[net].append(label + "*MULTI"); comp_pins[des][p["num"]] = net + "*MULTI"
            else:
                unconnected.append({"des": des, "pin": p["num"], "name": p.get("name")})

    return {
        "counts": {"components": sum(1 for c in components if c.get("des")),
                   "wires": len(wires), "nets": len(nets),
                   "connected_pins": sum(len(x) for x in nets.values()),
                   "unconnected_pins": len(unconnected)},
        "nets": {k: sorted(v) for k, v in sorted(nets.items())},
        "components": comp_pins,
        "unconnected": unconnected,
        "inventory": [{"des": c.get("des"), "name": c.get("name"), "lcsc": c.get("lcsc")}
                      for c in components if c.get("des")],
    }


def _main():
    if len(sys.argv) < 2:
        print(__doc__); return
    dump = json.load(open(sys.argv[1]))
    v = dump.get("v", dump)                                   # tolerate the CDP {ok,v} envelope
    result = reconstruct(v["components"], v["wires"])
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if out:
        json.dump(result, open(out, "w"), indent=1)
    c = result["counts"]
    print(f"nets: {c['nets']}  connected: {c['connected_pins']}  "
          f"unconnected: {c['unconnected_pins']}" + (f"  -> {out}" if out else ""))


if __name__ == "__main__":
    _main()
