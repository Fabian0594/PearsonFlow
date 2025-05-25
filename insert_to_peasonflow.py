from pymongo import MongoClient
import pandas as pd
import numpy as np
import sys

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
    try:
        print("Intentando conectar a MongoDB Atlas...")
        # Conectar a MongoDB Atlas
        conn_string = "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/"
        client = MongoClient(conn_string, serverSelectionTimeoutMS=5000)
        
        # Verificar la conexión
        print("Verificando conexión...")
        client.admin.command('ping')
        print("¡Conexión exitosa a MongoDB Atlas!")
        
        # Listar bases de datos
        print("\nBases de datos disponibles:")
        dbs = client.list_database_names()
        for db_name in dbs:
            print(f"- {db_name}")
            
        # Seleccionar la base de datos correcta
        db_name = "PeasonFlow"
        print(f"\nSeleccionando/creando base de datos: {db_name}")
        db = client[db_name]
        
        # Crear una colección de prueba
        collection_name = "datos_prueba"
        print(f"Seleccionando/creando colección: {collection_name}")
        collection = db[collection_name]
        
        # Crear datos de prueba
        print("Generando datos de prueba...")
        df = create_test_data()
        
        # Convertir DataFrame a lista de diccionarios
        records = df.to_dict('records')
        
        # Eliminar la colección si ya existe
        collection.drop()
        print(f"Colección {collection_name} eliminada (si existía)")
        
        # Insertar los datos
        print(f"Insertando {len(records)} documentos...")
        result = collection.insert_many(records)
        
        # Mostrar resultado
        print(f"\n¡Éxito! Se han insertado {len(result.inserted_ids)} documentos en la colección '{collection_name}'")
        
        # Mostrar un ejemplo de documento
        print("\nEjemplo de documento:")
        print(collection.find_one())
        
        # Listar colecciones para confirmar
        collections = db.list_collection_names()
        print(f"\nColecciones en {db_name}:")
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"- {coll} ({count} documentos)")
        
        # Cerrar conexión
        client.close()
        print("\nConexión cerrada")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return False
        
    return True

if __name__ == "__main__":
    try:
        success = insert_to_mongodb()
        if success:
            print("\n¡Datos insertados correctamente en PeasonFlow!")
        else:
            print("\nOcurrió un error al insertar los datos.")
    except Exception as e:
        print(f"Error inesperado: {str(e)}", file=sys.stderr) 