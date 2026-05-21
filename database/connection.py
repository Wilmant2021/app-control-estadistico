import sqlite3
from pathlib import Path

DB_FILE = Path('cec_agro.db')

DDL_SCRIPT = '''
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS PRODUCTO (
    id_producto   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    tipo          TEXT NOT NULL CHECK(tipo IN ('fruta','hortaliza','planta_medicinal')),
    variedad      TEXT,
    unidad_medida TEXT NOT NULL,
    descripcion   TEXT
);

CREATE TABLE IF NOT EXISTS ANALISTA (
    id_analista INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    apellido    TEXT NOT NULL,
    cargo       TEXT,
    contacto    TEXT
);

CREATE TABLE IF NOT EXISTS VARIABLE_CONFIG (
    id_variable    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto    INTEGER NOT NULL REFERENCES PRODUCTO(id_producto),
    nombre_variable TEXT NOT NULL,
    tipo_dato       TEXT DEFAULT 'continua',
    lcs             REAL,
    lci             REAL,
    valor_nominal   REAL,
    tam_subgrupo    INTEGER DEFAULT 5
);

CREATE TABLE IF NOT EXISTS ATRIBUTO_CONFIG (
    id_atributo    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto    INTEGER NOT NULL REFERENCES PRODUCTO(id_producto),
    nombre_atributo TEXT NOT NULL,
    tipo_grafico    TEXT NOT NULL CHECK(tipo_grafico IN ('P','NP','C','U')),
    tam_subgrupo    INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS CATALOGO_VARIABLES (
    id_catalogo_variable INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_variable      TEXT NOT NULL UNIQUE,
    tipo_dato            TEXT NOT NULL DEFAULT 'continua',
    tam_subgrupo         INTEGER DEFAULT 5
);

CREATE TABLE IF NOT EXISTS CATALOGO_ATRIBUTOS (
    id_catalogo_atributo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_atributo      TEXT NOT NULL UNIQUE,
    tipo_grafico         TEXT NOT NULL DEFAULT 'P'
);

CREATE TABLE IF NOT EXISTS MUESTRA (
    id_muestra    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto   INTEGER NOT NULL REFERENCES PRODUCTO(id_producto),
    id_analista   INTEGER NOT NULL REFERENCES ANALISTA(id_analista),
    fecha_hora    DATETIME NOT NULL DEFAULT (datetime('now','localtime')),
    num_subgrupo  INTEGER NOT NULL,
    lote          TEXT,
    origen        TEXT,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS MEDICION_VARIABLE (
    id_medicion     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_muestra      INTEGER NOT NULL REFERENCES MUESTRA(id_muestra),
    id_variable     INTEGER NOT NULL REFERENCES VARIABLE_CONFIG(id_variable),
    num_observacion INTEGER NOT NULL,
    valor           REAL NOT NULL,
    es_atipico      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS MEDICION_ATRIBUTO (
    id_med_atrib    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_muestra      INTEGER NOT NULL REFERENCES MUESTRA(id_muestra),
    id_atributo     INTEGER NOT NULL REFERENCES ATRIBUTO_CONFIG(id_atributo),
    n_inspeccionados INTEGER NOT NULL,
    n_defectuosos    INTEGER NOT NULL DEFAULT 0,
    fuera_control    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS USUARIO (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('admin','analista'))
);
'''


def create_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def populate_defaults(conn):
    default_variables = [
        ('Peso (g)', 'continua', 5),
        ('Diámetro (cm)', 'continua', 5),
        ('Grados Brix (°Bx)', 'continua', 5),
        ('pH', 'continua', 5),
        ('Firmeza', 'continua', 5),
        ('Color', 'continua', 5),
        ('Textura', 'continua', 5),
        ('Altura de la planta (cm)', 'continua', 5),
        ('Longitud de hojas (cm)', 'continua', 5),
        ('Ancho de hojas (cm)', 'continua', 5),
        ('Contenido de humedad (%)', 'continua', 5),
        ('Contenido de aceites esenciales (%)', 'continua', 5),
        ('Temperatura de secado (°C)', 'continua', 5),
        ('Actividad de agua (aw)', 'continua', 5),
        ('Contenido de principios activos (mg/g)', 'continua', 5),
        ('Rendimiento del extracto (%)', 'continua', 5)
    ]
    default_atributos = [
        ('Presencia de manchas (P)', 'P'),
        ('Daños por plagas (P)', 'P'),
        ('Golpes o magulladuras (P)', 'P'),
        ('Frutos podridos (P)', 'P'),
        ('Defectos de color (P)', 'P'),
        ('Presencia de enfermedmedades (P)', 'P'),
        ('Daños mecánicos (P)', 'P'),
        ('Contaminación por hongos (P)', 'P'),
        ('Presencia de material extraño (P)', 'P'),
        ('Uniformidad del color (P)', 'P'),
        ('Presencia de insectos (P)', 'P'),
        ('Empaque adecuado (P)', 'P'),
        ('Nivel de limpieza (P)', 'P'),
        ('Cumplimiento BPA (P)', 'P'),
        ('Cumplimiento BPM (P)', 'P')
    ]

    if conn.execute('SELECT COUNT(*) FROM CATALOGO_VARIABLES').fetchone()[0] == 0:
        conn.executemany(
            'INSERT INTO CATALOGO_VARIABLES (nombre_variable, tipo_dato, tam_subgrupo) VALUES (?, ?, ?)',
            default_variables
        )

    if conn.execute('SELECT COUNT(*) FROM CATALOGO_ATRIBUTOS').fetchone()[0] == 0:
        conn.executemany(
            'INSERT INTO CATALOGO_ATRIBUTOS (nombre_atributo, tipo_grafico) VALUES (?, ?)',
            default_atributos
        )


def init_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.executescript(DDL_SCRIPT)
    populate_defaults(conn)
    conn.commit()
    conn.close()
