import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow import phases


def test_phase_table():
    assert len(phases.PHASES) == 12
    assert phases.phase_name(1) == "requirement-analysis"
    assert phases.phase_name(12) == "final-verification"
    assert phases.phase_agent(11) == "router"
    assert phases.next_phase(1) == 2
    assert phases.next_phase(12) is None
    assert phases.is_last(12) and not phases.is_last(1)
    try:
        phases.phase(0); assert False
    except ValueError:
        pass


if __name__ == "__main__":
    test_phase_table()
    print("PASS — phases: 12-phase table, names, agents, ordering.")
