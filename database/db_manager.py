import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

class DBManager:
    def __init__(self, db_path='database/quality_control.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla para trazabilidad y datos de inspección
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inspecciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT NOT NULL,
                tipo_control TEXT NOT NULL, -- 'Variable' o 'Atributo'
                nombre_variable TEXT NOT NULL,
                analista TEXT NOT NULL,
                unidades TEXT, -- cm, g, %, etc.
                datos_json TEXT NOT NULL, -- Datos en formato JSON
                subgrupos INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def guardar_inspeccion(self, producto, tipo_control, nombre_variable, analista, unidades, datos):
        """Guarda una nueva inspección en la base de datos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        datos_json = json.dumps(datos)
        cursor.execute('''
            INSERT INTO inspecciones (producto, tipo_control, nombre_variable, analista, unidades, datos_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (producto, tipo_control, nombre_variable, analista, unidades, datos_json))
        conn.commit()
        conn.close()

    def obtener_inspecciones(self):
        """Retorna todas las inspecciones como un DataFrame de Pandas."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM inspecciones ORDER BY timestamp DESC", conn)
        conn.close()
        return df

    def borrar_inspeccion(self, id_inspeccion):
        """Elimina una inspección por ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inspecciones WHERE id = ?", (id_inspeccion,))
        conn.commit()
        conn.close()
