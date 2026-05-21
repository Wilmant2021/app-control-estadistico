# CEC Agroindustrial - Control Estadístico

Aplicación web para gestión de control estadístico de calidad en procesos agroindustriales.

## 📋 Características

- 📊 Configuración de productos y parámetros de control
- 👥 Gestión de analistas
- 📝 Registro de muestras de control
- 📈 Control de variables (gráficos de control, capacidad de proceso)
- 🏷️ Control de atributos
- 📄 Generación de reportes en Excel y PowerPoint
- 📉 Análisis estadísticos avanzados

## 🛠️ Requisitos

- Python 3.8 o superior
- pip o conda

## 🚀 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/Wilmant2021/app-control-estadistico.git
cd app-control-estadistico
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## 🌐 Despliegue en Streamlit Cloud

### Pasos:
1. Pushear los cambios a GitHub (este repositorio)
2. Ir a [Streamlit Cloud](https://streamlit.io/cloud)
3. Crear una nueva app y seleccionar este repositorio
4. Seleccionar `app.py` como archivo principal
5. ¡Listo! Tu app estará online en minutos

**Nota**: La app será accesible desde cualquier lugar con el enlace generado por Streamlit Cloud.

## 📦 Estructura del Proyecto

```
├── app.py                 # Archivo principal
├── requirements.txt       # Dependencias
├── database/              # Gestión de base de datos
│   ├── connection.py
│   ├── db_manager.py
│   └── queries.py
├── app_pages/             # Páginas de la aplicación
│   ├── 01_configuracion.py
│   ├── 02_productos.py
│   ├── 03_analistas.py
│   ├── 04_registro_muestras.py
│   ├── 05_control_variables.py
│   ├── 06_control_atributos.py
│   └── 07_reportes.py
├── logic/                 # Lógica de negocio
│   └── stats.py
└── modules/               # Módulos adicionales
    ├── estadisticas.py
    ├── exportacion.py
    └── graficos.py
```

## 📝 Variables de Entorno

Si necesitas usar variables secretas en producción, crea un archivo `.streamlit/secrets.toml` (consulta `.streamlit/secrets.toml.example`).

## 🔗 Enlaces

- [Documentación de Streamlit](https://docs.streamlit.io)
- [GitHub del Proyecto](https://github.com/Wilmant2021/app-control-estadistico)

## 👤 Autor

Proyecto de ingeniería industrial - Control Estadístico de Calidad

---

**¿Preguntas o sugerencias?** Abre un issue en el repositorio.
