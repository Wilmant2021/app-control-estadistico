-- Database schema for agricultural quality monitoring system
-- Defines tables for products, sessions, variable measurements, and attribute inspections

-- Products table: stores agricultural products being monitored
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table: stores measurement sessions
CREATE TABLE IF NOT EXISTS sesiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Variable measurements table: stores continuous variable measurements
CREATE TABLE IF NOT EXISTS mediciones_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sesion_id INTEGER NOT NULL,
    variable_nombre TEXT NOT NULL,
    valor REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones(id)
);

-- Attribute inspections table: stores attribute-based inspections
CREATE TABLE IF NOT EXISTS inspecciones_atributos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sesion_id INTEGER NOT NULL,
    atributo_nombre TEXT NOT NULL,
    resultado TEXT NOT NULL,
    defecto TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones(id)
);
