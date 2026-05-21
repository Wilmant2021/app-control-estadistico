import streamlit as st
import pandas as pd
from database import queries
from ui import section_card


def render_page():
    st.header('03 - Analistas')
    st.write('Registra a los analistas responsables de los muestreos.')

    with section_card('Registrar analista', 'Agrega un analista y su información de contacto para los registros.'):
        with st.form('form_analista'):
            nombre = st.text_input('Nombre')
            apellido = st.text_input('Apellido')
            cargo = st.text_input('Cargo')
            contacto = st.text_input('Contacto')
            submitted = st.form_submit_button('Guardar analista')

            if submitted:
                if not nombre.strip() or not apellido.strip():
                    st.error('Nombre y apellido son obligatorios.')
                else:
                    queries.insert_analista(nombre.strip(), apellido.strip(), cargo.strip(), contacto.strip())
                    st.success('Analista guardado correctamente.')
                    st.rerun()

    st.markdown('---')
    with section_card('Listado de analistas', 'Consulta a los analistas ya registrados en el sistema.'):
        analistas = pd.DataFrame(queries.get_analistas())
        if analistas.empty:
            st.info('No hay analistas registrados.')
        else:
            st.dataframe(analistas)
