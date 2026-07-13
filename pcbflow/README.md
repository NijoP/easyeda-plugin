# pcbflow — the CLI / harness

One command-line entry point that ties the 12-phase workflow, the reliability layer,
and the automation tools together. Pure Python 3 standard library at the core (the only
dependency, `websockets`, is used solely by the headless EasyEDA driver).

## Install

```bash
pip install -e .          # from the repo root — gives you the `pcbflow` command
# or, with nothing installed at all:
python3 -m pcbflow <command>
```
On Windows use `python` instead of `python3` (see `handbook/windows-setup.md`).

## Commands

**Project (the harness):**
```bash
pcbflow init my-board --description "USB-C LED blinker"   # create a project
pcbflow status my-board                                   # current phase + verdict
pcbflow verdict my-board 1 PASS --note "feasible"          # record a phase verdict
pcbflow advance my-board                                   # -> next phase (REQUIRES a PASS)
pcbflow phases                                             # list the 12 phases
```
`advance` refuses to move on without a `PASS` — *place nothing over wrong*, enforced.
Project state lives in `projects/<name>/pcbflow_state.json` (JSON, so a crash never
loses your place).

**Engineering:**
```bash
pcbflow ipc 10                 # IPC-2221: 10 A -> 7.19 mm [plane/pour] + ~12 vias
pcbflow ipc 2 --oz 2           # 2 A on 2 oz copper
pcbflow ipc 3 --internal       # inner-layer (0.5 oz) derating
```

**Tools (delegates to the automation):**
```bash
pcbflow doctor                 # check the environment
pcbflow launch                 # open EasyEDA in Chrome (cross-platform)
pcbflow dump dump.json         # dump the live schematic
pcbflow recon dump.json net.json   # rebuild the netlist (phase-5 audit)
pcbflow drc board.kicad_pcb rules.kicad_pro   # KiCad DRC (phantom-guard)
```

## How it maps to the framework

| Layer | Where |
|---|---|
| Phase order + gating | `pcbflow/phases.py`, `pcbflow/project.py` |
| IPC-2221 solver | `pcbflow/ipc.py` |
| CLI dispatch | `pcbflow/cli.py` |
| Reliability (logging, diagnose, retry, heal) | `tools/` (used by the workflow) |
| EDA automation | `automation/` (driven by `pcbflow dump`/`recon`/`drc`/`launch`) |

## Tests

```bash
python3 -m pytest            # if pytest is installed
# or standalone (no deps):
python3 tests/test_ipc.py && python3 tests/test_project.py \
  && python3 tests/test_phases.py && python3 tests/test_cli.py
```
