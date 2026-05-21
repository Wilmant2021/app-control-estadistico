import streamlit as st
import pandas as pd
import numpy as np
from database import queries
from modules import estadisticas, graficos
from ui import section_card


def render_page():
    st.header('05 - Control de Variables')
    st.write('Visualiza los gráficos de control y capacidad para variables continuas.')

    with section_card('Gráficos de control de variables', 'Elige una muestra variable para ver gráficos de X-barra, R, S y capacidad.'):
        muestras = pd.DataFrame(queries.get_muestras_variables())
        if muestras.empty:
            st.warning('No hay muestras variables registradas.')
            return

        opciones = [f"{int(row['id_muestra'])} - {row['producto']} / {row['nombre_variable']} ({row['fecha_hora']})" for _, row in muestras.iterrows()]
        seleccion = st.selectbox('Selecciona muestra variable', opciones)
        id_muestra = int(seleccion.split(' - ')[0])
        muestra = muestras[muestras['id_muestra'] == id_muestra].iloc[0]

        datos_mediciones = pd.DataFrame(queries.get_mediciones_variables_by_muestra(id_muestra))
        valores = datos_mediciones['valor'].astype(float).tolist()
        if len(valores) < 2:
            st.error('Esta muestra no tiene suficientes valores de medición.')
            return

        tipo_grafico = st.radio('Tipo de gráfico', ['X-barra y R', 'X-barra y S'])
        if len(valores) >= 50:
            n_default = max(2, min(25, len(valores) // 25))
            st.info(f'Se ajustó el tamaño del subgrupo a {n_default} para generar al menos 25 subgrupos con los datos disponibles.')
        else:
            n_default = int(muestra['num_subgrupo']) if 2 <= int(muestra['num_subgrupo']) <= 25 else 5

        n = st.number_input('Tamaño del subgrupo', min_value=2, max_value=25, value=n_default)

        subgrupos = [valores[i:i+n] for i in range(0, len(valores) - len(valores) % n, n)]
        if len(subgrupos) < 25:
            st.warning('No se pueden formar 25 subgrupos completos con la cantidad actual de observaciones. Añada más observaciones o reduzca el tamaño del subgrupo si es posible.')

        st.markdown('### Datos de la muestra')
        st.write(f"Subgrupos calculados: {len(subgrupos)}")
        st.write(f"Producto: {muestra['producto']}")
        st.write(f"Variable: {muestra['nombre_variable']}")
        st.write(f"Cantidad de observaciones: {len(valores)}")
        st.write(f"Subgrupos disponibles: {len(subgrupos)}")

        if tipo_grafico == 'X-barra y R':
            resultado = estadisticas.calcular_xbar_r(subgrupos)
            fig_x, fig_r = graficos.crear_grafico_xbar_r(
                resultado['xbars'], resultado['rangos'], resultado['xbar_bar'], resultado['r_bar'],
                resultado['lcs_xbar'], resultado['lci_xbar'], resultado['lcs_r'], resultado['lci_r']
            )
            st.plotly_chart(fig_x, width='stretch')
            st.plotly_chart(fig_r, width='stretch')
        else:
            resultado = estadisticas.calcular_xbar_s(subgrupos)
            fig_x, fig_s = graficos.crear_grafico_xbar_s(
                resultado['xbars'], resultado['s'], resultado['xbar_bar'], resultado['s_bar'],
                resultado['lcs_xbar'], resultado['lci_xbar'], resultado['lcs_s'], resultado['lci_s']
            )
            st.plotly_chart(fig_x, width='stretch')
            st.plotly_chart(fig_s, width='stretch')

        config = queries.get_variable_config_by_id(int(muestra['id_variable']))
        if config:
            lcs = float(config['lcs'] or 0.0)
            lci = float(config['lci'] or 0.0)
            capacidad = estadisticas.calcular_capacidad(valores, lcs, lci)
            st.markdown('### Capacidad del proceso')

            def semaforo(valor: float) -> str:
                if valor is None or np.isnan(valor):
                    return 'gray'
                if valor >= 1.33:
                    return 'green'
                if valor >= 1.0:
                    return 'orange'
                return 'red'

            cols = st.columns(4)
            for column, label, metric in zip(cols, ['Cp', 'Cpk', 'Pp', 'Ppk'], [capacidad['cp'], capacidad['cpk'], capacidad['pp'], capacidad['ppk']]):
                valor_text = 'N/A' if np.isnan(metric) else f'{metric:.3f}'
                color = semaforo(metric)
                column.markdown(f"**{label}**<br><span style='color:{color}; font-size:1.3em'>{valor_text}</span>", unsafe_allow_html=True)

            if capacidad['cpk'] >= 1.33:
                st.success('✅ Proceso capaz')
            elif capacidad['cpk'] >= 1.0:
                st.warning('⚠️ Proceso marginalmente capaz')
            else:
                st.error('🔴 Proceso no capaz')

        normalidad = estadisticas.prueba_normalidad(valores)
        st.markdown('### Normalidad')
        st.write(f"Estadístico: {normalidad['estadistico']:.4f} | p-valor: {normalidad['p_valor']:.4f}")
        if normalidad['es_normal']:
            st.success(normalidad['interpretacion'])
        else:
            st.warning(normalidad['interpretacion'])
        st.plotly_chart(graficos.crear_histograma(valores, bins=15, titulo='Histograma de mediciones'), width='stretch')
