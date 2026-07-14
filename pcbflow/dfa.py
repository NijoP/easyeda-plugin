"""Design-for-assembly / test (HW10) — fiducials, test points, tombstoning risk.

Advisory (heuristic) checks that catch the assembly/bring-up omissions a geometry DRC can't see:
  - **fiducials:** SMT assembly wants ≥2 global fiducials for optical alignment;
  - **test points:** power + key nets should be probeable for bring-up / ICT;
  - **tombstoning risk:** a 2-pad passive with very asymmetric copper connectivity (one pad on a
    plane-like net, the other on a sparse net) reflows unevenly and can lift.

Emits `info`-severity findings (advisory — never blocks). Pure Python 3 standard library.
"""
from .findings import finding


def _f(rule_id, summary, where, comps=None, rec=""):
    return finding(detector="dfa", rule_id=rule_id, category="manufacturability", severity="info",
                   confidence="heuristic", evidence_source="heuristic_rule", summary=summary,
                   where=where, components=comps, recommendation=rec)


def run(enet, parts):
    refs = [c.designator or c.id for c in enet.components.values()]
    nets = enet.nets()
    V = []
    if sum(1 for r in refs if r.upper().startswith(("FID", "FD"))) < 2:
        V.append(_f("fiducials", "fewer than 2 fiducials — SMT assembly wants ≥2 global fiducials",
                    "<board>", rec="add 2–3 fiducials near the board corners"))
    if not any(r.upper().startswith("TP") for r in refs):
        V.append(_f("no_test_points", "no test points — add them on power + key nets for bring-up/ICT",
                    "<board>", rec="place test points on the rails and critical signals"))
    for c in enet.components.values():
        des = c.designator or c.id
        if parts.role(des) not in ("cap", "resistor"):
            continue
        pnets = [p.net for p in c.pins.values() if p.net]
        if len(pnets) != 2:
            continue
        sizes = sorted(len(nets.get(n, [])) for n in pnets)
        if sizes[0] <= 2 and sizes[1] >= 8:
            V.append(_f("tombstoning_risk",
                        f"{des}: asymmetric pad connectivity ({sizes[0]} vs {sizes[1]} pins) — "
                        "tombstoning risk", des, [des], "balance thermal relief on the two pads"))
    return V
