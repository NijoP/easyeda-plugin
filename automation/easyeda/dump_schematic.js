/* ============================================================================
 * PCB Flow — dump the live schematic to JSON (for headless verification)
 * ----------------------------------------------------------------------------
 * Emits {components, wires} in the shape the netlist reconstructor expects:
 *   components: [{des, name, lcsc, pins:[{num, name, x, y}]}]
 *   wires:      [{net, line:[x1,y1,x2,y2,...]}]
 * Wires carry the net; pins do not — recon.py matches pins to wire vertices.
 *
 * RUN (headless, via the CDP driver):
 *   python3 automation/browser/cdp.py eval automation/easyeda/dump_schematic.js > dump.json
 *   python3 automation/browser/recon.py dump.json netlist.json
 *
 * ⚠️  Field names (designator/pin num) vary by EasyEDA build — run api_probe.js
 *     first and adjust the marked lines if your build differs.
 * ========================================================================== */
(async () => {
  const eda = window._EXTAPI_ROOT_ || window.eda;   // CDP context uses _EXTAPI_ROOT_

  const comps = [];
  const all = await eda.sch_PrimitiveComponent.getAll();
  for (const c of all) {
    const pid = c.primitiveId || c.id || c.pid;
    let pins = [];
    try { pins = await eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId(pid); } catch (e) {}
    comps.push({
      des:  c.designator || c.name || null,          // <- adjust per api_probe.js
      name: c.device || c.symbolName || c.name || null,
      lcsc: c.manufacturerId || null,
      pins: (pins || []).map(p => ({
        num:  p.num != null ? p.num : (p.number != null ? p.number : p.name),  // <- adjust
        name: p.name,
        x: p.x, y: p.y
      }))
    });
  }

  // wires carry .net and a flat point list (.line or .points, build-dependent)
  const rawWires = await eda.sch_PrimitiveWire.getAll();
  const wires = (rawWires || []).map(w => ({ net: w.net, line: w.line || w.points || [] }));

  return { components: comps, wires: wires };   // cdp.py returns this as {ok:true, v:{...}}
})();
