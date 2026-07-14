"""Pure-Python SVG visual map of a placement plan — the artifact the engineer approves BEFORE any
placement executes (human checkpoint #1). Draws the board outline, keep-outs, component courtyards
with reference designators, and the ratsnest (net connection lines) so trace-length intent is
visible. No dependencies. Pure Python 3 standard library.
"""


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(plan, intent, enet, path=None, px_per_mm=12.0):
    from .placer import net_refs
    w, h = intent.outline()
    pw, ph = w * px_per_mm, h * px_per_mm
    S = px_per_mm
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{pw:.0f}" height="{ph:.0f}" '
           f'viewBox="0 0 {pw:.0f} {ph:.0f}">',
           f'<rect x="0" y="0" width="{pw:.0f}" height="{ph:.0f}" fill="#0d1117"/>',
           f'<rect x="1" y="1" width="{pw-2:.0f}" height="{ph-2:.0f}" fill="none" '
           f'stroke="#3fb950" stroke-width="2"/>']

    for k in intent.keepouts():
        out.append(f'<rect x="{k["x"]*S:.1f}" y="{k["y"]*S:.1f}" width="{k["w"]*S:.1f}" '
                   f'height="{k["h"]*S:.1f}" fill="none" stroke="#f85149" '
                   f'stroke-width="1" stroke-dasharray="4 3"/>')

    # ratsnest: star each net to its centroid
    for refs in net_refs(enet).values():
        pts = [(plan[r]["x"], plan[r]["y"]) for r in refs if r in plan]
        if len(pts) >= 2:
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            for x, y in pts:
                out.append(f'<line x1="{x*S:.1f}" y1="{y*S:.1f}" x2="{cx*S:.1f}" y2="{cy*S:.1f}" '
                           f'stroke="#30363d" stroke-width="0.6"/>')

    for ref, p in sorted(plan.items()):
        sw, sh = intent.size(ref)
        x, y = (p["x"] - sw / 2) * S, (p["y"] - sh / 2) * S
        edge = intent.connector_edge(ref)
        color = "#d29922" if edge else "#58a6ff"
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sw*S:.1f}" height="{sh*S:.1f}" '
                   f'fill="none" stroke="{color}" stroke-width="1.2"/>')
        out.append(f'<text x="{p["x"]*S:.1f}" y="{p["y"]*S:.1f}" fill="#c9d1d9" font-size="9" '
                   f'text-anchor="middle" dominant-baseline="middle">{_esc(ref)}</text>')

    out.append("</svg>")
    svg = "\n".join(out)
    if path:
        from pathlib import Path
        Path(path).write_text(svg, encoding="utf-8")
    return svg
