import importlib
import streamlit as st
from database.connection import init_db

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

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #071427 0%, #0f172a 100%);
        color: #f8fafc;
        transition: background-color 200ms ease;
    }
    /* Soften the top header / nav area to blend with dark mode */
    .css-18e3th9,
    .css-1d391kg,
    .css-1v0mbdj {
        background: linear-gradient(90deg, rgba(7,20,39,0.95) 0%, rgba(11,26,42,0.85) 100%);
        border-bottom: 1px solid rgba(255,255,255,0.03);
        box-shadow: 0 6px 18px rgba(2,6,23,0.45);
    }
    .stSidebar {
        background: linear-gradient(180deg, rgba(7,20,39,0.98), rgba(15,23,42,0.98));
    }
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 20px;
        padding: 22px 24px 24px;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.4);
    }
    div[data-testid="stForm"] .stButton>button {
        background-color: #14b8a6;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 1.2rem;
    }
    div[data-testid="stForm"] .stButton>button:hover {
        background-color: #0f766e;
    }
    div[data-testid="stForm"] input,
    div[data-testid="stForm"] textarea,
    div[data-testid="stForm"] select {
        background: #111827;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 12px;
    }
    .section-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 24px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.4);
    }
    .section-card-header h2 {
        margin: 0 0 8px;
        color: #f8fafc;
        font-size: 1.65rem;
    }
    .section-card-header p {
        margin: 0 0 18px;
        color: #94a3b8;
        line-height: 1.6;
    }
    .stButton>button {
        background-color: #14b8a6;
        color: white;
    }
    .stButton>button:hover {
        background-color: #0d9488;
    }
    h1, h2, h3, h4, h5 {
        color: #f8fafc;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    /* Make the main header less harsh */
    .stMarkdown h1 {
        background: linear-gradient(90deg, rgba(20,184,166,0.06), rgba(99,102,241,0.03));
        padding: 18px 22px;
        border-radius: 12px;
        display: inline-block;
    }
    .stAlert {
        background-color: #1f2937;
        border-color: rgba(148, 163, 184, 0.18);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('# CEC Agroindustrial')
st.markdown('### Plataforma de control estadístico para procesos agroindustriales')
st.markdown('Usa la barra lateral para acceder a la gestión de productos, analistas, muestras y generar tus gráficos o reportes.')
st.markdown('---')

try:
    page_module = importlib.import_module(PAGES[selected_page])
    page_module.render_page()
except Exception as error:
    st.error(f'Error al cargar la página: {error}')
