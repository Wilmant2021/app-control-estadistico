import streamlit as st
import pandas as pd
from datetime import datetime
from database import queries
from ui import section_card


def render_page():
    st.header('04 - Registro de Muestras')
    st.write('Registra muestras variables y atributos para el control estadístico.')

    productos = pd.DataFrame(queries.get_productos())
    analistas = pd.DataFrame(queries.get_analistas())

    with section_card('Datos de muestra', 'Selecciona producto, analista y configura la muestra antes de registrarla.'):
        if productos.empty or analistas.empty:
            st.warning('Necesitas al menos un producto y un analista para registrar muestras.')
            return

        producto_seleccionado = st.selectbox('Producto', [''] + productos['nombre'].tolist())
        analista_seleccionado = st.selectbox('Analista', [''] + (analistas['nombre'] + ' ' + analistas['apellido']).tolist())

        if not producto_seleccionado or not analista_seleccionado:
            st.info('Selecciona un producto y un analista.')
            return

        id_producto = int(productos.loc[productos['nombre'] == producto_seleccionado, 'id_producto'].iloc[0])
        id_analista = int(analistas.loc[(analistas['nombre'] + ' ' + analistas['apellido']) == analista_seleccionado, 'id_analista'].iloc[0])

        tipo_control = st.radio('Tipo de control', ['Variable', 'Atributo'])
        fecha_hora = st.datetime_input('Fecha y hora de la muestra', value=datetime.now())
        num_subgrupo = st.number_input('Tamaño del subgrupo', min_value=1, max_value=50, value=5)
        lote = st.text_input('Lote')
        origen = st.text_input('Origen')
        observaciones = st.text_area('Observaciones')

        if tipo_control == 'Variable':
            configs = pd.DataFrame(queries.get_variables_by_producto(id_producto))
            opcions = ['<Nueva configuración>'] + [f"{row['id_variable']} - {row['nombre_variable']}" for _, row in configs.iterrows()]
            seleccion = st.selectbox('Configuración de variable', opcions)

            if seleccion != '<Nueva configuración>':
                id_variable = int(seleccion.split(' - ')[0])
                config = queries.get_variable_config_by_id(id_variable)
                st.markdown(f"**Variable:** {config['nombre_variable']} | Tipo: {config['tipo_dato']} | LCI: {config['lci']} | LCS: {config['lcs']}")
            else:
                nombre_variable = st.text_input('Nombre de la variable')
                tipo_dato = st.selectbox('Tipo de dato', ['continua', 'discreta'])
                lcs = st.number_input('Límite de control superior (LCS)', value=0.0)
                lci = st.number_input('Límite de control inferior (LCI)', value=0.0)
                valor_nominal = st.number_input('Valor nominal', value=0.0)

            valores = st.text_area('Valores de la variable (separados por espacios o comas)')
            if st.button('Guardar muestra de variable'):
                if seleccion == '<Nueva configuración>' and not nombre_variable.strip():
                    st.error('Debes ingresar el nombre de la variable.')
                else:
                    datos = [float(x) for x in valores.replace(',', ' ').split() if x.strip()]
                    if len(datos) < 2:
                        st.error('Ingresa al menos dos valores válidos.')
                    else:
                        if seleccion == '<Nueva configuración>':
                            id_variable = queries.insert_variable_config(id_producto, nombre_variable.strip(), tipo_dato, lcs, lci, valor_nominal, num_subgrupo)
                        muestra_id = queries.insert_muestra(id_producto, id_analista, num_subgrupo, lote.strip(), origen.strip(), observaciones.strip(), fecha_hora.strftime('%Y-%m-%d %H:%M:%S'))
                        for idx, valor in enumerate(datos, start=1):
                            queries.insert_medicion_variable(muestra_id, id_variable, idx, float(valor))
                        st.success('Muestra de variable registrada correctamente.')
                        st.rerun()

        else:
            configs = pd.DataFrame(queries.get_atributos_by_producto(id_producto))
            opcions = ['<Nueva configuración>'] + [f"{row['id_atributo']} - {row['nombre_atributo']}" for _, row in configs.iterrows()]
            seleccion = st.selectbox('Configuración de atributo', opcions)

            if seleccion != '<Nueva configuración>':
                id_atributo = int(seleccion.split(' - ')[0])
                config = queries.get_atributo_by_id(id_atributo)
                st.markdown(f"**Atributo:** {config['nombre_atributo']} | Tipo gráfico: {config['tipo_grafico']} | Tamaño subgrupo: {config['tam_subgrupo']}")
                tipo_grafico = config['tipo_grafico']
                tam_subgrupo = int(config['tam_subgrupo'] or num_subgrupo)
            else:
                nombre_atributo = st.text_input('Nombre del atributo')
                tipo_grafico = st.selectbox('Tipo de gráfico', ['P', 'NP', 'C', 'U'])
                tam_subgrupo = st.number_input('Tamaño del subgrupo para atributo', min_value=1, max_value=1000, value=num_subgrupo)

            inspeccionados = st.text_area('N° inspeccionados por muestra (ejemplo: 100 100 100)')
            defectuosos = st.text_area('N° defectuosos por muestra (ejemplo: 5 4 3)')

            if st.button('Guardar muestra de atributo'):
                if seleccion == '<Nueva configuración>' and not nombre_atributo.strip():
                    st.error('Debes ingresar el nombre del atributo.')
                else:
                    n_inspeccionados = [int(x) for x in inspeccionados.replace(',', ' ').split() if x.strip()]
                    n_defectuosos = [int(x) for x in defectuosos.replace(',', ' ').split() if x.strip()]
                    if len(n_inspeccionados) == 0 or len(n_inspeccionados) != len(n_defectuosos):
                        st.error('Ingresa listas válidas de inspeccionados y defectuosos de igual tamaño.')
                    else:
                        if seleccion == '<Nueva configuración>':
                            id_atributo = queries.insert_atributo_config(id_producto, nombre_atributo.strip(), tipo_grafico, tam_subgrupo)
                        muestra_id = queries.insert_muestra(id_producto, id_analista, num_subgrupo, lote.strip(), origen.strip(), observaciones.strip(), fecha_hora.strftime('%Y-%m-%d %H:%M:%S'))
                        for n, d in zip(n_inspeccionados, n_defectuosos):
                            queries.insert_medicion_atributo(muestra_id, id_atributo, int(n), int(d))
                        st.success('Muestra de atributo registrada correctamente.')
                        st.rerun()
