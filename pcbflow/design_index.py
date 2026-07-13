"""PCB design index — a queryable knowledge model of a board's connectivity.

This is the 'pcbmunch' intelligence core: index a board once, then answer grounded
questions (net/component lookups, blast radius, power rails, health) so an AI produces
better PCB-design output instead of guessing. Pure Python; fully testable.

Input = a reconstructed netlist (automation/browser/recon.py output):
    {"nets": {net: ["REF.pin(name)", ...]},
     "components": {ref: {pin: net}},
     "inventory": [{"des","name","lcsc"}],
     "unconnected": [{"des","pin","name"}]}
Optional: a net-class map {net: class}, and per-net peak currents {net: amps}.
"""
import re

from . import ipc

_POWER = re.compile(r"^(VBUS|VSYS|VBAT|BAT\+|B\+|VDD.*|VCC.*|\+?\d+V\d*|\+?5V)$", re.I)
_GND = re.compile(r"^(GND|GNDA|AGND|DGND|PGND)$", re.I)


def _ref_of(member):
    """'U1.1(VDD)' -> 'U1'."""
    return member.split(".", 1)[0]


class DesignIndex:
    def __init__(self, netlist, net_class=None, currents=None):
        self.raw = netlist
        self.net_class = dict(net_class or {})
        self.currents = dict(currents or {})

        self._nets = {}
        for net, members in netlist.get("nets", {}).items():
            refs = sorted({_ref_of(m) for m in members})
            self._nets[net] = {"members": list(members), "npins": len(members), "components": refs}

        inv = {c["des"]: c for c in netlist.get("inventory", [])}
        self._comps = {}
        for ref, pins in netlist.get("components", {}).items():
            info = inv.get(ref, {})
            self._comps[ref] = {"name": info.get("name"), "lcsc": info.get("lcsc"),
                                "pins": pins, "nets": sorted(set(pins.values()))}

    # --- summary ---
    def summary(self):
        return {"components": len(self._comps), "nets": len(self._nets),
                "classed_nets": len(self.net_class),
                "unconnected_pins": len(self.raw.get("unconnected", []))}

    # --- queries ---
    def net(self, name):
        if name not in self._nets:
            return None
        n = self._nets[name]
        out = {"net": name, "class": self.net_class.get(name), "npins": n["npins"],
               "components": n["components"], "members": n["members"]}
        cur = self.currents.get(name)
        if cur is not None:
            r = ipc.recommend(cur)
            out.update(i_peak_a=cur, width_mm=r["width_mm"], method=r["method"])
        return out

    def component(self, ref):
        if ref not in self._comps:
            return None
        c = self._comps[ref]
        neighbors = sorted({r for net in c["nets"]
                            for r in self._nets.get(net, {}).get("components", []) if r != ref})
        return {"ref": ref, "name": c["name"], "lcsc": c["lcsc"],
                "pins": c["pins"], "nets": c["nets"], "neighbors": neighbors}

    def search_nets(self, pattern):
        rx = re.compile(pattern, re.I)
        return [{"net": nm, "class": self.net_class.get(nm), "npins": self._nets[nm]["npins"]}
                for nm in sorted(self._nets) if rx.search(nm)]

    def power_rails(self):
        rails = []
        for nm, n in self._nets.items():
            cls = self.net_class.get(nm) or ""
            if _POWER.match(nm) or _GND.match(nm) or "POWER" in cls or "GND" in cls:
                rails.append({"net": nm, "class": self.net_class.get(nm), "consumers": len(n["components"])})
        return sorted(rails, key=lambda r: -r["consumers"])

    def decaps_of(self, ref):
        """Capacitors sharing a power net with this IC (likely decoupling)."""
        if ref not in self._comps:
            return []
        caps = []
        for net in self._comps[ref]["nets"]:
            if not _POWER.match(net):
                continue
            for r in self._nets.get(net, {}).get("components", []):
                if r != ref and r.upper().startswith("C") and r not in caps:
                    caps.append(r)
        return sorted(caps)

    # --- impact analysis (blast radius) ---
    def net_blast_radius(self, name):
        if name not in self._nets:
            return None
        comps = self._nets[name]["components"]
        touched = sorted({net for r in comps
                          for net in self._comps.get(r, {}).get("nets", []) if net != name})
        return {"net": name, "components": comps, "also_touches_nets": touched,
                "impact": f"{len(comps)} components, {len(touched)} adjacent nets"}

    def component_blast_radius(self, ref):
        if ref not in self._comps:
            return None
        nets = self._comps[ref]["nets"]
        comps = sorted({r for net in nets
                        for r in self._nets.get(net, {}).get("components", []) if r != ref})
        return {"ref": ref, "nets": nets, "adjacent_components": comps,
                "impact": f"touches {len(nets)} nets and {len(comps)} other components"}

    # --- health radar ---
    def health(self):
        single = sorted(nm for nm, n in self._nets.items() if n["npins"] < 2)
        issues = {"single_pin_nets": single,
                  "unconnected_pins": len(self.raw.get("unconnected", []))}
        if self.net_class:
            issues["unclassed_nets"] = sorted(nm for nm in self._nets if nm not in self.net_class)
        if self.currents:
            issues["nets_needing_plane"] = sorted(nm for nm, a in self.currents.items()
                                                  if ipc.needs_plane(a))
        missing = []
        for ref, c in self._comps.items():
            if not ref.upper().startswith("U"):
                continue
            for net in c["nets"]:
                if _POWER.match(net) and not any(
                        r.upper().startswith("C") for r in self._nets[net]["components"]):
                    missing.append(f"{ref} on {net}")
        issues["ic_power_nets_without_a_cap"] = sorted(set(missing))
        issues["ok"] = not (single or issues["unconnected_pins"] or missing
                            or issues.get("unclassed_nets"))
        return issues
