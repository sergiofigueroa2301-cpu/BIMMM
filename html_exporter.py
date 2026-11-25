import html
import json


def generar_html(df_base, meta: dict, resumen_excel: dict, explicaciones: dict) -> str:
    """Genera un archivo HTML interactivo y autocontenido a partir del itemizado cargado."""
    records = df_base.to_dict(orient="records")
    payload = {
        "meta": meta,
        "resumen": resumen_excel,
        "explicaciones": explicaciones,
        "partidas": records,
    }
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    titulo = html.escape(meta.get("proyecto") or "Visor Didáctico de Itemizado BIM")
    ubicacion = html.escape(meta.get("ubicacion") or "")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Itemizado BIM — {titulo}</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --surface: #ffffff;
      --surface-2: #f1f5f9;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #64748b;
      --primary: #2563eb;
      --primary-soft: #eff6ff;
      --warn-bg: #fef3c7;
      --warn-border: #f59e0b;
      --warn-text: #92400e;
      --info-bg: #e0f2fe;
      --info-border: #0284c7;
      --info-text: #075985;
      --radius: 12px;
      --shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 320px 1fr;
      min-height: 100vh;
    }}
    aside {{
      background: var(--surface);
      border-right: 1px solid var(--border);
      padding: 20px;
      overflow-y: auto;
      max-height: 100vh;
      position: sticky;
      top: 0;
    }}
    main {{
      padding: 24px 32px;
      max-width: 1400px;
      width: 100%;
    }}
    h1 {{ margin: 0 0 6px; font-size: 1.75rem; }}
    h2 {{ margin: 0 0 12px; font-size: 1.15rem; }}
    h3 {{ margin: 16px 0 8px; font-size: 0.95rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }}
    .subtitle {{ color: var(--muted); margin-bottom: 18px; font-size: 0.95rem; }}
    .control-group {{ margin-bottom: 16px; }}
    label.check {{
      display: flex;
      gap: 8px;
      align-items: flex-start;
      font-size: 0.9rem;
      margin-bottom: 8px;
      cursor: pointer;
    }}
    input[type="text"], input[type="number"] {{
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.9rem;
      background: var(--surface);
      color: var(--text);
    }}
    .cap-list {{
      max-height: 220px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px;
      background: var(--surface-2);
    }}
    .cap-actions {{
      display: flex;
      gap: 8px;
      margin-bottom: 6px;
    }}
    .btn-sm {{
      border: 1px solid var(--border);
      background: var(--surface);
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.78rem;
      cursor: pointer;
    }}
    .btn-sm:hover {{ background: var(--surface-2); }}
    .btn-primary {{
      background: var(--primary);
      color: #fff;
      border: none;
      padding: 9px 14px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.9rem;
    }}
    .btn-primary:hover {{ filter: brightness(0.95); }}
    .days-row {{
      display: grid;
      grid-template-columns: 1fr 74px;
      gap: 8px;
      align-items: center;
      margin-bottom: 6px;
      font-size: 0.84rem;
    }}
    .alert {{
      padding: 12px 14px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.9rem;
      border-left: 4px solid;
    }}
    .alert-warn {{ background: var(--warn-bg); border-color: var(--warn-border); color: var(--warn-text); }}
    .alert-info {{ background: var(--info-bg); border-color: var(--info-border); color: var(--info-text); }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, minmax(180px, 1fr));
      gap: 14px;
      margin: 16px 0 22px;
    }}
    .kpi {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      box-shadow: var(--shadow);
    }}
    .kpi-label {{ font-size: 0.85rem; color: var(--muted); margin-bottom: 4px; }}
    .kpi-val {{ font-size: 1.45rem; font-weight: 700; }}
    .kpi-delta {{ font-size: 0.82rem; color: var(--primary); margin-top: 2px; }}
    .tabs {{
      display: flex;
      gap: 8px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 18px;
    }}
    .tab-btn {{
      background: none;
      border: none;
      padding: 10px 16px;
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -2px;
    }}
    .tab-btn.active {{ color: var(--primary); border-bottom-color: var(--primary); }}
    .tab-panel {{ display: none; }}
    .tab-panel.active {{ display: block; }}
    details.cap-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      margin-bottom: 10px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }}
    details.cap-card summary {{
      padding: 13px 16px;
      cursor: pointer;
      font-weight: 600;
      list-style: none;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }}
    details.cap-card summary:hover {{ background: var(--surface-2); }}
    .cap-body {{ padding: 0 16px 16px; border-top: 1px solid var(--border); }}
    .subcap-title {{
      margin: 14px 0 6px;
      font-weight: 700;
      color: #1e293b;
      font-size: 0.94rem;
    }}
    .item-list {{ margin: 0; padding-left: 18px; }}
    .item-list li {{ margin: 5px 0; font-size: 0.9rem; }}
    code {{
      background: var(--surface-2);
      padding: 2px 6px;
      border-radius: 5px;
      font-size: 0.84rem;
    }}
    .badge-zero {{
      background: var(--warn-bg);
      color: var(--warn-text);
      padding: 1px 6px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      margin-left: 4px;
    }}
    .charts-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      box-shadow: var(--shadow);
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 190px 1fr 110px;
      gap: 10px;
      align-items: center;
      margin: 8px 0;
      font-size: 0.85rem;
    }}
    .bar-label {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .bar-track {{
      background: var(--surface-2);
      border-radius: 6px;
      height: 18px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: linear-gradient(90deg, #2563eb, #38bdf8);
      border-radius: 6px;
    }}
    .bar-fill.time {{ background: linear-gradient(90deg, #0d9488, #34d399); }}
    .bar-val {{ text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }}
    #treemapBox {{ width: 100%; height: 340px; position: relative; }}
    .tm-node {{
      position: absolute;
      border: 1px solid rgba(255,255,255,0.85);
      color: #fff;
      padding: 5px 6px;
      font-size: 0.75rem;
      overflow: hidden;
      border-radius: 4px;
      cursor: default;
      transition: filter 0.15s;
    }}
    .tm-node:hover {{ filter: brightness(1.08); z-index: 2; }}
    .table-wrap {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: auto;
      max-height: 540px;
      box-shadow: var(--shadow);
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.87rem; }}
    th, td {{ padding: 9px 12px; border-bottom: 1px solid var(--border); text-align: left; }}
    th {{
      position: sticky;
      top: 0;
      background: var(--surface-2);
      font-weight: 600;
      z-index: 1;
    }}
    td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .tooltip {{
      position: fixed;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.92);
      color: #fff;
      padding: 7px 10px;
      border-radius: 6px;
      font-size: 0.8rem;
      display: none;
      z-index: 999;
      max-width: 280px;
    }}
    @media (max-width: 980px) {{
      .layout {{ grid-template-columns: 1fr; }}
      aside {{ position: static; max-height: none; border-right: none; border-bottom: 1px solid var(--border); }}
      .kpis {{ grid-template-columns: repeat(2, 1fr); }}
      .charts-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h3>🔎 Filtros</h3>
      <div class="control-group">
        <label class="check">
          <input type="checkbox" id="chkAtipicos" checked />
          <span>Excluir partidas &gt; 40% del total (limpiar errores)</span>
        </label>
        <label class="check">
          <input type="checkbox" id="chkSinPrecio" />
          <span>Ocultar partidas sin valorización ($0)</span>
        </label>
      </div>
      <div class="control-group">
        <input type="text" id="txtBuscar" placeholder="Buscar partida o ítem (ej: hormigón, LED)..." />
      </div>
      <div class="control-group">
        <h3>📂 Capítulos</h3>
        <div class="cap-actions">
          <button class="btn-sm" id="btnAllCaps" type="button">Todos</button>
          <button class="btn-sm" id="btnNoneCaps" type="button">Ninguno</button>
        </div>
        <div class="cap-list" id="capList"></div>
      </div>
      <div class="control-group">
        <h3>⏱️ Días estimados por capítulo</h3>
        <div id="daysInputs"></div>
      </div>
      <div class="control-group">
        <h3>💼 Cierre (GG / Util / IVA)</h3>
        <div class="days-row"><span>Gastos Generales ($)</span><input type="number" id="inpGG" min="0" step="500000" /></div>
        <div class="days-row"><span>Utilidades (%)</span><input type="number" id="inpUtil" min="0" max="100" step="1" /></div>
        <div class="days-row"><span>IVA (%)</span><input type="number" id="inpIva" min="0" max="50" step="1" /></div>
      </div>
    </aside>

    <main>
      <h1>🏗️ Visor Didáctico de Itemizado BIM</h1>
      <div class="subtitle">📍 {titulo}{f" — {ubicacion}" if ubicacion else ""} · Reporte HTML interactivo</div>
      <div id="alertsArea"></div>
      <section class="kpis" id="kpisArea"></section>

      <div class="tabs">
        <button class="tab-btn active" data-tab="tab1">📘 Explicación Didáctica</button>
        <button class="tab-btn" data-tab="tab2">📊 Gráficos</button>
        <button class="tab-btn" data-tab="tab3">📄 Tabla y Auditoría</button>
      </div>

      <section id="tab1" class="tab-panel active"></section>
      <section id="tab2" class="tab-panel">
        <div class="charts-grid">
          <div class="card">
            <h2>Distribución de Costos por Capítulo (Treemap)</h2>
            <div id="treemapBox"></div>
          </div>
          <div class="card">
            <h2>Tiempos Estimados por Capítulo (Días)</h2>
            <div id="timeBars"></div>
          </div>
        </div>
        <div class="card">
          <h2>Costo Directo por Capítulo (CLP)</h2>
          <div id="costBars"></div>
        </div>
      </section>
      <section id="tab3" class="tab-panel">
        <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
          <span id="tableCount" style="color: var(--muted); font-size: 0.9rem;"></span>
          <button class="btn-primary" id="btnCsv" type="button">⬇️ Descargar tabla filtrada (CSV)</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Capítulo</th>
                <th>Subcapítulo</th>
                <th>Ítem</th>
                <th>Designación</th>
                <th>U</th>
                <th class="num">Cantidad</th>
                <th class="num">Valor Unit.</th>
                <th class="num">Total</th>
              </tr>
            </thead>
            <tbody id="tableBody"></tbody>
          </table>
        </div>
        <div id="auditArea" style="margin-top: 18px;"></div>
      </section>
    </main>
  </div>
  <div class="tooltip" id="tooltip"></div>

  <script>
    const DATA = {data_json};
    const PALETTE = ["#2563eb", "#0891b2", "#0d9488", "#059669", "#65a30d", "#d97706", "#ea580c", "#dc2626", "#9333ea", "#4f46e5"];
    const clp = v => "$ " + Math.round(v).toLocaleString("es-CL");
    const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));

    const allCaps = [...new Set(DATA.partidas.map(p => p.Capitulo))];
    const state = {{
      selectedCaps: new Set(allCaps),
      days: Object.fromEntries(allCaps.map(c => [c, 20])),
      gg: Math.round(DATA.resumen?.GG?.monto ?? 0),
      util: Number(((DATA.resumen?.UTIL?.tasa ?? 0.15) * 100).toFixed(2)),
      iva: Number(((DATA.resumen?.IVA?.tasa ?? 0.19) * 100).toFixed(2)),
    }};

    document.getElementById("inpGG").value = state.gg;
    document.getElementById("inpUtil").value = state.util;
    document.getElementById("inpIva").value = state.iva;

    function buildCapControls() {{
      const capList = document.getElementById("capList");
      const daysInputs = document.getElementById("daysInputs");
      capList.innerHTML = "";
      daysInputs.innerHTML = "";
      allCaps.forEach(cap => {{
        const lbl = document.createElement("label");
        lbl.className = "check";
        const cb = document.createElement("input");
        cb.type = "checkbox";
        cb.checked = state.selectedCaps.has(cap);
        cb.addEventListener("change", () => {{
          if (cb.checked) state.selectedCaps.add(cap);
          else state.selectedCaps.delete(cap);
          render();
        }});
        lbl.appendChild(cb);
        lbl.appendChild(document.createTextNode(cap));
        capList.appendChild(lbl);

        const drow = document.createElement("div");
        drow.className = "days-row";
        const span = document.createElement("span");
        span.textContent = cap.slice(0, 26);
        span.title = cap;
        const inp = document.createElement("input");
        inp.type = "number";
        inp.min = 1;
        inp.max = 365;
        inp.value = state.days[cap];
        inp.addEventListener("input", () => {{
          state.days[cap] = Math.max(1, Number(inp.value) || 1);
          render();
        }});
        drow.appendChild(span);
        drow.appendChild(inp);
        daysInputs.appendChild(drow);
      }});
    }}

    function squarifyTreemap(items, x, y, w, h) {{
      if (!items.length || w <= 0 || h <= 0) return [];
      const total = items.reduce((s, d) => s + d.value, 0);
      if (total <= 0) return [];
      const rects = [];
      let cx = x, cy = y, cw = w, ch = h, remTotal = total;
      const sorted = [...items].sort((a, b) => b.value - a.value);
      sorted.forEach(item => {{
        const frac = item.value / remTotal;
        if (cw >= ch) {{
          const rw = cw * frac;
          rects.push({{ ...item, x: cx, y: cy, w: rw, h: ch }});
          cx += rw;
          cw -= rw;
        }} else {{
          const rh = ch * frac;
          rects.push({{ ...item, x: cx, y: cy, w: cw, h: rh }});
          cy += rh;
          ch -= rh;
        }}
        remTotal -= item.value;
      }});
      return rects;
    }}

    function getFiltered() {{
      const exclAtip = document.getElementById("chkAtipicos").checked;
      const hideZero = document.getElementById("chkSinPrecio").checked;
      const q = document.getElementById("txtBuscar").value.trim().toLowerCase();
      const totalBruto = DATA.partidas.reduce((s, p) => s + p.Total, 0);

      const atipicos = [];
      let rows = DATA.partidas.filter(p => {{
        if (exclAtip && totalBruto > 0 && p.Total > totalBruto * 0.4) {{
          atipicos.push(p);
          return false;
        }}
        return true;
      }});
      if (hideZero) rows = rows.filter(p => !p.Sin_Precio);
      rows = rows.filter(p => state.selectedCaps.has(p.Capitulo));
      if (q) {{
        rows = rows.filter(p =>
          p.Item.toLowerCase().includes(q) ||
          p.Designacion.toLowerCase().includes(q) ||
          p.Subcapitulo.toLowerCase().includes(q)
        );
      }}
      return {{ rows, atipicos }};
    }}

    function render() {{
      const {{ rows, atipicos }} = getFiltered();
      const sinPrecio = rows.filter(r => r.Sin_Precio);
      const totalDirecto = rows.reduce((s, r) => s + r.Total, 0);
      const activeCaps = allCaps.filter(c => rows.some(r => r.Capitulo === c));
      const diasTotales = activeCaps.reduce((s, c) => s + (state.days[c] || 20), 0);

      const gg = Number(document.getElementById("inpGG").value) || 0;
      const utilPct = Number(document.getElementById("inpUtil").value) || 0;
      const ivaPct = Number(document.getElementById("inpIva").value) || 0;
      const utilMonto = (totalDirecto + gg) * (utilPct / 100);
      const neto = totalDirecto + gg + utilMonto;
      const totalIva = neto * (1 + ivaPct / 100);

      let alertsHtml = "";
      if (atipicos.length) {{
        alertsHtml += `<div class="alert alert-warn">⚠️ Se excluyó automáticamente ${{atipicos.length}} partida(s) atípica(s) (&gt;40% del total bruto): ` +
          atipicos.map(a => `<strong>${{esc(a.Item)}} ${{esc(a.Designacion)}}</strong> (${{clp(a.Total)}})`).join(", ") +
          `. Puedes volver a incluirla en el panel izquierdo.</div>`;
      }}
      if (sinPrecio.length) {{
        alertsHtml += `<div class="alert alert-info">ℹ️ Hay <strong>${{sinPrecio.length}}</strong> partidas sin precio unitario ($0) en la vista actual: ` +
          sinPrecio.map(s => `<code>${{esc(s.Item)}}</code>`).join(", ") + `</div>`;
      }}
      document.getElementById("alertsArea").innerHTML = alertsHtml;

      document.getElementById("kpisArea").innerHTML = `
        <div class="kpi"><div class="kpi-label">💰 Costo Directo</div><div class="kpi-val">${{clp(totalDirecto)}}</div></div>
        <div class="kpi"><div class="kpi-label">🧾 Total c/ IVA</div><div class="kpi-val">${{clp(totalIva)}}</div><div class="kpi-delta">Neto: ${{clp(neto)}}</div></div>
        <div class="kpi"><div class="kpi-label">⏱️ Tiempo Estimado</div><div class="kpi-val">${{diasTotales}} días</div><div class="kpi-delta">~${{(diasTotales / 22).toFixed(1)}} meses</div></div>
        <div class="kpi"><div class="kpi-label">📋 Partidas</div><div class="kpi-val">${{rows.length}}</div><div class="kpi-delta">${{sinPrecio.length}} en $0</div></div>
      `;

      // Tab 1: Explicacion
      const tab1 = document.getElementById("tab1");
      if (!rows.length) {{
        tab1.innerHTML = `<div class="alert alert-warn">No hay partidas que coincidan con los filtros seleccionados.</div>`;
      }} else {{
        tab1.innerHTML = activeCaps.map(cap => {{
          const grp = rows.filter(r => r.Capitulo === cap);
          const totCap = grp.reduce((s, r) => s + r.Total, 0);
          const pct = totalDirecto ? (totCap / totalDirecto * 100) : 0;
          const capNum = grp[0].Cap_Num;
          const expl = DATA.explicaciones[capNum] || "Etapa constructiva del proyecto.";
          const subcaps = [...new Set(grp.map(r => r.Subcapitulo))];
          const subHtml = subcaps.map(sc => {{
            const srows = grp.filter(r => r.Subcapitulo === sc);
            const scTot = srows.reduce((s, r) => s + r.Total, 0);
            const header = sc !== cap ? `<div class="subcap-title">${{esc(sc)}} (${{clp(scTot)}})</div>` : "";
            const lis = srows.map(r => {{
              const badge = r.Sin_Precio ? `<span class="badge-zero">⚠️ sin precio</span>` : "";
              return `<li><strong>${{esc(r.Item)}} ${{esc(r.Designacion)}}</strong>: <code>${{r.Cantidad.toLocaleString("es-CL", {{maximumFractionDigits:2}})}} ${{esc(r.Unidad)}}</code> × ${{clp(r.Valor)}} = <strong>${{clp(r.Total)}}</strong>${{badge}}</li>`;
            }}).join("");
            return `${{header}}<ul class="item-list">${{lis}}</ul>`;
          }}).join("");
          return `<details class="cap-card">
            <summary><span>${{esc(cap)}}</span><span>${{clp(totCap)}} (${{pct.toFixed(1)}}%) · ⏱️ ${{state.days[cap]}} días</span></summary>
            <div class="cap-body"><div class="alert alert-info" style="margin-top:12px;">${{esc(expl)}}</div>${{subHtml}}</div>
          </details>`;
        }}).join("");
      }}

      // Tab 2: Graficos
      const capCosts = activeCaps.map((cap, idx) => ({{
        label: cap,
        value: rows.filter(r => r.Capitulo === cap).reduce((s, r) => s + r.Total, 0),
        color: PALETTE[idx % PALETTE.length],
      }}));
      const maxCost = Math.max(1, ...capCosts.map(c => c.value));
      document.getElementById("costBars").innerHTML = capCosts
        .slice()
        .sort((a, b) => b.value - a.value)
        .map(c => `
          <div class="bar-row">
            <div class="bar-label" title="${{esc(c.label)}}">${{esc(c.label)}}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${{(c.value / maxCost * 100).toFixed(2)}}%"></div></div>
            <div class="bar-val">${{clp(c.value)}}</div>
          </div>
        `).join("");

      const maxDays = Math.max(1, ...activeCaps.map(c => state.days[c] || 1));
      document.getElementById("timeBars").innerHTML = activeCaps.map(c => `
        <div class="bar-row" style="grid-template-columns: 160px 1fr 70px;">
          <div class="bar-label" title="${{esc(c)}}">${{esc(c)}}</div>
          <div class="bar-track"><div class="bar-fill time" style="width:${{((state.days[c] || 1) / maxDays * 100).toFixed(2)}}%"></div></div>
          <div class="bar-val">${{state.days[c]}} d</div>
        </div>
      `).join("");

      const tmBox = document.getElementById("treemapBox");
      const tmRects = squarifyTreemap(capCosts.filter(c => c.value > 0), 0, 0, tmBox.clientWidth || 500, 340);
      const tip = document.getElementById("tooltip");
      tmBox.innerHTML = "";
      tmRects.forEach(rc => {{
        const div = document.createElement("div");
        div.className = "tm-node";
        div.style.left = rc.x + "px";
        div.style.top = rc.y + "px";
        div.style.width = Math.max(0, rc.w) + "px";
        div.style.height = Math.max(0, rc.h) + "px";
        div.style.background = rc.color;
        const pct = totalDirecto ? (rc.value / totalDirecto * 100).toFixed(1) : "0.0";
        if (rc.w > 70 && rc.h > 36) {{
          div.innerHTML = `<strong>${{esc(rc.label)}}</strong><br>${{clp(rc.value)}} (${{pct}}%)`;
        }}
        div.addEventListener("mousemove", e => {{
          tip.style.display = "block";
          tip.style.left = (e.clientX + 12) + "px";
          tip.style.top = (e.clientY + 12) + "px";
          tip.innerHTML = `<strong>${{esc(rc.label)}}</strong><br>${{clp(rc.value)}} (${{pct}}%)`;
        }});
        div.addEventListener("mouseleave", () => tip.style.display = "none");
        tmBox.appendChild(div);
      }});

      // Tab 3: Tabla y Auditoria
      document.getElementById("tableCount").textContent = `Mostrando ${{rows.length}} partidas`;
      document.getElementById("tableBody").innerHTML = rows.map(r => `
        <tr>
          <td>${{esc(r.Capitulo)}}</td>
          <td>${{esc(r.Subcapitulo)}}</td>
          <td><code>${{esc(r.Item)}}</code></td>
          <td>${{esc(r.Designacion)}}</td>
          <td>${{esc(r.Unidad)}}</td>
          <td class="num">${{r.Cantidad.toLocaleString("es-CL", {{minimumFractionDigits:2, maximumFractionDigits:2}})}}</td>
          <td class="num">${{clp(r.Valor)}}</td>
          <td class="num"><strong>${{clp(r.Total)}}</strong></td>
        </tr>
      `).join("");

      let auditHtml = "";
      if (atipicos.length || sinPrecio.length) {{
        auditHtml += `<h3>🔍 Auditoría de datos del Excel</h3>`;
        if (atipicos.length) {{
          auditHtml += `<div class="alert alert-warn"><strong>Partidas atípicas (&gt;40%):</strong> ` +
            atipicos.map(a => `${{esc(a.Item)}} ${{esc(a.Designacion)}} (${{clp(a.Total)}})`).join("; ") + `</div>`;
        }}
        if (sinPrecio.length) {{
          auditHtml += `<div class="alert alert-info"><strong>Partidas con valorización en $0:</strong> ` +
            sinPrecio.map(s => `${{esc(s.Item)}} ${{esc(s.Designacion)}}`).join("; ") + `</div>`;
        }}
      }}
      document.getElementById("auditArea").innerHTML = auditHtml;
    }}

    document.querySelectorAll(".tab-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll(".tab-btn, .tab-panel").forEach(el => el.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(btn.dataset.tab).classList.add("active");
        if (btn.dataset.tab === "tab2") render();
      }});
    }});

    document.getElementById("btnAllCaps").addEventListener("click", () => {{
      state.selectedCaps = new Set(allCaps);
      buildCapControls();
      render();
    }});
    document.getElementById("btnNoneCaps").addEventListener("click", () => {{
      state.selectedCaps.clear();
      buildCapControls();
      render();
    }});
    ["chkAtipicos", "chkSinPrecio", "txtBuscar", "inpGG", "inpUtil", "inpIva"].forEach(id => {{
      document.getElementById(id).addEventListener("input", render);
    }});

    document.getElementById("btnCsv").addEventListener("click", () => {{
      const {{ rows }} = getFiltered();
      const headers = ["Capitulo", "Subcapitulo", "Item", "Designacion", "Unidad", "Cantidad", "Valor", "Total"];
      const csv = [headers.join(",")].concat(
        rows.map(r => headers.map(h => `"${{String(r[h] ?? "").replace(/"/g, '""')}}"`).join(","))
      ).join("\\n");
      const blob = new Blob(["\\uFEFF" + csv], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "itemizado_bim_filtrado.csv";
      a.click();
      URL.revokeObjectURL(url);
    }});

    window.addEventListener("resize", render);
    buildCapControls();
    render();
  </script>
</body>
</html>
"""
