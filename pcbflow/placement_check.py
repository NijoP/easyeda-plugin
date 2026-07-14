"""Placement gate — score a placement plan against the design intent, before routing.

Checks (emitting harmonized findings):
  - **decoupling proximity:** cap ≤ 2.0 mm from its IC = ok; 2.0–4.0 mm = WARN; > 4.0 mm = FAIL
    (dense boards shouldn't hard-block on a marginal placement). Distance is center-to-center
    (the plan carries ref centers). Ref: knowledge/design-standards.md (decap ≤ 2 mm).
  - **connectors on their assigned edge** (else the connector can't open out).
  - **courtyard spacing** (reuses pcbflow.geometry) and **keep-out intrusion**.
  - **HPWL** reported as an info metric (the trace-length objective the placer minimized).

Pure Python 3 standard library.
"""
import math

from . import geometry
from .findings import finding
from .placer import hpwl, net_refs

DECAP_OK_MM = 2.0
DECAP_WARN_MM = 4.0


def _dist(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def _bbox(p, size):
    sw, sh = size
    return [p["x"] - sw / 2, p["y"] - sh / 2, p["x"] + sw / 2, p["y"] + sh / 2]


def _on_edge(p, edge, w, h, tol):
    return {"left": p["x"] <= tol, "right": p["x"] >= w - tol,
            "top": p["y"] <= tol, "bottom": p["y"] >= h - tol}[edge]


def run(plan, intent, enet, min_gap_mm=0.15):    # 0.15 mm = the JLCPCB clearance floor (dfm.py)
    V = []

    for cap, ic in intent.decoupling().items():
        if cap not in plan or ic not in plan:
            continue
        d = _dist(plan[cap], plan[ic])
        if d > DECAP_WARN_MM:
            V.append(finding(detector="placement", rule_id="decoupling_too_far", category="placement",
                             severity="error", confidence="deterministic", evidence_source="geometry",
                             summary=f"{cap} is {d:.1f} mm from {ic} (> {DECAP_WARN_MM} mm)",
                             where=cap, components=[cap, ic], provenance={"dist_mm": round(d, 2)},
                             recommendation="move the decoupling cap adjacent to the IC power pin"))
        elif d > DECAP_OK_MM:
            V.append(finding(detector="placement", rule_id="decoupling_far", category="placement",
                             severity="warning", confidence="deterministic", evidence_source="geometry",
                             summary=f"{cap} is {d:.1f} mm from {ic} (want ≤ {DECAP_OK_MM} mm)",
                             where=cap, components=[cap, ic], provenance={"dist_mm": round(d, 2)},
                             recommendation="tighten the decap-to-IC spacing if the layout allows"))

    w, h = intent.outline()
    tol = 2.0
    for ref, edge in intent.connectors().items():
        if ref in plan and not _on_edge(plan[ref], edge, w, h, tol):
            V.append(finding(detector="placement", rule_id="connector_off_edge", category="placement",
                             severity="error", confidence="deterministic", evidence_source="geometry",
                             summary=f"connector {ref} is not on its assigned '{edge}' edge",
                             where=ref, components=[ref],
                             recommendation=f"place {ref} against the {edge} board edge"))

    parts = [{"ref": r, "layer": plan[r]["layer"], "bbox": _bbox(plan[r], intent.size(r))} for r in plan]
    for v in geometry.spacing_audit(parts, min_gap=min_gap_mm):
        V.append(finding(detector="placement", rule_id="courtyard_overlap", category="placement",
                         severity="error", confidence="deterministic", evidence_source="geometry",
                         summary=f"courtyards overlap: {v['a']} & {v['b']} gap {v['gap']} mm",
                         where=f"{v['a']}<->{v['b']}", components=[v["a"], v["b"]],
                         recommendation="increase spacing"))

    for p in parts:                                          # keep-out intrusion (rect overlap)
        x0, y0, x1, y1 = p["bbox"]
        for k in intent.keepouts():
            if x0 < k["x"] + k["w"] and x1 > k["x"] and y0 < k["y"] + k["h"] and y1 > k["y"]:
                V.append(finding(detector="placement", rule_id="keepout_intrusion", category="placement",
                                 severity="error", confidence="deterministic", evidence_source="geometry",
                                 summary=f"{p['ref']} intrudes keep-out '{k.get('name','?')}'",
                                 where=p["ref"], components=[p["ref"]],
                                 recommendation="move the part out of the keep-out"))

    V.append(finding(detector="placement", rule_id="hpwl", category="placement", severity="info",
                     confidence="deterministic", evidence_source="geometry",
                     summary=f"total HPWL (trace-length proxy) = "
                             f"{hpwl({r: [plan[r]['x'], plan[r]['y']] for r in plan}, net_refs(enet)):.1f} mm",
                     where="<board>"))
    return V
