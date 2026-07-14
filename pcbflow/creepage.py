"""Creepage & clearance (HW12) — conductor spacing vs voltage (IPC-2221).

For anything above low voltage, copper spacing must grow with the voltage between nets or the
board arcs / fails safety cert. This looks up the required spacing for the design's maximum
net-to-net voltage (from the power tree) and flags it if the board's minimum clearance is below
that. Uses IPC-2221 Table 6-1, B4 (external conductors, uncoated).

Pure Python 3 standard library.
"""
from .findings import finding

# IPC-2221 B4 (external, uncoated) — (peak voltage ≤, min spacing mm)
_TABLE = [(15, 0.13), (30, 0.13), (50, 0.13), (100, 0.13), (150, 0.40),
          (170, 0.40), (250, 0.40), (300, 0.40), (500, 0.80)]


def required_spacing_mm(v_peak):
    """Minimum conductor spacing for a peak voltage (IPC-2221 B4); linear above 500 V."""
    for vmax, mm in _TABLE:
        if v_peak <= vmax:
            return mm
    return 0.80 + 0.00305 * (v_peak - 500)


def run(enet, rails, min_clearance_mm=0.15):
    """Compare the design's max net-to-net ΔV against the board's min clearance."""
    volts = [0.0] + [(r.get("voltage") or 0.0) for r in (rails or {}).values()]
    max_dv = max(volts) - min(volts)
    req = required_spacing_mm(max_dv)
    if req > min_clearance_mm + 1e-9:
        return [finding(detector="creepage", rule_id="insufficient_creepage", category="safety",
                        severity="error", confidence="datasheet-backed", evidence_source="datasheet",
                        summary=f"max ΔV {max_dv:.0f} V needs {req} mm spacing (board clearance "
                                f"{min_clearance_mm} mm)", where="<board>",
                        provenance={"max_dv": max_dv, "required_mm": req, "clearance_mm": min_clearance_mm},
                        recommendation="increase clearance for the voltage class (IPC-2221)")]
    return []
