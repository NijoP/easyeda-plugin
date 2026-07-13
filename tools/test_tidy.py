#!/usr/bin/env python3
"""Tests for Phase-5 schematic tidy (pure geometry). Run: python3 tools/test_tidy.py"""
import tidy_schematic as T


def test_resolve_removes_overlaps():
    blocks = [{"id": "A", "x": 0, "y": 0, "w": 10, "h": 10},
              {"id": "B", "x": 5, "y": 5, "w": 10, "h": 10},
              {"id": "C", "x": 6, "y": 1, "w": 4, "h": 4}]
    assert T.has_overlaps(blocks)
    fixed = T.resolve_overlaps(blocks, gap=1.0)
    assert not T.has_overlaps(fixed, gap=0.0)


def test_snap_to_grid():
    snapped = T.snap_to_grid([{"id": "A", "x": 3.1, "y": 7.9, "w": 1, "h": 1}], pitch=2.54)
    # 3.1/2.54 ≈ 1.22 → 1 → 2.54 ; 7.9/2.54 ≈ 3.11 → 3 → 7.62
    assert abs(snapped[0]["x"] - 2.54) < 1e-6
    assert abs(snapped[0]["y"] - 7.62) < 1e-6


def test_tidy_is_grid_aligned_and_separated():
    blocks = [{"id": "A", "x": 0.3, "y": 0.1, "w": 5, "h": 5},
              {"id": "B", "x": 2.0, "y": 2.0, "w": 5, "h": 5}]
    out = T.tidy(blocks, gap=1.0, pitch=2.54)
    assert not T.has_overlaps(out, gap=0.0)
    for b in out:                                   # every block lands on the grid
        assert abs((b["x"] / 2.54) - round(b["x"] / 2.54)) < 1e-6
        assert abs((b["y"] / 2.54) - round(b["y"] / 2.54)) < 1e-6


if __name__ == "__main__":
    test_resolve_removes_overlaps()
    test_snap_to_grid()
    test_tidy_is_grid_aligned_and_separated()
    print("PASS — tidy: de-collision + grid snap + combined tidy (grid-aligned, separated).")
