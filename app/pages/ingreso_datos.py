"""
Data entry page for the application.
Provides forms to input products, sessions, measurements, and inspections.
"""

import streamlit as st
from db.crud import create_producto, create_sesion, create_medicion_variable, create_inspeccion_atributo


def render_producto_form():
    """
    Renders a form to create a new product.
    """
    pass


def render_sesion_form():
    """
    Renders a form to create a new measurement session.
    """
    pass


def render_medicion_variable_form():
    """
    Renders a form to input variable measurements.
    """
    pass


def render_inspeccion_atributo_form():
    """
    Renders a form to input attribute inspections.
    """
    pass


def main():
    """
    Main function to render the data entry page.
    """
    st.title("Ingreso de Datos")
    
    # Tab navigation for different data entry types
    tab1, tab2, tab3, tab4 = st.tabs(["Productos", "Sesiones", "Mediciones Variables", "Inspecciones Atributos"])
    
    with tab1:
        render_producto_form()
    
    with tab2:
        render_sesion_form()
    
    with tab3:
        render_medicion_variable_form()
    
    with tab4:
        render_inspeccion_atributo_form()


if __name__ == "__main__":
    main()
