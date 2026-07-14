"""Thermal (HW7) — junction temperature vs. the part's limit.

`Tj = Ta + P·θJA`. Power comes from the parts spec (`p_diss`) or, for a linear regulator, is
derived as `P = (Vin − Vout)·Iout` from the power tree (the other half of the LDO-brownout class:
a regulator that doesn't brown out can still cook). Flags `Tj > Tj_max` (default 125 °C).

Needs `theta_ja` in the parts spec to run for a part — degrades gracefully otherwise.
Pure Python 3 standard library.
"""
from .findings import finding

TA_DEFAULT = 25.0
TJ_DEFAULT_MAX = 125.0


def _rail_v(net, rails):
    return (rails.get(net) or {}).get("voltage")


def run(enet, parts, rails, ta=TA_DEFAULT):
    rails = rails or {}
    pin_nets = enet.comp_pin_nets()
    V = []
    for des in parts.designators():
        r, role, pins = parts.ratings(des), parts.role(des), pin_nets.get(des, {})
        theta = r.get("theta_ja")
        if theta is None:
            continue
        p = r.get("p_diss")
        if p is None and role in ("ldo", "regulator"):
            vin = max((_rail_v(n, rails) for pn, n in pins.items()
                       if parts.pin_type(des, pn) == "pwr_in" and _rail_v(n, rails) is not None),
                      default=None)
            out_net = next((n for pn, n in pins.items() if parts.pin_type(des, pn) == "pwr_out"), None)
            iout = (rails.get(out_net) or {}).get("i_load") if out_net else None
            iout = iout or r.get("iout") or r.get("i_load")
            vout = r.get("vout")
            if vin is not None and vout is not None and iout:
                p = (vin - vout) * iout
        if p is None:
            continue
        tj = ta + p * theta
        tj_max = r.get("tj_max", TJ_DEFAULT_MAX)
        if tj > tj_max + 1e-9:
            V.append(finding(detector="thermal", rule_id="thermal_overtemp", category="reliability",
                             severity="error", confidence="datasheet-backed", evidence_source="datasheet",
                             summary=f"{des}: Tj ≈ {tj:.0f} °C > {tj_max:.0f} °C "
                                     f"(P={p*1000:.0f} mW, θJA={theta} °C/W)",
                             where=des, components=[des],
                             provenance={"tj_c": round(tj, 1), "p_w": round(p, 4), "theta_ja": theta},
                             recommendation="add copper area / a thermal pad, or cut dissipation"))
    return V
