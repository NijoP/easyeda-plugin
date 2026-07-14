"""Requirements-to-design traceability (HW13) — verify the feasibility targets against reality.

The feasibility study (phase 1) states a power budget, board size, layer count, cost target, and
part count. Those are usually written in a doc and never re-checked. This compares the declared
targets (a `feasibility.json` spec) against the actuals computed from the design, and flags any
that blew their budget — catching silent scope drift.

Only keys present in **both** the spec and the actuals are checked (partial data → partial check).
Pure Python 3 standard library.
"""
from .findings import finding


def _f(rule_id, severity, summary, prov=None, rec=""):
    return finding(detector="feasibility", rule_id=rule_id, category="requirements",
                   severity=severity, confidence="deterministic", evidence_source="topology",
                   summary=summary, where="<project>", provenance=prov, recommendation=rec)


def run(spec, actuals):
    """spec/actuals may carry: power_w / power_budget_w, size_mm [w,h], layers, cost / cost_target,
    components / max_components. Returns harmonized findings for each exceeded budget."""
    spec, actuals, V = spec or {}, actuals or {}, []

    budget, val = spec.get("power_budget_w"), actuals.get("power_w")
    if budget is not None and val is not None and val > budget + 1e-9:
        V.append(_f("power_over_budget", "error", f"power {val:.2f} W > budget {budget} W",
                    {"power_w": val, "budget_w": budget}, "reduce load or raise the budget"))

    if spec.get("size_mm") and actuals.get("size_mm"):
        (sw, sh), (aw, ah) = spec["size_mm"], actuals["size_mm"]
        if aw > sw + 1e-6 or ah > sh + 1e-6:
            V.append(_f("size_over_budget", "error",
                        f"board {aw}×{ah} mm exceeds target {sw}×{sh} mm",
                        {"actual": [aw, ah], "target": [sw, sh]}, "shrink the layout or resize the target"))

    tgt, act = spec.get("layers"), actuals.get("layers")
    if tgt is not None and act is not None and act > tgt:
        V.append(_f("layers_over_budget", "warning", f"{act}-layer board exceeds the {tgt}-layer target",
                    {"actual": act, "target": tgt}, "re-plan for fewer layers or accept the cost"))

    tgt, act = spec.get("cost_target"), actuals.get("cost")
    if tgt is not None and act is not None and act > tgt + 1e-9:
        V.append(_f("cost_over_budget", "error", f"BOM cost {act} > target {tgt}",
                    {"actual": act, "target": tgt}, "value-engineer the BOM"))

    tgt, act = spec.get("max_components"), actuals.get("components")
    if tgt is not None and act is not None and act > tgt:
        V.append(_f("component_count_over", "warning", f"{act} components exceed the {tgt} target",
                    {"actual": act, "target": tgt}))
    return V
