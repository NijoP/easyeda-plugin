# 02 · KiCad — Architecture Teardown

Reverse-engineered from the [`KiCad` org](https://github.com/orgs/KiCad/repositories)
(100 repos — `kicad-source-mirror`, `kicad-symbols`/`-footprints`/`-packages3D`,
`kicad-library-utils`, `kicad-footprint-wizards`, `kicad-templates`, the deprecated
`kicad-python`) plus the well-documented file formats, the DRC rule language, `kicad-cli`,
and the KiCad 9 **IPC API** (`kipy`, developed on GitLab). GitHub is a **read-only mirror**;
KiCad's real home is GitLab. We study the *architecture and contracts*, not to reproduce C++.

> **Thesis of KiCad's design:** a native C++ application built on an **explicit,
> serialized object model** (BOARD → FOOTPRINT → PAD/TRACK/VIA/ZONE), with **text
> s-expression files as the source of truth**, a **data-driven DRC constraint engine**, and
> automation offered at two altitudes: **`kicad-cli`** (headless, stable, the CI contract)
> and the **IPC API** (out-of-process, versioned, the interactive contract).

---

## A. Subsystem-by-subsystem

### A1 · Data model — *an explicit, typed board object graph*
- **Model:** `BOARD` owns `FOOTPRINT`s (which own `PAD`s, graphics), `PCB_TRACK`/`PCB_ARC`,
  `PCB_VIA`, `ZONE` (copper pours), `PCB_SHAPE`, `PCB_TEXT`, `NETINFO`. Schematic side:
  `SCHEMATIC` → `SCH_SHEET` → `SCH_SYMBOL`/`SCH_LINE`/`SCH_LABEL`. Every object is typed with
  a layer, net, and geometry.
- **Connectivity:** computed by a dedicated `CONNECTIVITY_DATA` engine (ratsnest, net
  propagation) — **derived, not stored as truth**; nets are IDs resolved from labels/pins.
- **Contrast with EasyEDA:** KiCad's model is *stricter and more explicit* (real classes,
  not attribute bags), which is why its DRC can be rigorous.

### A2 · File format — *s-expressions as durable source*
- `.kicad_pcb`, `.kicad_sch`, `.kicad_sym`, `.kicad_mod` are **s-expression** text: diffable,
  git-friendly, forward/back-compatible via a version token. `.kicad_pro` is **JSON** holding
  project settings, **net classes, and DRC rules**. Library tables (`sym-lib-table`,
  `fp-lib-table`) map nicknames → paths.
- **Lesson:** *text-first, human-diffable formats* make geometry reviewable and
  version-controllable — the discipline our "commit the artifact" gate needs.

### A3 · DRC / ERC — *a data-driven constraint engine*
- **Architecture:** DRC is a **rule engine**, not hardcoded checks. Rules (in `.kicad_pro`
  / a custom-rules DSL) express **constraints** (clearance, track width, hole size, annular
  ring, courtyard, silk) guarded by **conditions** (net class, layer, area) with a
  **severity**. The engine evaluates constraints against the connectivity + geometry.
- **ERC:** schematic-side electrical checks (pin-type conflict matrix, unconnected, power
  driven, bus/label consistency).
- **Why it's powerful:** rules are **data**; you author manufacturer profiles as rule sets,
  not code. This is the same shape as EasyEDA's data-driven DFM — **strong cross-tool
  convergence: DRC/DFM should be a swappable rule document.**

### A4 · Automation — *two deliberate altitudes*
- **`kicad-cli` (headless, stable):** `pcb drc`, `pcb export gerbers/drill/step/pdf`,
  `sch export netlist/bom`, `sch erc`. Deterministic, scriptable, **the correct CI/verification
  contract** — and already our DRC ground truth.
- **IPC API (`kipy`, KiCad 9+):** an **out-of-process** Python API talking to a running KiCad
  over a socket (protobuf), versioned, decoupled from the C++ ABI. Supersedes the legacy
  **in-process SWIG `pcbnew`** module (which coupled scripts to the binary's ABI).
- **Deprecated:** the GitHub `KiCad/kicad-python` (SWIG-era) → community `atait/kicad-python`.
- **Lesson:** offer automation at **two altitudes** — a *stable headless verifier* (kicad-cli)
  and an *out-of-process interactive API* (kipy) — and never couple in-process.

### A5 · Libraries — *curated, checkable, generatable*
- `kicad-symbols` / `kicad-footprints` / `kicad-packages3D`: official, versioned libraries.
- `kicad-library-utils`: **KLC (Library Convention) compliance checkers** — automated linting
  of symbols/footprints against a written standard.
- `kicad-footprint-wizards`: **parametric generators** (footprints from parameters).
- **Lesson:** parts should be **validated against a convention** and **generated from
  parameters**, not trusted from fuzzy vendor search (the exact failure our project hit).

### A6 · Rendering / export — *plotter abstraction*
- A `PLOTTER` hierarchy (Gerber/PDF/SVG/PS) renders the same board model to many outputs;
  3D via the packages3D + a viewer. **Rendering is a projection of the model** — screenshots
  are never truth (aligns with our "verify geometry from coordinates" rule).

### A7 · Project lifecycle — *project file as settings hub*
- `.kicad_pro` centralizes net classes, DRC rules, and settings; the board/schematic
  reference it. **Lesson:** keep *rules + intent* in a project-level config, separate from
  geometry — a board without its rules sidecar yields **phantom DRC** (a bug our project hit:
  a bare `.kicad_pcb` DRC'd against defaults reports garbage).

---

## B. Engineering principles KiCad demonstrates

| Principle | Evidence | Take for us |
|---|---|---|
| **Explicit typed object model** | BOARD/FOOTPRINT/PAD/ZONE | our internal board model should be typed, not dicts-forever |
| **Text-first, diffable source** | s-expr files | commit geometry as reviewable source |
| **Data-driven rule engine** | DRC constraints+conditions+severity | DRC/DFM = rule documents, tool-agnostic |
| **Derived connectivity** | CONNECTIVITY_DATA/ratsnest | netlist is computed from intent, not hand-kept |
| **Two automation altitudes** | kicad-cli + kipy | stable verifier + out-of-process API |
| **Convention-checked libraries** | KLC checkers, wizards | validate/generate parts, don't trust search |
| **Rules live with the project** | .kicad_pro | never DRC a board without its ruleset |

---

## C. What to ADOPT · REDESIGN · AVOID

**ADOPT (conceptually):** `kicad-cli` as the **verification ground truth** (done); the
**data-driven DRC rule model** (constraints + conditions + severity) as our tool-agnostic
rule schema; **text-first diffable geometry**; the **KLC-checker + parametric-generator**
approach to libraries; the **project-holds-rules** discipline (no phantom DRC); the
**kipy out-of-process** pattern as our KiCad interactive adapter.

**REDESIGN:** we don't want KiCad's monolithic native app coupling — we want its *contracts*
(cli, files, rules, kipy) behind a **CAD-adapter interface** so KiCad is one backend among
several.

**SIMPLIFY:** skip the GUI, the SWIG in-process path, and most `.pretty` libraries beyond
what we consume; use `kicad-cli` + `kipy` + selected libraries only.

**NEVER COPY:** the C++ source, the SWIG binding, or the deprecated `kicad-python`. Bind to
`kicad-cli` (subprocess) and `kipy` (socket) — stable, out-of-process, license-clean.

---

## D. EasyEDA vs KiCad — the convergent lessons

| Dimension | EasyEDA | KiCad | Convergent principle for us |
|---|---|---|---|
| Source of truth | typed document trees | s-expr files | **structured, versioned source; geometry derived** |
| Connectivity | net-name merge | CONNECTIVITY_DATA | **netlist from intent, name-keyed** |
| Rules | DFM plugin (data) | DRC engine (data) | **rules are swappable data documents** |
| Automation | out-of-proc Bridge | kicad-cli + kipy | **out-of-process, multi-altitude, envelope’d** |
| Routing | external engines bridged | (freerouting import) | **adapt external routers; no custom one** |
| Extensibility | plugin runtime | (fewer plugins) | **kernel + adapters/plugins** |
| Libraries | LCSC-linked | KLC-checked + wizards | **validate + generate parts** |

Both, independently, converge on: **structured source + derived geometry + data-driven rules
+ out-of-process automation + external routing.** That convergence is the strongest signal
for our own architecture.
