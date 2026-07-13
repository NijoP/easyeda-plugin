import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow import routing as r


def test_trace_width_table():
    t = r.trace_width_table([{"net": "VSYS", "i_peak_a": 10}, {"net": "SDA", "i_peak_a": 0.05}])
    vsys = next(x for x in t if x["net"] == "VSYS")
    sda = next(x for x in t if x["net"] == "SDA")
    assert vsys["method"] == "plane/pour" and vsys["width_mm"] > 5
    assert sda["method"] == "trace"


def test_stitch_pitch_from_edge_rate():
    # 500 MHz knee (t_rise 0.7 ns) -> ~14.5 mm pitch (design-standards reference)
    assert abs(r.edge_knee_mhz(0.7) - 500.0) < 1.0
    assert 13.5 < r.stitch_pitch_mm(0.7) < 15.5


def test_stitch_collision():
    # a via at (5,5); a pad circle at (5,5,r=0.4) blocks it; clearance 0.15
    assert not r.stitch_clear(5, 5, keep=0.15, pads=[(5, 5, 0.4)])
    assert r.stitch_clear(5, 5, keep=0.15, pads=[(9, 9, 0.4)])
    # a track passing near blocks it
    assert not r.stitch_clear(5, 5, keep=0.15, tracks=[(0, 5, 10, 5, 0.1)])
    grid = r.stitch_grid([0, 0, 4, 4], pitch=2.0, keep=0.15, pads=[(2, 2, 1.0)])
    assert (2.0, 2.0) not in grid and (0.0, 0.0) in grid


if __name__ == "__main__":
    test_trace_width_table(); test_stitch_pitch_from_edge_rate(); test_stitch_collision()
    print("PASS — routing: width table, λ/20 stitch pitch, collision-checked stitching.")
