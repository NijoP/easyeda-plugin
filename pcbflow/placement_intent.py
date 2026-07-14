"""Placement intent — the design-intent a placement must honor (so the placer optimizes against
real constraints and the gate scores against them, not ad-hoc judgement).

Optional sidecar `placement_intent.json` beside the netlist:

    {
      "board":     {"outline_mm": [40.0, 22.0]},          # rectangle (0,0)..(w,h)
      "connectors": {"J1": "left", "J2": "bottom"},        # ref -> edge: left|right|top|bottom
      "clusters":   {"power": ["U1", "C1", "C2"]},          # functional groups to keep together
      "keepouts":   [{"x": 5, "y": 5, "w": 4, "h": 4, "name": "mount"}],
      "decoupling": {"C1": "U1", "C2": "U1"},               # cap ref -> the IC it decouples
      "sizes_mm":   {"U1": [3.0, 3.0], "C1": [1.0, 0.5]}    # component courtyard sizes
    }

Pure Python 3 standard library.
"""
import json
from pathlib import Path

EDGES = ("left", "right", "top", "bottom")
DEFAULT_SIZE = (1.0, 1.0)


class PlacementIntent:
    def __init__(self, spec=None):
        self.spec = spec or {}

    @classmethod
    def from_dict(cls, d):
        return cls(dict(d or {}))

    @classmethod
    def load(cls, path):
        p = Path(path)
        return cls.from_dict(json.loads(p.read_text(encoding="utf-8"))) if p.exists() else cls()

    @classmethod
    def beside(cls, netlist_path):
        return cls.load(Path(netlist_path).parent / "placement_intent.json")

    def outline(self):
        return tuple((self.spec.get("board") or {}).get("outline_mm", [40.0, 25.0]))

    def connectors(self):
        return {r: e for r, e in (self.spec.get("connectors") or {}).items() if e in EDGES}

    def connector_edge(self, ref):
        return self.connectors().get(ref)

    def clusters(self):
        return self.spec.get("clusters") or {}

    def cluster_of(self, ref):
        for name, members in self.clusters().items():
            if ref in members:
                return name
        return None

    def keepouts(self):
        return self.spec.get("keepouts") or []

    def decoupling(self):
        return self.spec.get("decoupling") or {}

    def decouples_ic(self, cap_ref):
        return self.decoupling().get(cap_ref)

    def size(self, ref):
        return tuple((self.spec.get("sizes_mm") or {}).get(ref, DEFAULT_SIZE))

    def has(self):
        return bool(self.spec)
