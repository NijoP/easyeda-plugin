import sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow.project import Project


def test_lifecycle_and_gating():
    with tempfile.TemporaryDirectory() as d:
        p = Project.init(d, "board1", "a test board")
        assert p.current_phase() == 1

        # "place nothing over wrong": can't advance without a PASS
        try:
            p.advance(); assert False, "advanced without a PASS"
        except RuntimeError:
            pass

        p.record_verdict(1, "PASS", "feasible")
        assert p.can_advance()
        assert p.advance() == 2

        s = p.status()
        assert s["current_phase"] == 2 and s["phase_name"] == "bom-planning"

        # invalid verdict + invalid phase are rejected
        try:
            p.record_verdict(2, "MAYBE"); assert False
        except ValueError:
            pass
        try:
            p.record_verdict(99, "PASS"); assert False
        except ValueError:
            pass


def test_missing_project():
    with tempfile.TemporaryDirectory() as d:
        try:
            Project(pathlib.Path(d) / "nope").current_phase(); assert False
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    test_lifecycle_and_gating()
    test_missing_project()
    print("PASS — project: init, verdict gating, advance-only-on-PASS, validation.")
