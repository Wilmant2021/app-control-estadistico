import streamlit as st
import pandas as pd
import numpy as np
from database import queries
from modules import estadisticas, graficos
from ui import section_card


def render_page():
    st.header('06 - Control de Atributos')
    st.write('Visualiza gráficos de control para atributos discretos.')

    with section_card('Gráficos de control de atributos', 'Selecciona una muestra de atributos para visualizar el gráfico y las métricas asociadas.'):
        muestras = pd.DataFrame(queries.get_muestras_atributos())
        if muestras.empty:
            st.warning('No hay muestras de atributos registradas.')
            return

        opciones = [f"{int(row['id_muestra'])} - {row['producto']} / {row['nombre_atributo']} ({row['fecha_hora']})" for _, row in muestras.iterrows()]
        seleccion = st.selectbox('Selecciona muestra de atributo', opciones)
        id_muestra = int(seleccion.split(' - ')[0])
        muestra = muestras[muestras['id_muestra'] == id_muestra].iloc[0]

        datos_atributo = pd.DataFrame(queries.get_mediciones_atributos_by_muestra(id_muestra))
        if datos_atributo.empty:
            st.error('No se encontraron mediciones de atributo para esta muestra.')
            return

        n_inspeccionados = datos_atributo['n_inspeccionados'].astype(int).tolist()
        n_defectuosos = datos_atributo['n_defectuosos'].astype(int).tolist()

        st.markdown(f"### Atributo: {muestra['nombre_atributo']}")
        st.write(f"Tipo de gráfico: {muestra['tipo_grafico']}")
        st.write(f"Tamaño de subgrupo: {muestra.get('tam_subgrupo', 'N/A')}")
        st.write(f"Subgrupos registrados: {len(n_inspeccionados)}")
        st.write(f"Mediciones registradas: {len(datos_atributo)}")

        if len(n_inspeccionados) < 25:
            st.warning('Se requieren al menos 25 subgrupos para generar gráficos de control de atributos fiables.')
            return

        try:
            if muestra['tipo_grafico'] == 'P':
                resultado = estadisticas.calcular_grafico_p(n_inspeccionados, n_defectuosos)
                fig = graficos.crear_grafico_p(list(range(len(n_defectuosos))), resultado['p'], resultado['p_bar'], resultado['lcs'], resultado['lci'], resultado['puntos_fuera'])
            elif muestra['tipo_grafico'] == 'NP':
                resultado = estadisticas.calcular_grafico_np(n_inspeccionados, n_defectuosos)
                fig = graficos.crear_grafico_np(list(range(len(n_defectuosos))), resultado['np'], resultado['np_bar'], resultado['lcs'], resultado['lci'])
            elif muestra['tipo_grafico'] == 'C':
                resultado = estadisticas.calcular_grafico_c(n_defectuosos)
                fig = graficos.crear_grafico_c(list(range(len(n_defectuosos))), resultado['c'], resultado['c_bar'], resultado['lcs'], resultado['lci'])
            else:
                resultado = estadisticas.calcular_grafico_u(n_inspeccionados, n_defectuosos)
                fig = graficos.crear_grafico_u(list(range(len(n_defectuosos))), resultado['u'], resultado['u_bar'], resultado['lcs'], resultado['lci'])
        except ValueError as error:
            st.error(f'Error al generar gráfico de atributos: {error}')
            return

        st.plotly_chart(fig, width='stretch')
        categorias = [f'Muestra {i+1}' for i in range(len(n_defectuosos))]
        st.plotly_chart(graficos.crear_grafico_pareto(categorias, n_defectuosos, titulo='Pareto de defectos'), width='stretch')
