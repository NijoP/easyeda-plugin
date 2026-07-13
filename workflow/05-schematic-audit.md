# Phase 5 — Schematic Audit

**Owning agent:** schematic-auditor · **Tool:** browser (headless readback) · **Autonomy:** Tier 1 (execute)

Before any PCB work, audit the schematic completely. **The schematic proceeds only
if all checks pass.** This is the cheap gate that protects every hour of layout.

- **Objective:** prove the realized schematic matches intent, net-for-net.
- **Inputs:** the live schematic; `net_connection.md` §membership; datasheets.
- **Method:** read the real board back headlessly and **reconstruct the netlist**
  from wire coordinates (the tool's own netlist API hangs headless — wires carry
  `.net`, pins don't → match by coordinate). Diff against the membership oracle.
- **Checks:** missing nets · floating pins · shorts · ERC violations · power
  integrity · signal integrity · net-naming consistency · interface validation ·
  datasheet compliance · design completeness.
- **Validation:** 0 shorts, 0 single-pin nets, 0 floating pins; analog ground ties
  to ground at exactly one point.
- **Deliverables:** `05_schematic_audit/audit_report.md` with a
  `PASS / CONDITIONAL(numbered) / FAIL` verdict.
- **Engineering checklist:**
  - [ ] No two pins accidentally merged (watch for collinear-wire auto-merge).
  - [ ] Every power pin on its intended rail (spot-check vs §membership).
  - [ ] Every net in `build_sheet.md` appears in `net_connection.md` and vice-versa.
- **Automation:** CDP extraction + coordinate matching + automatic diff
  ([`../automation/browser/`](../automation/browser/)); optionally a reviewer swarm,
  one per subsystem, with adversarial verification of each finding.
- **Human review:** confirms the verdict; client confirms any part/topology question
  it surfaces.
- **Exit gate:** all checks pass, verdict = PASS → proceed to placement.

> Run this **before** any PCB work, never as an afterthought — see
> [`../docs/09_VALIDATION.md`](../docs/09_VALIDATION.md).
