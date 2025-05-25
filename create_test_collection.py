from pymongo import MongoClient
import pandas as pd
import numpy as np

def create_test_data():
    """Crear datos de prueba para la colección de MongoDB"""
    # Crear un DataFrame con datos aleatorios
    np.random.seed(42)
    df = pd.DataFrame({
        'nombre': [f'Usuario{i}' for i in range(1, 51)],
        'edad': np.random.randint(18, 65, 50),
        'salario': np.random.randint(30000, 100000, 50),
        'puntuacion': np.random.uniform(0, 10, 50).round(2),
        'activo': np.random.choice([True, False], 50),
        'fecha_registro': pd.date_range(start='2023-01-01', periods=50).strftime('%Y-%m-%d').tolist()
    })
    return df

def insert_to_mongodb():
    """Insertar datos de prueba en MongoDB"""
    # Conectar a MongoDB Atlas
    conn_string = "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/"
    client = MongoClient(conn_string)
    
    # Seleccionar la base de datos
    db = client["PeasonFlow"]
    
    # Crear una colección de prueba
    collection = db["datos_prueba"]
    
    # Crear datos de prueba
    df = create_test_data()
    
    # Convertir DataFrame a lista de diccionarios
    records = df.to_dict('records')
    
    # Eliminar la colección si ya existe
    collection.drop()
    
    # Insertar los datos
    result = collection.insert_many(records)
    
    # Mostrar resultado
    print(f"Se han insertado {len(result.inserted_ids)} documentos en la colección 'datos_prueba'")
    
    # Mostrar un ejemplo de documento
    print("\nEjemplo de documento:")
    print(collection.find_one())
    
    # Cerrar conexión
    client.close()

if __name__ == "__main__":
    try:
        insert_to_mongodb()
        print("\n¡Datos insertados correctamente!")
    except Exception as e:
        print(f"Error al insertar datos: {str(e)}") 