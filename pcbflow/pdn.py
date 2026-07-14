"""Power-distribution network integrity (HW6) — IR drop + via ampacity.

Uses the rail currents from `pcbflow.power_tree`, the routed geometry (`pcbflow.kicad_sexp`), and
the stack-up copper thickness.

Physics:
  - **Trace resistance:** R = ρ·L / (w·t), ρ_Cu = 1.72e−8 Ω·m (20 °C).
  - **IR drop:** V = I·R; flag when it exceeds a budget (default 3% of the rail voltage).
  - **Via ampacity:** model the plated barrel wall as copper of cross-section A ≈ π·d·t_plating
    and apply the IPC-2221 external-conductor law I = k·ΔT^0.44·A(mils²)^0.725 (k=0.048, ΔT=10 °C);
    flag when the net's total via capacity is below its current.

Degrades gracefully — no rail currents / no routed geometry ⇒ nothing to check.
Pure Python 3 standard library.
"""
import math

from .findings import finding

RHO_CU = 1.72e-8             # Ω·m at 20 °C
PLATING_MM = 0.0254         # 1 mil typical via barrel plating
MM2_TO_MILS2 = 1550.0


def trace_resistance(length_mm, width_mm, thickness_mm):
    if width_mm <= 0 or thickness_mm <= 0 or length_mm <= 0:
        return None
    return RHO_CU * (length_mm / 1e3) / ((width_mm / 1e3) * (thickness_mm / 1e3))


def via_current(drill_mm, plating_mm=PLATING_MM, dt_c=10.0, k=0.048):
    """Current a single plated via carries for a given ΔT (IPC-2221 external law on the barrel wall)."""
    a_mils2 = math.pi * drill_mm * plating_mm * MM2_TO_MILS2
    return k * (dt_c ** 0.44) * (a_mils2 ** 0.725)


def _f(rule_id, severity, summary, where, nets=None, prov=None, rec=""):
    return finding(detector="pdn", rule_id=rule_id, category="power", severity=severity,
                   confidence="deterministic", evidence_source="geometry", summary=summary,
                   where=where, nets=nets, provenance=prov, recommendation=rec)


def run(enet, geometry, stack, rails, currents=None, ir_budget_pct=3.0):
    """rails = {net:{voltage,i_load}} from power_tree; `currents` overrides per-net amps."""
    from .kicad_sexp import net_lengths
    lengths = net_lengths(geometry)
    t = stack.copper_thickness()
    currents = currents or {}
    V = []
    for net, r in (rails or {}).items():
        i = currents.get(net, r.get("i_load") or 0.0)
        if i <= 0:
            continue
        length = lengths.get(net)
        widths = [tk["width"] for tk in geometry["tracks"] if tk["net"] == net and tk["width"] > 0]
        if length and widths:
            res = trace_resistance(length, min(widths), t)
            drop = i * res if res else 0.0
            vref = r.get("voltage") or 0.0
            budget = (vref * ir_budget_pct / 100.0) if vref else 0.1
            if drop > budget + 1e-9:
                V.append(_f("ir_drop", "error",
                            f"rail '{net}': IR drop ≈ {drop*1000:.0f} mV at {i} A "
                            f"(> {budget*1000:.0f} mV budget)", net, [net],
                            {"drop_v": round(drop, 4), "i_a": i, "budget_v": round(budget, 4)},
                            "widen the trace, use a plane, or shorten the run"))
        vias_on = [vi for vi in geometry["vias"] if vi["net"] == net and vi["drill"] > 0]
        if vias_on:
            cap = sum(via_current(vi["drill"]) for vi in vias_on)
            if i > cap + 1e-9:
                V.append(_f("via_ampacity", "error",
                            f"rail '{net}': {len(vias_on)} via(s) carry ≈ {cap:.2f} A < {i} A",
                            net, [net], {"i_a": i, "via_capacity_a": round(cap, 2)},
                            "add stitching vias or increase drill"))
    return V
