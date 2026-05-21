import io
import streamlit as st
import pandas as pd
from database import queries
from modules import exportacion, estadisticas


def render_page():
    st.header('07 - Reportes')
    st.write('Genera reportes y exporta información de muestras, productos, analistas y controles de CEP.')

    muestras = pd.DataFrame(queries.get_muestras())
    productos = pd.DataFrame(queries.get_productos())
    analistas = pd.DataFrame(queries.get_analistas())

    st.subheader('Resumen de registros')
    c1, c2, c3 = st.columns(3)
    c1.metric('Productos', len(productos))
    c2.metric('Analistas', len(analistas))
    c3.metric('Muestras', len(muestras))

    st.markdown('---')
    st.subheader('Detalle de muestras')
    if muestras.empty:
        st.info('No hay muestras registradas.')
    else:
        st.dataframe(muestras)

    st.markdown('---')
    st.subheader('Exportar datos')
    datos = {
        'Muestras': muestras,
        'Productos': productos,
        'Analistas': analistas
    }
    nombre_archivo = 'cec_agro_reportes.xlsx'

    if st.button('Generar archivo de exportación'):
        ruta = exportacion.exportar_a_excel(datos, nombre_archivo)
        st.success(f'Archivo generado: {ruta}')
        with open(ruta, 'rb') as f:
            st.download_button('Descargar reporte Excel', f.read(), file_name=nombre_archivo, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    st.markdown('---')
    st.subheader('Exportar reporte CEP de control estadístico')
    tipo_control = st.radio('Selecciona el tipo de control', ['Variable', 'Atributos'], horizontal=True)

    if tipo_control == 'Variable':
        muestras_var = pd.DataFrame(queries.get_muestras_variables())
        if muestras_var.empty:
            st.info('No hay muestras variables registradas para exportar.')
        else:
            opciones = [f"{int(row['id_muestra'])} - {row['producto']} / {row['nombre_variable']} ({row['fecha_hora']})" for _, row in muestras_var.iterrows()]
            seleccion = st.selectbox('Selecciona muestra variable', opciones)
            id_muestra = int(seleccion.split(' - ')[0])
            muestra = muestras_var[muestras_var['id_muestra'] == id_muestra].iloc[0]
            tipo_grafico = st.selectbox('Tipo de gráfico', ['X-barra y R', 'X-barra y S'])
            datos_mediciones = pd.DataFrame(queries.get_mediciones_variables_by_muestra(id_muestra))

            if datos_mediciones.empty:
                st.warning('No se encontraron mediciones variables para esta muestra.')
            else:
                valores = datos_mediciones['valor'].astype(float).tolist()
                tam_subgrupo = int(muestra['num_subgrupo']) if 2 <= int(muestra['num_subgrupo']) <= 25 else 5
                subgrupos = [valores[i:i+tam_subgrupo] for i in range(0, len(valores) - len(valores) % tam_subgrupo, tam_subgrupo)]
                capacidad = None
                normalidad = estadisticas.prueba_normalidad(valores)
                if tipo_grafico == 'X-barra y R':
                    resultados_control = estadisticas.calcular_xbar_r(subgrupos)
                else:
                    resultados_control = estadisticas.calcular_xbar_s(subgrupos)

                muestra_completa = queries.get_muestra_by_id(id_muestra)
                analista_nombre = 'N/A'
                if muestra_completa:
                    analista = queries.get_analista_by_id(int(muestra_completa['id_analista']))
                    if analista:
                        analista_nombre = f"{analista['nombre']} {analista['apellido']}"
                    config = queries.get_variable_config_by_id(int(muestra['id_variable']))
                    if config:
                        lcs = float(config['lcs'] or 0.0)
                        lci = float(config['lci'] or 0.0)
                        capacidad = estadisticas.calcular_capacidad(valores, lcs, lci)

                metadata = {
                    'producto': muestra['producto'],
                    'analista': analista_nombre,
                    'variable_atributo': muestra['nombre_variable'],
                    'fecha_hora': muestra['fecha_hora'],
                    'tam_subgrupo': tam_subgrupo,
                    'subgrupos_calculados': len(subgrupos),
                }

                if st.button('Generar reporte CEP variable'):
                    nombre_archivo_cep = f'cep_reporte_variable_{id_muestra}.xlsx'
                    ruta = exportacion.exportar_reporte_control_excel(
                        nombre_archivo_cep,
                        metadata,
                        'Variable',
                        tipo_grafico,
                        datos_mediciones,
                        resultados_control,
                        capacidad,
                        normalidad,
                        tam_subgrupo,
                    )
                    st.success(f'Reporte CEP generado: {ruta}')
                    with open(ruta, 'rb') as f:
                        st.download_button('Descargar reporte CEP', f.read(), file_name=nombre_archivo_cep, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    else:
        muestras_atr = pd.DataFrame(queries.get_muestras_atributos())
        if muestras_atr.empty:
            st.info('No hay muestras de atributos registradas para exportar.')
        else:
            opciones = [f"{int(row['id_muestra'])} - {row['producto']} / {row['nombre_atributo']} ({row['fecha_hora']})" for _, row in muestras_atr.iterrows()]
            seleccion = st.selectbox('Selecciona muestra de atributo', opciones)
            id_muestra = int(seleccion.split(' - ')[0])
            muestra = muestras_atr[muestras_atr['id_muestra'] == id_muestra].iloc[0]
            datos_mediciones = pd.DataFrame(queries.get_mediciones_atributos_by_muestra(id_muestra))

            if datos_mediciones.empty:
                st.warning('No se encontraron mediciones de atributo para esta muestra.')
            else:
                tipo_grafico = muestra['tipo_grafico']
                n_inspeccionados = datos_mediciones['n_inspeccionados'].astype(int).tolist()
                n_defectuosos = datos_mediciones['n_defectuosos'].astype(int).tolist()
                if tipo_grafico == 'P':
                    resultados_control = estadisticas.calcular_grafico_p(n_inspeccionados, n_defectuosos)
                elif tipo_grafico == 'NP':
                    resultados_control = estadisticas.calcular_grafico_np(n_inspeccionados, n_defectuosos)
                elif tipo_grafico == 'C':
                    resultados_control = estadisticas.calcular_grafico_c(n_defectuosos)
                else:
                    resultados_control = estadisticas.calcular_grafico_u(n_inspeccionados, n_defectuosos)

                muestra_completa = queries.get_muestra_by_id(id_muestra)
                analista_nombre = 'N/A'
                if muestra_completa:
                    analista = queries.get_analista_by_id(int(muestra_completa['id_analista']))
                    if analista:
                        analista_nombre = f"{analista['nombre']} {analista['apellido']}"

                metadata = {
                    'producto': muestra['producto'],
                    'analista': analista_nombre,
                    'variable_atributo': muestra['nombre_atributo'],
                    'fecha_hora': muestra['fecha_hora'],
                    'tam_subgrupo': int(muestra['tam_subgrupo']) if muestra.get('tam_subgrupo') is not None else 'N/A',
                    'subgrupos_calculados': len(datos_mediciones),
                }

                if st.button('Generar reporte CEP de atributos'):
                    nombre_archivo_cep = f'cep_reporte_atributos_{id_muestra}.xlsx'
                    ruta = exportacion.exportar_reporte_control_excel(
                        nombre_archivo_cep,
                        metadata,
                        'Atributo',
                        tipo_grafico,
                        datos_mediciones,
                        resultados_control,
                        None,
                        None,
                        int(muestra['tam_subgrupo']) if muestra.get('tam_subgrupo') is not None else None,
                    )
                    st.success(f'Reporte CEP generado: {ruta}')
                    with open(ruta, 'rb') as f:
                        st.download_button('Descargar reporte CEP', f.read(), file_name=nombre_archivo_cep, mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
