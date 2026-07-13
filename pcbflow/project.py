"""Project state — the orchestrator's source of truth.

Enforces the two governance rules that keep work safe:
  - "place nothing over wrong": you cannot advance a phase without a PASS verdict.
  - resume-safe: state is a plain JSON file (no YAML dependency), so a crash never
    loses where you are.

State lives in  projects/<name>/pcbflow_state.json .
"""
import json
from pathlib import Path

from . import phases

_VALID = ("PASS", "CONDITIONAL", "FAIL", "PENDING")


class Project:
    def __init__(self, path):
        self.path = Path(path)                       # projects/<name>/
        self.state_file = self.path / "pcbflow_state.json"

    @property
    def name(self):
        return self.path.name

    # --- lifecycle ---
    @classmethod
    def init(cls, projects_dir, name, description=""):
        p = cls(Path(projects_dir) / name)
        p.path.mkdir(parents=True, exist_ok=True)
        if not p.state_file.exists():
            p._write({"name": name, "description": description,
                      "current_phase": phases.FIRST, "verdicts": [], "decisions": []})
        return p

    def _read(self):
        if not self.state_file.exists():
            raise FileNotFoundError(f"no project at {self.path} — run `pcbflow init {self.name}` first")
        return json.loads(self.state_file.read_text())

    def _write(self, state):
        self.state_file.write_text(json.dumps(state, indent=2))

    # --- phase state ---
    def current_phase(self):
        return self._read()["current_phase"]

    def record_verdict(self, phase_no, verdict, note="", date=""):
        verdict = verdict.upper()
        if verdict not in _VALID:
            raise ValueError(f"verdict must be one of {_VALID}")
        phases.phase(phase_no)                       # validate the phase number
        s = self._read()
        s["verdicts"].append({"phase": phase_no, "verdict": verdict, "note": note, "date": date})
        self._write(s)
        return s

    def latest_verdict(self, phase_no):
        vs = [v for v in self._read()["verdicts"] if v["phase"] == phase_no]
        return vs[-1] if vs else None

    def can_advance(self):
        v = self.latest_verdict(self.current_phase())
        return bool(v and v["verdict"] == "PASS")

    def advance(self):
        cur = self.current_phase()
        if not self.can_advance():
            raise RuntimeError(
                f"phase {cur} ({phases.phase_name(cur)}) has no PASS verdict — not advancing "
                "(place nothing over wrong)")
        nxt = phases.next_phase(cur)
        if nxt is None:
            return cur                               # already at the last phase
        s = self._read()
        s["current_phase"] = nxt
        self._write(s)
        return nxt

    def status(self):
        s = self._read()
        cur = s["current_phase"]
        return {
            "name": s["name"],
            "current_phase": cur,
            "phase_name": phases.phase_name(cur),
            "owning_agent": phases.phase_agent(cur),
            "latest_verdict": self.latest_verdict(cur),
            "verdicts": s["verdicts"],
        }
