import streamlit as st
import pandas as pd
from database import queries
from ui import section_card

TIPOS_PRODUCTO = ['fruta', 'hortaliza', 'planta_medicinal']


def render_page():
    st.header('02 - Productos')
    st.write('Registra y consulta los productos del sistema.')

    catalogo_variables = [item['nombre_variable'] for item in queries.get_catalogo_variables()]
    catalogo_atributos = [item['nombre_atributo'] for item in queries.get_catalogo_atributos()]

    with section_card('Registrar un nuevo producto', 'Añade un producto y configura sus variables y atributos iniciales.'):
        variables_personalizadas = ''
        atributos_personalizadas = ''
        with st.form('form_producto'):
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

            submitted = st.form_submit_button('Guardar producto y asignar configuración')

        if submitted:
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
                    atributos_personalizados=[line.strip() for line in atributos_personalizados.splitlines() if line.strip()]
                )
                st.success('Producto guardado correctamente.')
                st.rerun()

    st.markdown('---')
    with section_card('Listado de productos', 'Consulta todos los productos registrados en el sistema.'):
        productos = pd.DataFrame(queries.get_productos())
        if productos.empty:
            st.info('No hay productos registrados.')
        else:
            st.dataframe(productos)
