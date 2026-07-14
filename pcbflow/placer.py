"""Connectivity-driven placement optimizer — minimize expected trace length before routing.

Objective: **half-perimeter wirelength (HPWL)** = Σ over nets of the bounding-box span of the
components on that net — the standard, cheap proxy for total trace length. The optimizer is a
deterministic force-directed relaxation: components on a net attract toward the net's centroid,
decoupling caps are pulled hard to their IC, courtyards repel to avoid overlap, connectors stay
pinned to their assigned board edge (sliding along it toward their nets). No randomness, so a
given (netlist, intent) always yields the same plan.

Output: a machine-readable placement plan {ref: {x, y, rot, layer}} the agent executes in EasyEDA,
plus HPWL metrics. The plan is rendered (pcbflow.render_svg) for human approval before execution.
Pure Python 3 standard library.
"""


def comp_refs(enet):
    return sorted(c.designator or c.id for c in enet.components.values())


def net_refs(enet):
    """net -> set of component refs on it (drops single-ref nets, which don't constrain HPWL)."""
    out = {}
    for net, members in enet.nets().items():
        refs = {m.split(".", 1)[0] for m in members}
        if len(refs) >= 2:
            out[net] = refs
    return out


def hpwl(pos, nrefs):
    """Total half-perimeter wirelength over all nets (mm)."""
    total = 0.0
    for refs in nrefs.values():
        xs = [pos[r][0] for r in refs if r in pos]
        ys = [pos[r][1] for r in refs if r in pos]
        if len(xs) >= 2:
            total += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return total


def _edge_pos(edge, w, h, m):
    return {"left": (m, h / 2), "right": (w - m, h / 2),
            "top": (w / 2, m), "bottom": (w / 2, h - m)}[edge]


def _radius(intent, ref):
    sw, sh = intent.size(ref)
    return max(sw, sh) / 2.0


def _slide(p, edge, cx, cy, w, h, m):
    if edge in ("left", "right"):
        p[1] = min(h - m, max(m, cy))
        p[0] = m if edge == "left" else w - m
    else:
        p[0] = min(w - m, max(m, cx))
        p[1] = m if edge == "top" else h - m


def _avoid_keepouts(p, intent, ref):
    r = _radius(intent, ref)
    for k in intent.keepouts():
        x0, y0 = k["x"] - r, k["y"] - r
        x1, y1 = k["x"] + k["w"] + r, k["y"] + k["h"] + r
        if x0 < p[0] < x1 and y0 < p[1] < y1:               # inside the inflated keepout → eject
            dl, dr = p[0] - x0, x1 - p[0]
            dt, db = p[1] - y0, y1 - p[1]
            mn = min(dl, dr, dt, db)
            if mn == dl:
                p[0] = x0
            elif mn == dr:
                p[0] = x1
            elif mn == dt:
                p[1] = y0
            else:
                p[1] = y1


def optimize(enet, intent, iters=250, step=0.15):
    """Return (plan, metrics). plan = {ref:{x,y,rot,layer}}; metrics has hpwl_initial/hpwl_final."""
    w, h = intent.outline()
    m = 1.0
    refs = comp_refs(enet)
    nrefs = net_refs(enet)
    nets_of = {}
    for net, rs in nrefs.items():
        for r in rs:
            nets_of.setdefault(r, []).append(net)
    conns = intent.connectors()
    decouple = intent.decoupling()

    pos = {}
    movable = [r for r in refs if r not in conns]
    cols = max(1, int(len(movable) ** 0.5) or 1)
    rows = max(1, (len(movable) + cols - 1) // cols)
    for i, r in enumerate(movable):
        cx = m + (w - 2 * m) * ((i % cols) / (cols - 1) if cols > 1 else 0.5)
        cy = m + (h - 2 * m) * ((i // cols) / (rows - 1) if rows > 1 else 0.5)
        pos[r] = [cx, cy]
    for r, edge in conns.items():
        pos[r] = list(_edge_pos(edge, w, h, m))

    def centroid(net):
        rs = [p for p in nrefs[net] if p in pos]
        n = len(rs)
        return ((sum(pos[p][0] for p in rs) / n, sum(pos[p][1] for p in rs) / n)
                if n else (w / 2, h / 2))

    hpwl0 = hpwl(pos, nrefs)
    for _ in range(iters):
        for r in movable:
            nets = nets_of.get(r, [])
            fx = fy = 0.0
            for net in nets:
                cx, cy = centroid(net)
                fx += cx - pos[r][0]
                fy += cy - pos[r][1]
            if nets:
                fx /= len(nets)
                fy /= len(nets)
            ic = decouple.get(r)                            # decap → snap to its IC
            if ic and ic in pos:
                fx += (pos[ic][0] - pos[r][0]) * 1.5
                fy += (pos[ic][1] - pos[r][1]) * 1.5
            for o in refs:                                  # courtyard repulsion
                if o == r or o not in pos:
                    continue
                dx, dy = pos[r][0] - pos[o][0], pos[r][1] - pos[o][1]
                d2 = dx * dx + dy * dy
                sep = _radius(intent, r) + _radius(intent, o) + 0.2
                if 1e-9 < d2 < sep * sep:
                    d = d2 ** 0.5
                    push = (sep - d) / d * 0.5
                    fx += dx * push
                    fy += dy * push
            pos[r][0] = min(w - m, max(m, pos[r][0] + step * fx))
            pos[r][1] = min(h - m, max(m, pos[r][1] + step * fy))
            _avoid_keepouts(pos[r], intent, r)
        for r, edge in conns.items():
            nets = nets_of.get(r, [])
            if not nets:
                continue
            cx = sum(centroid(n)[0] for n in nets) / len(nets)
            cy = sum(centroid(n)[1] for n in nets) / len(nets)
            _slide(pos[r], edge, cx, cy, w, h, m)

    _legalize(pos, refs, intent, w, h, m, conns)             # remove courtyard overlaps (spread)
    plan = {r: {"x": round(pos[r][0], 3), "y": round(pos[r][1], 3), "rot": 0, "layer": "TOP"}
            for r in refs}
    return plan, {"hpwl_initial": round(hpwl0, 3), "hpwl_final": round(hpwl(pos, nrefs), 3),
                  "iters": iters}


def _legalize(pos, refs, intent, w, h, m, conns, gap=0.45, iters=800):
    """Spread overlapping courtyards apart until legal (or iters exhausted). Trades a little HPWL
    for a manufacturable placement. Connectors slide along their edge; others move freely."""
    for _ in range(iters):
        moved = False
        for i in range(len(refs)):
            for j in range(i + 1, len(refs)):
                a, b = refs[i], refs[j]
                if a not in pos or b not in pos:
                    continue
                dx, dy = pos[b][0] - pos[a][0], pos[b][1] - pos[a][1]
                d = (dx * dx + dy * dy) ** 0.5
                sep = _radius(intent, a) + _radius(intent, b) + gap
                if d < sep:
                    ux, uy = (dx / d, dy / d) if d > 1e-6 else (1.0, 0.0)
                    over = sep - d
                    for ref, sign in ((a, -1), (b, 1)):
                        if ref in conns:                     # connector: move only along its edge
                            if conns[ref] in ("left", "right"):
                                pos[ref][1] += sign * uy * over
                            else:
                                pos[ref][0] += sign * ux * over
                        else:
                            pos[ref][0] += sign * ux * over * 0.5
                            pos[ref][1] += sign * uy * over * 0.5
                        pos[ref][0] = min(w - m, max(m, pos[ref][0]))
                        pos[ref][1] = min(h - m, max(m, pos[ref][1]))
                    moved = True
        if not moved:
            break
