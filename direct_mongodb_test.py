from pymongo import MongoClient

def test_connection():
    # URI de conexión
    uri = "mongodb+srv://fabianhurtado:fabian0594@peasonflowdb.zvucsvh.mongodb.net/"
    
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
    
    # Crear nueva base de datos y colección
    db_name = "PeasonFlow"
    coll_name = "test_collection"
    
    print(f"\nCreando colección '{coll_name}' en base de datos '{db_name}'")
    
    # En MongoDB, las bases de datos y colecciones se crean cuando se insertan datos
    db = client[db_name]
    collection = db[coll_name]
    
    # Insertar un documento
    result = collection.insert_one({"test": True, "message": "Conexión exitosa", "value": 42})
    print(f"Documento insertado con ID: {result.inserted_id}")
    
    # Listar colecciones para verificar
    print(f"\nColecciones en {db_name}:")
    collections = db.list_collection_names()
    for coll in collections:
        print(f"- {coll}")
    
    # Leer el documento insertado
    doc = collection.find_one({"test": True})
    print("\nDocumento recuperado:")
    print(doc)
    
    # Cerrar conexión
    client.close()
    print("\nConexión cerrada")

if __name__ == "__main__":
    try:
        test_connection()
        print("\n¡Test completado con éxito!")
    except Exception as e:
        print(f"\nError: {e}") 