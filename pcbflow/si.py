"""Signal integrity (HW5) — controlled impedance + length matching.

Consumes the intent the `.enet` already carries (`netClass` impedance targets, `differentialPair`,
`equalLengthNetGroup`), the routed geometry (`pcbflow.kicad_sexp`), and the physical stack-up
(`pcbflow.stackup`) — data that existed but nothing read until now.

Physics:
  - **Microstrip impedance (IPC-2141):** Z0 = 87/√(Er+1.41) · ln(5.98·h / (0.8·w + t)),
    valid for 0.1 < w/h < 2.0, with copper thickness t from the stack-up.
  - **Length match:** for each differential pair, |len(P) − len(N)| ≤ skew tolerance; for each
    equal-length group, (max − min) ≤ tolerance. Lengths are the routed track lengths.

Degrades gracefully — a board with no impedance targets / diff pairs / equal-length groups
produces nothing (a simple board has no SI-critical nets). Pure Python 3 standard library.
"""
import math

from .findings import finding

DEFAULT_Z_TOL_PCT = 10.0     # ±10% impedance tolerance if the net class doesn't state one
DEFAULT_SKEW_MM = 0.15       # intra-pair skew tolerance
DEFAULT_EQLEN_MM = 0.5       # equal-length group tolerance


def microstrip_z0(w_mm, h_mm, t_mm, er):
    """IPC-2141 surface-microstrip characteristic impedance (Ω). Returns None outside the
    formula's validity window (0.1 < w/h < 2.0)."""
    if h_mm <= 0 or w_mm <= 0:
        return None
    if not (0.1 < w_mm / h_mm < 2.0):
        return None
    return (87.0 / math.sqrt(er + 1.41)) * math.log(5.98 * h_mm / (0.8 * w_mm + t_mm))


def _f(rule_id, severity, summary, where, nets=None, prov=None, rec=""):
    return finding(detector="si", rule_id=rule_id, category="signal_integrity", severity=severity,
                   confidence="deterministic", evidence_source="geometry", summary=summary,
                   where=where, nets=nets, provenance=prov, recommendation=rec)


def _min_width(net, geometry):
    ws = [t["width"] for t in geometry["tracks"] if t["net"] == net and t["width"] > 0]
    return min(ws) if ws else None


def _pairs(enet):
    """Normalize `.enet` differentialPair into [(name, posnet, negnet, skew_mm)]."""
    out = []
    for name, spec in (enet.differential_pair or {}).items():
        if isinstance(spec, dict):
            nets = spec.get("nets") or [spec.get("pos"), spec.get("neg")]
            tol = spec.get("skew_mm", spec.get("tolerance_mm", DEFAULT_SKEW_MM))
        else:
            nets, tol = spec, DEFAULT_SKEW_MM
        nets = [n for n in (nets or []) if n]
        if len(nets) >= 2:
            out.append((name, nets[0], nets[1], tol))
    return out


def _groups(enet):
    out = []
    for name, spec in (enet.equal_length or {}).items():
        if isinstance(spec, dict):
            nets, tol = spec.get("nets", []), spec.get("tol_mm", DEFAULT_EQLEN_MM)
        else:
            nets, tol = spec, DEFAULT_EQLEN_MM
        if len([n for n in (nets or []) if n]) >= 2:
            out.append((name, [n for n in nets if n], tol))
    return out


def run(enet, geometry, stack):
    """enet (nets + SI intent) × routed geometry × stack-up → harmonized findings."""
    from .kicad_sexp import net_lengths
    lengths = net_lengths(geometry)
    ref = stack.signal_layers()[0].name if stack.signal_layers() else None
    dref = stack.dielectric_to_reference(ref) if ref else None
    V = []

    # impedance targets from net classes
    for cls, spec in (enet.net_class or {}).items():
        if not isinstance(spec, dict):
            continue
        z_target = spec.get("impedance_ohm") or spec.get("impedance")
        if not z_target or not dref:
            continue
        tol = spec.get("tolerance_pct", DEFAULT_Z_TOL_PCT)
        h, er = dref
        for net in spec.get("nets", []):
            w = _min_width(net, geometry)
            if not w:
                continue
            z0 = microstrip_z0(w, h, stack.copper_thickness(), er)
            if z0 is None:
                continue
            if abs(z0 - z_target) > z_target * tol / 100.0:
                V.append(_f("impedance_out_of_spec", "warning",
                            f"net '{net}' Z0≈{z0:.1f} Ω vs {z_target} Ω ±{tol:.0f}% (w={w} mm)",
                            net, [net], {"z0": round(z0, 1), "target": z_target},
                            "adjust trace width or stack-up for the impedance target"))

    # differential-pair skew
    for name, pos, neg, tol in _pairs(enet):
        lp, ln = lengths.get(pos), lengths.get(neg)
        if lp is not None and ln is not None and abs(lp - ln) > tol + 1e-9:
            V.append(_f("diffpair_skew", "error",
                        f"diff pair '{name}': |{lp}−{ln}| = {abs(lp-ln):.3f} mm > {tol} mm skew",
                        name, [pos, neg], {"len_p": lp, "len_n": ln, "tol": tol},
                        "length-tune the shorter leg"))

    # equal-length groups
    for name, nets, tol in _groups(enet):
        ls = [lengths[n] for n in nets if n in lengths]
        if len(ls) >= 2 and (max(ls) - min(ls)) > tol + 1e-9:
            V.append(_f("equal_length_violation", "warning",
                        f"group '{name}': spread {max(ls)-min(ls):.3f} mm > {tol} mm", name, nets,
                        {"min": min(ls), "max": max(ls), "tol": tol}, "length-tune the group"))
    return V
