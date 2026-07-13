import sys, pathlib, io, contextlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from pcbflow import cli


def _run(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(args)
    return rc, buf.getvalue()


def test_phases_command():
    rc, out = _run(["phases"])
    assert rc == 0 and "requirement-analysis" in out and "final-verification" in out


def test_ipc_command():
    rc, out = _run(["ipc", "10"])
    assert rc == 0 and "plane/pour" in out
    rc, out = _run(["ipc", "1"])
    assert rc == 0 and "trace" in out


def test_parser_builds_all_commands():
    ap = cli.build_parser()
    # every subcommand parses without error
    for argv in (["phases"], ["ipc", "5"], ["init", "x"], ["status", "x"],
                 ["verdict", "x", "5", "PASS"], ["advance", "x"], ["doctor"],
                 ["launch"], ["dump", "o.json"], ["recon", "d.json"], ["drc", "b.kicad_pcb"]):
        ap.parse_args(argv)   # raises SystemExit on a bad definition


if __name__ == "__main__":
    test_phases_command()
    test_ipc_command()
    test_parser_builds_all_commands()
    print("PASS — cli: phases, ipc, and every subcommand parses.")
