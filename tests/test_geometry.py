import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow import geometry as g


def test_rect_gap():
    a = [0, 0, 10, 10]
    assert g.rect_gap(a, [12, 0, 20, 10]) == 2.0        # 2mm apart in x
    assert g.rect_gap(a, [5, 5, 15, 15]) < 0            # overlap
    assert abs(g.rect_gap(a, [13, 14, 20, 20]) - 5.0) < 1e-9  # diagonal 3,4,5


def test_spacing_audit():
    parts = [
        {"ref": "R1", "layer": "TOP", "bbox": [0, 0, 1, 1]},
        {"ref": "R2", "layer": "TOP", "bbox": [1.2, 0, 2, 1]},   # gap 0.2 < 0.5 -> violation
        {"ref": "U1", "layer": "BOTTOM", "bbox": [1.1, 0, 2, 1]},  # other layer -> ok
    ]
    v = g.spacing_audit(parts, min_gap=0.5)
    assert len(v) == 1 and {v[0]["a"], v[0]["b"]} == {"R1", "R2"}
    assert g.spacing_audit(parts, min_gap=0.5, whitelist=[("R1", "R2")]) == []


def test_keepout_and_board():
    parts = [{"ref": "C1", "layer": "TOP", "bbox": [0, 0, 1, 1]}]
    assert g.keepout_intrusion(parts, [{"x": 1.2, "y": 0.5, "r": 0.5}])   # 0.2 < 0.5
    assert not g.keepout_intrusion(parts, [{"x": 5, "y": 5, "r": 0.5}])
    assert g.out_of_board(parts, [0.2, 0, 5, 5]) == ["C1"]                # x0=0 < 0.2
    assert g.out_of_board(parts, [0, 0, 5, 5]) == []


if __name__ == "__main__":
    test_rect_gap(); test_spacing_audit(); test_keepout_and_board()
    print("PASS — geometry: gaps, spacing audit, keepout, board containment.")
