"""Exercise the in-process CLI verbs end-to-end (exit codes + wiring). Complements test_cli.py
(which checks parsing). Standalone or pytest:  python3 tests/test_cli_commands.py"""
import contextlib
import io
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow import cli  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(REPO, "projects", "example-usb-c-3v3", "04_schematic", "netlist.enet")


def _run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(argv)
    return rc, buf.getvalue()


def _tmp(obj, suffix):
    p = tempfile.mktemp(suffix=suffix)
    with open(p, "w") as f:
        json.dump(obj, f)
    return p


def test_ipc_and_engineering_verbs():
    assert _run(["ipc", "10"])[0] == 0
    assert _run(["stitch-pitch", "0.7"])[0] == 0
    nets = _tmp([{"net": "VBUS", "i_peak_a": 2.0}, {"net": "GND", "i_peak_a": 5.0}], ".json")
    assert _run(["widths", nets])[0] == 0


def test_spacing_and_congestion():
    place = _tmp({"parts": [{"ref": "R1", "layer": "TOP", "bbox": [0, 0, 1, 1]},
                            {"ref": "R2", "layer": "TOP", "bbox": [1.2, 0, 2, 1]}], "min_gap": 0.5}, ".json")
    rc, out = _run(["spacing", place])
    assert rc == 1 and "violation" in out            # 0.2mm gap < 0.5 -> flagged
    cong = _tmp({"nets": [{"drc_class": "POWER_HC", "bbox": [0, 0, 4, 4]}], "w": 20, "h": 20}, ".json")
    assert _run(["congestion", cong])[0] == 0


def test_enet_erc_dfm_verify_on_example():
    if not os.path.exists(EX):
        return
    assert _run(["enet", EX])[0] == 0
    assert _run(["erc", EX])[0] == 0
    assert _run(["erc", EX, "--json"])[0] == 0
    assert _run(["verify", EX])[0] == 0
    board = _tmp({"board": {"layers": 2}, "tracks": [{"net": "SDA", "width": 0.10, "layer": "F"}]}, ".json")
    assert _run(["dfm", board])[0] == 1              # sub-min track -> FAIL
    assert _run(["dfm", board, "--json"])[0] == 1


def test_import_check_verb():
    board = os.path.join(REPO, "projects", "example-usb-c-3v3", "10_kicad_export", "board.kicad_pcb")
    if os.path.exists(EX) and os.path.exists(board):
        assert _run(["import-check", EX, board])[0] == 0


def test_gate_and_export_verbs(tmp_path=None):
    import pathlib
    d = tempfile.mkdtemp()
    sub = os.path.join(d, "04_schematic")
    os.makedirs(sub)
    with open(os.path.join(sub, "netlist.enet"), "w") as f:
        json.dump({"version": "2.0.0", "components": {
            "u": {"props": {"Designator": "U1"}, "pinInfoMap": {
                "1": {"number": "1", "name": "1", "net": "VBUS"},
                "2": {"number": "2", "name": "2", "net": "GND"}}},
            "c": {"props": {"Designator": "C1"}, "pinInfoMap": {
                "1": {"number": "1", "name": "1", "net": "VBUS"},
                "2": {"number": "2", "name": "2", "net": "GND"}}}}}, f)
    parent, name = pathlib.Path(d).parent, pathlib.Path(d).name
    orig = cli.PROJECTS
    cli.PROJECTS = parent
    try:
        assert _run(["gate", name, "5"])[0] == 0                  # computes + records PASS
        assert _run(["export", name])[0] == 1                     # blocked: no approval
        ap = _tmp({"approved_by": "x", "approved_at_utc": "t", "scope": "s"}, ".json")
        assert _run(["export", name, "--approval", ap])[0] == 0   # cleared
    finally:
        cli.PROJECTS = orig


def _run_all():
    for nm, fn in sorted(globals().items()):
        if nm.startswith("test_") and callable(fn):
            fn()
    print("PASS — cli commands: ipc/widths/stitch, spacing/congestion, enet/erc/dfm/verify, "
          "import-check, gate/export.")


if __name__ == "__main__":
    _run_all()
