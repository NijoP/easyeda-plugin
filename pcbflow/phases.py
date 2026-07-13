"""The 12-phase pipeline definition — the single source of truth for phase order,
names, and the agent that owns each. Mirrors workflow/ (the human docs)."""

# (number, slug, owning-agent)
PHASES = [
    (1, "requirement-analysis", "feasibility-analyst"),
    (2, "bom-planning", "bom-planner"),
    (3, "easyeda-initialization", "schematic-generator"),
    (4, "schematic-generation", "schematic-generator"),
    (5, "schematic-audit", "schematic-auditor"),
    (6, "placement-planning", "placement-planner"),
    (7, "placement-knowledge-graph", "placement-planner"),
    (8, "visual-placement", "placement-planner"),
    (9, "automated-placement", "placement-planner"),
    (10, "export-to-kicad", "router"),
    (11, "ai-routing", "router"),
    (12, "final-verification", "verification-engineer"),
]

_BY_NUM = {n: (n, name, agent) for (n, name, agent) in PHASES}
FIRST, LAST = 1, 12


def phase(n):
    if n not in _BY_NUM:
        raise ValueError(f"no phase {n} (valid {FIRST}..{LAST})")
    return _BY_NUM[n]


def phase_name(n):
    return phase(n)[1]


def phase_agent(n):
    return phase(n)[2]


def next_phase(n):
    phase(n)                      # validate
    return n + 1 if n < LAST else None


def is_last(n):
    return phase(n)[0] == LAST
