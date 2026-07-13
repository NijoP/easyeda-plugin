# architecture/ — Architecture Audit & Target Design

The foundational architecture package for PCB Flow as an **AI-native Electronics Engineering
Workspace**. Produced by reverse-engineering the *contracts and engineering decisions* of
mature ECAD ecosystems (EasyEDA/JLCEDA, KiCad) — **no code copied** — and synthesizing a
tool-agnostic target architecture.

> **Status: audit / design. Not yet implemented** (except Phase 0 transport, already merged).
> Do not build beyond Phase 0 until this audit is approved.

| Doc | What it is |
|---|---|
| [`00_AUDIT_REPORT.md`](00_AUDIT_REPORT.md) | **The deliverable** — learnings, adopt/avoid, gap analysis, roadmap |
| [`01_EASYEDA_TEARDOWN.md`](01_EASYEDA_TEARDOWN.md) | EasyEDA subsystem-by-subsystem reverse-engineering |
| [`02_KICAD_TEARDOWN.md`](02_KICAD_TEARDOWN.md) | KiCad subsystem-by-subsystem + the convergence table |
| [`03_TARGET_ARCHITECTURE.md`](03_TARGET_ARCHITECTURE.md) | The 7-layer tool-agnostic architecture + CAD-adapter seam |
| [`04_KNOWLEDGE_GRAPH.md`](04_KNOWLEDGE_GRAPH.md) | Concepts, relationships, data/decision/validation/automation flows |

**Reading order:** `01`+`02` (learnings) → `03` (design) → `04` (graph) → `00` (verdict +
roadmap). Start at `00` for the executive view.

**Relationship to `docs/`:** `docs/00–17` are the *methodology + board-design knowledge* (incl.
[`docs/17_UPSTREAM_TOOLING_VERDICT.md`](../docs/17_UPSTREAM_TOOLING_VERDICT.md), the repo-level
verdict). This `architecture/` package is the *platform architecture* built on those learnings.
Upstream asset pointers: [`knowledge/upstream/`](../knowledge/upstream/README.md).
