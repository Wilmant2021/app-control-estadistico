import importlib
import streamlit as st
from database.connection import init_db
from database import queries
from database.seed import seed_database

st.set_page_config(
    page_title='CEC Agroindustrial',
    page_icon='🌿',
    layout='wide',
    initial_sidebar_state='expanded'
)

init_db()

PAGES = {
    '01 - Configuración': 'app_pages.01_configuracion',
    '02 - Productos': 'app_pages.02_productos',
    '03 - Analistas': 'app_pages.03_analistas',
    '04 - Registro de Muestras': 'app_pages.04_registro_muestras',
    '05 - Control de Variables': 'app_pages.05_control_variables',
    '06 - Control de Atributos': 'app_pages.06_control_atributos',
    '07 - Reportes': 'app_pages.07_reportes'
}

st.sidebar.title('CEC Agroindustrial')
st.sidebar.markdown('### Navegación')
st.sidebar.write('Selecciona una sección para gestionar la calidad y los controles estadísticos.')
selected_page = st.sidebar.radio('Seleccionar sección', list(PAGES.keys()), label_visibility='collapsed')

st.markdown('# CEC Agroindustrial')
st.markdown('### Plataforma de control estadístico para procesos agroindustriales')

# Seed de datos de ejemplo cuando la base está vacía
if len(queries.get_productos()) == 0 and len(queries.get_analistas()) == 0:
    seed_database()
st.markdown('Usa la barra lateral para acceder a la gestión de productos, analistas, muestras y generar tus gráficos o reportes.')
st.markdown('---')

try:
    page_module = importlib.import_module(PAGES[selected_page])
    page_module.render_page()
except Exception as error:
    st.error(f'Error al cargar la página: {error}')
