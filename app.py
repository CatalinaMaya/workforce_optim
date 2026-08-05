"""
Optimización de asignación de turnos
MVP para Holafly 
"""

import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pyomo.environ import value

from datos import (
    TURNOS, DIAS, generar_instancia,
    guardar_requerimiento, guardar_disponibilidad,
    cargar_requerimiento, cargar_disponibilidad,
    R_a_dataframe,
)
from modelo import construir_modelo
from solver import resolver_modelo, extraer_resultados
from utils import calcular_metricas, exportar_resultados, to_excel_bytes

DATA_DIR = "data"
OUTPUT_DIR = "outputs"
LOGO_PATH = "Holafly-logo.svg.webp"

st.set_page_config(page_title="Workforce | Holafly", page_icon="🗓️", layout="wide")
st.image(LOGO_PATH, width=130)
st.title("🗓️ Workforce")
st.caption("Optimización de asignación de turnos de operación· Modelo de programación lineal")

if "resultados" not in st.session_state:
    st.session_state.resultados = None

# ============================================================
# SIDEBAR - PARÁMETROS Y FUENTE DE DATOS
# ============================================================
with st.sidebar:
    st.header("⚙️ Parámetros")

    fuente = st.radio("Origen de los datos", ["Generar aleatoriamente", "Cargar desde data/*.xlsx"])

    carga_desde_data = fuente == "Cargar desde data/*.xlsx"
    n_colaboradores = st.number_input(
        "Total de colaboradores",
        min_value=1,
        max_value=500,
        value=60,
        step=1,
        disabled=carga_desde_data,
    )
    mercados_input = st.text_input(
        "Mercados (separados por coma)",
        value="America, Europa, Asia",
        disabled=carga_desde_data,
    )
    mercados = [m.strip() for m in mercados_input.split(",") if m.strip()]

    st.markdown(f"**Días:** {', '.join(DIAS)}")
    st.markdown(f"**Turnos:** {', '.join(TURNOS)} ")

    st.divider()

    if fuente == "Generar aleatoriamente":
        st.subheader("Parámetros de generación")
        prob_disponibilidad = st.slider("Probabilidad de disponibilidad (%)", 50, 100, 90) / 100
        r_min, r_max = st.slider("Rango de personal requerido", 1, 30, (4, 10))
        semilla = 10
        guardar_en_data = st.checkbox("Guardar esta instancia en data/*.xlsx", value=False)
    else:
        st.subheader("Archivos de entrada")
        st.caption(f"Se leerán `{DATA_DIR}/requerimiento.xlsx` y `{DATA_DIR}/disponibilidad.xlsx`.")
        req_existe = os.path.exists(os.path.join(DATA_DIR, "requerimiento.xlsx"))
        disp_existe = os.path.exists(os.path.join(DATA_DIR, "disponibilidad.xlsx"))
        st.write(f"{'✅' if req_existe else '❌'} requerimiento.xlsx")
        st.write(f"{'✅' if disp_existe else '❌'} disponibilidad.xlsx")

    st.divider()

    ejecutar = st.button("🚀 Ejecutar Optimización", type="primary", use_container_width=True)

if not mercados:
    st.error("Debes definir al menos un mercado.")
    st.stop()

colaboradores = [f"C{i}" for i in range(1, int(n_colaboradores) + 1)]

# ============================================================
# OBTENER A, R SEGÚN LA FUENTE ELEGIDA
# ============================================================
error_carga = None
if fuente == "Generar aleatoriamente":
    A, R = generar_instancia(colaboradores, DIAS, TURNOS, mercados, prob_disponibilidad, r_min, r_max, semilla)
    if guardar_en_data:
        os.makedirs(DATA_DIR, exist_ok=True)
        guardar_requerimiento(R, os.path.join(DATA_DIR, "requerimiento.xlsx"))
        guardar_disponibilidad(A, os.path.join(DATA_DIR, "disponibilidad.xlsx"))
        st.sidebar.success("Instancia guardada en data/*.xlsx")
else:
    try:
        R = cargar_requerimiento(os.path.join(DATA_DIR, "requerimiento.xlsx"))
        A = cargar_disponibilidad(os.path.join(DATA_DIR, "disponibilidad.xlsx"))
        # Los conjuntos reales se derivan de los archivos cargados, no de los parámetros de la barra lateral
        colaboradores = sorted({i for (i, d, t) in A.keys()})
        mercados = sorted({m for (d, t, m) in R.keys()})
    except FileNotFoundError as e:
        error_carga = str(e)
        A, R = {}, {}

# ============================================================
# TABS
# ============================================================
tab_instancia, tab_resultados = st.tabs(["🔎 Instancia", "📈 Resultados"])

with tab_instancia:
    if error_carga:
        st.error(f"No se pudieron cargar los archivos: {error_carga}")
        st.info("Genera y guarda una instancia primero, o revisa que los archivos existan en data/.")
    else:
        st.subheader("Vista previa de los parámetros de entrada")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Disponibilidad total por día y turno**")
            import pandas as pd
            df_disp_resumen = pd.DataFrame([
                {"Día": d, "Turno": t, "Disponibles": sum(A.get((i, d, t), 0) for i in colaboradores)}
                for d in DIAS for t in TURNOS
            ])
            fig_disp = px.bar(
                df_disp_resumen,
                x="Día",
                y="Disponibles",
                color="Turno",
                barmode="group",
                color_discrete_sequence=["#E7485C", "#CC9F72", "#6ECF89"],
            )
            fig_disp.update_layout(height=380)
            st.plotly_chart(fig_disp, use_container_width=True)

        with col2:
            st.markdown("**Personal requerido por día y turno**")
            df_r_resumen = pd.DataFrame([
                {"Día": d, "Turno": t, "Requerido": sum(R.get((d, t, m), 0) for m in mercados)}
                for d in DIAS for t in TURNOS
            ])
            fig_r = px.bar(
                df_r_resumen,
                x="Día",
                y="Requerido",
                color="Turno",
                barmode="group",
                color_discrete_sequence=["#E7485C", "#CC9F72", "#6ECF89"],
            )
            fig_r.update_layout(height=380)
            st.plotly_chart(fig_r, use_container_width=True)

        with st.expander("Ver tabla completa de personal requerido"):
            st.dataframe(R_a_dataframe(R), use_container_width=True, hide_index=True)

# ============================================================
# EJECUCIÓN
# ============================================================
if ejecutar and not error_carga:
    st.toast("Ejecutando optimización...")
    with st.spinner("Construyendo y resolviendo el modelo..."):
        try:
            model = construir_modelo(colaboradores, DIAS, TURNOS, mercados, R, A)
            result, elapsed = resolver_modelo(model, solver_name="appsi_highs")
            df_asignacion, df_resumen = extraer_resultados(model)

            metricas = calcular_metricas(
                df_asignacion, df_resumen, len(colaboradores), len(DIAS), value(model.obj), elapsed
            )
            path_asig, path_res = exportar_resultados(df_asignacion, df_resumen, OUTPUT_DIR)

            st.session_state.resultados = {
                "df_asignacion": df_asignacion,
                "df_resumen": df_resumen,
                "metricas": metricas,
                "status": str(result.solver.status),
                "termination": str(result.solver.termination_condition),
                "path_asignaciones": path_asig,
                "path_resumen": path_res,
            }
            st.toast("Ejecución exitosa. Revise la pestaña de resultados.")
        except Exception as e:
            st.error(f"Ocurrió un error al resolver el modelo: {e}")
            st.session_state.resultados = None

# ============================================================
# TAB RESULTADOS
# ============================================================
with tab_resultados:
    if st.session_state.resultados is None:
        st.info("Configura los parámetros y presiona **Ejecutar Optimización** para ver resultados aquí.")
    else:
        res = st.session_state.resultados
        df_asignacion = res["df_asignacion"]
        df_resumen = res["df_resumen"]
        m = res["metricas"]

        st.success(f"Modelo resuelto · Estado: **{res['status']}** ({res['termination']})")
        st.caption(f"Resultados guardados en `{res['path_asignaciones']}` y `{res['path_resumen']}`")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total asignaciones", m["total_asignado"])
        c2.metric("Utilización de headcount", f"{m['utilizacion']:.1f}%")
        c3.metric("Desviación total (obj.)", f"{m['objetivo']:.0f}")
        c4.metric("Turnos con déficit", f"{m['turnos_con_deficit']}/{m['total_celdas']}")
        c5.metric("Tiempo del solver", f"{m['tiempo']:.2f} s")

        if m["turnos_con_exceso"] > 0:
            st.caption(f"⚠️ {m['turnos_con_exceso']} combinación(es) turno-mercado-día con exceso de personal.")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Requerido vs. Asignado por turno (agregado)**")
            agg_turno = df_resumen.groupby("Turno")[["Requerido", "Asignado"]].sum().reindex(TURNOS).reset_index()
            fig1 = go.Figure()
            fig1.add_bar(x=agg_turno["Turno"], y=agg_turno["Requerido"], name="Requerido", marker_color="#E7485C")
            fig1.add_bar(x=agg_turno["Turno"], y=agg_turno["Asignado"], name="Asignado", marker_color="#CC9F72")
            fig1.update_layout(barmode="group", height=380)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("**Requerido vs. Asignado por mercado (agregado)**")
            agg_mercado = df_resumen.groupby("Mercado")[["Requerido", "Asignado"]].sum().reset_index()
            fig2 = go.Figure()
            fig2.add_bar(x=agg_mercado["Mercado"], y=agg_mercado["Requerido"], name="Requerido", marker_color="#E7485C")
            fig2.add_bar(x=agg_mercado["Mercado"], y=agg_mercado["Asignado"], name="Asignado", marker_color="#CC9F72")
            fig2.update_layout(barmode="group", height=380)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Evolución por día: total requerido vs. asignado**")
        agg_dia = df_resumen.groupby("Día")[["Requerido", "Asignado"]].sum().reindex(DIAS).reset_index()
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=agg_dia["Día"],
            y=agg_dia["Requerido"],
            mode="lines+markers",
            name="Requerido",
            line=dict(color="#E7485C"),
            marker=dict(color="#E7485C"),
        ))
        fig3.add_trace(go.Scatter(
            x=agg_dia["Día"],
            y=agg_dia["Asignado"],
            mode="lines+markers",
            name="Asignado",
            line=dict(color="#CC9F72"),
            marker=dict(color="#CC9F72"),
        ))
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("**Mapa de calor: Déficit − Exceso por turno y mercado (suma en la semana)**")
        df_resumen["Neto"] = df_resumen["Déficit"] - df_resumen["Exceso"]
        heat = df_resumen.groupby(["Turno", "Mercado"])["Neto"].sum().reset_index()
        heat_pivot = heat.pivot(index="Turno", columns="Mercado", values="Neto").reindex(TURNOS)
        fig4 = px.imshow(
            heat_pivot,
            text_auto=True,
            color_continuous_scale=["#FFFFFF", "#F8D1D9", "#E7485C"],
            origin="upper",
            labels=dict(color="Déficit (+) / Exceso (-)"),
        )
        fig4.update_layout(height=350)
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("**Distribución de turnos asignados por colaborador**")
        if not df_asignacion.empty:
            turnos_por_colab = df_asignacion.groupby("Colaborador").size().reset_index(name="Turnos asignados")
            fig5 = px.histogram(
                turnos_por_colab,
                x="Turnos asignados",
                nbins=8,
                color_discrete_sequence=["#E7485C"],
            )
            fig5.update_layout(height=320)
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No hubo asignaciones para graficar.")

        st.divider()
        st.subheader("📋 Tabla de resumen (cobertura por día/turno/mercado)")
        st.dataframe(df_resumen, use_container_width=True, hide_index=True)

        st.subheader("📋 Tabla de asignación de turnos (detalle por colaborador)")
        st.dataframe(df_asignacion, use_container_width=True, hide_index=True)
