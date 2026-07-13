"""2 mm-bin routing-congestion predictor (phase 7).

Predicts where routing demand will exceed channel capacity, so a via-fan to the
other layer can be planned *before* routing (rather than discovered mid-route).
Pure and testable.

A net = {"drc_class": str, "bbox": [x0, y0, x1, y1]}  (its routing span, mm).
"""
import math

# routing demand weight per net class (high-current/wide nets cost more channel)
DEFAULT_WEIGHTS = {
    "USB_DIFF": 2.4, "POWER_MOTOR": 3.0, "POWER_HC": 3.5, "POWER": 1.4,
    "ANALOG_PWR": 1.2, "GATE": 0.9, "ANALOG_SENS": 1.1,
    "GND_PLANE": 0.0, "GNDA_PLANE": 0.6, "SIGNAL": 1.0,
}


def grid(nets, w_mm, h_mm, bin_mm=2.0, weights=None):
    """Add each net's class weight to every bin its bbox spans.
    Returns {nx, ny, bin_mm, cells:[[demand]]}."""
    weights = weights or DEFAULT_WEIGHTS
    nx = max(1, int(math.ceil(w_mm / bin_mm)))
    ny = max(1, int(math.ceil(h_mm / bin_mm)))
    cells = [[0.0] * nx for _ in range(ny)]
    for n in nets:
        wt = weights.get(n.get("drc_class"), 1.0)
        if wt <= 0:
            continue
        x0, y0, x1, y1 = n["bbox"]
        gx0, gx1 = int(x0 // bin_mm), int(x1 // bin_mm)
        gy0, gy1 = int(y0 // bin_mm), int(y1 // bin_mm)
        for gy in range(max(0, gy0), min(ny, gy1 + 1)):
            for gx in range(max(0, gx0), min(nx, gx1 + 1)):
                cells[gy][gx] += wt
    return {"nx": nx, "ny": ny, "bin_mm": bin_mm, "cells": cells}


def capacity(bin_mm=2.0, trace_w=0.2, clearance=0.15):
    """Routable tracks across one bin edge = bin / (track + clearance)."""
    return bin_mm / (trace_w + clearance)


def saturated(g, cap=None):
    """Bins whose demand exceeds capacity — each needs a via-fan to the other layer.
    Returns [{bin:(gx,gy), demand, cap}]."""
    cap = capacity(g["bin_mm"]) if cap is None else cap
    hot = []
    for gy in range(g["ny"]):
        for gx in range(g["nx"]):
            d = g["cells"][gy][gx]
            if d > cap:
                hot.append({"bin": (gx, gy), "demand": round(d, 2), "cap": round(cap, 2)})
    return hot
