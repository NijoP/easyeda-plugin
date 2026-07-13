"""Electrical Rule Check (ERC) — the schematic audit you run FIRST on any board.

Operates purely on the `.enet` netlist (pcbflow.enet) — no live tool, no geometry — so it
runs offline the moment you have a netlist, which is exactly when you're starting a fresh
board. It catches the connectivity mistakes that waste a layout: floating pins, dangling nets,
a power rail with no decoupling, a missing ground.

These are *topology* checks (what's inferable from connectivity alone). Pin-direction/type
conflict checking needs electrical pin types the netlist doesn't reliably carry — flagged as a
known limit rather than guessed. Pairs with pcbflow.dfm (manufacturability) and the phase-5 gate.
Pure Python 3 standard library.
"""
import re

from .design_index import _GND, _POWER

_CAP = re.compile(r"^C\d", re.I)      # capacitor designator (C1, C12…) → decoupling presence


def _viol(rule, severity, where, reason):
    return {"rule": rule, "severity": severity, "where": where, "reason": reason}


def run_erc(enet):
    """Run ERC on an Enet. Returns a list of violation dicts {rule, severity, where, reason}."""
    V = []
    nets = enet.nets()                       # net -> ['REF.pin(name)', ...]

    # E-GND: a board must have a ground net
    if not any(_GND.match(n) for n in nets):
        V.append(_viol("no_ground", "error", "<board>",
                       "no ground net found (expected GND/GNDA/AGND/DGND/PGND)"))

    # E-FLOAT: pins connected to nothing
    for fp in enet.floating_pins():
        V.append(_viol("floating_pin", "error", f"{fp['des']}.{fp['pin']}",
                       "pin is not connected to any net"))

    # per-net checks
    for net, members in nets.items():
        refs = {m.split(".", 1)[0] for m in members}
        npins = len(members)
        is_power, is_gnd = bool(_POWER.match(net)), bool(_GND.match(net))

        # E-DANGLE: a named net that reaches only one pin (a wire to nowhere)
        if npins == 1 and not net.startswith("$"):
            sev = "error" if (is_power or is_gnd) else "warning"
            V.append(_viol("single_pin_net", sev, net,
                           f"net '{net}' connects only {members[0]} — dangling / unterminated"))

        # E-DECOUPLE: a power rail with no capacitor anywhere on it
        if is_power and npins >= 2 and not any(_CAP.match(r) for r in refs):
            V.append(_viol("power_no_decoupling", "warning", net,
                           f"power rail '{net}' has no decoupling capacitor on it"))

    return V


def report(violations):
    """Summarize ERC results (mirrors dfm.report): pass iff no error-severity findings."""
    errs = sum(1 for v in violations if v["severity"] == "error")
    warns = len(violations) - errs
    by_rule = {}
    for v in violations:
        by_rule[v["rule"]] = by_rule.get(v["rule"], 0) + 1
    return {"total": len(violations), "errors": errs, "warnings": warns,
            "by_rule": by_rule, "pass": errs == 0}
