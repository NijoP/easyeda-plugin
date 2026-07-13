# Recovery Playbooks

Step-by-step recovery for each subsystem. Each playbook: **Symptoms → Detect →
Auto-recover → Fallback → Escalate (plain-English)**. These are what the self-healing
engine ([`SELF_HEALING.md`](SELF_HEALING.md)) executes per fault class.

---

## EasyEDA — session / auth (EDA-1/2/3, BR-3)
- **Symptoms:** HTTP 401/403; a login form appears on the editor tab; writes rejected.
- **Detect:** intercept HTTP status; check for the login DOM before/after a step.
- **Auto-recover:** re-`rsync` the logged-in profile if launched from a stale clone;
  reload the editor; retry the step once.
- **Fallback:** pause the phase at its checkpoint; keep all work.
- **Escalate:** *"Your EasyEDA session expired — please log in again; I'll continue
  from where we stopped. No work is lost."*

## EasyEDA — renderer hang (EDA-7)
- **Symptoms:** evals stop returning; screenshots time out; page won't navigate.
- **Detect:** any eval exceeds a hang threshold (e.g. 20 s) with no result.
- **Auto-recover:** browser-level `Target.createTarget(editorURL)` → `Target.closeTarget(hungTab)`
  → reopen project → replay the last (unsaved) step from the manifest checkpoint.
- **Fallback:** full Chrome relaunch from the clone.
- **Escalate (rare):** *"The EasyEDA window froze (a known glitch). I restarted it and
  replayed the last step — it recovered."* **Prevention:** never probe `*.create`
  signatures in a loop; save after each block.

## EasyEDA — rate limit / server (EDA-5/6)
- **Detect:** HTTP 429/5xx.
- **Auto-recover:** exponential backoff (1/4/16 s, 3×) + slow the part-search cadence.
- **Escalate:** only if retries exhaust — *"EasyEDA is throttling or having a hiccup;
  I'll keep retrying. Nothing to do."*

## EasyEDA — component generation (EDA-10)
- **Detect:** empty search result / no token match / array-part rejected.
- **Auto-recover:** broaden the query → try the LCSC id → try an alternate package.
- **Escalate:** *"I couldn't find a match for `<part>` in the library — please pick a
  part or give me an LCSC number."*

## Chrome / CDP (BR-1/2/4/5/6)
- **Detect:** no `:9222` socket; launch error; Singleton lock; edit-lock banner.
- **Auto-recover:** `rm Singleton*` and relaunch with debug flags; if edit-locked,
  close the duplicate session and retry; re-attach to the correct single editor tab.
- **Fallback:** re-clone the profile; full relaunch.
- **Escalate:** *"Please close any extra EasyEDA browser windows and make sure one is
  open and signed in, then say 'retry'."*

## KiCad — import (KI-1/2/3/4)
- **Detect:** footprint count in ≠ out; missing nets; missing mounting holes.
- **Auto-recover:** remap known footprints; **restore mounting holes** (they don't
  survive PADS export); re-verify fidelity (0 dropped, sub-µm residual).
- **Escalate:** *"These footprints didn't come across from EasyEDA: `<list>`. I need a
  KiCad footprint for each before routing."*

## KiCad — DRC / phantom (KI-5/6)
- **Detect:** `kicad-cli` missing; no `.kicad_pro` sibling next to the board.
- **Auto-recover:** always run DRC via `automation/kicad/drc.sh` (copies the ruleset
  first). **Never** run bare `kicad-cli pcb drc`.
- **Escalate:** *"KiCad's command-line tool isn't installed — install KiCad, then say
  'retry'."* (This is the highest-value guard in the toolchain — KI-6 ships bad boards
  silently.)

## Node.js / Python scripts (SC-1/2/3/6/7)
- **Detect:** non-zero exit; import error; timeout; the `{ok:false,err}` envelope.
- **Auto-recover:** run the missing-dependency install step; retry transient timeouts
  once with a longer budget; **never swallow** an error (return it as data).
- **Fallback:** checkpoint and stop after max attempts.
- **Escalate:** *"A helper needs `<package>` installed — run `<exact command>` and say
  'retry'."*

## Git / publishing (auth)
- **Detect:** push rejected (401/403); no credential helper.
- **Auto-recover:** none possible without a credential — this is inherently human.
- **Escalate:** *"I saved everything locally but couldn't publish to GitHub — you need
  to sign in (a Personal Access Token or the VS Code GitHub login). Your work is safe
  and committed."* **Note:** commits are always local-safe; only the upload needs you.

## VS Code / crash / resume (ST-2/5)
- **Detect:** on start, `project.yaml` shows a phase started but not `PASS`; stray
  `.logs/*.jsonl`.
- **Auto-recover:** read the manifest → find the last committed (done) step → replay
  only the incomplete step → announce the resume point.
- **Escalate:** none normally — *"Resuming `<board>` at Phase N, step '<x>'; the
  previous step passed and is saved."*

## Placement (Phase 9)
- **Detect:** real-geometry audit finds spacing violations; stale snapshot suspected.
- **Auto-recover:** re-`getAll()` in a fresh eval; surgically re-place the few
  residual violators (don't re-tune relaxation — it oscillates); re-audit.
- **Escalate:** *"Two parts can't both fit where the plan wants them — I need you to
  approve moving `<x>` or resizing the board."*

## Routing (Phase 11)
- **Detect:** unrouted nets remain after passes; DRC errors.
- **Auto-recover:** rip-up-reroute the obstructing tracks (not re-floorplan);
  collision-checked stitching; re-run `drc.sh` until clean.
- **Escalate:** *"A few fine-pitch connections need a manual hand — here's exactly
  which and a step-by-step for them."* (The interactive tail is expected on dense
  boards.)

## Engineering validation (any audit)
- **Detect:** a check returns CONDITIONAL/FAIL.
- **Auto-recover:** apply the numbered fixes it can (re-derivable edits); re-verify.
- **Escalate:** present the remaining items as a plain checklist for your decision.

---

Every playbook ends the same way: **the engineer's work is never lost, and they're
told in plain English what (if anything) to do.**
