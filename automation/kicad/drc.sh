#!/usr/bin/env bash
# drc.sh — the DRC GROUND TRUTH for a KiCad board.
#
# kicad-cli reads its rules from the sibling .kicad_pro. A bare .kicad_pcb reports
# the weak built-in defaults as "clean" — the phantom-DRC trap. This wrapper copies
# the operative ruleset next to the board, THEN runs kicad-cli. Never run a bare
# `kicad-cli pcb drc` on a naked board file.
#
# Usage:  drc.sh <board.kicad_pcb> [ruleset.kicad_pro]
# Exit:   non-zero if there are DRC violations (--exit-code-violations).

set -euo pipefail

BOARD="${1:?usage: drc.sh <board.kicad_pcb> [ruleset.kicad_pro]}"
RULESET="${2:-}"

if [[ ! -f "$BOARD" ]]; then
  echo "drc.sh: board not found: $BOARD" >&2; exit 2
fi

PRO_SIBLING="${BOARD%.kicad_pcb}.kicad_pro"

# If a ruleset was supplied, place it beside the board (this is the whole point).
if [[ -n "$RULESET" ]]; then
  if [[ ! -f "$RULESET" ]]; then echo "drc.sh: ruleset not found: $RULESET" >&2; exit 2; fi
  cp -f "$RULESET" "$PRO_SIBLING"
fi

if [[ ! -f "$PRO_SIBLING" ]]; then
  echo "drc.sh: WARNING — no sibling .kicad_pro next to the board." >&2
  echo "drc.sh: results will use DEFAULT rules and may be PHANTOM-CLEAN. Supply a ruleset." >&2
fi

REPORT="${BOARD%.kicad_pcb}.drc.rpt"

kicad-cli pcb drc \
  --severity-error \
  --exit-code-violations \
  --schematic-parity \
  --output "$REPORT" \
  "$BOARD"

echo "drc.sh: report → $REPORT"
