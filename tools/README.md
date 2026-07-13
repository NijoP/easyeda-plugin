# tools/ — Reliability Tools (Phase 1)

The first pieces of the [self-healing system](../reliability/README.md). Pure
Python 3 standard library — **nothing to install**. These make failures *visible* and
*explained* instead of cryptic.

## `doctor.py` — the preflight environment check

Run it before starting work (or any time something feels off). It checks your OS,
tools, and AXON setup, and tells you in plain English how to fix anything missing.

```bash
python3 tools/doctor.py           # readiness to get started (phases 1–2)
python3 tools/doctor.py --phase 4 # readiness up to a given workflow phase
python3 tools/doctor.py --all     # readiness for the whole pipeline (needs KiCad)
python3 tools/doctor.py --json    # machine-readable (for the AI)
python3 tools/doctor.py --ascii   # plain symbols if your terminal lacks emoji
```

It checks: operating system · Python · Git (+ identity) · AXON config files · Node.js ·
Chrome · rsync · VS Code · EasyEDA reachability · KiCad. Tools you don't need yet
(e.g. KiCad before phase 10) show as a note, not a blocker. **Exit code 0 = ready;
1 = a required tool is missing** — so the AI can gate on it automatically.

Design: [`../reliability/DEPENDENCY_VALIDATION.md`](../reliability/DEPENDENCY_VALIDATION.md).

## `axon_log.py` — structured logging

Gives every automation step two safeguards:

- **The `{ok, err}` envelope** — a step's success or failure is returned as *data* and
  logged, so an error is never silently swallowed.
- **The JSONL schema** — one record per attempt (timestamp, phase, step, command,
  error class, stack, recovery, human message) written to
  `projects/<board>/.logs/<phase>.jsonl`, readable by both the AI and you.

Read a phase log in plain English:
```bash
python3 tools/axon_log.py render projects/<board>/.logs/<phase>.jsonl
```

Design: [`../reliability/SELF_HEALING.md`](../reliability/SELF_HEALING.md) §1.

## `test_axon_log.py` — proof it works

```bash
python3 tools/test_axon_log.py    # PASS = envelope never swallows, schema correct
```

## What's next

Phase 1 is these two tools. Phases 2–5 (auto-diagnosis, retry wrappers, autonomous
resume, per-subsystem recovery, cross-platform hardening) are in
[`../reliability/ROADMAP.md`](../reliability/ROADMAP.md).
