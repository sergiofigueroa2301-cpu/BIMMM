from pathlib import Path
import re

import openpyxl
import pandas as pd
import plotly.express as px
import streamlit as st

from html_exporter import generar_html

DEFAULT_EXCEL = Path(__file__).with_name("Itemizado BIM.xlsx")

EXPLICACIONES = {
    "1": "Permisos, instalación de faenas y preparación del terreno.",
    "2": "Estructura principal: fundaciones, muros y techumbre.",
    "3": "Acabados visibles: pisos, revestimientos, puertas, ventanas y pintura.",
    "4": "Veredas, accesos y pavimentos exteriores.",
    "5": "Áreas verdes, especies vegetales y paisajismo.",
    "6": "Equipamiento exterior como escaños, basureros y señalética.",
    "7": "Redes de agua potable, alcantarillado y artefactos sanitarios.",
    "8": "Tableros, cableado, iluminación y conectividad eléctrica.",
    "9": "Obras adicionales de cierre y seguridad.",
    "10": "Aseo profundo y entrega final de la obra.",
}


def clp(valor: float) -> str:
    return f"$ {valor:,.0f}".replace(",", ".")


def _to_float(val) -> float | None:
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    text = str(val).strip()
    if not text:
        return None
    text = text.replace("$", "").replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        parts = text.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _clean_text(val) -> str:
    if val is None:
        return ""
    return str(val).strip()


def _detect_header(ws) -> tuple[int | None, int | None]:
    for r in range(1, min(30, ws.max_row + 1)):
        for c in range(1, min(15, ws.max_column + 1)):
            if _clean_text(ws.cell(r, c).value).upper() == "ITEM":
                return r, c
    return None, None


@st.cache_data
def cargar_excel(source: str | bytes, nombre_archivo: str = ""):
    if isinstance(source, bytes):
        from io import BytesIO

        wb = openpyxl.load_workbook(BytesIO(source), data_only=True)
    else:
        wb = openpyxl.load_workbook(source, data_only=True)

    ws = wb.active
    fila_hdr, col_ini = _detect_header(ws)
    if fila_hdr is None or col_ini is None:
        raise ValueError("No se encontró la columna 'ITEM' en las primeras 30 filas.")

    meta = {"proyecto": "", "ubicacion": ""}
    for r in range(1, fila_hdr):
        etiqueta = _clean_text(ws.cell(r, col_ini).value).upper().rstrip(":")
        valor = _clean_text(ws.cell(r, col_ini + 1).value)
        if "PROYECTO" in etiqueta and valor:
            meta["proyecto"] = valor.strip("“”\"")
        elif "UBICACI" in etiqueta and valor:
            meta["ubicacion"] = valor

    partidas = []
    resumen_excel = {}
    cap_num, cap_nom, subcap_nom = "0", "0. General", ""

    for r in range(fila_hdr + 1, ws.max_row + 1):
        item = _clean_text(ws.cell(r, col_ini).value)
        desig = _clean_text(ws.cell(r, col_ini + 1).value)
        unidad = _clean_text(ws.cell(r, col_ini + 2).value)
        cant = _to_float(ws.cell(r, col_ini + 3).value)
        val = _to_float(ws.cell(r, col_ini + 4).value)
        tot = _to_float(ws.cell(r, col_ini + 5).value)

        etiqueta_resumen = _clean_text(ws.cell(r, col_ini + 3).value).upper()
        if not item and etiqueta_resumen in {"DIRECTO", "GG", "UTIL", "NETO", "IVA", "TOTAL"}:
            resumen_excel[etiqueta_resumen] = {
                "tasa": val,
                "monto": 0.0 if tot is None else tot,
            }
            continue

        if not item and not desig:
            continue

        if re.fullmatch(r"\d+", item):
            cap_num = item
            cap_nom = f"{item}. {desig}"
            subcap_nom = ""
            continue

        if cant is None:
            if item and desig:
                if item == f"{cap_num}.1" and any(
                    p["Cap_Num"] == cap_num and p["Item"].startswith(f"{cap_num}.9")
                    for p in partidas
                ):
                    item = f"{cap_num}.10"
                subcap_nom = f"{item} {desig}"
            continue

        if item and tot is not None:
            valor_num = 0.0 if val is None else val
            partidas.append(
                {
                    "Cap_Num": cap_num,
                    "Capitulo": cap_nom,
                    "Subcapitulo": subcap_nom or cap_nom,
                    "Item": item,
                    "Designacion": desig,
                    "Unidad": unidad or "GL",
                    "Cantidad": cant,
                    "Valor": valor_num,
                    "Total": tot,
                    "Sin_Precio": valor_num == 0 or tot == 0,
                }
            )

    df = pd.DataFrame(partidas)
    return df, meta, resumen_excel


def main():
    st.set_page_config(page_title="Itemizado BIM", page_icon="🏗️", layout="wide")
    st.title("🏗️ Visor Didáctico de Itemizado BIM")

    archivo_subido = st.sidebar.file_uploader("Sube tu Excel (.xlsx)", type=["xlsx"])
    if archivo_subido is not None:
        df_base, meta, resumen_excel = cargar_excel(
            archivo_subido.getvalue(), archivo_subido.name
        )
        origen_texto = f"Archivo cargado: `{archivo_subido.name}`"
    elif DEFAULT_EXCEL.exists():
        df_base, meta, resumen_excel = cargar_excel(str(DEFAULT_EXCEL), DEFAULT_EXCEL.name)
        origen_texto = f"Archivo local cargado automáticamente: `{DEFAULT_EXCEL.name}`"
    else:
        st.info("👈 Sube tu archivo `Itemizado BIM.xlsx` en la barra lateral.")
        st.stop()

    if meta.get("proyecto") or meta.get("ubicacion"):
        subtitulo = " — ".join(p for p in [meta.get("proyecto"), meta.get("ubicacion")] if p)
        st.caption(f"📍 {subtitulo} | {origen_texto}")
    else:
        st.caption(origen_texto)

    if df_base.empty:
        st.error("No se encontraron partidas válidas en el archivo Excel.")
        st.stop()

    st.sidebar.header("🔎 Filtros")
    excluir_atipicos = st.sidebar.checkbox(
        "Excluir partidas > 40% del total (limpiar errores)", value=True
    )
    ocultar_sin_precio = st.sidebar.checkbox(
        "Ocultar partidas sin valorización ($0)", value=False
    )
    busqueda = st.sidebar.text_input("Buscar partida o ítem", placeholder="Ej: hormigón, LED, 2.3...")

    total_bruto = df_base["Total"].sum()
    atipicos_df = pd.DataFrame()
    df = df_base.copy()

    if excluir_atipicos and total_bruto > 0:
        mascara_atipica = df["Total"] > total_bruto * 0.40
        atipicos_df = df[mascara_atipica].copy()
        df = df[~mascara_atipica]

    if ocultar_sin_precio:
        df = df[~df["Sin_Precio"]]

    capitulos_disponibles = list(df["Capitulo"].unique())
    caps = st.sidebar.multiselect(
        "Capítulos:", capitulos_disponibles, default=capitulos_disponibles
    )
    df = df[df["Capitulo"].isin(caps)]

    if busqueda.strip():
        q = busqueda.strip().lower()
        df = df[
            df["Item"].str.lower().str.contains(q, na=False)
            | df["Designacion"].str.lower().str.contains(q, na=False)
            | df["Subcapitulo"].str.lower().str.contains(q, na=False)
        ]

    html_report = generar_html(df_base, meta, resumen_excel, EXPLICACIONES)
    st.sidebar.download_button(
        "🌐 Descargar visor interactivo (.html)",
        data=html_report.encode("utf-8"),
        file_name="visor_itemizado_bim.html",
        mime="text/html",
    )

    if df.empty:
        st.warning("No hay partidas que coincidan con los filtros seleccionados.")
        st.stop()

    st.sidebar.subheader("⏱️ Días estimados por capítulo")
    tiempos = {
        c: st.sidebar.number_input(c[:28], min_value=1, max_value=365, value=20, key=f"t_{c}")
        for c in df["Capitulo"].unique()
    }

    gg_default = int(round(resumen_excel.get("GG", {}).get("monto", 0.0)))
    util_default = float(resumen_excel.get("UTIL", {}).get("tasa") or 0.15) * 100
    iva_default = float(resumen_excel.get("IVA", {}).get("tasa") or 0.19) * 100

    with st.sidebar.expander("💼 Parámetros de Cierre (GG / Util / IVA)", expanded=False):
        gg_monto = st.number_input("Gastos Generales ($)", min_value=0, value=gg_default, step=500000)
        util_pct = st.number_input("Utilidades (%)", min_value=0.0, max_value=100.0, value=util_default, step=1.0)
        iva_pct = st.number_input("IVA (%)", min_value=0.0, max_value=50.0, value=iva_default, step=1.0)

    if not atipicos_df.empty:
        items_txt = ", ".join(
            f"**{r['Item']} {r['Designacion']}** ({clp(r['Total'])})"
            for _, r in atipicos_df.iterrows()
        )
        st.warning(
            f"⚠️ Se excluyó automáticamente {len(atipicos_df)} partida(s) atípica(s) (>40% del total bruto): {items_txt}. "
            "Puedes volver a incluirla desde la barra lateral."
        )

    sin_precio_df = df[df["Sin_Precio"]]
    if not sin_precio_df.empty:
        st.info(
            f"ℹ️ Hay **{len(sin_precio_df)}** partidas sin precio unitario ($0) en la vista actual: "
            + ", ".join(f"`{i}`" for i in sin_precio_df["Item"].tolist())
        )

    total_directo = df["Total"].sum()
    util_monto = (total_directo + gg_monto) * (util_pct / 100.0)
    neto_calc = total_directo + gg_monto + util_monto
    iva_monto = neto_calc * (iva_pct / 100.0)
    total_c_iva = neto_calc + iva_monto
    dias_totales = sum(tiempos.values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Costo Directo", clp(total_directo))
    c2.metric("🧾 Total c/ IVA", clp(total_c_iva), f"Neto: {clp(neto_calc)}")
    c3.metric("⏱️ Tiempo Estimado", f"{dias_totales} días", f"~{dias_totales / 22:.1f} meses")
    c4.metric("📋 Partidas", len(df), f"{len(sin_precio_df)} en $0")

    tab1, tab2, tab3 = st.tabs(["📘 Explicación Didáctica", "📊 Gráficos", "📄 Tabla y Auditoría"])

    with tab1:
        for cap, grp in df.groupby("Capitulo", sort=False):
            tot_cap = grp["Total"].sum()
            pct = (tot_cap / total_directo * 100) if total_directo else 0.0
            with st.expander(f"**{cap}** — {clp(tot_cap)} ({pct:.1f}%) | ⏱️ {tiempos[cap]} días"):
                st.info(EXPLICACIONES.get(grp["Cap_Num"].iloc[0], "Etapa constructiva del proyecto."))
                for subcap, subgrp in grp.groupby("Subcapitulo", sort=False):
                    if subcap != cap:
                        st.markdown(f"**{subcap}** ({clp(subgrp['Total'].sum())})")
                    for _, r in subgrp.iterrows():
                        aviso = " ⚠️ *(sin precio)*" if r["Sin_Precio"] else ""
                        st.markdown(
                            f"- **{r['Item']} {r['Designacion']}**: "
                            f"`{r['Cantidad']:,.2f} {r['Unidad']}` × {clp(r['Valor'])} = **{clp(r['Total'])}**{aviso}"
                        )

    with tab2:
        df_pos = df[df["Total"] > 0]
        col1, col2 = st.columns(2)
        with col1:
            if df_pos.empty:
                st.info("No hay partidas con monto mayor a $0 para graficar el treemap.")
            else:
                fig_tree = px.treemap(
                    df_pos,
                    path=["Capitulo", "Designacion"],
                    values="Total",
                    title="Distribución de Costos por Capítulo y Partida",
                )
                st.plotly_chart(fig_tree, width="stretch")
        with col2:
            df_t = pd.DataFrame({"Capitulo": list(tiempos.keys()), "Dias": list(tiempos.values())})
            fig_bar = px.bar(
                df_t,
                x="Dias",
                y="Capitulo",
                orientation="h",
                text="Dias",
                title="Tiempos Estimados por Capítulo (Días)",
            )
            fig_bar.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_bar, width="stretch")

        df_cap_cost = (
            df.groupby("Capitulo", sort=False, as_index=False)["Total"]
            .sum()
            .sort_values("Total", ascending=True)
        )
        fig_cap = px.bar(
            df_cap_cost,
            x="Total",
            y="Capitulo",
            orientation="h",
            title="Costo Directo por Capítulo (CLP)",
        )
        st.plotly_chart(fig_cap, width="stretch")

    with tab3:
        cols_vista = ["Capitulo", "Subcapitulo", "Item", "Designacion", "Unidad", "Cantidad", "Valor", "Total"]
        st.dataframe(
            df[cols_vista],
            width="stretch",
            hide_index=True,
            column_config={
                "Cantidad": st.column_config.NumberColumn("Cantidad", format="%.2f"),
                "Valor": st.column_config.NumberColumn("Valor Unit.", format="$ %,.0f"),
                "Total": st.column_config.NumberColumn("Total", format="$ %,.0f"),
            },
        )

        csv_bytes = df[cols_vista].to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Descargar tabla filtrada (CSV)",
            data=csv_bytes,
            file_name="itemizado_bim_filtrado.csv",
            mime="text/csv",
        )

        if not atipicos_df.empty or not sin_precio_df.empty:
            st.subheader("🔍 Auditoría de datos del Excel")
            if not atipicos_df.empty:
                st.markdown("**Partidas con monto atípico (>40% del total bruto):**")
                st.dataframe(
                    atipicos_df[["Item", "Designacion", "Unidad", "Cantidad", "Valor", "Total"]],
                    width="stretch",
                    hide_index=True,
                )
            if not sin_precio_df.empty:
                st.markdown("**Partidas con valorización en $0:**")
                st.dataframe(
                    sin_precio_df[["Capitulo", "Item", "Designacion", "Unidad", "Cantidad", "Valor", "Total"]],
                    width="stretch",
                    hide_index=True,
                )


if __name__ == "__main__":
    main()
