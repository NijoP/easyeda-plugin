# AUDIT.md — pcbflow read-only audit (Phase 1)

**Scope:** the entire pcbflow repo at `/home/nijo/axon`, read-only. Ground truth was
established by reading the source (not the docs about the source) and by running the suite.

**Measured facts (this run, 2026-07-14):**
- Test suite: **38 passed, 0 failed** (`tests/` 12 suites + 7 co-located). Fast (0.22 s), fully offline.
- Coverage on the `pcbflow/` package: **71 % overall**. Pure analyzers are strong
  (`dfm` 100 %, `geometry` 100 %, `ipc` 100 %, `congestion` 100 %, `phases` 100 %,
  `project` 98 %, `erc` 97 %, `routing` 93 %, `design_index` 92 %, `enet` 89 %).
  Weak/absent: `cli.py` **47 %**, `mcp_server.py` **0 %**, `munch_server.py` **0 %**.
- No CI (`.github/workflows/` absent). No coverage gate. No known-bad fixtures.
- No Light-Dome fingerprints (one template placeholder `BAT+` in `templates/net_connection.template.md`, correct).

---

## 1. Claims-vs-evidence table

Every substantive README claim, marked **PROVEN** / **PARTIAL** / **UNPROVEN**, with evidence.

| # | Claim (README §) | Verdict | Evidence |
|---|---|---|---|
| C1 | §1 "a workspace and a method, not a program you run" | **PROVEN** | Markdown method + helper scripts; `workflow/`, `agents/`, `pcbflow/`. |
| C2 | §2 "never sizes a power path below its limit, never signs off a DRC, never orders a board" | **PROVEN (as policy)** | No auto-signoff / auto-order code exists anywhere; `pcbflow/ipc.py`+`routing.py` size to IPC-2221. It's a design stance, not an enforced interlock — nothing *could* order a board, which is the point. |
| C3 | §3 "Twelve phases, each with a checkpoint… you never start a phase until the previous is confirmed correct" | **PROVEN (mechanism)** | `pcbflow/phases.py` (12 phases) ↔ `workflow/` (12 files) ↔ `pcbflow/project.py:63-79` `can_advance()`/`advance()` **hard-refuses** advance without a recorded `PASS`. ⚠️ Caveat (see §3 gap): the verdict is **human/agent-asserted** (`record_verdict`), **not machine-computed** from the checks — the guard is enforced, the *judgment* is not automated. |
| C4 | §4 repository-overview folder table | **PROVEN** | Every listed folder exists. |
| C5 | §5 "AI-model-agnostic… Claude Code, Codex, OpenCode, Cursor, Gemini CLI… instructions live in plain Markdown" | **PARTIAL** | `CLAUDE.md`+`AGENTS.md` are model-neutral markdown, so *any* agent can read them — true in principle. But there are **no per-agent adapters/manifests** (`.claude-plugin/`, `.codex-plugin/`, `.cursor/rules/`, `GEMINI.md`, `action.yml`). "Works with X" is aspirational beyond "reads markdown". |
| C6 | §6 "official Bridge (run-api-gateway)… raw Chrome-DevTools fallback" | **PARTIAL** | Both paths are real code: `automation/easyeda/bridge.py`+`session.py` (Bridge) and `automation/browser/cdp.py` (CDP). **Neither is validated end-to-end** — `bridge.py:27-28` self-documents "unit-tested against a stdlib mock… needs a live EasyEDA session to validate". Minor drift: §6 names the fallback "`tools/launch_easyeda.py`" but that only launches Chrome; the CDP driver is `automation/browser/cdp.py`. |
| C7 | §7 "run `python3 tools/doctor.py`… lists each tool ✅/⚠️/❌" | **PROVEN** | `tools/doctor.py` implements it; checks OS/Python/Git/Node/Chrome/rsync/KiCad. |
| C8 | §7 "`projects/example-usb-c-3v3/` is **a complete, real reference board**" | **UNPROVEN / OVERSTATED** | Only **5 of 12 phases** have artifacts (brief, feasibility, bom, net_connection, netlist.enet, design_rules.json). **No placement, no KiCad board, no routed board, no DRC report, no gerbers, no findings report.** The example's *own* README correctly disclaims this ("geometry… this text repo intentionally doesn't vendor"); the top-level README does not. `ROADMAP.md` marks it 🚧 in-progress — a status conflict with §7. |
| C9 | §7 "Its netlist is machine-checkable: `python3 -m pcbflow.enet …`" | **PROVEN** | Runs; `pcbflow/enet.py` `verify()` returns clean on the shipped `.enet` (89 % covered). |
| C10 | §8 "Built now: 12-phase workflow" | **PROVEN** | `phases.py` + `workflow/`. |
| C11 | §8 "Built now: AI agent roster" | **PROVEN** | `agents/*.md` — one per phase-owner. |
| C12 | §8 "Built now: EasyEDA + KiCad automation" | **PARTIAL** | Exists but live-untested + brittle (see §2 tech-debt). KiCad side is `kicad-cli` shell (`automation/kicad/drc.sh` + `tools/drc.py`), tested for the guard logic only. |
| C13 | §8 "Built now: engineering knowledge base" | **PROVEN** | `knowledge/` is real, substantive content: `learning-db.md` (8 seed lessons L1–L8 with heuristic/why/instance/validation/prevention), `design-standards.md` (concrete IPC/DFM numbers), `knowledge-graph.md`, `knowledge-inheritance.md`, `principles.md`. Not templates. |
| C14 | §8 "Built now: a **complete self-healing reliability layer** (environment check, logging, auto-diagnosis, retry, recovery, resume, cross-platform tools)" | **PARTIAL / OVERSTATED** | Component reality: env-check ✅ (`doctor.py`, tested); auto-diagnosis ✅ (`diagnose.py`, tested); retry ✅ (`recover.py` backoff, tested); resume ✅ logic (`state.py`, **untested**); cross-platform ⚠️ (`platform_utils.py` path-logic tested, **not** live-validated on macOS/Windows); **logging ⚠️ unwired** (`pcbflow_log.py` `PhaseLogger` **not called by any workflow/agent** — grep-confirmed); **recovery ⚠️** (`recovery.py` browser strategies are correct *logic* but self-flagged "must be validated against a real session"; `heal.py` engine **not wired into any workflow**). "Complete" and "self-healing" overstate a reliability **library that is largely not wired in**. |
| C15 | §9 "The AI stops for approval before drawing copper; leaves safety/DRC/fab-order to you" | **PROVEN (as policy)** | Consistent with C2; human-in-the-loop by construction. |
| C16 | §9 "The AI's reliability layer **auto-recovers** common failures" | **PARTIAL** | `heal.py`/`recovery.py` implement the loop but nothing invokes them in a real path (C14). Auto-recovery is *available*, not *active*. |
| C17 | §9 "developed and validated on Linux; cross-platform tooling… **still needs real-world validation** on macOS/Windows" | **PROVEN (honest disclaimer)** | This one is correctly hedged and matches reality — a model for how the other claims should read. |
| C18 | Provenance: "extracted from a real ESP32 robotics board, including the honest record of what went wrong" | **PROVEN** | `knowledge/learning-db.md` + `docs/13_LESSONS_LEARNED.md`. |

**Headline:** the *architecture* is honest and internally consistent (phases ↔ workflow ↔ code
gate ↔ knowledge all harmonize). The two material honesty defects are **C8** ("complete
reference board" — it's front-half only) and **C14** ("complete self-healing reliability
layer" — it's a partly-wired library). Both are fixable by *either* completing the thing *or*
truthing the sentence; DoD-5 requires one of the two.

---

## 2. Tech-debt inventory

### 2a. Untested / weakly-tested code
| Item | Evidence | Severity |
|---|---|---|
| `pcbflow/mcp_server.py` — **0 % coverage** | no `tests/test_mcp_server.py`; entire MCP surface unexercised | HIGH |
| `pcbflow/munch_server.py` — **0 % coverage** | no test; `pcbmunch` entry point unexercised | HIGH |
| `pcbflow/cli.py` — **47 % coverage** | pass-through/arg-wiring branches untested | MED |
| `tools/state.py` (resume) — no test file | resume logic unvalidated | MED |
| Live-session code cannot run in CI | `cdp.py` `_eval`/`_shot`, `dump_schematic.js`, `section_generator.template.js`, `api_probe.js`, `launch_easyeda.py` actual-launch | MED (inherent; needs mock/NEEDS-LIVE-VALIDATION log) |
| Bridge + CDP end-to-end untested | `bridge.py:27-28`, `test_bridge.py` mock-only | HIGH (this is the EasyEDA transport) |

### 2b. Unwired / dead-on-arrival code (exists, nothing calls it)
| Item | Evidence | Severity |
|---|---|---|
| `PhaseLogger` never instantiated in any workflow/agent | grep: only `tools/heal.py` docstring + tests | HIGH (contradicts C14 "logging") |
| `heal.py` engine not invoked from any real path | no import outside tests | HIGH (contradicts C16 "auto-recovers") |
| `recovery.py` browser strategies untested vs live | `recovery.py:14-15` self-flag | MED |

### 2c. Brittle automation selectors / assumptions (will break on EasyEDA change)
| Assumption | Location | Severity |
|---|---|---|
| `window._EXTAPI_ROOT_` root object | `dump_schematic.js:17` | HIGH |
| Field-name fallback chains (`designator\|\|name`, `p.num\|\|p.number\|\|p.name`) silently pick wrong field | `dump_schematic.js:13,30` | HIGH |
| library-search method probed among 6 candidates | `section_generator.template.js` / `api_probe.js` | HIGH (needs manual probe per EasyEDA build) |
| Bridge port range 49620-49629; CDP port 9222 | `bridge.py:37-38`, `cdp.py` | LOW (env-overridable) |
| `session._detect()` swallows *all* bridge exceptions → silent CDP fallback, no reason logged | `session.py` | MED |
| `recon.py` rounds wire coords to int — 0.5-unit segments could miss a junction | `recon.py:30,43` | MED |

### 2d. Platform assumptions
| Item | Evidence | Severity |
|---|---|---|
| rsync-based profile clone marked N/A on Windows | `doctor.py` rsync check; `launch_easyeda.py` "best effort" on locked Windows profile | MED |
| Bash `automation/kicad/drc.sh` vs `tools/drc.py` — cross-platform story only partially unified | drc via `.sh`; README says use `.py` on Windows | LOW |

### 2e. Doc/code drift
| Drift | Evidence | Severity |
|---|---|---|
| README §7 "complete reference board" vs example README "intentionally doesn't vendor geometry" vs ROADMAP "🚧 in progress" | three docs, three scopes | HIGH |
| README §6 names CDP fallback as `tools/launch_easyeda.py` (actually launches Chrome; driver is `automation/browser/cdp.py`) | §6 line ~140 | LOW |
| `automation/easyeda/README.md` implies `session.py` is used in "phases 3,4,9"; it's only in tests/examples | README vs grep | LOW |
| Example project dir missing 7 of 12 phase subdirs that `_template/` has | `projects/example-usb-c-3v3/` | MED |

### 2f. Dead files
**None found.** Every `cli.py` pass-through target and README-referenced file exists. (This is a genuine positive — no orphaned modules.)

---

## 3. Gap analysis vs. the target improvement patterns

| Improvement pattern | pcbflow today | Gap |
|---|---|---|
| **H1** harmonized findings schema (detector/rule_id/severity/confidence/evidence_source/recommendation/provenance/stable-id) | `erc.py` emits `{rule,severity,where,reason}`; `dfm.py` emits `{rule,severity,value,limit,where,reason}` — **two ad-hoc shapes, no confidence/evidence/provenance/id** | **FULL GAP** — foundational; blocks trust rollup + diffable reports |
| **H2** offline pure-Python S-expr reader for `.kicad_sch`/`.kicad_pcb` | none — KiCad only via `kicad-cli`; EasyEDA only via live browser | **FULL GAP** — blocks the import-diff (DoD-3) and offline KiCad tests |
| **H3** committed example reports (real output) | none vendored | **FULL GAP** — DoD-1 |
| **H6** agent-facing install-guidance (per-platform quirks) | human platform docs exist; no agent-facing quirks file | **PARTIAL GAP** |
| **H9** deterministic finding IDs + ordering | none | **FULL GAP** (follows H1) |
| **P1** machine-**computed** gates (run the checks → verdict) | advance-guard enforced (`can_advance`), but verdict is **asserted, not computed**; no `compute_gate()` running ERC/DFM | **PARTIAL GAP** — the guard exists; the automated judgment does not |
| **P2** hard-blocked `export_manufacturing_package` (gates PASS + human approval evidence) | none | **FULL GAP** — DoD-3, phase-12 |
| **P3** known-good **and** known-bad fixture corpus | 1 good example only | **FULL GAP** — DoD-4 (can't prove gates *block*) |
| **P6** single env/config table + honest limitation notes | §9 has honest notes; env vars (`EDA_BRIDGE_PORT_*`, `CDP_PORT`, `EDA_BACKEND`) scattered, no table | **PARTIAL GAP** |
| **H4** VALIDATION.md (what was tested, baselines, ledger) | `docs/09_VALIDATION.md` is a methodology *narrative*; no root VALIDATION.md with a tested corpus + NEEDS-LIVE-VALIDATION log | **PARTIAL GAP** — DoD-2 |
| **P7** packaging (lockfile/PyPI/uvx/CI/version-consistency) | `pyproject` (setuptools) + 3 entry points; **no lockfile, no PyPI, no CI, no release automation** | **PARTIAL GAP** — DoD-6 |
| **H5** multi-agent manifests (thin shim over one core) | agent job-description markdown only | **FULL GAP** (do last) |

---

## 4. Risk-ranked top-10 highest-impact fixes

Sequenced by the prompt's risk order (proof → machine gates → robustness/file-parsing → CI →
fixtures+tests → packaging → docs-truthing → agent packaging), with effort S/M/L.

| # | Fix | Why (DoD / risk) | Effort |
|---|---|---|---|
| 1 | **Truth the two overstated claims now** (C8 "complete reference board" → "front-half worked example"; C14 "complete self-healing reliability layer" → "reliability *library*, partly wired"), and reconcile README §7 ↔ example README ↔ ROADMAP. | DoD-5 honesty. A known-false claim is a bug; this is the cheapest possible fix and unblocks trust. | **S** |
| 2 | **Complete the worked example end-to-end** — add placement + KiCad export + routed board + DRC report + gerbers + a committed example *findings report*, with **one documented command** to re-verify, ending DRC-clean. Where a step needs a live tool this env lacks, ship the artifact + log it NEEDS-LIVE-VALIDATION with exact manual steps. | DoD-1 (proof) + H3. The single biggest credibility lever; a stranger must reproduce in <1 h. | **L** |
| 3 | **Harmonized findings schema [H1] + stable IDs [H9]** — one `finding()` factory (detector, rule_id, severity, confidence, evidence_source, components, nets, recommendation, provenance, stable id); migrate `erc.py`+`dfm.py`+`verify` onto it; add a trust rollup. | Foundation for every traceable output; DoD-5. | **M** |
| 4 | **Machine-computed gates + hard-blocked export [P1/P2]** — `compute_gate(phase)` that *runs* ERC/DFM/spacing and returns a `GateOutcome` feeding `record_verdict`; a phase-12 `export` verb that **refuses** unless all gates PASS **and** a human approval-evidence file exists. Never auto-sign-off. | DoD-3 + realizes the stated safety model in code. | **M** |
| 5 | **Offline KiCad S-expr reader [H2] + EasyEDA→KiCad import-diff** that fails loudly on net/component mismatch. | DoD-3 robustness; also unlocks offline KiCad tests in CI. | **M/L** |
| 6 | **Fixture corpus [P3]** — ≥1 known-BAD project per gate (floating pin, no-ground, sub-min track, hole-to-hole, edge clearance) that must stay blocked + the clean example that must pass; assert both in tests. | DoD-4 (prove gates block, not just pass). | **M** |
| 7 | **CI on GitHub Actions (ubuntu + macos + windows)** running the suite + coverage gate (≥80 % on pure logic) + README badges; a root **VALIDATION.md [H4]** documenting what's tested vs NEEDS-LIVE-VALIDATION. | DoD-2 (trust). Closes the biggest single credibility gap. | **M** |
| 8 | **Resolve the reliability-layer honesty gap** — either wire `PhaseLogger` + `heal()` into ≥1 automation path (prove the loop), or de-scope C14/C16 to "opt-in library"; add a live-session smoke test logged NEEDS-LIVE-VALIDATION. | DoD-5; removes "aspirational" from a headline claim. | **M** |
| 9 | **Cover the 0 %/47 % modules** — test or mark-experimental `mcp_server.py`+`munch_server.py`; raise `cli.py` coverage; add `session._detect` logging + `recon.py` float-match note. | DoD-4 quality; kills the largest untested surfaces. | **M** |
| 10 | **Packaging + config discipline [P7/P6/H6]** — pinned/locked deps, `pip`/`uvx`-installable, single env/config table, agent-facing install-guidance; **defer** multi-agent manifests [H5] to the very end. | DoD-6 (DX). | **M** |

---

**STOP — Phase 1 (audit) complete. Awaiting your review before Phase 2 (IMPROVEMENT_PLAN.md).**
