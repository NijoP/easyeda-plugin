"""Pure placement geometry (phases 6-9).

Operates on rectangles read back from the real board — never the placer's own grid
model (which shows phantom overlaps). No EDA tool needed; fully testable offline.

A part = {"ref": str, "layer": "TOP"|"BOTTOM", "bbox": [x0, y0, x1, y1]}  (mm).
"""
import math


def rect_gap(a, b):
    """Axis-aligned gap (mm) between two bboxes. >=0 = clear (corner distance if
    diagonally separated); <0 = overlap penetration depth."""
    sx = max(a[0] - b[2], b[0] - a[2])
    sy = max(a[1] - b[3], b[1] - a[3])
    if sx > 0 and sy > 0:
        return math.hypot(sx, sy)
    return max(sx, sy)


def spacing_audit(parts, min_gap=0.5, whitelist=()):
    """Same-layer pad-gap check. Returns a list of violations
    {a, b, gap, limit}. `whitelist` = iterable of (refA, refB) pairs to skip."""
    wl = {frozenset(p) for p in whitelist}
    viol = []
    n = len(parts)
    for i in range(n):
        for j in range(i + 1, n):
            A, B = parts[i], parts[j]
            if A["layer"] != B["layer"]:
                continue
            if frozenset((A["ref"], B["ref"])) in wl:
                continue
            g = round(rect_gap(A["bbox"], B["bbox"]), 4)
            if g < min_gap - 1e-6:
                viol.append({"a": A["ref"], "b": B["ref"], "gap": g, "limit": min_gap})
    return viol


def keepout_intrusion(parts, keepouts):
    """Which parts intrude a circular keepout. keepouts = [{"x","y","r"}] (e.g. M2
    mounting rings). Returns [{ref, keepout}]."""
    hits = []
    for p in parts:
        x0, y0, x1, y1 = p["bbox"]
        for k in keepouts:
            nx = min(max(k["x"], x0), x1)      # nearest point on the bbox to the centre
            ny = min(max(k["y"], y0), y1)
            if math.hypot(nx - k["x"], ny - k["y"]) < k["r"]:
                hits.append({"ref": p["ref"], "keepout": (k["x"], k["y"], k["r"])})
    return hits


def out_of_board(parts, outline, overhang=0.0):
    """Parts whose bbox extends beyond the board outline [x0,y0,x1,y1] by more than
    `overhang` (connectors may be whitelisted by giving them a larger overhang)."""
    bx0, by0, bx1, by1 = outline
    out = []
    for p in parts:
        x0, y0, x1, y1 = p["bbox"]
        if (x0 < bx0 - overhang or y0 < by0 - overhang
                or x1 > bx1 + overhang or y1 > by1 + overhang):
            out.append(p["ref"])
    return out
