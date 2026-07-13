import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow import ipc


def test_trace_width_matches_ipc2221_reference():
    # knowledge/design-standards.md: 1 oz external @ΔT10 -> 1A≈0.25mm, 5A≈2.79mm
    assert 0.20 < ipc.trace_width_mm(1, delta_t_c=10) < 0.35
    assert 2.60 < ipc.trace_width_mm(5, delta_t_c=10) < 2.95
    assert ipc.trace_width_mm(0) == 0.0


def test_high_current_needs_a_plane():
    assert ipc.needs_plane(10, delta_t_c=10)          # ~7 mm -> plane
    assert not ipc.needs_plane(2, delta_t_c=10)
    assert ipc.recommend(10, delta_t_c=10)["method"] == "plane/pour"
    assert ipc.recommend(2, delta_t_c=10)["method"] == "trace"


def test_via_count():
    assert ipc.via_count(10, 0.3) >= 11               # ~12x 0.3mm vias for 10 A
    assert ipc.via_count(1, 0.3) == 2                 # ceil(1/0.9)


if __name__ == "__main__":
    test_trace_width_matches_ipc2221_reference()
    test_high_current_needs_a_plane()
    test_via_count()
    print("PASS — ipc: IPC-2221 widths, plane threshold, via farm.")
