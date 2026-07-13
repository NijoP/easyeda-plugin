# automation/browser/ — Headless CDP Driver + Netlist Reconstruction

How agents read the *real* EasyEDA board back — the backbone of the verification
layer. Used in phases 4, 5, 9.

## Why it exists

EasyEDA is a cloud web app with no offline API. The only way to read real board
state programmatically is to drive the running editor over Chrome DevTools Protocol
and call its in-page API (`window._EXTAPI_ROOT_`).

## The launch recipe (each step is mandatory)

```bash
# 1. clone the LOGGED-IN profile (a fresh profile launches logged out — cookies are
#    bound to the OS keyring, unreachable from a script-launched Chrome)
rsync -a --exclude '*/Cache' ~/.config/google-chrome/ ~/.cache/eda-chrome-profile/
# 2. remove the locks
rm -f ~/.cache/eda-chrome-profile/Singleton*
# 3. launch on the CLONE with remote debugging (never the default profile; OAuth
#    blocks automation-controlled Chrome)
google-chrome-stable --user-data-dir="$HOME/.cache/eda-chrome-profile" \
      --remote-debugging-port=9222 "https://easyeda.com/editor"
```

Drive `:9222` with a **raw websocket client** — a generic devtools MCP spawns its
own browser and won't attach. One session at a time (two = cloud edit-lock fails
writes). The clone is wiped on reboot → re-`rsync` each session.

## Netlist reconstruction (the tool's netlist API hangs headless)

Pins carry **no** net; **wires do.** Rebuild pin→net by coordinate match: for each
wire endpoint `(x,y)` record its `.net`; for each pin, look up the net at its
`(x,y)`. This is the Phase-5 verification oracle. The net resolver *lags* after a
bulk wire create — re-dump before trusting a FLOAT reading.

## Hang recovery

A wrong `*.create` or a blocking modal freezes the renderer. Recover at the
**browser level**: `Target.createTarget` (fresh tab) → `Target.closeTarget` (hung
tab). Prevention: never probe `*.create` in a loop; save often.

> **Cross-platform launch:** instead of the bash recipe above, run
> `python3 tools/launch_easyeda.py` (Windows: `python tools\launch_easyeda.py`) — it
> clones the profile, clears locks, and launches Chrome with the debug port on any OS.

## Files (runnable)

| File | What it does |
|---|---|
| [`cdp.py`](cdp.py) | the CDP driver — `eval` JS in the editor tab, `shot` a screenshot, `tabs` / `version` |
| [`recon.py`](recon.py) | rebuild the netlist (pin → net) from a schematic dump |
| [`test_recon.py`](test_recon.py) | test for the reconstructor (`python3 automation/browser/test_recon.py`) |

## The verification pipeline

```bash
python3 tools/launch_easyeda.py                                   # open EasyEDA (debug port)
python3 automation/browser/cdp.py eval automation/easyeda/dump_schematic.js > dump.json
python3 automation/browser/recon.py dump.json netlist.json       # rebuild the netlist
python3 automation/browser/cdp.py shot board.png                 # optional sanity screenshot
```
Then diff `netlist.json` against `net_connection.md` — that's the phase-5 audit.

Full CDP design: [`../../docs/07_BROWSER_AUTOMATION.md`](../../docs/07_BROWSER_AUTOMATION.md).
