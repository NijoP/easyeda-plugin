"""EasyEDA `.enet` v2.0.0 netlist — the tool-neutral netlist IR for PCB Flow.

`.enet` (github.com/easyeda/easyeda-pro-netlist-format) is EasyEDA Pro's official schematic
netlist: a versioned JSON file that carries connectivity **plus design intent** (net classes,
differential pairs, equal-length groups) **plus physical design rules** in one place. We adopt
it verbatim as our netlist interchange (roadmap Phase 1) so schematic capture, design
intelligence, and DRC all read one validated artifact instead of drifting parallel sources.

Structure:
    {version, components{id:{props, pinInfoMap{pin:{name,number,net,props}}}},
     designRule, differentialPair, netClass, equalLengthNetGroup}

This module parses/emits `.enet`, exposes engineering views (nets, BOM, floating pins,
net classes), a structural `verify()` gate, and `to_design_index_netlist()` — which feeds
`pcbflow.design_index` (pcbmunch), so a real EasyEDA export becomes queryable design
intelligence. Pure Python 3 standard library.

The authoritative conformance gate is upstream `enet-format-verify.mjs` (Node); `verify()`
here is the always-available structural pre-check. Use both.
"""
import json
from dataclasses import dataclass, field

VERSION = "2.0.0"


def _is_auto_net(net):
    """EasyEDA auto-generated (unnamed) nets look like '$1N2'; real nets are named (VCC)."""
    return bool(net) and net.startswith("$")


@dataclass
class Pin:
    number: str
    name: str
    net: str
    props: dict = field(default_factory=dict)


@dataclass
class Component:
    id: str
    props: dict = field(default_factory=dict)
    pins: dict = field(default_factory=dict)  # pin-number -> Pin

    # convenience accessors over the string-valued props bag
    def prop(self, key, default=""):
        return self.props.get(key, default)

    @property
    def designator(self):
        return self.prop("Designator")

    @property
    def value(self):
        return self.prop("Value")

    @property
    def device_name(self):
        return self.prop("DeviceName")

    @property
    def footprint_name(self):
        return self.prop("FootprintName")

    @property
    def in_bom(self):
        return self.prop("Add into BOM", "yes").lower() == "yes"

    @property
    def to_pcb(self):
        return self.prop("Convert to PCB", "yes").lower() == "yes"

    @property
    def lcsc(self):
        return self.prop("Supplier Part") if self.prop("Supplier").upper() == "LCSC" else self.prop("LCSC Part Name")

    @property
    def mfr_part(self):
        return self.prop("Manufacturer Part")


class Enet:
    def __init__(self, version=VERSION, components=None, design_rule=None,
                 differential_pair=None, net_class=None, equal_length=None):
        self.version = version
        self.components = components or {}      # id -> Component
        self.design_rule = design_rule or {}
        self.differential_pair = differential_pair or {}
        self.net_class = net_class or {}
        self.equal_length = equal_length or {}

    # ── parse / emit ────────────────────────────────────────────────
    @classmethod
    def from_dict(cls, d):
        comps = {}
        for cid, c in (d.get("components") or {}).items():
            pins = {}
            for pnum, p in (c.get("pinInfoMap") or {}).items():
                pins[pnum] = Pin(number=p.get("number", pnum), name=p.get("name", pnum),
                                 net=p.get("net", ""), props=p.get("props", {}) or {})
            comps[cid] = Component(id=cid, props=c.get("props", {}) or {}, pins=pins)
        return cls(version=d.get("version", VERSION), components=comps,
                   design_rule=d.get("designRule", {}) or {},
                   differential_pair=d.get("differentialPair", {}) or {},
                   net_class=d.get("netClass", {}) or {},
                   equal_length=d.get("equalLengthNetGroup", {}) or {})

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_dict(self):
        comps = {}
        for cid, c in self.components.items():
            comps[cid] = {
                "props": c.props,
                "pinInfoMap": {pn: {"name": p.name, "number": p.number, "net": p.net, "props": p.props}
                               for pn, p in c.pins.items()},
            }
        return {"version": self.version, "components": comps, "designRule": self.design_rule,
                "differentialPair": self.differential_pair, "netClass": self.net_class,
                "equalLengthNetGroup": self.equal_length}

    def dump(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    # ── engineering views ───────────────────────────────────────────
    def nets(self):
        """net name -> ['REF.pin(name)', ...] (design_index member format). Skips floating pins."""
        out = {}
        for c in self.components.values():
            ref = c.designator or c.id
            for p in c.pins.values():
                if not p.net:
                    continue
                out.setdefault(p.net, []).append(f"{ref}.{p.number}({p.name})")
        return {n: sorted(m) for n, m in out.items()}

    def comp_pin_nets(self):
        """designator -> {pin-number: net}."""
        return {(c.designator or c.id): {p.number: p.net for p in c.pins.values()}
                for c in self.components.values()}

    def floating_pins(self):
        """Pins with no net assigned — the ERC 'unconnected' set."""
        out = []
        for c in self.components.values():
            for p in c.pins.values():
                if not p.net:
                    out.append({"des": c.designator or c.id, "pin": p.number, "name": p.name})
        return out

    def unnamed_nets(self):
        return sorted(n for n in self.nets() if _is_auto_net(n))

    def net_class_map(self):
        """Flatten netClass -> {net: className} (netClass values may list their nets)."""
        out = {}
        for cls_name, spec in self.net_class.items():
            nets = spec.get("nets") if isinstance(spec, dict) else spec
            for n in (nets or []):
                out[n] = cls_name
        return out

    def bom(self):
        """Aggregate BOM by identical part (mfr/lcsc + value + footprint)."""
        rows = {}
        for c in self.components.values():
            if not c.in_bom:
                continue
            key = (c.mfr_part or c.lcsc or c.device_name, c.value, c.footprint_name)
            r = rows.setdefault(key, {"qty": 0, "refs": [], "value": c.value,
                                      "device": c.device_name, "footprint": c.footprint_name,
                                      "mfr_part": c.mfr_part, "lcsc": c.lcsc})
            r["qty"] += 1
            r["refs"].append(c.designator or c.id)
        for r in rows.values():
            r["refs"].sort()
        return sorted(rows.values(), key=lambda r: r["refs"][0] if r["refs"] else "")

    def stats(self):
        nets = self.nets()
        return {"version": self.version, "components": len(self.components),
                "nets": len(nets), "unnamed_nets": len(self.unnamed_nets()),
                "pins": sum(len(c.pins) for c in self.components.values()),
                "floating_pins": len(self.floating_pins()),
                "bom_lines": len(self.bom())}

    # ── bridges ─────────────────────────────────────────────────────
    def to_design_index_netlist(self):
        """Shape an .enet into the dict pcbflow.design_index.DesignIndex expects."""
        inventory = [{"des": c.designator or c.id,
                      "name": c.device_name or c.value,
                      "lcsc": c.lcsc} for c in self.components.values()]
        return {"nets": self.nets(), "components": self.comp_pin_nets(),
                "inventory": inventory, "unconnected": self.floating_pins()}

    def design_index(self, currents=None):
        """Build a queryable DesignIndex (pcbmunch core) from this netlist."""
        from .design_index import DesignIndex
        return DesignIndex(self.to_design_index_netlist(),
                           net_class=self.net_class_map(), currents=currents)

    # ── validation (structural pre-check; not a substitute for enet-format-verify.mjs) ──
    def verify(self):
        """Return a list of structural issues (empty = structurally clean)."""
        issues = []
        if self.version != VERSION:
            issues.append(f"version is {self.version!r}, expected {VERSION!r}")
        seen = {}
        for cid, c in self.components.items():
            if not c.props:
                issues.append(f"component {cid}: missing props")
            if not c.pins:
                issues.append(f"component {cid}: no pins (pinInfoMap empty)")
            des = c.designator
            if not des:
                issues.append(f"component {cid}: missing Designator")
            elif des in seen:
                issues.append(f"duplicate designator {des} ({seen[des]} and {cid})")
            else:
                seen[des] = cid
            for pn, p in c.pins.items():
                if "net" not in (self.components[cid].pins[pn].__dict__):
                    issues.append(f"{des or cid}.{pn}: pin has no 'net' field")
        return issues


def main(argv):
    import sys
    if not argv:
        print("usage: python3 -m pcbflow.enet <file.enet>", file=sys.stderr)
        return 2
    net = Enet.load(argv[0])
    issues = net.verify()
    print(json.dumps({"stats": net.stats(), "verify_issues": issues}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
