import hashlib
import sqlite3
from database.connection import create_connection


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def _rows_to_dicts(rows):
    return [dict(row) for row in rows] if rows is not None else []


# Usuarios

def create_user(username: str, password: str, rol: str = 'analista') -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO USUARIO (username, password_hash, rol) VALUES (?, ?, ?)',
        (username, hash_password(password), rol)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM USUARIO WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_users():
    conn = create_connection()
    rows = conn.execute('SELECT * FROM USUARIO').fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# Productos

def insert_producto(nombre: str, tipo: str, variedad: str, unidad_medida: str, descripcion: str) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO PRODUCTO (nombre, tipo, variedad, unidad_medida, descripcion) VALUES (?, ?, ?, ?, ?)',
        (nombre, tipo, variedad, unidad_medida, descripcion)
    )
    conn.commit()
    producto_id = cursor.lastrowid
    conn.close()
    return producto_id


def insert_producto_con_configuracion(
    nombre: str,
    tipo: str,
    variedad: str,
    unidad_medida: str,
    descripcion: str,
    catalogo_variables: list[str] | None = None,
    catalogo_atributos: list[str] | None = None,
    variables_personalizadas: list[str] | None = None,
    atributos_personalizados: list[str] | None = None,
) -> int:
    catalogo_variables = catalogo_variables or []
    catalogo_atributos = catalogo_atributos or []
    variables_personalizadas = [v.strip() for v in (variables_personalizadas or []) if v and v.strip()]
    atributos_personalizados = [a.strip() for a in (atributos_personalizados or []) if a and a.strip()]
    todas_variables = list(dict.fromkeys(catalogo_variables + variables_personalizadas))
    todos_atributos = list(dict.fromkeys(catalogo_atributos + atributos_personalizados))

    producto_id = insert_producto(nombre, tipo, variedad, unidad_medida, descripcion)

    for variable in variables_personalizadas:
        insert_catalogo_variable(variable)
    for atributo in atributos_personalizados:
        insert_catalogo_atributo(atributo)

    for variable in todas_variables:
        insert_variable_config(producto_id, variable, 'continua', None, None, None, 5)

    for atributo in todos_atributos:
        insert_atributo_config(producto_id, atributo, 'P', 50)

    return producto_id


def get_productos():
    conn = create_connection()
    rows = conn.execute('SELECT * FROM PRODUCTO ORDER BY nombre').fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_producto_by_id(id_producto: int):
    conn = create_connection()
    row = conn.execute('SELECT * FROM PRODUCTO WHERE id_producto = ?', (id_producto,)).fetchone()
    conn.close()
    return row


# Analistas

def insert_analista(nombre: str, apellido: str, cargo: str, contacto: str) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO ANALISTA (nombre, apellido, cargo, contacto) VALUES (?, ?, ?, ?)',
        (nombre, apellido, cargo, contacto)
    )
    conn.commit()
    analista_id = cursor.lastrowid
    conn.close()
    return analista_id


def get_analistas():
    conn = create_connection()
    rows = conn.execute('SELECT * FROM ANALISTA ORDER BY apellido, nombre').fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_analista_by_id(id_analista: int):
    conn = create_connection()
    row = conn.execute('SELECT * FROM ANALISTA WHERE id_analista = ?', (id_analista,)).fetchone()
    conn.close()
    return row


# Variables y atributos

def insert_variable_config(id_producto: int, nombre_variable: str, tipo_dato: str, lcs: float, lci: float, valor_nominal: float, tam_subgrupo: int) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO VARIABLE_CONFIG (id_producto, nombre_variable, tipo_dato, lcs, lci, valor_nominal, tam_subgrupo) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (id_producto, nombre_variable, tipo_dato, lcs, lci, valor_nominal, tam_subgrupo)
    )
    conn.commit()
    id_variable = cursor.lastrowid
    conn.close()
    return id_variable


def get_variable_config_by_id(id_variable: int):
    conn = create_connection()
    row = conn.execute('SELECT * FROM VARIABLE_CONFIG WHERE id_variable = ?', (id_variable,)).fetchone()
    conn.close()
    return row


def get_variables_by_producto(id_producto: int):
    conn = create_connection()
    rows = conn.execute('SELECT * FROM VARIABLE_CONFIG WHERE id_producto = ? ORDER BY nombre_variable', (id_producto,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def insert_atributo_config(id_producto: int, nombre_atributo: str, tipo_grafico: str, tam_subgrupo: int) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO ATRIBUTO_CONFIG (id_producto, nombre_atributo, tipo_grafico, tam_subgrupo) VALUES (?, ?, ?, ?)',
        (id_producto, nombre_atributo, tipo_grafico, tam_subgrupo)
    )
    conn.commit()
    id_atributo = cursor.lastrowid
    conn.close()
    return id_atributo


def get_atributos_by_producto(id_producto: int):
    conn = create_connection()
    rows = conn.execute('SELECT * FROM ATRIBUTO_CONFIG WHERE id_producto = ? ORDER BY nombre_atributo', (id_producto,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_atributo_by_id(id_atributo: int):
    conn = create_connection()
    row = conn.execute('SELECT * FROM ATRIBUTO_CONFIG WHERE id_atributo = ?', (id_atributo,)).fetchone()
    conn.close()
    return row


def get_catalogo_variables():
    conn = create_connection()
    rows = conn.execute('SELECT * FROM CATALOGO_VARIABLES ORDER BY nombre_variable').fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_catalogo_atributos():
    conn = create_connection()
    rows = conn.execute('SELECT * FROM CATALOGO_ATRIBUTOS ORDER BY nombre_atributo').fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def insert_catalogo_variable(nombre_variable: str, tipo_dato: str = 'continua', tam_subgrupo: int = 5) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR IGNORE INTO CATALOGO_VARIABLES (nombre_variable, tipo_dato, tam_subgrupo) VALUES (?, ?, ?)',
        (nombre_variable, tipo_dato, tam_subgrupo)
    )
    conn.commit()
    catalogo_id = cursor.lastrowid
    conn.close()
    return catalogo_id


def insert_catalogo_atributo(nombre_atributo: str, tipo_grafico: str = 'P') -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR IGNORE INTO CATALOGO_ATRIBUTOS (nombre_atributo, tipo_grafico) VALUES (?, ?)',
        (nombre_atributo, tipo_grafico)
    )
    conn.commit()
    catalogo_id = cursor.lastrowid
    conn.close()
    return catalogo_id


# Muestras y mediciones

def insert_muestra(id_producto: int, id_analista: int, num_subgrupo: int, lote: str, origen: str, observaciones: str, fecha_hora: str = None) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    if fecha_hora:
        cursor.execute(
            'INSERT INTO MUESTRA (id_producto, id_analista, fecha_hora, num_subgrupo, lote, origen, observaciones) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (id_producto, id_analista, fecha_hora, num_subgrupo, lote, origen, observaciones)
        )
    else:
        cursor.execute(
            'INSERT INTO MUESTRA (id_producto, id_analista, num_subgrupo, lote, origen, observaciones) VALUES (?, ?, ?, ?, ?, ?)',
            (id_producto, id_analista, num_subgrupo, lote, origen, observaciones)
        )
    conn.commit()
    muestra_id = cursor.lastrowid
    conn.close()
    return muestra_id


def get_muestras():
    conn = create_connection()
    rows = conn.execute(
        '''SELECT m.*, p.nombre AS producto, a.nombre || ' ' || a.apellido AS analista
           FROM MUESTRA m
           JOIN PRODUCTO p ON p.id_producto = m.id_producto
           JOIN ANALISTA a ON a.id_analista = m.id_analista
           ORDER BY fecha_hora DESC'''
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_muestra_by_id(id_muestra: int):
    conn = create_connection()
    row = conn.execute('SELECT * FROM MUESTRA WHERE id_muestra = ?', (id_muestra,)).fetchone()
    conn.close()
    return row


def insert_medicion_variable(id_muestra: int, id_variable: int, num_observacion: int, valor: float, es_atipico: int = 0) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO MEDICION_VARIABLE (id_muestra, id_variable, num_observacion, valor, es_atipico) VALUES (?, ?, ?, ?, ?)',
        (id_muestra, id_variable, num_observacion, valor, es_atipico)
    )
    conn.commit()
    medicion_id = cursor.lastrowid
    conn.close()
    return medicion_id


def get_mediciones_variables_by_muestra(id_muestra: int):
    conn = create_connection()
    rows = conn.execute(
        'SELECT * FROM MEDICION_VARIABLE WHERE id_muestra = ? ORDER BY num_observacion', (id_muestra,)
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def insert_medicion_atributo(id_muestra: int, id_atributo: int, n_inspeccionados: int, n_defectuosos: int, fuera_control: int = 0) -> int:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO MEDICION_ATRIBUTO (id_muestra, id_atributo, n_inspeccionados, n_defectuosos, fuera_control) VALUES (?, ?, ?, ?, ?)',
        (id_muestra, id_atributo, n_inspeccionados, n_defectuosos, fuera_control)
    )
    conn.commit()
    medicion_id = cursor.lastrowid
    conn.close()
    return medicion_id


def get_mediciones_atributos_by_muestra(id_muestra: int):
    conn = create_connection()
    rows = conn.execute(
        'SELECT * FROM MEDICION_ATRIBUTO WHERE id_muestra = ? ORDER BY id_med_atrib', (id_muestra,)
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_muestras_variables():
    conn = create_connection()
    rows = conn.execute(
        '''SELECT DISTINCT m.id_muestra, p.nombre AS producto, vc.id_variable, vc.nombre_variable, m.fecha_hora, m.num_subgrupo
           FROM MEDICION_VARIABLE mv
           JOIN MUESTRA m ON m.id_muestra = mv.id_muestra
           JOIN VARIABLE_CONFIG vc ON vc.id_variable = mv.id_variable
           JOIN PRODUCTO p ON p.id_producto = m.id_producto
           ORDER BY m.fecha_hora DESC'''
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_muestras_atributos():
    conn = create_connection()
    rows = conn.execute(
        '''SELECT DISTINCT m.id_muestra, p.nombre AS producto, ac.id_atributo, ac.nombre_atributo, ac.tipo_grafico, ac.tam_subgrupo, m.fecha_hora
           FROM MEDICION_ATRIBUTO ma
           JOIN MUESTRA m ON m.id_muestra = ma.id_muestra
           JOIN ATRIBUTO_CONFIG ac ON ac.id_atributo = ma.id_atributo
           JOIN PRODUCTO p ON p.id_producto = m.id_producto
           ORDER BY m.fecha_hora DESC'''
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)
