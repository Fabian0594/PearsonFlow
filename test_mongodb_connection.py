from pymongo import MongoClient
import sys

def test_mongodb_connection():
    """Test simple de conexión a MongoDB Atlas"""
    try:
        # Conectar a MongoDB Atlas
        print("Intentando conectar a MongoDB Atlas...")
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
        
        # Verificar si existe la base de datos PeasonFlow
        if "PeasonFlow" in dbs:
            print("\nLa base de datos PeasonFlow existe")
            db = client["PeasonFlow"]
            
            # Listar colecciones
            collections = db.list_collection_names()
            if collections:
                print("Colecciones disponibles:")
                for coll in collections:
                    print(f"- {coll}")
            else:
                print("No hay colecciones en PeasonFlow")
                
            # Crear colección de prueba
            print("\nCreando colección de prueba...")
            collection = db["test_collection"]
            result = collection.insert_one({"test": "data", "value": 123})
            print(f"Documento insertado con ID: {result.inserted_id}")
            
            # Verificar que se haya creado
            print("\nVerificando colecciones después de inserción:")
            collections = db.list_collection_names()
            for coll in collections:
                print(f"- {coll}")
        else:
            print("\nLa base de datos PeasonFlow no existe")
            print("Creando base de datos PeasonFlow...")
            db = client["PeasonFlow"]
            collection = db["test_collection"]
            result = collection.insert_one({"test": "data", "value": 123})
            print(f"Documento insertado con ID: {result.inserted_id}")
            
            # Verificar que se haya creado
            print("\nVerificando bases de datos después de inserción:")
            dbs = client.list_database_names()
            for db_name in dbs:
                print(f"- {db_name}")
        
    except Exception as e:
        print(f"Error al conectar a MongoDB Atlas: {e}", file=sys.stderr)
        return False
    finally:
        if 'client' in locals():
            client.close()
            print("\nConexión cerrada")
    
    return True

if __name__ == "__main__":
    test_mongodb_connection() 