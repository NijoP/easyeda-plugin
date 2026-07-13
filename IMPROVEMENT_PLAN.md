# IMPROVEMENT_PLAN.md — pcbflow → 10/10 (Phase 2)

Ordered workstreams that take pcbflow from v0.1.0-beta to the Definition-of-Done bar.
Sequenced by **risk to credibility** (the prompt's order): proof → machine-enforced gates →
robustness/file-parsing → CI → fixture corpus + tests → packaging → docs-truthing →
multi-agent packaging. Each workstream has a goal, DoD/ADOPT mapping, **file-level scope**,
**testable acceptance criteria**, effort (S/M/L), and dependencies.

Derived from the improvement-pattern analysis and `AUDIT.md` (top-10 fixes + measured gaps).
Nothing here is aspirational: every acceptance criterion is checkable in this repo.

---

## Environment reality (verified 2026-07-14, shapes the acceptance criteria)

| Tool | Status | Consequence for the plan |
|---|---|---|
| `kicad-cli` **10.0.4** | ✅ present | The proof example can reach **DRC-clean + gerbers fully offline on CI** (`kicad-cli pcb drc / export gerbers / sch export netlist`). No NEEDS-LIVE-VALIDATION for the KiCad side. |
| `python3 -m pcbnew` | ❌ not importable | Fine — project convention is *kicad-cli is DRC ground truth*; we deliberately avoid pcbnew. |
| `java` **21** | ✅ present | Optional autoroute (freerouting) possible as an *external* tool (timeout-wrapped), not a Python dep. Prefer a checked-in routed board verified by kicad-cli. |
| `node` **22** | ✅ present | Bridge server can run; but EasyEDA itself needs a live signed-in browser → **EasyEDA schematic capture + placement is the one true live boundary** (logged NEEDS-LIVE-VALIDATION). |
| sample real `.kicad_pcb` files | available locally | Reader golden tests use **our own** generated board; real boards are only an offline cross-check that the parser handles production files. |

**Net:** the worked example becomes fully reproducible offline — the `.enet` is the contract,
an import-diff proves the KiCad board matches it, and kicad-cli produces the DRC verdict +
gerbers. EasyEDA front-end capture is documented as the single honest manual step.

---

## Guardrails (apply to every workstream)

- **Never weaken human-in-the-loop.** No auto DRC sign-off, no auto fab order. Export only
  *assembles* files *after* a human approval-evidence file exists.
- **Zero/low-dependency pure Python** for all analyzers/parsers. A new runtime dependency
  requires written justification in the PR body. (Current runtime dep: `websockets`, CDP only.)
- **Prefer deletion/simplification over addition.** No speculative generality (YAGNI).
- **No aspirational docs.** Every claim links to a committed artifact or test, or it moves to
  `ROADMAP.md`.
- **Original implementation.** Analyzers and parsers are written from the published file-format
  specifications; only general engineering patterns are reused, never third-party code.
- **Conventional commits, one workstream ≈ one reviewable series**, `CHANGELOG.md` updated,
  full suite + `tools/doctor.py` run after each, then STOP for review.

---

## Traceability: Definition of Done → workstreams

| DoD | Requirement | Workstream(s) |
|---|---|---|
| **1 · PROOF** | example reproducible end-to-end, one command, ends DRC-clean + gerbers, committed real reports, <1 h for a stranger | **WS1** (+ WS2 reports, WS4 import-diff) |
| **2 · TRUST** | CI ubuntu/macos/windows green on main, badges, VALIDATION.md | **WS5** |
| **3 · ROBUSTNESS** | no dead-end step; timeouts/retries/manual-fallback; import verified by automated diff that fails loudly | **WS4** (+ WS3 export block) |
| **4 · QUALITY** | ≥80 % coverage on pure logic; golden-file parser/exporter tests; known-good AND known-bad fixture corpus | **WS2** (golden) + **WS6** (fixtures, coverage) |
| **5 · HONESTY** | every claim → artifact/test; unverifiable → ROADMAP or deleted | **WS0** (hotfix) + **WS8** (deep truthing + claims-linter) |
| **6 · DX** | pip/uvx installable, pinned deps, `pcbflow` CLI, versioned releases + changelog | **WS7** (+ WS9 agent packaging) |

## Traceability: ADOPT list → workstreams

H1 schema→WS2 · H2 offline S-expr reader→WS4 · H3 example reports→WS1 · H4 VALIDATION.md→WS5 ·
H5 agent manifests→WS9 · H6 install-guidance→WS7 · H7 trust rollup→WS2 · H9 stable ids→WS2 ·
P1 computed gates→WS3 · P2 hard-block export→WS3 · P3 fixture corpus→WS6 · P6 config table→WS7 ·
P7 packaging→WS7 · P8 source-of-truth linter→WS8 (+ WS6 phase/gate consistency test).
**Deferred to ROADMAP (YAGNI now):** P4 design-intent scoring, P5 VCS-checkpoint verbs,
H8 run-cache/capability-mode, P9 profiles, P10 Docker/release-please.

---

## WS0 · Honesty hotfix  *(effort: S · deps: none · DoD-5)*

**Goal:** stop shipping the two known-false headlines *before* the long proof work — a false
claim is a correctness bug. (Distinct from WS8, which is the deep, repo-wide truthing after the
machinery lands.)

**Scope (files):** `README.md` §7 (C8 "complete reference board" → "front-half worked example,
completing in WS1"), §8 (C14 "complete self-healing reliability layer" → "reliability *library*
— env-check/diagnosis/retry wired; logging + heal opt-in, live-recovery unvalidated"), §6
(fallback filename drift); `ROADMAP.md` (reconcile status with README); `automation/easyeda/README.md`
("used in phases 3,4,9" → "referenced by").

**Acceptance criteria:**
- No README claim lacks a backing artifact/test *or* an explicit hedge (grep audit of the words
  "complete", "auto-recover", "self-healing" — each occurrence backed or softened).
- README §7 ↔ example README ↔ ROADMAP tell one consistent story about example scope.
- Suite still 38/38.

---

## WS1 · PROOF — reproducible worked example, one command, DRC-clean + gerbers  *(L · deps: WS2, WS4 · DoD-1, H3)*

**Goal:** a stranger runs one command and, fully offline, reproduces the example from `.enet`
contract to a **kicad-cli-DRC-clean board + gerbers**, with committed real reports at each
phase. This is the credibility anchor. The board is the tiny existing USB-C→3V3 (8 parts) —
deliberately small so the <1 h bar is real.

**Scope (files):**
- Fill `projects/example-usb-c-3v3/`: `05_schematic_audit/audit.report.md` (harmonized ERC +
  structure), `06_placement_plan/…`, `08_visual_placement/…`, `09_placement_exec/…`,
  `10_kicad_export/board.kicad_pcb` + `import_diff.report.md`, `11_routing/board_routed.kicad_pcb`
  + `drc.report.md`, `12_verification/{drc.rpt, gerbers/, verification.report.md, bom.csv}`.
- `tools/reproduce_example.py` (+ `make example`) — runs the offline chain: enet → erc → dfm →
  verify → import-diff → `kicad-cli pcb drc` → `kicad-cli pcb export gerbers`, writing the
  committed reports. Windows-safe (pure `.py`, no `.sh`).
- The KiCad board is authored to match the `.enet`; **import-diff (WS4) proves board == netlist**;
  EasyEDA capture (phases 3–4, 8–9) documented as the one manual front-end step (VALIDATION.md).

**Acceptance criteria:**
- `python3 tools/reproduce_example.py` (or `make example`) exits **0 offline** on a clean clone.
- Every phase dir under the example is non-empty; committed reports show **real** tool output.
- Final step: `kicad-cli pcb drc` reports **0 violations** against the project's own ruleset;
  gerbers are produced and committed.
- `import_diff` reports **0 mismatches** between `netlist.enet` and `board.kicad_pcb`.
- A `handbook`/README section walks the repro in ≤ one screen; timed dry-run < 1 h.

---

## WS2 · Harmonized findings schema + stable IDs + trust rollup  *(M · deps: none · H1, H7, H9, DoD-4)*

**Goal:** one traceable finding shape for every check, so reports are diffable and every claim
carries its own evidence + confidence.

**Scope (files):**
- New `pcbflow/findings.py`: `finding(detector, rule_id, category, severity, confidence,
  evidence_source, summary, components, nets, recommendation, provenance)` factory; taxonomies
  (severity error/warning/info; confidence deterministic/heuristic/datasheet-backed; evidence
  topology/geometry/bom/heuristic_rule/…); **stable `id`** (sha256 of normalized locator);
  `sort_findings()` (deterministic); `trust_summary()` (by_confidence/by_evidence/level);
  `to_json()` / `to_markdown()` emitters.
- Migrate `pcbflow/erc.py`, `pcbflow/dfm.py`, and `pcbflow/geometry.py` spacing output onto it.
- Update `pcbflow/cli.py` `erc`/`dfm`/`verify` to render harmonized output (keep `--json`).
- New `tests/test_findings.py`; update `tests/test_erc.py`, `tests/test_dfm.py`.

**Acceptance criteria:**
- `erc`, `dfm`, spacing all emit the identical field set; `--json` validates against a schema.
- **Golden test:** re-running a check yields **byte-identical** IDs + ordering (stability proven).
- `trust_summary()` computes level from confidence mix; covered ≥95 %.
- Suite green; no new runtime dependency.

---

## WS3 · Machine-computed gates + hard-blocked export  *(M · deps: WS2 · P1, P2, DoD-3)*

**Goal:** turn the 12 checkpoints from asserted verdicts into **computed** gates, and make
phase-12 export refuse fab output unless gates pass **and** a human approved it.

**Scope (files):**
- New `pcbflow/gates.py`: `GateOutcome(name,status,summary,details)`; status hierarchy
  `EMPTY>BLOCKED>FAIL>WARN>PASS`; `compute_gate(phase, project)` running the phase's real checks
  (5 = structure+ERC; 6/9 = spacing; 11/12 = DFM + kicad-cli DRC); `project_gate()` combiner.
- Edit `pcbflow/project.py`: `record_verdict` may be fed by `compute_gate` (audit trail keeps
  who/what); `advance()` requires a computed PASS (human `CONDITIONAL` override stays explicit).
- New CLI verbs in `cli.py`: `gate <proj> <phase>` and `export <proj>` — export **hard-blocks**
  on any non-PASS gate and on a missing/invalid `approval.json` (`approved_by`, `approved_at_utc`,
  `scope`). Export never signs off and never orders.
- New `tests/test_gates.py`.

**Acceptance criteria:**
- `pcbflow gate` runs the real checks and returns a `GateOutcome` (not a stored assertion).
- `pcbflow export` **refuses** (nonzero) when any gate ≠ PASS *or* approval evidence absent —
  proven against a known-bad fixture (WS6); succeeds only with clean gates + approval file.
- Human-in-the-loop preserved: no code path signs a DRC or orders a board (grep-asserted in test).
- Suite green.

---

## WS4 · Robustness: offline KiCad S-expr reader + import-diff + tool-call hardening  *(M/L · deps: none; feeds WS1 · H2, DoD-3)*

**Goal:** verify the EasyEDA→KiCad hand-off with an automated diff that **fails loudly**, and
make every external-tool call survivable (timeout/retry/manual fallback).

**Scope (files):**
- New `pcbflow/kicad_sexp.py`: zero-dep S-expr tokenizer + reader for `.kicad_pcb`/`.kicad_sch`
  (components, pads, nets), written from the KiCad board file-format structure.
- New `pcbflow/import_diff.py`: compare `.enet` netlist vs KiCad board netlist → Findings (WS2);
  nonzero exit on any component/net mismatch.
- New CLI verb `import-check`; wire into WS1 phase-10 report.
- Harden subprocess calls (`tools/drc.py`, `automation/kicad/drc.sh` caller, `cdp.py`,
  `session._detect`): explicit timeouts, one bounded retry, a documented `--manual` fallback that
  prints exact commands; log *why* a bridge→CDP fallback happened.
- New `tests/test_kicad_sexp.py`, `tests/test_import_diff.py` (golden `.kicad_pcb` we generate).

**Acceptance criteria:**
- Reader parses a generated `.kicad_pcb` offline; golden test locks the parse.
- `import-check` **FAILS** on an injected net mismatch and **PASSES** on a matching pair (both tested).
- Every external-tool invocation has a timeout + a documented manual fallback; no silent swallow
  (session fallback logs a reason).
- Suite green; no new runtime dependency (stdlib parser).

---

## WS5 · CI + VALIDATION.md  *(M · deps: WS1, WS6 preferred (can land then tighten) · DoD-2, H4)*

**Goal:** prove it works on someone else's machine, on three OSes, on every push.

**Scope (files):**
- New `.github/workflows/ci.yml`: matrix ubuntu/macos/windows; steps = `pytest` + coverage gate
  (**≥80 % on the pure-logic modules**, measured on an explicit include-list), `make example`
  offline chain (ubuntu, where kicad-cli installs), `tools/doctor.py` smoke. Coverage/CI badges
  in `README.md`.
- New root `VALIDATION.md`: what's tested + current coverage numbers + the fixture corpus (WS6)
  + a **NEEDS-LIVE-VALIDATION ledger** (EasyEDA bridge/CDP capture, cross-platform launch,
  live browser recovery) each with **exact manual steps** and expected output.

**Acceptance criteria:**
- CI green on all three OSes on `main`; badges render.
- Coverage gate enforced in CI (fails the build under threshold).
- `VALIDATION.md` links every README claim to a test *or* a NEEDS-LIVE-VALIDATION entry (0 orphans).

---

## WS6 · Fixture corpus (known-good + known-bad) + close coverage gaps  *(M · deps: WS3 · P3, DoD-4)*

**Goal:** prove gates **block bad designs**, not just pass good ones; kill the 0 %/47 % surfaces.

**Scope (files):**
- New `tests/fixtures/` with a `manifest.json` (`expected_outcome` + `defect_class`): known-bad
  `floating_pin.enet`, `no_ground.enet`, `dangling_net.enet`; board-features `sub_min_track.json`,
  `hole_to_hole.json`, `edge_clearance.json`; plus the clean example (must PASS).
- New `tests/test_fixtures.py`: each bad fixture is BLOCKED by the correct gate; clean PASSES.
- New `tests/test_cli.py` expansion; test or **quarantine** `mcp_server.py`/`munch_server.py`
  (if quarantined: excluded from the coverage denominator *and* noted honestly in VALIDATION.md).
- A phase/agent/gate consistency test (lean P8): `phases.py` ↔ `workflow/` ↔ `agents/` ↔ gates align.

**Acceptance criteria:**
- Every gate has ≥1 known-bad it blocks + the clean example passes (all asserted).
- Pure-logic coverage **≥80 %**; 0 %-coverage modules are tested or explicitly quarantined.
- Consistency test fails if a phase/agent/gate mapping drifts.

---

## WS7 · Packaging + config discipline + agent-facing install-guidance  *(M · deps: WS2/WS3 stable CLI · P6, P7, H6, DoD-6)*

**Goal:** installable, pinned, self-documenting.

**Scope (files):**
- `pyproject.toml`: classifiers, pinned deps + a lockfile (`requirements.lock` via pip-tools —
  justify in PR; no new *runtime* dep), optional-dep groups, entry points confirmed.
- New `docs/CONFIG.md`: **single env/config table** (`EDA_BACKEND`, `EDA_BRIDGE_PORT_START/END`,
  `CDP_PORT`, tool timeouts) with defaults + honest limitation notes.
- New `install-guidance.md` (agent-facing quirks: Bridge port/handshake, Chrome/CDP profile
  clone, `kicad-cli` discovery, Windows `.py` vs `.sh`).

**Acceptance criteria:**
- `pipx install .` and `uvx pcbflow --version` both work from a clean checkout.
- Every env var appears exactly once in `docs/CONFIG.md` with a default; `pcbflow --help`
  documents every verb.
- Deps pinned; a CI job verifies the lockfile is in sync.

---

## WS8 · Deep docs-truthing + claims linter  *(S/M · deps: WS1–WS7 · DoD-5, P8)*

**Goal:** after the machinery is real, make every doc match the proven reality and keep it that way.

**Scope (files):** sweep `README.md`, `handbook/`, `workflow/`, `docs/`; move anything still
unproven to `ROADMAP.md`; add a claims ledger (in `VALIDATION.md`) mapping each README claim →
evidence. New `tools/check_claims.py`: parses README claim markers and asserts each links to a
committed artifact/test (run in CI).

**Acceptance criteria:**
- `tools/check_claims.py` passes: **0 unproven claims** outside `ROADMAP.md`.
- Re-grade the C1–C18 table from AUDIT.md: every prior PARTIAL/UNPROVEN is now PROVEN or moved.

---

## WS9 · Multi-agent packaging  *(M · deps: WS2/WS3 stable CLI · H5, DoD-6 — LAST)*

**Goal:** make the §5 "works with Claude/Codex/OpenCode/Cursor/Gemini + Action" claim *true* via
thin shims over one core.

**Scope (files):** `.claude-plugin/{plugin.json,marketplace.json}`, `.codex-plugin/plugin.json`,
`.cursor/rules/pcbflow.mdc`, `GEMINI.md`, `llms.txt`, and `action.yml` (a GitHub Action wrapping
the offline `verify`/`gate`). Each points at the single core (`agents/`, `workflow/`, `pcbflow`
CLI). Lean metadata-lint that validates each manifest points at the shared core.

**Acceptance criteria:**
- One manifest per advertised agent, each referencing the shared core (no duplicated logic).
- Metadata-lint passes in CI; the §5 claim now has a per-agent artifact behind it.

---

## Sequencing & dependency graph

```
WS0 (honesty hotfix, do first, S)
        │
WS2 (findings schema) ──┬─────────────► WS3 (gates + export)
        │               │                    │
        │               └──► WS1 (PROOF) ◄────┤   WS1 also needs:
        │                        ▲            │
WS4 (KiCad reader + import-diff)─┘            │
        │                                     │
        ├──────────────► WS6 (fixtures + coverage) ◄─ WS3
        │                        │
        └──────────────► WS5 (CI + VALIDATION.md) ◄─ WS1, WS6
                                 │
                         WS7 (packaging + config)
                                 │
                         WS8 (deep docs-truthing + claims linter)
                                 │
                         WS9 (multi-agent packaging)  [LAST]
```

**Recommended execution order (respects both the risk-priority and the build dependencies):**
**WS0 → WS2 → WS4 → WS3 → WS1 → WS6 → WS5 → WS7 → WS8 → WS9.**
Rationale: the schema (WS2) and the reader/import-diff (WS4) are the foundations the PROOF
(WS1) needs to emit *traceable* reports and a real import-diff; gates (WS3) then compute the
example's verdicts. Proof is the north star, but it is *built last among the core four* because
it consumes them — attempting it first would mean redoing the reports once the schema lands.
CI (WS5) follows once there's a fixture corpus (WS6) worth gating on. Packaging, deep truthing,
and agent shims close it out.

**Effort roll-up:** WS0 S · WS1 L · WS2 M · WS3 M · WS4 M/L · WS5 M · WS6 M · WS7 M · WS8 S/M ·
WS9 M. (~1 L, 6–7 M, 2 S.)

**After each workstream:** full suite + `tools/doctor.py`, report proven-now-vs-before, STOP for review.

---

**STOP — Phase 2 (plan) complete. Awaiting your approval to begin Phase 3 (execute WS0 → WS2 → …, one workstream per phase).**
