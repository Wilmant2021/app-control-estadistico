from database.db_manager import DBManager
import numpy as np

def generate_sample_data():
    db = DBManager()
    
    # 1. Variable: pH en Sábila
    ph_data = np.random.normal(loc=4.5, scale=0.2, size=30).tolist()
    db.guardar_inspeccion(
        producto="Sábila (Aloe vera)",
        tipo_control="Variable (Numérico)",
        nombre_variable="pH del Gel",
        analista="Sistema Demo",
        unidades="pH",
        datos=ph_data
    )
    
    # 2. Variable: Peso de Aguacate
    peso_data = np.random.normal(loc=250, scale=15, size=25).tolist()
    db.guardar_inspeccion(
        producto="Aguacate",
        tipo_control="Variable (Numérico)",
        nombre_variable="Peso Fruto",
        analista="Sistema Demo",
        unidades="g",
        datos=peso_data
    )
    
    # 3. Atributo: Manchas en Mango (Defectos por lote de 100)
    manchas_data = np.random.poisson(lam=5, size=20).tolist()
    db.guardar_inspeccion(
        producto="Mango",
        tipo_control="Atributo (Defectos)",
        nombre_variable="Manchas por lote",
        analista="Sistema Demo",
        unidades="Defectos",
        datos=manchas_data
    )

    print("Datos de ejemplo generados correctamente.")

if __name__ == "__main__":
    generate_sample_data()
