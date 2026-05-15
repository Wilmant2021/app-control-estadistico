"""
Main application entry point for Streamlit agricultural quality monitoring.
Provides navigation menu and initializes the database.
"""

import streamlit as st
from db.conexion import init_db


def main():
    """Main function to run the Streamlit application."""
    # Initialize database on startup
    init_db()
    
    # Sidebar navigation menu
    st.sidebar.title("Control Estadístico Agrícola")
    page = st.sidebar.radio(
        "Navegación",
        ["Inicio", "Ingreso de Datos", "Gráficos de Control", "Reportes"]
    )
    
    # Page routing
    if page == "Inicio":
        st.title("Bienvenido al Sistema de Monitoreo de Calidad Agrícola")
        st.write("Seleccione una opción del menú lateral para comenzar.")
    elif page == "Ingreso de Datos":
        # TODO: Import and render ingreso_datos page
        st.title("Ingreso de Datos")
    elif page == "Gráficos de Control":
        # TODO: Import and render graficos_control page
        st.title("Gráficos de Control")
    elif page == "Reportes":
        # TODO: Import and render reportes page
        st.title("Reportes")


if __name__ == "__main__":
    main()
