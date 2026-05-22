import streamlit as st
import pandas as pd
from database import queries
from database.connection import init_db
from ui import section_card

TIPOS_PRODUCTO = ['fruta', 'hortaliza', 'planta_medicinal']


def render_page():
    st.header('01 - Configuración')
    st.write('Administra la inicialización de la base de datos y revisa las configuraciones actuales de productos, variables y atributos.')

    productos = pd.DataFrame(queries.get_productos())
    analistas = pd.DataFrame(queries.get_analistas())

    with section_card('Control del sistema', 'Inicializa la base de datos y revisa el estado actual de los registros en un solo lugar.'):
        if st.button('🛠️ Inicializar / actualizar base de datos'):
            init_db()
            st.success('Base de datos inicializada correctamente.')
            st.rerun()

        c1, c2 = st.columns(2)
        c1.metric('Productos registrados', len(productos))
        c2.metric('Analistas registrados', len(analistas))

    st.markdown('---')

    with section_card('Crear nuevo producto con configuración inicial', 'Agrega un producto y asigna variables y atributos predeterminados para su control.'):
        catalogo_variables = [item['nombre_variable'] for item in queries.get_catalogo_variables()]
        catalogo_atributos = [item['nombre_atributo'] for item in queries.get_catalogo_atributos()]
        variables_personalizadas = ''
        atributos_personalizadas = ''

        with st.form('form_nuevo_producto'):
            nombre = st.text_input('Nombre del producto')
            tipo = st.selectbox('Tipo de producto', TIPOS_PRODUCTO)
            variedad = st.text_input('Variedad')
            unidad = st.text_input('Unidad de medida', 'kg')
            descripcion = st.text_area('Descripción')

            st.write('Selecciona las variables continuas predeterminadas para este producto:')
            variables_seleccionadas = st.multiselect('Variables del catálogo', catalogo_variables)

            st.write('Selecciona los atributos predeterminados para este producto:')
            atributos_seleccionados = st.multiselect('Atributos del catálogo', catalogo_atributos)

            st.write('Agrega variables personalizadas (una por línea)')
            variables_personalizadas = st.text_area('Variables personalizadas')

            st.write('Agrega atributos personalizados (uno por línea)')
            atributos_personalizados = st.text_area('Atributos personalizados')

            submitted_producto = st.form_submit_button('Guardar producto y asignar configuración')

            if submitted_producto:
                if not nombre.strip():
                    st.error('El nombre del producto es obligatorio.')
                else:
                    queries.insert_producto_con_configuracion(
                        nombre.strip(),
                        tipo,
                        variedad.strip(),
                        unidad.strip(),
                        descripcion.strip(),
                        catalogo_variables=variables_seleccionadas,
                        catalogo_atributos=atributos_seleccionados,
                        variables_personalizadas=[line.strip() for line in variables_personalizadas.splitlines() if line.strip()],
                        atributos_personalizados=[line.strip() for line in atributos_personalizadas.splitlines() if line.strip()]
                    )
                    st.success('Producto y configuración inicial guardados correctamente.')
                    st.rerun()

    st.markdown('---')

    with section_card('Productos actuales', 'Revisa los productos definidos y su configuración asociada.'):
        if productos.empty:
            st.info('No hay productos definidos aún.')
        else:
            st.dataframe(productos)

    with section_card('Analistas actuales', 'Consulta los analistas registrados y su información de contacto.'):
        if analistas.empty:
            st.info('No hay analistas definidos aún.')
        else:
            st.dataframe(analistas)

    st.markdown('---')

    with section_card('Configuraciones por producto', 'Selecciona un producto para ver sus variables y atributos configurados.'):
        if productos.empty:
            st.info('Crea productos para ver y definir variables / atributos.')
            return

        producto_seleccionado = st.selectbox('Selecciona producto', [''] + productos['nombre'].tolist())
        if producto_seleccionado:
            id_producto = int(productos.loc[productos['nombre'] == producto_seleccionado, 'id_producto'].iloc[0])
            variables = pd.DataFrame(queries.get_variables_by_producto(id_producto))
            atributos = pd.DataFrame(queries.get_atributos_by_producto(id_producto))

            st.write(f'### Variables para {producto_seleccionado}')
            if variables.empty:
                st.info('No hay configuraciones de variables para este producto.')
            else:
                st.dataframe(variables)

            st.write(f'### Atributos para {producto_seleccionado}')
            if atributos.empty:
                st.info('No hay configuraciones de atributos para este producto.')
            else:
                st.dataframe(atributos)
