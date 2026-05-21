-- Database schema for the new inspection system
-- This schema matches the photo-based model: analistas, productos, muestras, configuraciones y mediciones.

CREATE TABLE IF NOT EXISTS analistas (
    id_analista INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    cargo TEXT,
    contacto TEXT
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT,
    variedad TEXT,
    unidad_medida TEXT,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS muestras (
    id_muestra INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    id_analista INTEGER NOT NULL,
    fecha_hora TEXT NOT NULL,
    num_subgrupo INTEGER,
    lote TEXT,
    origen TEXT,
    observaciones TEXT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_analista) REFERENCES analistas(id_analista)
);

CREATE TABLE IF NOT EXISTS variable_config (
    id_variable INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    nombre_variable TEXT NOT NULL,
    tipo_dato TEXT,
    lcs REAL,
    lci REAL,
    valor_nominal REAL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE IF NOT EXISTS atributo_config (
    id_atributo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    nombre_atributo TEXT NOT NULL,
    tipo_grafico TEXT NOT NULL,
    tam_subgrupo INTEGER,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE IF NOT EXISTS medicion_variable (
    id_medicion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_muestra INTEGER NOT NULL,
    id_variable INTEGER NOT NULL,
    valor REAL NOT NULL,
    FOREIGN KEY (id_muestra) REFERENCES muestras(id_muestra),
    FOREIGN KEY (id_variable) REFERENCES variable_config(id_variable)
);

CREATE TABLE IF NOT EXISTS medicion_atributo (
    id_med_atrib INTEGER PRIMARY KEY AUTOINCREMENT,
    id_muestra INTEGER NOT NULL,
    id_atributo INTEGER NOT NULL,
    n_inspeccionados INTEGER NOT NULL,
    n_defectuosos INTEGER NOT NULL,
    FOREIGN KEY (id_muestra) REFERENCES muestras(id_muestra),
    FOREIGN KEY (id_atributo) REFERENCES atributo_config(id_atributo)
);
