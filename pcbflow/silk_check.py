"""Silkscreen-over-pad/via check (G1) — no silkscreen text on a pad or via.

Silk ink on a pad won't solder / can lift; on a via it wicks. `kicad-cli` DRC's `silk_over_copper`
is the full geometric ground truth (used in the routing gate); this is a fast, board-file-direct
check that catches the common case — a reference-designator or graphic text anchored on top of a
pad — by testing each silk text anchor against every pad's rectangle (absolute footprint + pad
position; rotation ignored, a conservative approximation).

Pure Python 3 standard library.
"""
from . import kicad_sexp as K
from .findings import finding


def _pads_and_silk(board):
    root = K.parse(K._load(board))
    if K._tag(root) != "kicad_pcb":
        raise ValueError("not a .kicad_pcb")
    pads, silk = [], []
    for fp in K._children(root, "footprint"):
        fat = K._first(fp, "at")
        fx, fy = (float(fat[1]), float(fat[2])) if fat and len(fat) >= 3 else (0.0, 0.0)
        ref = K._footprint_ref(fp) or "?"
        for pad in K._children(fp, "pad"):
            pat, size = K._first(pad, "at"), K._first(pad, "size")
            if pat and len(pat) >= 3:
                sw, sh = ((float(size[1]), float(size[2])) if size and len(size) >= 3 else (0.5, 0.5))
                pads.append((fx + float(pat[1]), fy + float(pat[2]), sw, sh, ref,
                             pad[1] if len(pad) > 1 else "?"))
        for ft in K._children(fp, "fp_text"):
            layer, tat = K._first(ft, "layer"), K._first(ft, "at")
            if layer and len(layer) >= 2 and "SilkS" in layer[1] and tat and len(tat) >= 3:
                silk.append((fx + float(tat[1]), fy + float(tat[2]), ft[2] if len(ft) > 2 else "", ref))
    for gt in K._children(root, "gr_text"):
        layer, tat = K._first(gt, "layer"), K._first(gt, "at")
        if layer and len(layer) >= 2 and "SilkS" in layer[1] and tat and len(tat) >= 3:
            silk.append((float(tat[1]), float(tat[2]), gt[1] if len(gt) > 1 else "", "<board>"))
    return pads, silk


def run(board):
    pads, silk = _pads_and_silk(board)
    V = []
    for sx, sy, txt, sref in silk:
        for px, py, sw, sh, pref, pname in pads:
            if abs(sx - px) <= sw / 2 and abs(sy - py) <= sh / 2:
                V.append(finding(detector="silk", rule_id="silk_over_pad", category="manufacturability",
                                 severity="error", confidence="deterministic", evidence_source="geometry",
                                 summary=f"silk text '{txt or sref}' overlaps pad {pref}.{pname}",
                                 where=f"{pref}.{pname}", components=[pref],
                                 recommendation="move the silkscreen text off the pad"))
                break
    return V
