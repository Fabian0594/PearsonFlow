import sys
from pymongo import MongoClient
import pandas as pd

def connect_to_mongodb():
    # URI de conexión
    uri = "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/"
    
    try:
        # Conectar a MongoDB
        print("Conectando a MongoDB Atlas...")
        client = MongoClient(uri)
        
        # Probar conexión
        print("Verificando conexión...")
        client.admin.command('ping')
        print("Conexión exitosa!")
        
        # Listar bases de datos disponibles
        print("\nBases de datos disponibles:")
        dbs = client.list_database_names()
        for db in dbs:
            print(f"- {db}")
        
        # Seleccionar base de datos
        db_name = "PeasonFlow"
        db = client[db_name]
        
        # Listar colecciones
        print(f"\nColecciones en {db_name}:")
        collections = db.list_collection_names()
        if collections:
            for i, coll in enumerate(collections, 1):
                count = db[coll].count_documents({})
                print(f"{i}. {coll} ({count} documentos)")
            
            # Seleccionar una colección
            if len(collections) == 1:
                collection_name = collections[0]
            else:
                print("\nSeleccione una colección (número):")
                selection = input("> ")
                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(collections):
                        collection_name = collections[idx]
                    else:
                        print("Selección inválida. Usando la primera colección.")
                        collection_name = collections[0]
                except ValueError:
                    print("Entrada inválida. Usando la primera colección.")
                    collection_name = collections[0]
            
            # Mostrar datos de la colección
            collection = db[collection_name]
            documents = list(collection.find(limit=10))
            
            if documents:
                # Convertir a DataFrame para mejor visualización
                df = pd.DataFrame(documents)
                if '_id' in df.columns:
                    df = df.drop('_id', axis=1)
                
                print(f"\nMostrando hasta 10 documentos de '{collection_name}':")
                print(df)
                
                # Mostrar estadísticas básicas
                print("\nEstadísticas básicas:")
                numeric_cols = df.select_dtypes(include=['number']).columns
                if not numeric_cols.empty:
                    print(df[numeric_cols].describe())
                else:
                    print("No hay columnas numéricas para análisis estadístico")
                
                print(f"\nTotal de documentos en la colección: {collection.count_documents({})}")
            else:
                print(f"La colección '{collection_name}' está vacía")
        else:
            print("No hay colecciones en esta base de datos")
            
            # Crear una colección de prueba
            print("\n¿Desea crear una colección de prueba? (s/n)")
            response = input("> ")
            if response.lower() in ["s", "si", "y", "yes"]:
                collection_name = "datos_prueba"
                collection = db[collection_name]
                
                # Crear datos de prueba
                import numpy as np
                # Crear un DataFrame con datos aleatorios
                np.random.seed(42)
                df = pd.DataFrame({
                    'nombre': [f'Usuario{i}' for i in range(1, 11)],
                    'edad': np.random.randint(18, 65, 10),
                    'salario': np.random.randint(30000, 100000, 10),
                    'activo': np.random.choice([True, False], 10),
                })
                
                # Insertar datos
                records = df.to_dict('records')
                result = collection.insert_many(records)
                
                print(f"Se han insertado {len(result.inserted_ids)} documentos en '{collection_name}'")
                print("\nDocumentos insertados:")
                print(df)
        
        # Cerrar conexión
        client.close()
        print("\nConexión cerrada")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    connect_to_mongodb() 