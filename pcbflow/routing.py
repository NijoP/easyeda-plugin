"""Routing-plan helpers (phases 7 & 11). Pure math + a collision-checked stitch test.

- trace_width_table: per-net IPC-2221 width + trace-vs-plane call (uses ipc.py).
- edge-rate + λ/20 stitch pitch: from the *edge rate*, not the clock.
- stitch_clear / stitch_grid: collision-checked ground-stitch via placement
  (never a blind via — that gave 250-815 shorts on the reference project).
"""
import math

from . import ipc

_C_MM_NS = 299.792458   # speed of light, mm/ns


def trace_width_table(nets, delta_t_c=10.0):
    """nets: [{"net", "i_peak_a", optional "oz", "internal"}]. Returns per-net
    {net, i_peak_a, width_mm, method}."""
    out = []
    for n in nets:
        r = ipc.recommend(n.get("i_peak_a", 0.0), delta_t_c=delta_t_c,
                          copper_oz=n.get("oz", 1.0), internal=n.get("internal", False))
        out.append({"net": n["net"], "i_peak_a": n.get("i_peak_a", 0.0),
                    "width_mm": r["width_mm"], "method": r["method"]})
    return out


def edge_knee_mhz(t_rise_ns):
    """Signal bandwidth from the edge: f_knee = 0.35 / t_rise. Returns MHz."""
    if t_rise_ns <= 0:
        return 0.0
    return round(0.35 / t_rise_ns * 1000.0, 1)     # 0.35/ns = GHz -> *1000 = MHz


def stitch_pitch_mm(t_rise_ns, er=4.3):
    """λ/20 ground-stitch pitch from the edge-rate knee (not the clock). FR-4 εr≈4.3.
    (Sanity: a 500 MHz knee -> ~14.5 mm pitch.)"""
    f_mhz = edge_knee_mhz(t_rise_ns)
    if f_mhz <= 0:
        return 0.0
    f_ghz = f_mhz / 1000.0
    lam_mm = _C_MM_NS / (f_ghz * math.sqrt(er))
    return round(lam_mm / 20.0, 3)


def _pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def stitch_clear(px, py, keep, pads=(), holes=(), tracks=(), exclusions=()):
    """Is a stitch via at (px, py) clear? pads/holes/exclusions = [(x,y,r)] circles;
    tracks = [(x1,y1,x2,y2,half_width)]. `keep` = required clearance (mm)."""
    for (cx, cy, cr) in list(pads) + list(holes) + list(exclusions):
        if math.hypot(px - cx, py - cy) < keep + cr:
            return False
    for (x1, y1, x2, y2, hw) in tracks:
        if _pt_seg(px, py, x1, y1, x2, y2) < keep + hw:
            return False
    return True


def stitch_grid(box, pitch, keep, pads=(), holes=(), tracks=(), exclusions=()):
    """Generate collision-checked stitch-via positions on a grid inside
    box=[x0,y0,x1,y1]. Returns [(x,y)] of the clear positions."""
    x0, y0, x1, y1 = box
    pts = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            if stitch_clear(x, y, keep, pads, holes, tracks, exclusions):
                pts.append((round(x, 3), round(y, 3)))
            x += pitch
        y += pitch
    return pts
