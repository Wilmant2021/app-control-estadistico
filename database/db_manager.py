import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

class DBManager:
    def __init__(self, db_path='database/quality_control.db'):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        return conn

    def _init_db(self):
        """Inicializa la base de datos y crea las tablas si no existen."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analistas (
                id_analista INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cargo TEXT,
                contacto TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT,
                variedad TEXT,
                unidad_medida TEXT,
                descripcion TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS muestras (
                id_muestra INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                id_analista INTEGER NOT NULL,
                fecha_hora TEXT NOT NULL,
                num_subgrupo INTEGER DEFAULT 1,
                lote TEXT,
                origen TEXT,
                observaciones TEXT,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
                FOREIGN KEY (id_analista) REFERENCES analistas(id_analista)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variable_config (
                id_variable INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                nombre_variable TEXT NOT NULL,
                tipo_dato TEXT,
                lcs REAL,
                lci REAL,
                valor_nominal REAL,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS atributo_config (
                id_atributo INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                nombre_atributo TEXT NOT NULL,
                tipo_grafico TEXT NOT NULL,
                tam_subgrupo INTEGER,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicion_variable (
                id_medicion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_muestra INTEGER NOT NULL,
                id_variable INTEGER NOT NULL,
                valor REAL NOT NULL,
                FOREIGN KEY (id_muestra) REFERENCES muestras(id_muestra),
                FOREIGN KEY (id_variable) REFERENCES variable_config(id_variable)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicion_atributo (
                id_med_atrib INTEGER PRIMARY KEY AUTOINCREMENT,
                id_muestra INTEGER NOT NULL,
                id_atributo INTEGER NOT NULL,
                n_inspeccionados INTEGER NOT NULL,
                n_defectuosos INTEGER NOT NULL,
                FOREIGN KEY (id_muestra) REFERENCES muestras(id_muestra),
                FOREIGN KEY (id_atributo) REFERENCES atributo_config(id_atributo)
            )
        ''')

        conn.commit()
        conn.close()

    def guardar_analista(self, nombre, apellido, cargo, contacto):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analistas (nombre, apellido, cargo, contacto)
            VALUES (?, ?, ?, ?)
        ''', (nombre, apellido, cargo, contacto))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def guardar_producto(self, nombre, tipo, variedad, unidad_medida, descripcion):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO productos (nombre, tipo, variedad, unidad_medida, descripcion)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, tipo, variedad, unidad_medida, descripcion))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def guardar_variable_config(self, id_producto, nombre_variable, tipo_dato, lcs, lci, valor_nominal):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO variable_config (id_producto, nombre_variable, tipo_dato, lcs, lci, valor_nominal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_producto, nombre_variable, tipo_dato, lcs, lci, valor_nominal))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def guardar_atributo_config(self, id_producto, nombre_atributo, tipo_grafico, tam_subgrupo):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO atributo_config (id_producto, nombre_atributo, tipo_grafico, tam_subgrupo)
            VALUES (?, ?, ?, ?)
        ''', (id_producto, nombre_atributo, tipo_grafico, tam_subgrupo))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def crear_muestra(self, id_producto, id_analista, fecha_hora=None, num_subgrupo=1, lote='', origen='', observaciones=''):
        fecha_hora = fecha_hora or datetime.now().isoformat(sep=' ', timespec='seconds')
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO muestras (id_producto, id_analista, fecha_hora, num_subgrupo, lote, origen, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_producto, id_analista, fecha_hora, num_subgrupo, lote, origen, observaciones))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def guardar_medicion_variable(self, id_muestra, id_variable, valor):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicion_variable (id_muestra, id_variable, valor)
            VALUES (?, ?, ?)
        ''', (id_muestra, id_variable, valor))
        conn.commit()
        conn.close()

    def guardar_medicion_atributo(self, id_muestra, id_atributo, n_inspeccionados, n_defectuosos):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicion_atributo (id_muestra, id_atributo, n_inspeccionados, n_defectuosos)
            VALUES (?, ?, ?, ?)
        ''', (id_muestra, id_atributo, n_inspeccionados, n_defectuosos))
        conn.commit()
        conn.close()

    def obtener_analistas(self):
        conn = self._connect()
        df = pd.read_sql_query('SELECT * FROM analistas ORDER BY nombre, apellido', conn)
        conn.close()
        return df

    def obtener_productos(self):
        conn = self._connect()
        df = pd.read_sql_query('SELECT * FROM productos ORDER BY nombre', conn)
        conn.close()
        return df

    def obtener_variable_configs(self, id_producto=None):
        conn = self._connect()
        if id_producto is not None:
            df = pd.read_sql_query('SELECT * FROM variable_config WHERE id_producto = ? ORDER BY nombre_variable', conn, params=(id_producto,))
        else:
            df = pd.read_sql_query('SELECT * FROM variable_config ORDER BY nombre_variable', conn)
        conn.close()
        return df

    def obtener_atributo_configs(self, id_producto=None):
        conn = self._connect()
        if id_producto is not None:
            df = pd.read_sql_query('SELECT * FROM atributo_config WHERE id_producto = ? ORDER BY nombre_atributo', conn, params=(id_producto,))
        else:
            df = pd.read_sql_query('SELECT * FROM atributo_config ORDER BY nombre_atributo', conn)
        conn.close()
        return df

    def obtener_variable_config_por_id(self, id_variable):
        conn = self._connect()
        df = pd.read_sql_query('SELECT * FROM variable_config WHERE id_variable = ?', conn, params=(id_variable,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    def obtener_atributo_config_por_id(self, id_atributo):
        conn = self._connect()
        df = pd.read_sql_query('SELECT * FROM atributo_config WHERE id_atributo = ?', conn, params=(id_atributo,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    def obtener_muestras(self):
        conn = self._connect()
        df = pd.read_sql_query('''
            SELECT
                m.id_muestra AS muestra_id,
                p.nombre AS producto,
                a.nombre || ' ' || a.apellido AS analista,
                m.fecha_hora,
                m.num_subgrupo,
                m.lote,
                m.origen,
                m.observaciones
            FROM muestras m
            LEFT JOIN productos p ON p.id_producto = m.id_producto
            LEFT JOIN analistas a ON a.id_analista = m.id_analista
            ORDER BY m.fecha_hora DESC
        ''', conn)
        conn.close()
        return df

    def obtener_muestras_variable(self):
        conn = self._connect()
        df = pd.read_sql_query('''
            SELECT DISTINCT
                m.id_muestra AS muestra_id,
                p.nombre AS producto,
                vc.id_variable,
                vc.nombre_variable,
                vc.tipo_dato,
                vc.lci,
                vc.lcs,
                vc.valor_nominal,
                m.fecha_hora,
                m.num_subgrupo,
                m.lote
            FROM medicion_variable mv
            JOIN muestras m ON mv.id_muestra = m.id_muestra
            JOIN variable_config vc ON mv.id_variable = vc.id_variable
            JOIN productos p ON p.id_producto = m.id_producto
            ORDER BY m.fecha_hora DESC
        ''', conn)
        conn.close()
        return df

    def obtener_muestras_atributo(self):
        conn = self._connect()
        df = pd.read_sql_query('''
            SELECT DISTINCT
                m.id_muestra AS muestra_id,
                p.nombre AS producto,
                ac.id_atributo,
                ac.nombre_atributo,
                ac.tipo_grafico,
                ac.tam_subgrupo,
                m.fecha_hora,
                m.lote
            FROM medicion_atributo ma
            JOIN muestras m ON ma.id_muestra = m.id_muestra
            JOIN atributo_config ac ON ma.id_atributo = ac.id_atributo
            JOIN productos p ON p.id_producto = m.id_producto
            ORDER BY m.fecha_hora DESC
        ''', conn)
        conn.close()
        return df

    def obtener_mediciones_variables_por_muestra(self, id_muestra):
        conn = self._connect()
        df = pd.read_sql_query('''
            SELECT valor
            FROM medicion_variable
            WHERE id_muestra = ?
            ORDER BY id_medicion
        ''', conn, params=(id_muestra,))
        conn.close()
        return df

    def obtener_mediciones_atributos_por_muestra(self, id_muestra):
        conn = self._connect()
        df = pd.read_sql_query('''
            SELECT n_inspeccionados, n_defectuosos
            FROM medicion_atributo
            WHERE id_muestra = ?
            ORDER BY id_med_atrib
        ''', conn, params=(id_muestra,))
        conn.close()
        return df
