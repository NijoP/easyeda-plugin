"""BOM audit (HW11) — buildability / sourcing.

A geometry-clean board is still unbuildable if parts can't be ordered. This checks each BOM line
for an orderable part number (manufacturer part or LCSC, from the netlist or the parts spec) and
flags what's missing. Duplicate designators are already caught by `enet.verify()`.

Pure Python 3 standard library.
"""
from .findings import finding


def _f(rule_id, severity, summary, where, comps=None, rec=""):
    return finding(detector="bom_audit", rule_id=rule_id, category="sourcing", severity=severity,
                   confidence="deterministic", evidence_source="bom", summary=summary,
                   where=where, components=comps, recommendation=rec)


def run(enet, parts=None):
    V = []
    spec = getattr(parts, "spec", {}) if parts else {}
    for c in enet.components.values():
        des = c.designator or c.id
        if not c.in_bom:
            continue
        mpn = c.mfr_part or c.lcsc or (spec.get(des, {}) or {}).get("mpn")
        if not mpn:
            V.append(_f("missing_mpn", "warning",
                        f"{des}: no manufacturer/LCSC part number (not orderable)",
                        des, [des], "add an MPN or mark the part DNP"))
    return V
