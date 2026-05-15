import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from database.db_manager import DBManager
from logic.stats import QCStats
import json
import io

# Configuración de página
st.set_page_config(
    page_title="BioStat QC - Control de Calidad Agroindustrial",
    page_icon="🌿",
    layout="wide"
)

# Inicializar componentes
db = DBManager()
stats_engine = QCStats()

# --- ESTILOS ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e7d32; color: white; }
    .stMetric { border: 1px solid #e0e0e0; padding: 10px; border-radius: 10px; background: white; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN ---
st.sidebar.title("🌿 BioStat QC v1.0")
menu = st.sidebar.selectbox(
    "Menú Principal",
    ["🏠 Inicio", "➕ Registro de Datos", "📊 Control de Variables", "📉 Control de Atributos", "📑 Historial y Reportes"]
)

def plot_control_chart(y, ucl, lcl, center, title, ylabel, units=""):
    fig = go.Figure()
    # Puntos de datos
    fig.add_trace(go.Scatter(y=y, mode='lines+markers', name='Valor', line=dict(color='#1f77b4')))
    
    # Límites
    fig.add_hline(y=ucl, line_dash="dash", line_color="red", annotation_text=f"UCL: {ucl:.2f}")
    fig.add_hline(y=lcl, line_dash="dash", line_color="red", annotation_text=f"LCL: {lcl:.2f}")
    fig.add_hline(y=center, line_color="green", annotation_text=f"CL: {center:.2f}")
    
    # Resaltar fuera de control
    out_of_control = [(i, val) for i, val in enumerate(y) if val > ucl or val < lcl]
    if out_of_control:
        indices, values = zip(*out_of_control)
        fig.add_trace(go.Scatter(x=indices, y=values, mode='markers', marker=dict(color='orange', size=12), name='Fuera de Control'))

    fig.update_layout(title=title, yaxis_title=f"{ylabel} ({units})", xaxis_title="Subgrupo / Muestra", template="plotly_white")
    return fig

# --- LOGICA DE PAGINAS ---

if menu == "🏠 Inicio":
    st.title("Sistema de Control Estadístico de Calidad")
    st.markdown("""
    ### Monitoreo de Frutas, Hortalizas y Plantas Medicinales
    Esta plataforma permite integrar herramientas de **CEC** para el análisis de variables continuas y atributos discretos.
    
    **Objetivos del Sistema:**
    - Aplicar herramientas estadísticas en tiempo real.
    - Facilitar la toma de decisiones agroindustriales.
    - Garantizar la trazabilidad de los procesos de calidad.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Tip:** Comience registrando una nueva inspección en la pestaña 'Registro de Datos'.")
        st.image("https://images.unsplash.com/photo-1615485290382-441e4d0c9cb5?auto=format&fit=crop&q=80&w=800", caption="Calidad en la Cosecha")
    with col2:
        df = db.obtener_inspecciones()
        st.metric("Total de Registros", len(df))
        if not df.empty:
            st.write("Últimos registros:")
            st.dataframe(df[['producto', 'nombre_variable', 'timestamp']].head(5))

elif menu == "➕ Registro de Datos":
    st.title("Registro de Nueva Inspección")
    
    with st.form("registro_form"):
        c1, c2 = st.columns(2)
        with c1:
            producto = st.text_input("Nombre del Producto / Planta", "Sábila")
            tipo = st.selectbox("Tipo de Control", ["Variable (X-R, X-S)", "Atributo (P, Np, C, U)"])
            analista = st.text_input("Nombre del Analista")
        with c2:
            variable = st.text_input("Nombre de la Variable / Atributo", "pH")
            unidades = st.text_input("Unidades de Medida", "pH")
            fecha_ingreso = st.datetime_input("Fecha y Hora de Ingreso")

        st.markdown("---")
        st.write("📦 **Ingreso de Datos**")
        data_str = st.text_area("Ingrese los datos (separados por espacio o coma). Para X-R/X-S, ingrese todos los datos seguidos.", placeholder="Ej: 4.5, 4.6, 4.4...")
        n_subgrupo = st.number_input("Tamaño del subgrupo (Solo para Variables)", min_value=1, max_value=10, value=5)

        if st.form_submit_button("Guardar en Base de Datos"):
            try:
                valores = [float(x) for x in data_str.replace(',', ' ').split()]
                if len(valores) == 0: raise ValueError
                db.guardar_inspeccion(producto, tipo, variable, analista, unidades, valores)
                st.success("✅ Registro guardado exitosamente.")
            except:
                st.error("❌ Error en los datos. Verifique que sean números válidos.")

elif menu == "📊 Control de Variables":
    st.title("Análisis de Variables Continuas")
    df = db.obtener_inspecciones()
    df_v = df[df['tipo_control'].str.contains("Variable")]
    
    if df_v.empty:
        st.warning("No hay datos de variables registrados.")
    else:
        sel = st.selectbox("Seleccione Inspección", df_v['nombre_variable'] + " (" + df_v['timestamp'] + ")")
        idx = df_v.index[df_v['nombre_variable'] + " (" + df_v['timestamp'] + ")" == sel][0]
        row = df_v.iloc[idx]
        datos = np.array(json.loads(row['datos_json']))
        
        # Agrupar en subgrupos
        n = st.slider("Ajustar tamaño de subgrupo (n)", 2, 10, 5)
        num_sub = len(datos) // n
        if num_sub < 2:
            st.error(f"Se necesitan al menos 2 subgrupos. Con n={n}, solo hay {num_sub}. Ingrese más datos.")
        else:
            datos_matriz = datos[:num_sub*n].reshape(num_sub, n)
            df_s = pd.DataFrame(datos_matriz)
            
            tipo_graf = st.radio("Tipo de Gráfico", ["X-barra y R", "X-barra y S"])
            
            if tipo_graf == "X-barra y R":
                res = stats_engine.calcular_x_barra_r(df_s)
                st.plotly_chart(plot_control_chart(res['x_barras'], res['ucl_x'], res['lcl_x'], res['x_doble_barra'], "Gráfico X-barra", row['nombre_variable'], row['unidades']))
                st.plotly_chart(plot_control_chart(res['rangos'], res['ucl_r'], res['lcl_r'], res['r_barra'], "Gráfico R (Rangos)", "Rango"))
            else:
                res = stats_engine.calcular_x_barra_s(df_s)
                st.plotly_chart(plot_control_chart(res['x_barras'], res['ucl_x'], res['lcl_x'], res['x_doble_barra'], "Gráfico X-barra", row['nombre_variable'], row['unidades']))
                st.plotly_chart(plot_control_chart(res['s'], res['ucl_s'], res['lcl_s'], res['s_barra'], "Gráfico S (Desv. Estándar)", "S"))

            # Normalidad y Capacidad
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Prueba de Normalidad")
                is_norm, p, msg = stats_engine.test_normalidad(datos)
                st.metric("Resultado", msg, delta=f"p={p:.4f}")
                fig_hist = px.histogram(datos, nbins=15, title="Distribución de los Datos")
                st.plotly_chart(fig_hist)
            
            with c2:
                st.subheader("Capacidad del Proceso")
                lse = st.number_input("LSE", value=float(np.mean(datos) + 3*np.std(datos)))
                lie = st.number_input("LIE", value=float(np.mean(datos) - 3*np.std(datos)))
                cap = stats_engine.calcular_capacidad_completa(datos, lse, lie)
                st.write(f"**Cp:** {cap['cp']} | **Cpk:** {cap['cpk']}")
                st.write(f"**Pp:** {cap['pp']} | **Ppk:** {cap['ppk']}")
                if cap['cpk'] < 1.33: st.warning("⚠️ Proceso no capaz (Cpk < 1.33)")
                else: st.success("✅ Proceso capaz")

elif menu == "📉 Control de Atributos":
    st.title("Análisis de Atributos Discretos")
    df = db.obtener_inspecciones()
    df_a = df[df['tipo_control'].str.contains("Atributo")]
    
    if df_a.empty:
        st.warning("No hay datos de atributos registrados.")
    else:
        sel = st.selectbox("Seleccione Inspección", df_a['nombre_variable'] + " (" + df_a['timestamp'] + ")")
        idx = df_a.index[df_a['nombre_variable'] + " (" + df_a['timestamp'] + ")" == sel][0]
        row = df_a.iloc[idx]
        datos = np.array(json.loads(row['datos_json']))
        
        tipo_a = st.radio("Gráfico de Atributos", ["P (Proporción)", "Np (Número defectuosos)", "C (Conteo defectos)", "U (Defectos por unidad)"])
        
        if tipo_a == "C":
            res = stats_engine.calcular_grafico_c(datos)
            st.plotly_chart(plot_control_chart(res['c'], res['ucl_c'], res['lcl_c'], res['c_barra'], "Gráfico C", "Defectos"))
        elif tipo_a == "P":
            n_lot = st.number_input("Tamaño de lote (n)", min_value=1, value=100)
            res = stats_engine.calcular_grafico_p(datos, [n_lot]*len(datos))
            st.plotly_chart(plot_control_chart(res['p'], res['ucl_p'], res['lcl_p'], res['p_barra'], "Gráfico P", "Proporción"))
        elif tipo_a == "Np":
            n_lot = st.number_input("Tamaño de lote (n)", min_value=1, value=100)
            res = stats_engine.calcular_grafico_np(datos, n_lot)
            st.plotly_chart(plot_control_chart(res['np'], res['ucl'], res['lcl'], res['np_barra'], "Gráfico Np", "Cant. Defectuosos"))
        elif tipo_a == "U":
            n_unid = st.number_input("Unidades por muestra", min_value=1, value=1)
            res = stats_engine.calcular_grafico_u(datos, [n_unid]*len(datos))
            st.plotly_chart(plot_control_chart(res['u'], res['ucl'], res['lcl'], res['u_barra'], "Gráfico U", "Defectos/Unidad"))

        st.markdown("### Diagrama de Pareto")
        # Ejemplo: Clasificación de defectos para el Pareto
        defect_types = ["Mancha", "Golpe", "Podrido", "Color", "Otro"]
        counts = [sum(datos)*0.4, sum(datos)*0.3, sum(datos)*0.15, sum(datos)*0.1, sum(datos)*0.05]
        df_p = stats_engine.calcular_pareto(defect_types, counts)
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(x=df_p['Categoria'], y=df_p['Frecuencia'], name="Frecuencia"))
        fig_p.add_trace(go.Scatter(x=df_p['Categoria'], y=df_p['PorcentajeCum'], name="% Acumulado", yaxis="y2"))
        fig_p.update_layout(yaxis2=dict(overlaying='y', side='right', range=[0, 110]), title="Pareto de Defectos")
        st.plotly_chart(fig_p)

elif menu == "📑 Historial y Reportes":
    st.title("Historial de Calidad")
    df = db.obtener_inspecciones()
    st.dataframe(df)
    
    if not df.empty:
        # Exportar a Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Historial_QC')
        
        st.download_button(
            label="📥 Descargar Historial (Excel)",
            data=buffer.getvalue(),
            file_name="historial_calidad.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if st.button("🗑️ Limpiar Base de Datos"):
            import os
            if os.path.exists('database/quality_control.db'):
                os.remove('database/quality_control.db')
                st.rerun()
