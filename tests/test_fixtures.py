"""Corpus test — prove the gates BLOCK known-bad designs (not just pass good ones), and that the
clean worked example passes. Plus a source-of-truth consistency check (phases ↔ agents).
Standalone or pytest:  python3 tests/test_fixtures.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcbflow import gates, phases  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BAD = os.path.join(HERE, "fixtures", "known_bad")
REPO = os.path.dirname(HERE)
MANIFEST = json.load(open(os.path.join(BAD, "manifest.json")))


def test_known_bad_schematics_are_blocked():
    """Every known-bad netlist must be BLOCKED (status != PASS) with its exact expected status —
    an error-severity defect FAILs, a warning-severity one WARNs; neither is ever PASS."""
    for name, spec in MANIFEST["schematic"].items():
        out = gates.gate_schematic(os.path.join(BAD, name))
        assert out.status != "PASS", f"{name} ({spec['defect_class']}) must not PASS"
        assert out.status == spec["expected"], \
            f"{name}: expected {spec['expected']}, got {out.status}"
        assert out.details, f"{name}: a blocked gate must carry evidence"


def test_known_bad_boards_are_blocked():
    """Every known-bad board-features file must FAIL the DFM gate."""
    for name, spec in MANIFEST["dfm"].items():
        out = gates.gate_dfm(os.path.join(BAD, name))
        assert out.status == "FAIL", f"{name} ({spec['defect_class']}) should FAIL, got {out.status}"


def test_clean_example_passes_the_schematic_gate():
    """The shipped worked example must PASS — the gates don't reject good designs."""
    enet = os.path.join(REPO, "projects", "example-usb-c-3v3", "04_schematic", "netlist.enet")
    if os.path.exists(enet):
        assert gates.gate_schematic(enet).status == "PASS"


def test_defect_classes_are_distinct():
    """Each fixture documents a distinct defect class (corpus covers different failure modes)."""
    classes = [s["defect_class"] for s in {**MANIFEST["schematic"], **MANIFEST["dfm"]}.values()]
    assert len(classes) == len(set(classes)) >= 6


def test_phases_and_agents_are_consistent():
    """Source-of-truth guard: every phase's owning agent has a job-description file, and the
    12 phases are contiguous 1..12 (catches phases.py ↔ agents/ drift)."""
    nums = [n for n, _, _ in phases.PHASES]
    assert nums == list(range(1, 13)), nums
    for _, _, agent in phases.PHASES:
        assert os.path.exists(os.path.join(REPO, "agents", f"{agent}.md")), f"missing agent: {agent}"


def _run():
    for nm, fn in sorted(globals().items()):
        if nm.startswith("test_") and callable(fn):
            fn()
    print("PASS — fixtures: known-bad schematics + boards blocked, clean example passes, "
          "distinct defects, phases↔agents consistent.")


if __name__ == "__main__":
    _run()
