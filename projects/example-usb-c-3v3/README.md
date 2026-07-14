# Example — USB-C → 3.3 V power supply + status LED

A small, self-contained **worked reference** board that shows what a PCB Flow project looks
like at each phase. It's deliberately simple (8 parts, 1 layer of logic) so you can read the whole
thing in a few minutes, then copy the *shape* for your own board.

> **This is a learning example, not a template.** To start your own board, copy
> [`../_template`](../_template) — not this folder. See [`handbook/04`](../../handbook/04-your-first-project.md).

## What the board does
Takes 5 V from **USB-C**, regulates it to **3.3 V** with an LDO, and lights a **status LED**.
CC pins have the mandatory 5.1 kΩ pull-downs so a USB-C source actually supplies VBUS.

## What's in here (the full workflow — end to end)
| Phase | File | Shows |
|---|---|---|
| — | [`project.yaml`](project.yaml) | the decision/state manifest (never file paths) |
| 1 | [`00_brief/brief.md`](00_brief/brief.md) | the captured requirement |
| 1 | [`01_feasibility/feasibility.md`](01_feasibility/feasibility.md) | feasibility + power budget with real numbers |
| 2 | [`02_bom/bom.md`](02_bom/bom.md) | the validated BOM |
| 3–4 | [`04_schematic/net_connection.md`](04_schematic/net_connection.md) | the exact net-by-net connection list |
| 3–4 | [`04_schematic/netlist.enet`](04_schematic/netlist.enet) | the **machine-checkable** netlist (EasyEDA `.enet` v2.0.0) |
| 10 | [`11_routing/design_rules.json`](11_routing/design_rules.json) | the JLCPCB DRC/DFM ruleset for this board |

The schematic capture (EasyEDA, phases 3–4) and interactive placement are the **live front-end**
step. Everything downstream is **generated and committed**: the routed **KiCad board**
(`10_kicad_export/board.kicad_pcb`, from `tools/gen_example_board.py`), the **import diff**
proving the board matches the netlist, a `kicad-cli` **DRC-clean** report, exported **gerbers**,
and the **BOM** — all reproducible with one command (see below).

## Try the tooling against it
The netlist here is real — the shipped Python tools read it directly:

```bash
# The full offline phase-5 audit: netlist structure + ERC (electrical rule check)
python3 -m pcbflow.cli verify projects/example-usb-c-3v3/04_schematic/netlist.enet
#   → netlist structure: clean · ERC: 0 error / 0 warning · VERDICT: PASS

# Or the pieces individually:
python3 -m pcbflow.cli enet <netlist.enet>   # parse + structural verify
python3 -m pcbflow.cli erc  <netlist.enet>   # electrical rule check
python3 -m pcbflow.cli dfm  <board.json>     # DRC/DFM against the JLCPCB profile
```

```python
# Turn it into queryable design intelligence (the pcbmunch core)
from pcbflow.enet import Enet
ix = Enet.load("projects/example-usb-c-3v3/04_schematic/netlist.enet").design_index()
print(ix.net("+3V3"))          # who is on the 3V3 rail, its net class, pin count
print(ix.component("U1"))      # the LDO's nets + neighbours
```

## Reproduce it end-to-end
One command regenerates the board, runs every offline check, writes the phase reports, and
exports gerbers — ending in a `kicad-cli` **DRC-clean** board:

```bash
make example          # or: python3 tools/reproduce_example.py
```
It prints a per-step PASS/FAIL table and writes the reports into the phase folders
(`05_schematic_audit/`, `10_kicad_export/`, `12_verification/`). The DRC + gerber steps need
`kicad-cli` (KiCad); without it the netlist / ERC / import-diff checks still run. A reviewer
verifies the whole chain in a few minutes.

## How to use it as a reference
Read `brief → feasibility → bom → net_connection` in order — that's the discipline PCB Flow
applies to *every* board, scaled down. Then open the [handbook](../../handbook/README.md) and
run the same phases on your own copy of `_template`.
