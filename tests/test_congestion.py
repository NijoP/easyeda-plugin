import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow import congestion as c


def test_grid_and_saturation():
    # a small board, one hot corner where many high-current nets overlap
    nets = [{"drc_class": "POWER_HC", "bbox": [0, 0, 2, 2]} for _ in range(5)]
    nets.append({"drc_class": "SIGNAL", "bbox": [6, 6, 8, 8]})
    g = c.grid(nets, w_mm=10, h_mm=10, bin_mm=2.0)
    assert g["nx"] == 5 and g["ny"] == 5
    # bin (0,0) got 5 * POWER_HC(3.5) = 17.5 demand
    assert g["cells"][0][0] == 5 * 3.5
    hot = c.saturated(g)                       # capacity ~ 2/(0.2+0.15) = 5.7
    assert any(h["bin"] == (0, 0) for h in hot)
    assert all(h["bin"] != (3, 3) for h in hot)   # the lone SIGNAL bin isn't saturated


def test_gnd_plane_is_free():
    g = c.grid([{"drc_class": "GND_PLANE", "bbox": [0, 0, 10, 10]}], 10, 10)
    assert c.saturated(g) == []               # a plane adds no routed demand


if __name__ == "__main__":
    test_grid_and_saturation(); test_gnd_plane_is_free()
    print("PASS — congestion: 2mm-bin demand grid, saturation detection, plane=0.")
