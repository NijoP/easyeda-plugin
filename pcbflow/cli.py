"""PCB Flow CLI — one entry point for the whole harness.

In-package commands (pure, fast): init, status, verdict, advance, phases, ipc.
Pass-through commands (delegate to the tools, so there's one front door):
doctor, launch, dump, recon, drc.

Run from the cloned repo (the pass-throughs resolve tool paths relative to it).
"""
import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__, ipc, phases
from .project import Project

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"


def _run(rel, *args):
    """Run a repo tool with the current interpreter (handles python vs python3)."""
    return subprocess.run([sys.executable, str(REPO / rel), *args]).returncode


# --- pass-throughs ---
def cmd_doctor(a):
    return _run("tools/doctor.py", *a.passthrough)


def cmd_launch(a):
    return _run("tools/launch_easyeda.py", *a.passthrough)


def cmd_drc(a):
    return _run("tools/drc.py", *([a.board] + ([a.ruleset] if a.ruleset else [])))


def cmd_recon(a):
    return _run("automation/browser/recon.py", *([a.dump] + ([a.out] if a.out else [])))


def cmd_dump(a):
    r = subprocess.run(
        [sys.executable, str(REPO / "automation/browser/cdp.py"), "eval",
         str(REPO / "automation/easyeda/dump_schematic.js")],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[:800] + "\n")
        return r.returncode
    Path(a.out).write_text(r.stdout)
    print(f"dumped live schematic -> {a.out}  (now: pcbflow recon {a.out} netlist.json)")
    return 0


# --- in-package ---
def cmd_init(a):
    p = Project.init(PROJECTS, a.name, a.description or "")
    print(f"initialized project '{a.name}' at {p.path.relative_to(REPO)}  (phase 1: "
          f"{phases.phase_name(1)})")
    return 0


def cmd_status(a):
    p = Project(PROJECTS / a.name)
    try:
        s = p.status()
    except FileNotFoundError as e:
        print(e)
        return 2
    lv = s["latest_verdict"]
    print(f"Project: {s['name']}")
    print(f"  Phase {s['current_phase']:>2}: {s['phase_name']}  (agent: {s['owning_agent']})")
    print(f"  Latest verdict: {lv['verdict'] if lv else 'PENDING'}")
    print(f"  Advance allowed: {'yes' if p.can_advance() else 'no — needs a PASS verdict'}")
    return 0


def cmd_verdict(a):
    p = Project(PROJECTS / a.name)
    p.record_verdict(a.phase, a.verdict, a.note or "")
    print(f"recorded {a.verdict.upper()} for '{a.name}' phase {a.phase} ({phases.phase_name(a.phase)})")
    return 0


def cmd_advance(a):
    p = Project(PROJECTS / a.name)
    try:
        nxt = p.advance()
    except RuntimeError as e:
        print(e)
        return 1
    print(f"advanced '{a.name}' -> phase {nxt} ({phases.phase_name(nxt)})")
    return 0


def cmd_phases(a):
    for n, name, agent in phases.PHASES:
        print(f"{n:>2}  {name:<28} {agent}")
    return 0


def cmd_ipc(a):
    r = ipc.recommend(a.current, delta_t_c=a.delta_t, copper_oz=a.oz, internal=a.internal)
    print(f"{a.current} A  ->  {r['width_mm']} mm  [{r['method']}]   ({r['margin_note']})")
    if r["method"] == "plane/pour":
        print(f"    plane + via farm: ~{ipc.via_count(a.current, 0.3)} x 0.3 mm vias")
    return 0


def build_parser():
    ap = argparse.ArgumentParser(prog="pcbflow", description="AI-assisted PCB design harness")
    ap.add_argument("--version", action="version", version=f"pcbflow {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="check the environment before working")
    d.add_argument("passthrough", nargs="*"); d.set_defaults(fn=cmd_doctor)

    i = sub.add_parser("init", help="create a new project")
    i.add_argument("name"); i.add_argument("--description", default=""); i.set_defaults(fn=cmd_init)

    s = sub.add_parser("status", help="show a project's current phase + verdict")
    s.add_argument("name"); s.set_defaults(fn=cmd_status)

    v = sub.add_parser("verdict", help="record a phase verdict (PASS/CONDITIONAL/FAIL)")
    v.add_argument("name"); v.add_argument("phase", type=int); v.add_argument("verdict")
    v.add_argument("--note", default=""); v.set_defaults(fn=cmd_verdict)

    adv = sub.add_parser("advance", help="advance to the next phase (requires a PASS)")
    adv.add_argument("name"); adv.set_defaults(fn=cmd_advance)

    sub.add_parser("phases", help="list the 12 phases").set_defaults(fn=cmd_phases)

    ic = sub.add_parser("ipc", help="IPC-2221 trace width / plane call for a current")
    ic.add_argument("current", type=float)
    ic.add_argument("--delta-t", dest="delta_t", type=float, default=10.0)
    ic.add_argument("--oz", type=float, default=1.0)
    ic.add_argument("--internal", action="store_true")
    ic.set_defaults(fn=cmd_ipc)

    ln = sub.add_parser("launch", help="launch EasyEDA in Chrome (cross-platform)")
    ln.add_argument("passthrough", nargs="*"); ln.set_defaults(fn=cmd_launch)

    dm = sub.add_parser("dump", help="dump the live EasyEDA schematic to JSON")
    dm.add_argument("out"); dm.set_defaults(fn=cmd_dump)

    rc = sub.add_parser("recon", help="reconstruct a netlist from a schematic dump")
    rc.add_argument("dump"); rc.add_argument("out", nargs="?"); rc.set_defaults(fn=cmd_recon)

    dr = sub.add_parser("drc", help="run KiCad DRC (guarded against phantom-clean)")
    dr.add_argument("board"); dr.add_argument("ruleset", nargs="?"); dr.set_defaults(fn=cmd_drc)

    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.fn(args) or 0


if __name__ == "__main__":
    sys.exit(main())
