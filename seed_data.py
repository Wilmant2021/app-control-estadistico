import os
import numpy as np
from database.connection import init_db, DB_FILE
from database import queries


def generate_sample_data():
    if DB_FILE.exists():
        os.remove(DB_FILE)

    init_db()

    # Usuarios de prueba
    queries.create_user('admin', 'admin123', rol='admin')
    queries.create_user('analista', 'analista123', rol='analista')

    # Analistas
    analista1 = queries.insert_analista('Carla', 'Díaz', 'Ingeniera de Calidad', 'carla.diaz@cec.com')
    analista2 = queries.insert_analista('Luis', 'Torres', 'Supervisor de Campo', 'luis.torres@cec.com')

    # Productos
    producto1 = queries.insert_producto('Maracuyá', 'fruta', 'Sweet', 'g', 'Fruta para jugos y concentrados')
    producto2 = queries.insert_producto('Tomate', 'hortaliza', 'Cherry', 'g', 'Tomate fresco para ensaladas')
    producto3 = queries.insert_producto('Aloe vera', 'planta_medicinal', 'Barbadensis', 'pH', 'Gel para cosmética natural')

    # Variables de control
    variable1 = queries.insert_variable_config(producto1, 'Peso del fruto', 'continua', 320.0, 180.0, 250.0, 5)
    variable2 = queries.insert_variable_config(producto2, 'Brix', 'continua', 7.0, 4.0, 5.5, 5)
    variable3 = queries.insert_variable_config(producto3, 'pH del gel', 'continua', 5.5, 4.5, 5.0, 5)

    # Atributos de control
    atributo1 = queries.insert_atributo_config(producto1, 'Frutos dañados', 'P', 100)
    atributo2 = queries.insert_atributo_config(producto2, 'Defectos por lote', 'NP', 100)
    atributo3 = queries.insert_atributo_config(producto3, 'Unidades con manchas', 'C', 30)

    # Muestras variables
    rng = np.random.default_rng(123)
    valores_peso = rng.normal(loc=250, scale=25, size=50).round(1).tolist()
    muestra1 = queries.insert_muestra(producto1, analista1, 5, 'Lote A1', 'Campo Norte', 'Muestreo de peso de maracuyá', '2026-05-01 08:00:00')
    for idx, valor in enumerate(valores_peso, start=1):
        queries.insert_medicion_variable(muestra1, variable1, idx, float(valor))

    valores_brix = rng.normal(loc=5.2, scale=0.6, size=55).round(2).tolist()
    muestra2 = queries.insert_muestra(producto2, analista2, 5, 'Lote B3', 'Invernadero', 'Muestreo de Brix en tomate cherry', '2026-05-02 09:15:00')
    for idx, valor in enumerate(valores_brix, start=1):
        queries.insert_medicion_variable(muestra2, variable2, idx, float(valor))

    valores_ph = rng.normal(loc=5.0, scale=0.15, size=55).round(3).tolist()
    muestra3 = queries.insert_muestra(producto3, analista1, 5, 'Lote C2', 'Cultivo Sombra', 'Muestreo de pH de aloe vera', '2026-05-03 10:30:00')
    for idx, valor in enumerate(valores_ph, start=1):
        queries.insert_medicion_variable(muestra3, variable3, idx, float(valor))

    # Atributos de control
    atributo1 = queries.insert_atributo_config(producto1, 'Frutos dañados', 'P', 100)
    atributo2 = queries.insert_atributo_config(producto2, 'Defectos por lote', 'NP', 100)
    atributo3 = queries.insert_atributo_config(producto3, 'Unidades con manchas', 'C', 30)
    atributo4 = queries.insert_atributo_config(producto1, 'Defectos por unidad', 'U', 100)

    # Muestras de atributos
    muestra_attr1 = queries.insert_muestra(producto1, analista2, 1, 'Lote A2', 'Campo Sur', 'Conteo daño por fruto', '2026-05-04 11:00:00')
    for n_defectuosos in [4, 6, 3, 5, 7, 4, 5, 6, 4, 5, 3, 7, 8, 6, 4, 5, 3, 6, 7, 5, 4, 6, 5, 7, 5, 4, 6, 5, 4, 6]:
        queries.insert_medicion_atributo(muestra_attr1, atributo1, 100, int(n_defectuosos))

    muestra_attr2 = queries.insert_muestra(producto2, analista1, 1, 'Lote B4', 'Huerto Este', 'Conteo defectos por lote', '2026-05-05 12:45:00')
    for n_defectuosos in [12, 9, 15, 10, 7, 13, 11, 14, 10, 9, 8, 15, 12, 11, 13, 10, 12, 14, 9, 11, 13, 12, 10, 9, 14, 13, 11, 12, 10, 13]:
        queries.insert_medicion_atributo(muestra_attr2, atributo2, 100, int(n_defectuosos))

    muestra_attr3 = queries.insert_muestra(producto3, analista2, 1, 'Lote C4', 'Cultivo Interior', 'Conteo manchas en aloe', '2026-05-06 14:00:00')
    for n_defectuosos in [1, 2, 0, 3, 2, 1, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 2, 3, 1, 0, 2, 1, 3, 2, 1, 2, 3, 1, 2]:
        queries.insert_medicion_atributo(muestra_attr3, atributo3, 30, int(n_defectuosos))

    muestra_attr4 = queries.insert_muestra(producto1, analista1, 1, 'Lote A5', 'Campo Norte', 'Conteo defectos por unidad', '2026-05-07 08:00:00')
    u_entries = [
        (35, 5), (40, 7), (28, 4), (32, 6), (45, 8), (30, 5), (38, 6), (42, 7), (31, 5), (29, 4),
        (33, 5), (36, 6), (37, 6), (34, 5), (41, 7), (39, 6), (27, 4), (43, 8), (44, 8), (26, 3),
        (30, 5), (32, 5), (28, 4), (35, 6), (37, 5), (40, 7), (33, 5), (31, 4), (42, 8), (29, 4)
    ]
    for n_inspeccionados, n_defectuosos in u_entries:
        queries.insert_medicion_atributo(muestra_attr4, atributo4, n_inspeccionados, int(n_defectuosos))

    print('Se cargaron datos de prueba en cec_agro.db con éxito.')


if __name__ == '__main__':
    generate_sample_data()
